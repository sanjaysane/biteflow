# BiteFlow — Business Plan (v1)

Date: 2026-09-07. Status: **draft for board review** — consistent with
[docs/milestones.md](milestones.md), which is a proposal pending board review.
Nothing here overrides the milestones document.

Label key (used throughout): **measured** = verified in this repo/CI;
**sourced** = from a third-party rate card or public reference, check at
pilot time; **assumption** = modeling estimate to be validated in the pilot.
Numbers are never presented as facts unless labeled measured.

Currency: INR for the India pilot context (milestones specify Marathi/India
pilot cooks); USD shown where the product already supports it (locale-aware
currency, commit `e936e28`).

---

## 1. What the product is and who pays

**The product.** BiteFlow is zero-client WhatsApp micro-commerce for home
cooks (tiffin services, home bakers, meal-prep sellers) and their customers
— designed so senior citizens can order without installing anything.
Measured capabilities (on `main`):

- Cook broadcasts a menu with photos, ingredients, prices; customers order
  with single-digit replies, 👍/👎 confirmations, mid-chat language switching
  (English, Spanish, Hindi full; Marathi partial with English fallback).
- Payments tracked as COD or P2P: customer sends a screenshot or typed
  reference, cook approves with one digit. **No money moves through
  BiteFlow; it tracks payment state only.** P2P proof is trust-based
  (a screenshot is a claim, not settled funds).
- Business-owner addendum: inventory with low-stock alerts, recipes as
  bills of materials with food-cost/margin math, supplier purchase logging,
  daily P&L digest, and marketing (dual-sided referrals, first-order offers,
  opted-in campaigns, 14-day win-back). The paneer counterfactual — double
  a supplier price and the cook gets one WhatsApp alert listing dishes
  whose margin fell below 20% — is implemented.

**Who pays.** Two distinct sides:

- **The cook (business customer)** pays for the platform — eventually.
  In MVP, the cook pays nothing (milestones mark cook subscriptions/billing
  explicitly out of scope for MVP). Monetization is gated on v1.2 growth
  gates and measured pilot data.
- **The customer's money** (order payment) flows **cook ↔ customer
  directly** — cash on delivery, or peer-to-peer transfer (UPI in India,
  Zelle/Venmo/Pix elsewhere). The platform never holds customer funds.
  This is deliberate: it keeps the platform out of payment-licensing
  territory (e.g. UPI/PPI licensing in India) and keeps pilot complexity
  near zero.

**Who does NOT pay.** The end customer (diner) never pays BiteFlow
anything. The unit of monetization is the cook, per order or per month.

---

## 2. Business model — how money moves

**Today (MVP — no platform take).**

```
Customer                Cook                        BiteFlow platform
   │                      │                                │
   │── order (WhatsApp) ─▶│                                │
   │◀── food ─────────────│                                │
   │── cash / UPI ───────▶│  (direct, off-platform)        │
   │                      │── nothing ───────────────────▶ │  (free in MVP)
```

- Every rupee moves cook↔customer. BiteFlow sees only payment *state*
  (`unpaid` → `pending_approval` → `verified`), plus a daily human
  reconciliation step (a person checks the cook's actual receipts during
  the pilot — milestones § "What must be true").
- No money-movement rails are built or operated by BiteFlow in MVP. This
  avoids payment-gateway fees, settlement risk, chargebacks, and KYC
  obligations for the pilot.

**From v1.2 (decision gated by measured pilot data — per milestones).**
The billing decision is one of:

- **Commission model:** platform takes a % of each completed order, or
- **Subscription model:** cook pays a flat monthly fee.

The milestones document names the decision gate explicitly: the billing
model is "chosen from measured pilot data, not before." The plan does
not pre-commit to either.

---

## 3. Revenue streams and pricing logic

### Stream 1 — Order commission (candidate v1.2 model A)

- **Pricing:** 8–12% per completed order (**assumption** from milestones
  v1.2, to validate against cook willingness-to-pay).
