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
- Owner addenda: kitchen economics, marketing/growth playbooks.
- 65 tests passing, 2 skipped; Ruff clean; CI green.

## Known gaps (must be closed before or during MVP)

1. **Marathi on Postgres**: `schema.sql` language constraint allows only
   `en/es/hi` — an `mr` registration could fail on live Postgres (SQLite tests
   pass). Fix + test against live Postgres before pilot.
2. **Webhook hardening**: no signature verification, no inbound dedupe, no
   rate-limiting (flagged in README). Minimum viable hardening is MVP scope.
3. **Payments are trust-based**: screenshot verification, no bank-verified rail.
4. **Demo used a fake/local WhatsApp client**, not the live Meta WhatsApp
   Cloud API. Pilot must run on the real API (template approvals needed).

## MVP — "First real kitchen"

**Goal:** one cook serving real paying customers end-to-end on the live
WhatsApp Cloud API.

**In scope**
1. Fix the `mr`/Postgres language constraint; test full `mr` registration
   against live Postgres.
2. Webhook hardening minimum: signature verification, inbound dedupe,
   rate-limiting.
3. Live Meta WhatsApp Cloud API connection; order-notification templates
   approved.
4. Payments: UPI intent/collect + screenshot reconciliation, with explicit
   in-chat trust framing. A human reconciles payments daily during the pilot.
   (Explicitly NOT a verified payment rail in MVP.)
5. Order status updates via WhatsApp: confirmed → preparing → ready → delivered.
6. Cook dashboard: today's orders + inventory burn-down against seeded stock.

**Out of scope:** in-app/verified payments, delivery logistics, multi-cook
marketplace/discovery, ratings & reviews, cook subscriptions/billing.

**Done criteria (metrics)**
- ≥ 50 completed paid orders across the pilot (1–2 cooks).
- Order completion rate ≥ 85% (ordered → delivered, as marked by cook).
- Repeat order within 14 days ≥ 30% (**assumption** — to be measured).
- Cook lists a dish with photo + ingredients in < 5 minutes, unassisted.
- Zero failed `mr` registrations against live Postgres.
- Zero lost/duplicate orders from webhook redelivery (dedupe verified).

**Risks**
- WhatsApp Business policy / template-approval delays.
- Payment fraud on trust-based verification (mitigation: human reconciliation,
  order caps per customer during pilot).
- Cook smartphone literacy; support burden per cook.
- Food-safety/regulatory exposure for home kitchens (**assumption** — needs
  local counsel, e.g. FSSAI norms in India).

**What must be true**
- WhatsApp Cloud API access approved.
- 1–2 committed pilot cooks (Marathi/India context, INR).
- A human available to reconcile payments daily during the pilot.

## v1.2 — "Repeatable kitchen economics"

**In scope:** customer ratings/reviews; delivery slot selection; cook analytics
(best sellers, repeat customers, waste); referral loop (customer invites
neighbor); billing decision — cook subscription OR per-order commission, gated
by MVP data.

**Growth gates**
- Repeat-purchase rate ≥ 40%.
- Contribution margin per order positive *after* payment-reconciliation labor.
- 10 cooks onboarded with < 1 day of support each.
- Billing model chosen from measured pilot data, not before.

**Business model (estimates — assumptions to validate)**
- Either 8–12% commission per order, or ₹999/month (India) / $29/month (US)
  cook subscription.
- Unit economics must include Meta WhatsApp per-conversation charges
  (**assumption** — price from Meta's rate card at time of pilot).

## Still open (v3 round)

- `docs/business-plan.md` (business model, revenue, GTM, risks).
- v3 pitch video (intro → walkthrough → summary/ask).
- 7-persona board review of these milestones.
