# BiteFlow — MVP and v1.2 Milestones

Date: 2026-09-07. Status: **proposal** (not yet board-reviewed).
Labels used below: **implemented** = verified on `main`; **assumption** = estimate to validate; **gap** = known deficiency.

## Where we are (implemented)

- Zero-client WhatsApp micro-commerce: cooks broadcast menus, customers order dinner
  inside plain WhatsApp chats (single-digit replies, 👍/👎 confirmations).
- Dish listings with photos, ingredients, descriptions (commit `113881b`).
- Nickname display with phone fallback; locale-aware currency — INR for
  India/Marathi context, USD for US/English (commit `e936e28`).
- Realistic raw-material inventory seed, non-zero stock (commit `814e6c4`).
- Locales: English, Spanish, Hindi full; Marathi partial (missing keys fall back
  to English). Mid-chat language switching with one word.
- Marathi `mr` locale on live Postgres: `sql/schema.sql` CHECK constraint allows
  `en/es/hi/mr` (commit `1844781`, `sql/migrations/006_allow_marathi_locale.sql`);
  verified by `docs/evidence/postgres-mr-verification.txt` Steps 2→4→5 (reject →
  migrate → `mr` insert succeeds) and `test_postgres_marathi_locale_accepted`
  (formerly known gap #1 — closed on `main`).
- Owner addenda: kitchen economics, marketing/growth playbooks (commit `b244696`).
- 69 tests passing (2026-09-07), Ruff clean, CI green.

## Known gaps (must be closed before or during MVP)

1. **Webhook hardening**: no signature verification, no inbound dedupe, no
   rate-limiting (flagged in README). Minimum viable hardening is MVP scope.
   **Board approval of the pilot is conditional on this landing before the
   first real order** — see MVP approval condition below (F-07).
2. **Payments are trust-based**: screenshot verification, no bank-verified rail.
3. **Demo used a fake/local WhatsApp client**, not the live Meta WhatsApp
   Cloud API. Pilot must run on the real API (template approvals needed).

## MVP — "First real kitchen"

**Goal:** one cook serving real paying customers end-to-end on the live
WhatsApp Cloud API.

**MVP approval condition (F-07).** Board approval of this MVP is conditional:
no real orders until webhook hardening is implemented and covered by tests —
`X-Hub-Signature-256` signature verification, inbound `wamid` dedupe, and
webhook rate-limiting. The trust-based screenshot payment model cannot
distinguish a forged approval POST from a real one; hardening comes first.

**In scope**
1. Webhook hardening minimum: signature verification, inbound dedupe,
   rate-limiting (implements the approval condition above).
2. Live Meta WhatsApp Cloud API connection; order-notification templates
   approved.
3. A rehearsed backup → restore runbook: backup taken → restored to a new
   database → app boots → orders/payment states intact; documented in
   `docs/TROUBLESHOOTING.md`. (No restore has been rehearsed yet — disclosed
   in the v3 pitch Ask.)
4. Payments: customer pays the cook directly off-platform (cash/UPI); the
   customer submits a screenshot (`photo:<media-id>`) or typed reference
   (`ref:<text>`); the cook verifies with a single digit; a human reconciles
   payments daily during the pilot. No UPI intent (deep-link) generation and
   no collect-request integration exist anywhere in `src/` — BiteFlow tracks
   payment state only (`unpaid` → `pending_approval` → `verified`, cook-verified
   not bank-verified), with explicit in-chat trust framing ("screenshot is a
   claim, not settled funds"). (Explicitly NOT a verified payment rail in MVP.)
5. Order status updates via WhatsApp: confirmed → preparing → ready → delivered.
6. Cook dashboard: today's orders + inventory burn-down against seeded stock.

**Out of scope:** in-app/verified payments, delivery logistics, multi-cook
marketplace/discovery, ratings & reviews, cook subscriptions/billing.

**Done criteria (metrics)** — the MVP validates **demand**, not the business
model: the ≥50 paid orders flow cook↔customer and the platform captures none
of it, so these criteria prove GMV exists, not that the platform can capture
value. The v1.2 contribution-margin gate is the first genuine business test.
- ≥ 50 completed paid orders across the pilot (1–2 cooks).
- Order completion rate ≥ 85% (ordered → delivered, as marked by cook).
- Repeat order within 14 days ≥ 30% (**assumption** — to be measured).
- Cook lists a dish with photo + ingredients in < 5 minutes, unassisted.
- Webhook hardening controls implemented and verified (F-07 approval
  condition): signature verification, `wamid` dedupe, and rate-limiting
  covered by tests.
- Recorded verification (2026-09-07): zero failed `mr` registrations against
  live Postgres — `docs/evidence/postgres-mr-verification.txt` Steps 2→4→5
  and `test_postgres_marathi_locale_accepted`.

**Risks**
- WhatsApp Business policy / template-approval delays.
- Payment fraud on trust-based verification (mitigation: human reconciliation,
  order caps per customer during pilot). Disclosed: BiteFlow stores only the
  Meta `media_id`, never screenshot bytes — post-hoc audit of a disputed
  payment is impossible for the platform; the screenshot exists only on the
  cook's device, so disputes rely on the cook's device copy.
- Cook smartphone literacy; support burden per cook.
- Food-safety/regulatory exposure for home kitchens (**assumption** — needs
  local counsel, e.g. FSSAI norms in India).

**What must be true**
- WhatsApp Cloud API access approved.
- 1–2 committed pilot cooks (Marathi/India context, INR).
- A human available to reconcile payments daily during the pilot.
- A documented read of Meta's WhatsApp Business Policy and Commerce Policy
  against the screenshot-verification flow (customers sending UPI IDs/payment
  screenshots; cooks confirming payments inside a business chat), completed
  before pilot cook onboarding — there is no verified rail to fall back on.
- Directional willingness-to-pay probe with each pilot cook: their stated
  reaction to a ₹999/month price, so the v1.2 billing decision is not made
  from a zero-price baseline.

## Pilot ops floor
- Alert on any `[biteflow] handler error` in server logs (no alerting or
  on-call exists today — this is the minimum).
- A daily payment-state reconciliation report (human-reconciler output).
- A named human on-call during service hours. A silent webhook outage during
  dinner service means orders customers placed that no cook sees, with money
  already moving cook↔customer off-platform — the pilot may not run silent.

## v1.2 — "Repeatable kitchen economics"

**In scope:** customer ratings/reviews; delivery slot selection; cook analytics
(best sellers, repeat customers, waste); referral loop (customer invites
neighbor); campaign outreach on approved WhatsApp templates with batching and
per-second rate control (the current unthrottled loop must not grow as-is);
billing decision — cook subscription OR per-order commission, gated by MVP data
and the business-plan §2 decision rule (commission additionally gated on a
collection mechanism the cook accepts, with its own acceptance test).

**Growth gates**
- Repeat-purchase rate ≥ 40%.
- Contribution margin per order positive *after* payment-reconciliation labor.
  This is the first genuine business test (the MVP proves demand only).
- 10 cooks onboarded with < 1 day of support each.
- Multi-worker + pooled-DB load test at 10x pilot traffic with zero handler
  errors. (The 18.3 req/s figure is a single-worker baseline, not a capacity
  claim — SCALE.md.)
- Alerting/SLO definition landed: alert on `[biteflow] handler error`,
  daily reconciliation report, named on-call during service hours — v1.2
  must not run on "grep the logs" ops.
- Subscription kill criterion: median orders/cook/month ≥ 100 AND median
  cook GMV ≥ ₹15,000/month required to hold ₹999/month pricing — below that
  the price is repriced or the subscription model is abandoned (a cook doing
  30 orders/month pays an effective ~₹33 per order and will churn).
- Campaign work requires approved WhatsApp templates + batching/per-second
  rate control (campaign sends are currently an unthrottled loop — ARCHITECTURE
  §10, SECURITY §6).
- Billing model chosen from measured pilot data, not before — via the
  decision rule in `docs/business-plan.md` §2 (commission requires a
  collection mechanism the cook accepts, with its own acceptance test;
  otherwise subscription wins by default).

**Business model (estimates — assumptions to validate)**
- Either 8–12% commission per order, or ₹999/month (India) / $29/month (US)
  cook subscription.
- Unit economics must include Meta WhatsApp per-conversation charges
  (**assumption** — price from Meta's rate card at time of pilot).

## Still open (v3 round)

- The 7-persona board review itself (this review round) — its verdict and
  any conditions it attaches to MVP approval.
- `docs/business-plan.md` and the v3 pitch video exist, dated 2026-09-07;
  both are under board review, not open work.
