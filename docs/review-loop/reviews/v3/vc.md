# BiteFlow — VC Review (v3 milestone package)

Reviewer: Persona #6 (VC). Rubric: monetization, unit economics,
money-movement honesty, moat. Independent review — findings only, no fixes.
Docs read: `docs/milestones.md`, `docs/business-plan.md` (each twice),
`docs/videos/v3-presentation-plan.md` (business-model sections).

**Verdict: NEEDS WORK**

The package is unusually honest (every number labeled measured / sourced /
assumption, binding unknowns named on screen), which is exactly why it
doesn't survive a VC pass yet: the arithmetic, re-run from the plan's own
assumptions, fails in two places, the billing "decision" is a punt, and the
moat question is never asked. Strengths first, because credit matters: the
money-movement stance is perfectly consistent across all three documents, and
the unit-economics table labels the binding unknown (Meta per-conversation
price) instead of hiding it.

---

## Blockers

### B1. Commission vs subscription "decision" has no decision rule — and the commission candidate is structurally uncollectable
- Refs: `docs/milestones.md` v1.2 growth gates ("Billing model chosen from
  measured pilot data, not before"); `docs/business-plan.md` §2, §3, §7
  risk 1; `docs/videos/v3-presentation-plan.md` §4.
- Expectation violated: a gated decision needs a stated mapping from measured
  inputs to the choice — e.g. "if repeat ≥ X, AOV ≥ ₹Y, orders/cook ≥ Z, and
  a collection mechanism the cook accepts → commission; else subscription."
  No such rule exists anywhere in the package. "Decide from pilot data" is
  currently a punt with good grammar.
- Worse, §7 risk 1 admits the commission model cannot be collected while
  payments stay cook↔customer: "the platform has no settlement point to
  deduct 8–12%… the commission model requires either a platform-touched
  payment flow (explicitly out of scope for MVP) or trust-based remittance
  by the cook," concluding "a collection mechanism the cook accepts — or the
  subscription model wins by default." If subscription wins by default
  unless an unsolved design problem is solved, the two models are not
  symmetric candidates — and the video plan (§4) presents them as symmetric
  alternatives. Say so in the docs: either state the decision rule (with the
  collection mechanism as the tie-breaker) or drop commission as a v1.2
  candidate.

### B2. Unit economics don't survive the package's own evidence: ₹150 AOV vs the ₹85 menu item
- Refs: `docs/business-plan.md` §6 (AOV ₹150, assumption); §3 (₹12–18/order
  at 8–12%); `docs/videos/v3-presentation-plan.md` §2 (real engine output:
  "Veg Pulao ₹85.00").
- Expectation violated: a labeled assumption is fine, but §6's entire
  commission case rests on it, and the package's own evidence frame shows a
  flagship menu item priced at ₹85 — 43% below the assumption. At ₹85, 10%
  commission grosses **₹8.50/order** against §6's own variable costs of
  ₹5–14 (₹2–5 WhatsApp + ₹3–8 reconciliation + <₹1 infra) — the model is
  underwater before the pilot starts. If AOV is ₹150 because orders average
  ~2 items, say that (with the basket-composition assumption made explicit);
  otherwise re-run §6 at the evidence price. A VC cannot underwrite
  contribution-per-order of "≈ ₹1–9" when the package itself shows the
  price point that would make it negative.

---

## Majors

### M1. Subscription-model arithmetic doesn't close — the upside is misstated
- Ref: `docs/business-plan.md` §6 (subscription table).
- Re-run from the plan's own assumptions: ₹999 ÷ 100 orders = ₹9.99
  effective revenue/order; variable cost ₹5–13/order (₹2–5 WhatsApp +
  ₹3–8 labor share). Contribution = 9.99 − 5 = **≈ +₹5** (best) to
  9.99 − 13 = **≈ −₹3** (worst). The plan states "≈ ₹0 to −₹3" —
  the entire positive tail is missing. The upside case is the one that
  justifies the ₹999 price point to a cook; erasing it misstates the
  model's own argument. Fix the range.

### M2. The full 8–12% commission range is never modeled — the low end is underwater
- Ref: `docs/business-plan.md` §6, §3.
- §6 models only the 10% midpoint (₹15 gross, ≈ ₹1–9 contribution). At the
  range's low end — 8% × ₹150 = ₹12 gross against ₹5–14 variable cost —
  contribution is **−₹2 to +₹7**, i.e. negative in the high-cost case.
  The candidate range's lower bound must appear in the table with its own
  contribution line, or the plan should drop 8% from the candidate range.

### M3. No moat — the defensibility question is never asked, let alone answered
- Refs: `docs/business-plan.md` (no moat/defensibility section); `docs/
  milestones.md` (multi-cook marketplace/discovery explicitly out of scope).
- Expectation violated: a subscription product at ₹999/month needs a "what
  stops a clone" answer. What's here is a zero-client WhatsApp bot plus a
  notebook-replacement P&L — both highly cloneable, including by any
  cook-savvy agency or by Meta's own WhatsApp Business feature evolution.
  With marketplace/discovery out of scope there are no network effects;
  the cook's customer list is the cook's, so switching cost is near zero;
  the only retention argument in the plan (§3: the owner addendum "must
  demonstrably save the cook money or time worth more than ₹999/month") is
  framed as a hope, not a moat. Add the honest version: the defensible bet
  is execution depth (locale/voice UX for seniors, margin-alert
  intelligence), cook relationships via the referral loop, and speed —
  not a structural moat. A VC funds this as an execution play only if the
  plan says so.

### M4. MVP success criteria prove a free product, not a business
- Refs: `docs/milestones.md` MVP done criteria; `docs/business-plan.md`
  §8 ("≥ 50 completed paid orders… there is real demand and real money").
- Expectation violated: the money that flows in MVP flows cook↔customer —
  the platform captures none of it. §8's "real money" readout overclaims:
  it proves cooks and diners will transact through the chat (GMV exists),
  not that the platform can capture value. There is zero willingness-to-pay
  signal in the MVP (the cook pays nothing by design). The package is saved
  from this only by the v1.2 gate — "positive contribution margin per order
  *after* payment-reconciliation labor" — which is the first genuine
  business test. §8 should label the MVP criteria as demand validation and
  name the contribution-margin gate as the business-validation moment;
  consider adding a directional WTP probe to the pilot (e.g. cook reaction
  to a stated ₹999/month price) so the billing decision isn't made from a
  zero-price baseline.

### M5. Commission collection is a design problem, not a measurement problem — the gate can't resolve it
- Refs: `docs/business-plan.md` §7 risk 1; §3 ("Collection mechanism must
  be designed… open question for v1.2"); `docs/milestones.md` v1.2 in scope.
- The growth gates measure repeat, margin, and support burden — none of
  which produces a collection mechanism. Trust-based remittance by the cook
  is the only named path and it has no enforcement. If the pilot shows
  great numbers and no collectible mechanism, the "decision" collapses to
  subscription by default (which the plan admits). The milestone package
  should name collection-mechanism design as explicit v1.2 scope with its
  own acceptance test, not leave it as an open question while the gate
  pretends the data will decide.

---

## Minors

### m1. "UPI intent/collect" in scope vs "no money-movement rails" in the plan — needs one clarifying line
- Refs: `docs/milestones.md` MVP in scope #4 ("UPI intent/collect +
  screenshot reconciliation"); `docs/business-plan.md` §2 ("No
  money-movement rails are built or operated by BiteFlow in MVP").
- If "UPI intent" means generating an intent against the *cook's* VPA
  (money still moves customer→cook directly), the two statements are
  compatible — but "collect" reads like platform-initiated collection.
  One line in the plan ("intents reference the cook's own VPA; the
  platform neither initiates settlement nor sees funds") removes the
  ambiguity. No other money-movement inconsistency found: milestones,
  plan, and video plan are unanimous that the platform never holds funds
  in MVP.

### m2. Reconciliation labor is the binding cost and the least-measured assumption
- Ref: `docs/business-plan.md` §5, §6 (₹3–8/order, "depends on daily batch
  size"); milestones "What must be true" (human available daily).
- The ₹3–8/order range is the widest relative input in §6 and it's the
  difference between ₹9 and ₹1 contribution. The pilot's single most
  valuable business measurement is minutes-per-reconciled-order; worth
  naming explicitly as the #1 pilot metric in §8's business-plan gate.

### m3. Subscription break-even is stated but the churn threshold isn't turned into a gate
- Ref: `docs/business-plan.md` §6 ("a cook doing 30 orders/month pays an
  effective ~₹33 per order and will churn").
- This is the subscription model's kill criterion and it deserves a place
  in the v1.2 growth gates: minimum median orders/cook/month (and minimum
  median cook GMV) below which the subscription price is repriced or the
  model is abandoned.

---

## Money-movement honesty (b)

Consistent across all three documents. Milestones: payments trust-based,
in-app/verified payments and cook subscriptions out of scope for MVP.
Business plan §1–§2: "No money moves through BiteFlow; it tracks payment
state only," with the explicit rationale (avoids UPI/PPI licensing).
Video plan §4: "BiteFlow takes no commission in this build; money moves
cook↔customer directly, off-platform." The diagram, the narration "must
say," and the claim-to-evidence map all restate it. No section implies
platform-held money. The only blemish is m1 (UPI collect wording).

## Deferred billing decision (c)

"Decide from pilot data" is a real gate on *timing* (the v1.2 growth gates
are measurable: ≥40% repeat, positive post-labor contribution margin, 10
cooks at <1 day support) but a punt on *the decision itself*: no rule maps
the measured inputs (AOV, conversation cost, reconciliation minutes,
repeat, orders/cook) to commission vs subscription, and B1 shows the
candidates aren't symmetric anyway. The gate will produce data; it won't
produce a decision.

## Moat (d)

None stated. See M3. The honest moat story is execution depth in
senior-accessible WhatsApp commerce + cook relationships + speed — but the
plan doesn't tell it.

## MVP success criteria as business proof (e)

They prove demand exists and the chat flow doesn't leak orders. They do
not prove a business: no platform revenue, no willingness-to-pay signal,
and the one money claim ("real money") describes money the platform never
touches. The v1.2 contribution-margin gate is the actual business test;
the package should say that plainly (M4).
