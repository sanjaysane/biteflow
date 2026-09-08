# Senior Technical Leader review — BiteFlow v3 milestone package

**Verdict: NEEDS WORK**

Reviewer persona: Senior Technical Leader. Rubric: production readiness;
scale/security/compliance/ops gaps that must be disclosed. The question
answered: *what breaks at 10x, and what must be disclosed before the board
approves real paid orders?*

Docs read: `docs/milestones.md`, `docs/business-plan.md`,
`docs/videos/v3-presentation-plan.md`, `docs/SCALE.md`, `SECURITY.md`,
`docs/TROUBLESHOOTING.md`, plus `docs/ARCHITECTURE.md` §10 and
`docs/how-to/supabase-setup.md` (backup note).

Overall: this is the most disclosure-honest package in the review round —
the label system (measured/sourced/assumption), the explicit "what must be
true" lists, and the v3 plan's spoken-transition disclosures are all real.
Honesty, however, is not readiness. The board is being asked to approve a
**real-money pilot** while three money-adjacent controls are still prose.
That is the core of this verdict.

---

## Blockers

### B1 — Board approval would greenlight paid orders before webhook hardening exists (milestones.md § "Known gaps" #2; SECURITY.md §1–3)

Milestones.md lists signature verification, inbound dedupe, and
rate-limiting as "minimum viable hardening is MVP scope." SECURITY.md is
blunter: "Anyone who knows your `/webhook` URL can inject fake
customer/cook messages. This is the single most important thing to fix
before going live." ARCHITECTURE.md §10 confirms none of the three exist.

Expectation violated: MVP *scope* is not MVP *done criteria*. The done
criteria (`docs/milestones.md` § MVP) require "zero lost/duplicate orders
from webhook redelivery (dedupe verified)" — but dedupe is not written, and
the criterion tests the outcome, not the control. A forged "accept" or
screenshot-approval POST (SECURITY.md §1) can fabricate a paid order
against a real cook, and the pilot's entire trust model (cook-verified
screenshots) cannot distinguish a forgery from a customer. For a pilot
handling real rupees, the signature check is not an MVP nice-to-have; it
is a **pre-first-order** gate.

Required disclosure/change: make the board's MVP approval **conditional**:
no real orders until `X-Hub-Signature-256` verification, `wamid` dedupe,
and webhook rate-limiting are implemented and covered by tests, with the
done criterion reworded to "hardening controls implemented and verified"
rather than only "dedupe verified" in the field. To its credit, the v3
presentation plan (§3 Transitions) names this gap verbatim and gives the
two OPEN items spoken airtime — keep that, and have the Ask section state
the condition explicitly.

### B2 — WhatsApp Business Policy review of the trust-based screenshot payment flow is missing from "what must be true" (milestones.md § MVP Risks; business-plan.md §7 risk 3)

Milestones.md names "WhatsApp Business policy / template-approval delays"
as a risk, and business-plan.md §7 risk 3 covers conversation pricing and
suspensions. But neither names the specific policy surface the pilot
lives on: **customers send UPI IDs/payment screenshots and cooks confirm
payments inside a business chat** — i.e., the product's core money loop is
payment coordination over WhatsApp Business. Meta's commerce and
financial-services policies restrict how payments can be solicited and
processed on the platform; a business number whose chats are dominated by
unstructured payment proof may face template rejections, rate limits, or
suspension review. This is a different risk from conversation pricing, and
it is the pilot's single point of regulatory-adjacent failure (there is
no verified rail to fall back on — milestones.md Known gaps #3).

Expectation violated: a production-readiness review must confirm the
*operating model itself* is policy-permitted, not just that templates get
approved. "Counsel confirms the operating model" exists for food safety
(business-plan.md §7 risk 5) but not for the platform the entire product
runs on.

Required: add to milestones.md "What must be true": a documented read of
Meta's WhatsApp Business Policy and Commerce Policy against the
screenshot-verification flow, before pilot cook onboarding.

### B3 — No tested backup/restore path before handling order + payment-state data (supabase-setup.md § "Backups"; business-plan.md §5)

