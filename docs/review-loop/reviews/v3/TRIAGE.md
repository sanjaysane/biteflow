# BiteFlow v3 review triage — accept / reject / defer per finding

Date: 2026-09-07. Triage owner (Phase 3b). Scope: all seven v3 persona
reviews in `docs/review-loop/reviews/v3/`.

## Verdict tally (confirmed while reading)

| Persona | Verdict |
|---|---|
| qa-analyst.md | NEEDS WORK |
| senior-engineer.md | NEEDS WORK |
| senior-technical-leader.md | NEEDS WORK |
| product-manager.md | NEEDS WORK |
| external-user.md | NEEDS WORK |
| vc.md | NEEDS WORK |
| board-director.md | NEEDS WORK |

**BiteFlow: 7× NEEDS WORK.** Confirmed as briefed.

## Triage rule applied

Framework rule: *"Fix in v3 what the video/docs can fix; disclose what the
code can't."* The only acceptable rejections are ones that would require
faking output or inventing numbers. The framework forbids silently
overruling a blocker — every rejected/deferred finding carries a written
reason below. Cross-persona duplicates are merged into single fix IDs
(shown as e.g. `QA M1 + SE m1 + BD M1 → F-01`).

**Fix-ID groups:** (A) code fixes · (B) doc fixes (milestones /
business-plan / SECURITY / TROUBLESHOOTING) · (C) v3-presentation-plan
fixes. **🎬 VIDEO-BLOCKING** = the v3 video build would otherwise narrate
or show something false; the plan must change before the build.

---

## Accepted fixes

### F-01 (B) — 🎬 Refresh stale test count in `docs/milestones.md` "Where we are"
- **Findings:** QA M1 + SE m1 + BD M1.
- **Verified:** `docs/milestones.md:17` says "65 tests passing, 2 skipped";
  `docs/evidence/test-run-2026-09-07.txt` (same date) ends
  `69 passed, 2 warnings in 1.87s` with zero skips. Wrong on both numbers.
- **Change:** `docs/milestones.md` → "69 tests passing (2026-09-07), Ruff
  clean, CI green."

### F-02 (B) — 🎬 Close `mr`/Postgres gap #1 in `docs/milestones.md`
- **Findings:** QA M2 + SE m2 + BD B1.
- **Verified:** gap is closed on `main` — commit `1844781`
  ("fix(i18n): allow Marathi 'mr' locale"), `sql/schema.sql:40` CHECK now
  `('en','es','hi','mr')`, `sql/migrations/006_allow_marathi_locale.sql`
  exists, `docs/evidence/postgres-mr-verification.txt` Steps 2→4→5 show
  reject → migrate → `mr` insert succeeds. The v3 plan §3 card's **FIXED**
  claim is the true one; milestones are stale.
- **Change:** move gap #1 into milestones "Where we are (implemented)"
  with commit + evidence cites; delete it from MVP "In scope"; convert the
  done criterion into a recorded verification (already verified:
  `test_postgres_marathi_locale_accepted` + verification transcript).
- **Video-blocking:** the v3 plan §3 Transition card lists milestones'
  Known gaps verbatim labeled FIXED/OPEN — with milestones stale, the
  narration would carry the stale framing.

### F-03 (B) — Relabel $0 pilot-infra line from **measured** to **sourced**
- **Findings:** QA m1 + BD m1.
- **Verified:** `docs/business-plan.md` §5 calls Supabase-free + Render-free
  "≈ $0/month (**measured** as a documented deployment option)" while its
  own label key (line 7) defines measured = "verified in this repo/CI". A
  FAQ-documented option is **sourced**, not measured. No numeric change
  needed.

### F-04 (B) — Rewrite MVP scope item 4 ("UPI intent/collect")
- **Findings:** SE M1 + VC m1.
- **Verified:** `docs/milestones.md:42` says "Payments: UPI intent/collect
  + screenshot reconciliation". `src/payments.py` implements COD and P2P
  (screenshot `photo:<media-id>` or `ref:<text>`, cook approves/denies with
  one digit) — no UPI intent (deep-link) generation and no collect-request
  integration exist anywhere in `src/`. "UPI intent/collect" is
  payment-rail terminology that contradicts the plan's own §1–§2:
  "No money moves through BiteFlow; it tracks payment state only."