- **Logic:** commission aligns platform revenue with cook success; zero
  fixed cost for the cook, so adoption friction is low. Counter-risk: at
  8–12% of a ₹150 home-kitchen order, per-order revenue is ₹12–18
  (**assumption** — arithmetic on the assumed order value, not measured),
  which means volume must be high to matter. Collection mechanism must be
  designed (deducted how, when money moves off-platform? — open question
  for v1.2, since today's payments are trust-based P2P).
- **Where it breaks:** if the cook is paid in cash/UPI directly, the
  platform cannot enforce the take without a trusted settlement point.
  This is the single biggest business-model dependency of the commission
  model — see §7.

### Stream 2 — Cook subscription (candidate v1.2 model B)

- **Pricing:** ₹999/month (India) / $29/month (US) (**assumption** from
  milestones v1.2).
- **Logic:** predictable revenue per cook; cooks who sell ≥ ~₹10,000/month
  through the chat pay an effective take under 10% (**assumption** —
  arithmetic: ₹999 ÷ ₹10,000). Subscription sidesteps the collection
  problem of the commission model (a recurring charge the cook pays
  directly, e.g. UPI Autopay in India).
- **Where it breaks:** willingness to pay ₹999/month is unproven for
  home cooks with thin, irregular income; churn risk is high if a cook's
  sales are seasonal. The owner-addendum value (daily P&L, procurement
  planning, margin alerts) is the retention argument — it must demonstrably
  save the cook money or time worth more than ₹999/month.

### Stream 3 — Value-added services (v3+, not modeled here)

- Optional later: printed menu/labels support, paid marketing reach
  (template message costs passed through), premium analytics. Not part of
  v1.2. Mentioned only to show the roadmap exists; no numbers attached.

### Pricing logic summary

| Model | Price (assumption) | Cook pays when | Platform revenue scales with |
|---|---|---|---|
| Commission | 8–12% / completed order | per sale | GMV × order count |
| Subscription | ₹999/mo (IN) / $29/mo (US) | monthly, regardless | active cook count |

The two models are alternatives for v1.2, not cumulative — milestones say
the choice is "cook subscription OR per-order commission."

---

## 4. Target customers / prospects and go-to-market

### The cook (paying side, v1.2+)

- **Profile:** home kitchens already selling to a regular customer base —
  tiffin services, home bakers, dabba/meals sellers, meal-prep sellers.
  They take orders today via phone calls and personal WhatsApp messages
  (inference from the product's design: BiteFlow exists to organize a
  flow cooks already run manually).
- **Why they'd adopt:** (1) customers who find Swiggy/Zomato apps
  overwhelming stay inside plain WhatsApp; (2) the owner addendum replaces
  notebook accounting with daily P&L, inventory alerts, and margin math
  the cook can't easily do by hand; (3) single-digit ordering reduces the
  "sorry, can you repeat the order?" churn of voice calls.
- **Pilot sourcing (assumption):** 1–2 cooks from the founder's own
  network in a Marathi/India context — milestones require "1–2 committed
  pilot cooks (Marathi/India context, INR)." Go-to-market for v1.2+
  repeats this pattern: one trusted cook per locality, referral loop
  (already built into the product: dual-sided referral credits), then
  cook-to-cook word of mouth.

### The customer (non-paying side, the value engine)

- **Profile:** regular diners of home kitchens, with seniors as the
  design center. They bring order volume and repeat behavior — which is
  what makes either revenue model viable.
- **Acquisition:** through the cook (the cook invites their existing
  customers into the chat). The product does not do direct-to-diner
  marketing; win-back and campaigns exist to reactivate a cook's own
  opted-in base.

### Go-to-market sequence

1. **MVP:** 1–2 pilot cooks, human payment reconciliation, measure the
   done criteria (≥50 paid orders, ≥85% completion, ≥30% repeat in
   14 days — assumption, to be measured).
2. **v1.2:** only if growth gates pass (repeat-purchase ≥40%, positive
   contribution margin per order *after* reconciliation labor, 10 cooks
   onboarded with <1 day of support each). Then pick the billing model
   from the measured data.
3. **Scale:** referrals and template-approved campaigns do the local
   marketing; each new cook brings their own customer list.

---

## 5. Costs

### Infrastructure (measured/sourced)

- **Pilot:** near-zero. FAQ documents the pilot stack: Supabase free tier
  (Postgres) + Render free tier ≈ $0/month (**measured** as a documented
  deployment option; free-tier limits are Meta/Render/Supabase policy and
  should be rechecked at pilot time — sourced, not guaranteed).
- **Small always-on setup:** roughly $7–12/month (**sourced** from the FAQ;
  covers a modest always-on host + managed Postgres; recheck at pilot
  time).
- **WhatsApp conversation charges:** Meta bills per 24-hour conversation
  window (**sourced** from Meta's WhatsApp Business pricing; the exact
  per-conversation price is **not in this repo** and must be read off
  Meta's rate card at pilot time — milestones flag this as an explicit
  open item for unit economics). User-initiated conversations (a customer
  messaging the cook first) are the cheapest class; business-initiated
  campaigns require approved templates and cost more. Budget implication:
  per-order variable cost is dominated by this line item.

### Operations labor (assumptions — validate in pilot)

- **Daily payment reconciliation (MVP):** one human checks the cook's
  receipts against BiteFlow payment states daily. Cost is whatever the
  reconciler's time is worth — this is the largest non-infra cost in MVP
  and the v1.2 growth gate explicitly requires contribution margin to be
  positive *after* this labor.
- **Cook onboarding/support:** milestones budget <1 day of support per
  cook for v1.2 scale; MVP expects heavier hand-holding (smartphone
  literacy is a named risk).
- **Template approvals / WhatsApp Business policy:** staff time to get
  order-notification and campaign templates approved by Meta; approval
  delays are a named MVP risk with no cost attached yet.

### What is NOT a cost in MVP

- Payment processing fees (no rail built), delivery logistics (out of
  scope), app-store fees (zero-client), per-seat licensing.

---

## 6. Unit economics per order

All inputs here are **assumptions for modeling** unless labeled otherwise.
They exist to show the shape of the math, not to claim results.

**Worked example — commission model (assumptions):**

| Line | Value | Label |
|---|---|---|
| Average order value | ₹150 | assumption (home-kitchen meal) |
| Platform commission | 10% | assumption (midpoint of 8–12%) |
| Gross revenue per order | ₹15 | arithmetic on assumptions |
| Meta WhatsApp conversation cost per order | ₹2–5 | assumption — **must read Meta rate card at pilot time** |
| Payment reconciliation labor per order | ₹3–8 | assumption — depends on daily batch size |
| Infra per order (amortized) | < ₹1 | assumption at 50+ orders/month on $7–12/mo stack |
| **Contribution per order** | **≈ ₹1–9** | **assumption** |

**Worked example — subscription model (assumptions):**

| Line | Value | Label |
|---|---|---|
| Monthly fee | ₹999 | assumption (milestones v1.2) |
| Orders/month per cook | 100 | assumption |
| Revenue per order (effective) | ₹9.99 | arithmetic on assumptions |
| Variable cost per order (WhatsApp + labor share) | ₹5–13 | assumption (same lines as above) |
| **Contribution per order (effective)** | **≈ ₹0 to −₹3** | **assumption — can go negative at low volume** |

**Reading the table honestly:**

- At 10% commission on a ₹150 order, the platform grosses ₹15 — but Meta
  conversation charges and human reconciliation labor can consume most or
  all of it at pilot scale. The business only works if (a) order values
  are higher, (b) commission % is at the top of the range, (c) WhatsApp
  costs are at the low end (user-initiated conversations), and
  (d) reconciliation labor is amortized across high order volume or
  automated in v1.2.
- The subscription model's viability hinges on orders-per-cook-per-month:
  a cook doing 100 orders/month at ₹999 makes the effective take ~₹10
  per order; a cook doing 30 orders/month pays an effective ~₹33 per
  order and will churn. **Do not set ₹999/month as fact until pilot data
  shows typical cook volume.**
- The single most important unmeasured input is Meta's per-conversation
  price at pilot time. Everything else is second-order until that is
  known.

---

## 7. Risks and what-must-be-true

Consistent with milestones § Risks and § "What must be true" (not
contradicting it; elaborating the business-model implications).

### Risks

1. **Commission collection problem.** If payments stay cook↔customer
   (cash/UPI), the platform has no settlement point to deduct 8–12%.
   The commission model requires either a platform-touched payment flow
   (explicitly out of scope for MVP) or trust-based remittance by the
   cook. **What must be true:** a collection mechanism the cook accepts
   — or the subscription model wins by default.
2. **Payment fraud on trust-based verification.** Screenshot claims can
   be faked; a cook approving a fake screenshot ships food unpaid.
   Mitigation in MVP: human daily reconciliation + per-customer order
   caps during pilot (per milestones). **What must be true:** fraud loss
   rate stays below the contribution margin per order — measure it.
3. **Meta WhatsApp cost and policy.** Conversation pricing can change;
   template approvals can stall; policy violations can suspend the
   business number. Mitigation: user-initiated flows where possible,
   pre-approved templates for business-initiated messages.
   **What must be true:** per-conversation cost known from the rate card
   before pricing is finalized.
4. **Cook support burden.** Smartphone literacy is a named MVP risk; if
   each cook needs days of hand-holding, the v1.2 gate (<1 day support
   per cook) fails. **What must be true:** the cook's-first-day flow
   (documented in `docs/how-to/`) actually works unassisted — the
   milestones done criterion (dish listed with photo + ingredients in
   <5 minutes, unassisted) tests this directly.
5. **Food-safety / regulatory exposure.** Home kitchens face local food
   safety norms (e.g. FSSAI in India — **assumption** flagged in
   milestones, needs local counsel). **What must be true:** counsel
   confirms the operating model before scaling beyond the pilot.
6. **Reconciliation labor doesn't scale.** Daily human reconciliation is
   fine for 1–2 cooks and fatal for 100. **What must be true:** by v1.2,
   either a verified payment rail exists or reconciliation is automated
   enough that contribution margin per order stays positive.

### What-must-be-true (business-model edition)

- WhatsApp Cloud API access approved; order templates approved.
- 1–2 committed pilot cooks; a human reconciler available daily.
- Meta's per-conversation price read off the rate card and plugged into
  the §6 table before any pricing decision.
- Measured repeat rate and order volume support whichever billing model
  is chosen — the choice is made from pilot data, not from this document.

---

## 8. MVP success criteria (tied to milestones.md)

The milestones "Done criteria" are the MVP scoreboard; the business-plan
readout maps each to a business question:

| Milestone done criterion | What it proves for the business |
|---|---|
| ≥ 50 completed paid orders (1–2 cooks) | there is real demand and real money |
| Order completion ≥ 85% (ordered → delivered) | the chat flow doesn't leak orders |
| Repeat order within 14 days ≥ 30% (**assumption**) | habit formation — the base of either revenue model |
| Cook lists dish (photo + ingredients) < 5 min, unassisted | onboarding cost is bounded |
| Zero failed `mr` registrations on live Postgres | India-pilot market is actually servable |
| Zero lost/duplicate orders from webhook redelivery | money-adjacent state is trustworthy |

**Business-plan gate to v1.2:** in addition to the above, the pilot must
produce the measured inputs for §6 — actual average order value, actual
Meta conversation cost per order, actual reconciliation minutes per order,
and actual repeat rate. The billing-model decision (commission vs
subscription) is made from those numbers, per the milestones growth gates
(repeat-purchase ≥ 40%, positive contribution margin after reconciliation
labor, 10 cooks at <1 day support each).