`docs/how-to/supabase-setup.md` notes "Supabase free tier includes daily
backups" and advises a manual backup before migrations. Nowhere in the
milestones, business plan, or ARCHITECTURE.md is there a **restore runbook**,
an RTO/RPO statement, or evidence that a restore has ever been rehearsed.
The database holds orders, payment states, inventory, and customer
sessions — the pilot's money-adjacent state. At 10x cooks, the same
unrehearsed restore is the difference between an incident and a
business-ending data loss.

Expectation violated: production readiness means *tested* recovery, not
*available* backups. "Free tier includes daily backups" is a vendor
feature, not an ops capability.

Required: milestones.md MVP scope should include a rehearsed restore
(backup → new database → app boots → orders/payment states intact),
documented in TROUBLESHOOTING.md. At minimum, disclose in the v3 Ask that
no restore has been rehearsed yet.

---

## Majors

### M1 — Single-worker, per-connection architecture is measured but not gated; no multi-worker or pool testing anywhere in the package (SCALE.md; ARCHITECTURE.md §10)

SCALE.md is exemplary in its honesty: 18.3 req/s, p95 ~1s, single worker,
~6–10 DB operations per webhook each opening a fresh TCP connection
("serverless-safe: no persistent pool to leak"). It names PgBouncer as the
fix. But: (a) multi-worker uvicorn is untested; (b) no connection pooling
is configured; (c) the MVP done criteria contain **no performance gate**;
(d) business-plan.md §6's per-order cost table omits any infra scaling
cost. At 10x cooks, campaign broadcasts (`ARCHITECTURE.md` §10: "sends in
a loop — no batching, no per-second rate control") plus order traffic on
one worker with per-op connection setup is where latency stops being
"healthy baseline" and starts being lost orders — and lost orders in a
payment-state system are reconciliation labor (business-plan.md §7 risk 6).

Expectation violated: "measured, not estimated" is good; "measured once,
never gated" is not. A production review expects the load profile to be a
go/no-go input to the scale decision.

Required: add a scale gate to the v1.2 growth gates (e.g., "multi-worker +
pooled DB load test at 10x pilot traffic with zero handler errors") and
disclose in the v3 Transitions that the 18.3 req/s figure is a single-worker
baseline, not a capacity claim. (The v3 plan's claim map correctly avoids
claiming capacity — extend that discipline to the Ask.)

### M2 — Multi-currency v1.2 pricing collides with the single-currency schema (business-plan.md §3; ARCHITECTURE.md §10)

Business-plan.md §3 prices v1.2 as ₹999/month (IN) / $29/month (US) —
assumptions, properly labeled. ARCHITECTURE.md §10: "Prices are
`NUMERIC(10,2)` with no currency column — single-currency assumption per
deployment." Serving both markets from one deployment in v1.2 therefore
requires either two deployments (two DBs, two webhook endpoints, doubled
ops — see M3) or a schema migration. Neither is named in the v1.2 scope
or costs (§5).

Expectation violated: a business plan that prices in two currencies must
disclose the schema constraint that prices in two currencies.

Required: one sentence in business-plan.md §3 or §5: v1.2 multi-market
billing implies either per-market deployments or a currency-column
migration — name which one the plan assumes.

### M3 — No monitoring, alerting, or on-call story; logs are the only ops surface (TROUBLESHOOTING.md; SCALE.md)

The entire ops model is "grep server logs for `[biteflow] handler error`"
(TROUBLESHOOTING.md; the load-test workflow greps for it). There is no
alerting on webhook failures, no dead-man's-switch, no SLO, no on-call
expectation. For a 1–2 cook pilot this is proportionate — but the v1.2
growth gates talk about 10 cooks and the milestones ask the board to fund
the path there. A silent webhook outage during dinner service means orders
taken by customers that no cook sees, with money already moving
cook↔customer off-platform: exactly the reconciliation nightmare
business-plan.md §7 risk 6 warns about, now caused by the platform.

Expectation violated: at any scale where money moves, "we'll notice in
the logs" is not an ops plan. A senior leader expects, at minimum, the
disclosed ops floor.

Required: milestones.md should state the pilot's ops floor (e.g., alert on
any `[biteflow] handler error`, daily payment-state reconciliation report,
named human on-call during service hours) and the v1.2 gate should include
an alerting/SLO definition. Disclose the current state in the v3
Transitions — one spoken sentence is enough.

### M4 — Secret handling is template-correct but rotation is unaddressed (SECURITY.md "Scope notes"; .env.example)

SECURITY.md covers "no secrets in issues or PRs" and tokens-via-environment;
`.env.example` is a redacted template. What is missing: rotation policy
(WhatsApp tokens and webhook verify tokens after staff/contractor changes —
relevant because the pilot will involve a human reconciler with access),
per-environment secret separation beyond the verify token, and any mention
of who holds the Meta app admin credentials. At 10x cooks with multiple
operators, "one shared `.env`" becomes the incident.

Expectation violated: production readiness includes a secret lifecycle,
not just secret placement.

Required: add a rotation + custody note to SECURITY.md (who rotates what,
when, and who holds Meta app admin). Minor effort, real disclosure.

---

## Minors

### m1 — Reconciliation labor is disclosed but unmeasured in the pilot plan (business-plan.md §5–§7)

Business-plan.md is admirably explicit that reconciliation labor is the
largest non-infra MVP cost and that v1.2 gates contribution margin
*after* it. But the MVP done criteria do not require measuring minutes
per reconciled order — §8's "business-plan gate" says the pilot must
produce it, which is the right place; just confirm it is a blocking
measurement, not an optional one.

### m2 — Campaign sends lack batching/rate control (ARCHITECTURE.md §10)

"Win-back and campaign sends are one-shot chat messages… production would
need approved templates." At 10x customer lists, a loop with no per-second
control is a Meta rate-limit incident waiting to happen. Already disclosed
in ARCHITECTURE.md §10 and SECURITY.md §6; ensure the v1.2 scope's
campaign work includes the template + batching requirement explicitly.

### m3 — In-memory fake DB wipes sessions on restart (TROUBLESHOOTING.md)

Documented ("Set a real `DATABASE_URL` for anything beyond a quick local
try"). Fine as documented; ensure no pilot or demo path can accidentally
run on the fake DB (a startup guard or explicit flag would remove the
foot-gun).

---

## On the v3 presentation plan (would it survive a production-savvy viewer?)

Yes — with the B1 condition stated in the Ask. The plan is the strongest
part of the package from this seat:

- The claim-to-evidence map (§3) is exactly what a production-savvy viewer
  wants: every narrated sentence traces to an evidence file, and the
  explicit non-goals (§4) pre-empt the eight claims a skeptical viewer
  would probe (no live Meta API, no verified rail, no commission as fact,
  no rate-card numbers, no Marathi parity, no kill-resume demo, no
  regulatory clearance, no pricing decision).
- The Transitions section (§3) names the two OPEN gaps with spoken
  narration rather than a footer flash — this fixes the v2 failure mode
  the plan itself identifies.
- The honest-scope framing in the Intro ("the pilot build has known gaps
  we'll name at the end") sets the right contract with a cold viewer.

Two hardening notes for the narration build: (1) the Ask section (§6)
should state B1's condition out loud — "approval is conditional on
webhook hardening landing before the first real order" — so the board's
approval cannot be read as approving unhardened money-adjacent traffic;
(2) the business-model section's contribution table should keep the
reconciliation-labor line visibly uncertain, since it is the line a
production viewer will attack first (business-plan.md §6 already does
this — don't let the video soften it).

---

## Summary of asks

1. **Blockers:** (B1) condition board approval on webhook hardening before
   first real order; (B2) add Meta policy review of the screenshot-payment
   flow to "what must be true"; (B3) rehearsed backup/restore runbook in
   MVP scope.
2. **Majors:** (M1) multi-worker + pooled-DB load gate for v1.2; (M2)
   disclose the single-currency schema constraint against two-currency
   pricing; (M3) state the pilot ops/alerting floor and a v1.2 SLO gate;
   (M4) secret rotation + custody note in SECURITY.md.
3. The v3 video plan survives scrutiny — add the B1 condition to the Ask.