- **Change:** rewrite as the actual mechanics — "customer pays cook
  directly off-platform (cash/UPI); submits screenshot or typed reference;
  cook verifies with one digit; human reconciles daily." Add one clarifying
  line to business-plan §2 ("intents, if ever generated, reference the
  cook's own VPA; the platform neither initiates settlement nor sees
  funds").

### F-05 (B) — Keep "cook-verified, not bank-verified" qualifier attached — standing rule
- **Finding:** SE m3 (hygiene only).
- **Verified:** the qualifier is already present where it counts
  (business-plan §1, ARCHITECTURE §10). No file change required.
- **Accepted as a standing editorial rule:** every board-facing mention of
  the `verified` payment state carries the "cook-verified" qualifier.
  No code change.

### F-06 (B) — Disclose screenshot non-retention
- **Finding:** SE m4.
- **Verified:** ARCHITECTURE §10 discloses BiteFlow stores only the Meta
  `media_id`, never file bytes — but no doc states the consequence: post-hoc
  audit of a disputed payment is impossible for the platform (screenshot
  exists only on the cook's device).
- **Change:** add one sentence to milestones MVP Risks (payment fraud) or
  business-plan §7: disputes rely on the cook's device copy; the platform
  cannot re-inspect proof.

### F-07 (B) — 🎬 Make board approval conditional on webhook hardening before first real order
- **Finding:** STL B1.
- **Verified:** milestones lists signature verification, inbound dedupe,
  rate-limiting as "minimum viable hardening is MVP scope"; SECURITY.md
  §1–3: "Anyone who knows your `/webhook` URL can inject fake
  customer/cook messages. This is the single most important thing to fix
  before going live." The done criterion ("zero lost/duplicate orders from
  webhook redelivery (dedupe verified)") tests the outcome, not the
  control — a forged approval POST can fabricate a paid order the
  trust-based screenshot model cannot distinguish.
- **Change:** milestones — MVP approval is conditional: no real orders until
  `X-Hub-Signature-256` verification, `wamid` dedupe, and webhook
  rate-limiting are implemented and covered by tests; reword the done
  criterion to "hardening controls implemented and verified."
- **Video-blocking:** the v3 Ask must not be readable as approving
  unhardened money-adjacent traffic (spoken condition — see F-08).

### F-08 (C) — 🎬 v3 plan: state the F-07 condition in the Ask; keep reconciliation labor uncertain
- **Finding:** STL B1 + "on the v3 presentation plan" notes.
- **Change:** plan §6 Ask states the condition out loud — "approval is
  conditional on webhook hardening landing before the first real order."
  The §4 contribution table keeps the reconciliation-labor line visibly
  uncertain (business-plan §6 already does this — the video must not
  soften it). The two OPEN gaps keep their spoken Transitions airtime.

### F-09 (B) — Add Meta platform-policy review of the screenshot-payment flow to "what must be true"
- **Finding:** STL B2.
- **Verified:** milestones names WhatsApp policy/template delays as a risk
  and business-plan §7 risk 3 covers conversation pricing — but neither
  names the specific policy surface the pilot lives on: customers sending
  UPI IDs/payment screenshots and cooks confirming payments inside a
  business chat. There is no verified rail to fall back on (milestones
  gap #3). Food safety has "counsel confirms" (business-plan §7 risk 5);
  the platform the product runs on does not.
- **Change:** milestones "What must be true" += a documented read of Meta's
  WhatsApp Business Policy and Commerce Policy against the
  screenshot-verification flow, before pilot cook onboarding.

### F-10 (B + C) — 🎬 Rehearsed backup/restore runbook; disclose the unrehearsed state
- **Finding:** STL B3.
- **Verified:** `docs/how-to/supabase-setup.md` notes "Supabase free tier
  includes daily backups" — a vendor feature, not an ops capability. No
  restore runbook, RTO/RPO, or rehearsed restore anywhere; the DB holds
  orders, payment states, inventory, customer sessions.
- **Change (B):** milestones MVP scope += a rehearsed restore (backup →
  new database → app boots → orders/payment states intact), documented in
  TROUBLESHOOTING.md. **(C):** at minimum, the v3 Ask discloses on mic
  that no restore has been rehearsed yet. The Ask disclosure is
  video-blocking; the rehearsal itself is pilot-gating.

### F-11 (B + C) — Add scale gate to v1.2; disclose single-worker baseline in Transitions
- **Finding:** STL M1.
- **Verified:** SCALE.md is honest (18.3 req/s, p95 ~1s, single worker,
  per-op fresh TCP connections, PgBouncer named as the fix) but multi-worker
  uvicorn is untested, no pooling is configured, and the MVP done criteria
  contain no performance gate. Business-plan §6 omits infra scaling cost.
- **Change (B):** v1.2 growth gates += "multi-worker + pooled-DB load test
  at 10x pilot traffic with zero handler errors." **(C):** Transitions
  disclose that 18.3 req/s is a single-worker baseline, not a capacity
  claim (the claim map already avoids claiming capacity — extend the
  discipline to the Ask).

### F-12 (B) — Disclose single-currency schema constraint against two-currency pricing
- **Finding:** STL M2.
- **Verified:** business-plan §3 prices v1.2 at ₹999/mo (IN) / $29/mo (US);
  ARCHITECTURE §10: "Prices are `NUMERIC(10,2)` with no currency column —
  single-currency assumption per deployment."
- **Change:** one sentence in business-plan §3 or §5: v1.2 multi-market
  billing implies either per-market deployments (doubled ops) or a
  currency-column migration — name which one the plan assumes.

### F-13 (B + C) — State the pilot ops floor; v1.2 SLO gate; spoken disclosure
- **Finding:** STL M3.
- **Verified:** ops model is "grep server logs for `[biteflow] handler
  error`" (TROUBLESHOOTING.md); no alerting, no on-call, no SLO. A silent
  webhook outage during dinner service means orders customers placed that
  no cook sees, with money already moving cook↔customer off-platform.
- **Change (B):** milestones states the pilot ops floor (e.g. alert on any
  `[biteflow] handler error`, daily payment-state reconciliation report,
  named human on-call during service hours); v1.2 gates += alerting/SLO
  definition. **(C):** one spoken sentence in Transitions disclosing the
  current state.

### F-14 (B) — SECURITY.md: secret rotation + custody note
- **Finding:** STL M4.
- **Change:** rotation policy (WhatsApp tokens, webhook verify tokens after
  staff/contractor changes — the pilot's human reconciler has access),
  per-environment separation, and who holds Meta app admin credentials.

### F-15 (B) — Make minutes-per-reconciled-order a blocking pilot measurement
- **Findings:** STL m1 + VC m2.
- **Verified:** §8's "business-plan gate" is the right home; it must be a
  blocking measurement, not optional. The ₹3–8/order reconciliation line is
  the widest relative input in §6 — the difference between ₹9 and ₹1
  contribution per order — and the pilot's single most valuable business
  metric.
- **Change:** name "minutes per reconciled order" explicitly as the #1
  pilot metric in the business-plan gate.

### F-16 (B) — v1.2 campaign scope includes templates + batching
- **Finding:** STL m2.
- **Verified:** ARCHITECTURE §10 + SECURITY.md §6 disclose campaign sends
  are an unthrottled loop with no batching/rate control.
- **Change:** v1.2 scope's campaign work explicitly requires approved
  templates + batching/per-second rate control.

### F-17 (A) — Guard against accidental fake-DB runs in pilot/demo paths
- **Finding:** STL m3.
- **Verified:** documented ("Set a real `DATABASE_URL` for anything beyond
  a quick local try") but the in-memory DB wipes sessions on restart — a
  foot-gun if any pilot/demo path runs without `DATABASE_URL`.
- **Change:** a startup guard or explicit flag refusing to boot pilot/demo
  paths on the fake DB (e.g. require explicit `BITEFLOW_FAKE_DB=1`).

### F-18 (C) — 🎬 Restructure the v3 walkthrough: the money loop, not the schema
- **Findings:** PM B1 + PM M1 + PM M2 + EU B1.
- **Verified against the plan:** §2's six on-screen frames are (1) `mr`
  user row on live Postgres, (2) Marathi menu listing, (3)
  nickname/currency lines, (4) inventory seed table, (5) Devanagari
  round-trip rows, (6) CHECK-constraint catalog line. None shows a customer
  placing an order, the single-digit order flow (`Reply 1`, quantity, `0`
  checkout — README "How a chat flows", `docs/how-to/cooks-first-day.md`),
  the cook's Accept/Reject, the payment screenshot approve/deny, or
  Cooking → ready → delivered status updates — while the §2 purpose line
  promises "the *complete* product loop … cook lists a dish → customer
  orders → cook accepts → customer is updated → money state is tracked."
  The claim map backs localization/inventory/registration, not the order
  loop.
- **Change:** (a) collapse items 1/5/6 into a single 45–60 s "the Marathi
  fix is real" beat; (b) at least half of the 6:00 shows one real customer
  order end-to-end from evidence transcripts — menu → order → cook
  accepts → payment state tracked → status updates; (c) one unhurried
  payment-approval beat showing the Marathi screen (`cook_payment_proof`
  → "1️⃣ पेमेंट मान्य करा 👍"), held until narration finishes: "the cook
  approves only when the money is really in their account — screenshot is
  a claim, not settled funds"; (d) show the cook's dish-listing flow once
  (name → price → photo + ingredients → live confirmation), held long
  enough to read, before the customer-side menu frame.

### F-19 (C) — 🎬 Add the who-pays one-liner to the intro
- **Finding:** PM m1.
- **Verified:** the plan's own §1 v2 analysis flagged "no who-pays framing"
  as a v2 failure; the v3 intro still leaves it out (customer-pays-nothing
  / cook-pays-eventually lands only in §4, ~minute 9).
- **Change:** add to §1 "Must say": "customers order for free; cooks use it
  free in the pilot — the platform monetizes the cook side later."

### F-20 (B) — Update "Still open (v3 round)"
- **Finding:** PM m2.
- **Verified:** `docs/milestones.md:91` lists `docs/business-plan.md` and
  the v3 pitch video as open, but both exist dated 2026-09-07.
- **Change:** the section reflects what is actually still open — the board
  review itself.

### F-21 (B) — Cite the owner-addenda line in "Where we are"
- **Finding:** BD m2.
- **Verified:** every implemented bullet cites a commit except "Owner
  addenda: kitchen economics, marketing/growth playbooks."
- **Change:** add the commit(s) or mark the pointer as "in-progress,
  uncommitted."

### F-22 (C) — 🎬 Rephrase "same code path as production" in the intro
- **Finding:** BD M2.
- **Verified:** plan §1 must-say line 78: "the WhatsApp side uses the same
  code path as production" — but milestones gap #4 states the demo used
  fake/local WhatsApp adapters, not the live Meta Cloud API. The engine and
  DB path are production; the transport is not.
- **Change:** "the engine and database path are the real production code;
  the WhatsApp transport in this demo is a local adapter, not the live
  Meta Cloud API." (Non-goal #1 already says this — align the intro with
  it.)

### F-23 (A) — 🎬 `locales/mr.json` `cook_home`: "उघड्या ऑर्डरी पहा" → "चालू ऑर्डरी पहा"
- **Finding:** EU B2 (v1 M1, unfixed — the persona's trust-in-review-loop
  point stands).
- **Verified:** key `cook_home` line 1 of mr.json contains
  "2️⃣ उघड्या ऑर्डरी पहा 📦". "उघडं" = uncovered/naked — the exact joke
  caught in v1.
- **Change:** "2️⃣ चालू ऑर्डरी पहा 📦".

### F-24 (A) — `locales/mr.json` `cook_registered`: "किचन" → "स्वयंपाकघर"
- **Finding:** EU minor (v1 minor, unfixed).
- **Verified:** key `cook_registered`: "चला, तुमचं किचन सुरू करूया."
  A real person writes "तुमचं स्वयंपाकघर सुरू करूया."

### F-25 (A) — 🎬 `locales/mr.json`: Zelle/Venmo/Pix → UPI only
- **Finding:** EU M1.
- **Verified:** `p2p_instructions`: "…{total} Zelle, Venmo, UPI किंवा Pix
  ने पाठवा"; `payment_title`: "2️⃣ फोनवरून पेमेंट (Zelle / Venmo / UPI /
  Pix) 📱". Zelle/Venmo/Pix do not exist for the India-pilot Marathi
  user; business-plan §1 already states the rail rule — "UPI in India,
  Zelle/Venmo/Pix elsewhere."
- **Change:** Marathi `p2p_instructions` / `payment_title` say UPI only
  ("UPI ने पाठवा"). Check `en` keeps the multi-rail list (US context).
- **Video-blocking:** the new F-18 payment beat will show these strings.

### F-26 (C) — Marathi-beat narration register guidance
- **Finding:** EU M2.
- **Verified:** "Must say" lines are board-register ("the same code path
  as production") with no register guidance for the Marathi-frame beats
  (v1 M7 carried).
- **Change:** plan §5 (or §2 beat notes) adds register guidance: warm,
  non-technical Marathi for UI-quoting beats; no "डेटाबेस/स्टेट
  मशीन/बॅकएंड" in voiceover where a senior would hear it.

### F-27 (B + C) — 🎬 Billing decision: state the decision rule; drop the false symmetry
- **Findings:** VC B1 + VC M5.
- **Verified:** milestones v1.2 gates say "Billing model chosen from
  measured pilot data, not before" — no mapping from measured inputs (AOV,
  conversation cost, reconciliation minutes, repeat, orders/cook) to the
  choice exists. Worse, §7 risk 1 admits commission is structurally
  uncollectable while payments stay cook↔customer ("the platform has no
  settlement point to deduct 8–12% … or the subscription model wins by
  default") — the candidates are not symmetric, but the video plan §4
  presents them as symmetric alternatives. The growth gates measure
  repeat/margin/support — none of which produces a collection mechanism.
- **Change (B):** either state the decision rule (e.g. "if repeat ≥ X, AOV
  ≥ ₹Y, orders/cook ≥ Z, and a collection mechanism the cook accepts →
  commission; else subscription") with collection-mechanism design as
  explicit v1.2 scope carrying its own acceptance test — or drop
  commission as a v1.2 candidate. **(C):** plan §4 presents the asymmetry
  honestly (commission = boundary-crossing candidate; subscription = wins
  by default). The §4 framing is video-blocking.

### F-28 (B) — §6: reconcile the ₹150 AOV assumption with the ₹85 evidence price
- **Finding:** VC B2.
- **Re-run confirmed:** at ₹85 (the "Veg Pulao ₹85.00" evidence frame in
  the plan's own §2), 10% commission grosses **₹8.50/order** against §6's
  own variable costs of ₹5–14 — underwater before the pilot starts. §6's
  entire commission case rests on the ₹150 AOV assumption.
- **Change:** either state the basket-composition assumption explicitly
  (orders average ~2 items) or re-run §6 at the evidence price.

### F-29 (B) — §6 subscription table: print the true contribution range
- **Finding:** VC M1.
- **Re-run confirmed:** ₹999 ÷ 100 orders = ₹9.99 effective revenue/order;
  variable cost ₹5–13/order → contribution **≈ +₹5 (best) to ≈ −₹3
  (worst)**. The plan states "≈ ₹0 to −₹3" — the positive tail is missing,
  erasing the model's own upside argument.
- **Change:** contribution row → "≈ −₹3 to +₹5".

### F-30 (B) — §6 commission table: model the 8% low end
- **Finding:** VC M2.
- **Re-run confirmed:** 8% × ₹150 = ₹12 gross against ₹5–14 variable cost
  → contribution **−₹2 to +₹7**, negative in the high-cost case. §6 models
  only the 10% midpoint.
- **Change:** add the 8% line with its own contribution, or drop 8% from
  the candidate range.

### F-31 (B) — Add the honest moat section
- **Finding:** VC M3.
- **Verified:** no moat/defensibility section exists; marketplace/discovery
  (the only network-effect candidate) is out of scope; the cook's customer
  list is the cook's, so switching cost is near zero.
- **Change:** add to the business plan the honest version: the defensible
  bet is execution depth (locale/voice UX for seniors, margin-alert
  intelligence), cook relationships via the referral loop, and speed — not
  a structural moat. A VC funds this as an execution play only if the plan
  says so.

### F-32 (B) — §8/milestones: MVP criteria = demand validation; name the business-validation moment
- **Finding:** VC M4.
- **Verified:** the MVP's ≥50 paid orders flow cook↔customer — the platform
  captures none of it. §8's "real money" proves GMV exists, not that the
  platform can capture value; zero willingness-to-pay signal in the MVP
  (the cook pays nothing by design).
- **Change:** label the MVP criteria as demand validation; name the v1.2
  contribution-margin gate as the first genuine business test; add a
  directional WTP probe to the pilot (cook reaction to a stated ₹999/month
  price) so the billing decision is not made from a zero-price baseline.

### F-33 (B) — v1.2 growth gates: churn threshold for the subscription model
- **Finding:** VC m3.
- **Verified:** business-plan §6 states "a cook doing 30 orders/month pays
  an effective ~₹33 per order and will churn" — this is the subscription
  model's kill criterion, currently not a gate.
- **Change:** gates += minimum median orders/cook/month (and minimum
  median cook GMV) below which the subscription price is repriced or the
  model is abandoned.

---

## Deferred (with written reason — not silently overruled)

### D-01 — EU B3: the cook's business/finance screens (all `o_*`/`m_*` keys) are still English — DEFERRED
- **Reason:** `locales/mr.json` holds 70 keys vs 162 in `en.json`; every
  owner/business-hub and marketing-hub key falls back to English. Filling
  ~92 finance/accounting strings by machine translation would be
  faked-quality content that violates the Marathi content standard
  (natural Marathi, never word-for-word) — exactly the class of failure
  this triage exists to prevent. This is real work requiring a native
  Marathi review pass, not a v3 docs/video-cycle fix.
- **What happens instead:** the current state is already disclosed
  (milestones "Marathi partial"; Board claim 11 verified supported).
  **F-18's plan must carry that disclosure into the spoken Transitions**
  ("the owner/business hub is still English-first — Marathi-first for the
  pilot is MVP scope"), and pilot-cook readiness in milestones must gate
  on it. Not rejected — scheduled as MVP work, wrong phase for v3.

---

## Rejected

None. Every other finding is fixable as a real docs/plan/locale/code change
— no finding would require faking output or inventing numbers.

## Verified-clean findings (no action)

- SE m2 — money story is prose-accurate and matches code (no platform-held
  money); noted, passes.
- QA "What verified cleanly" sections, Board claims 3–9, 12–13 — no action.

## Video-blocking summary (must change before the v3 build)

F-02 (gap-FIXED framing) · F-07 + F-08 (conditional-approval Ask) ·
F-10 (Ask disclosure: no rehearsed restore) · F-18 (walkthrough
restructure: first order + payment beat + listing flow) · F-19 (who-pays
intro) · F-22 ("same code path" rephrase) · F-23 (cook-home Marathi
string) · F-25 (UPI-only Marathi payment strings) · F-27 (plan §4 billing
asymmetry).

## Counts

- Raw findings across 7 reviews: **46** (QA 3, SE 5, STL 11, PM 5, EU 6,
  VC 11, BD 5).
- Accepted fix IDs: **33** (A: 4 · B: 20 · C: 9, with F-10/F-11/F-13/F-27
  spanning B+C).
- Deferred: **1** (D-01, with reason). Rejected: **0**.
