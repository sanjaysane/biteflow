# Product Manager review — BiteFlow v3 milestone package

Reviewer persona: Product Manager (the user's first hour).
Scope: `docs/milestones.md`, `docs/business-plan.md`,
`docs/videos/v3-presentation-plan.md`, `README.md`, `docs/how-to/`.
Reviewers never fix — findings only.

## Verdict: NEEDS WORK

---

## Blocker

### B1. The v3 walkthrough never shows a first order — the money-adjacent loop the business model depends on

- **Ref:** `docs/videos/v3-presentation-plan.md` §2 (Walkthrough, target 6:00).
- **Expectation violated:** PM rubric (b) — the walkthrough must cover the true
  day-one flows (first order) completely and unhurried. Also violated: the
  plan's own §2 purpose line, which promises "the *complete* product loop a
  real user would live through: cook lists a dish → customer orders → cook
  accepts → customer is updated → money state is tracked."
- **Finding:** §2's six on-screen frames are (1) the `mr` user row on live
  Postgres, (2) the menu listing the Marathi customer received, (3) the
  nickname/currency lines, (4) the inventory seed table, (5) the Devanagari
  round-trip rows, (6) the CHECK-constraint catalog line. None of them shows
  a customer placing an order, the single-digit order flow (`Reply 1`,
  quantity, `0` checkout — documented in `README.md` "How a chat flows" and
  `docs/how-to/cooks-first-day.md`), the cook's Accept/Reject, the payment
  screenshot approve/deny, or the Cooking → ready → delivered status updates.
  The claim-to-evidence map (§3) confirms the hole: every row backs
  localization, inventory, and registration — not the order loop. A first-hour
  viewer never sees what the MVP's own first done criterion (≥50 completed
  paid orders, `docs/milestones.md`) actually looks like, and the board is
  asked to approve a business model (business-plan.md §2, §6) whose core
  transaction never appears on screen. The v2 §1 critique already flagged
  "v2's center of gravity is setup mechanics, not product behavior" — §2
  replaces setup mechanics with localization mechanics and still skips the
  product's primary transaction.
- **Required:** re-balance §2 so at least half of the 6:00 shows one real
  customer order end-to-end (menu → order → cook accepts → payment state
  tracked → status updates), from evidence transcripts — drop two of the
  three DB-introspection frames (see M1) to make room.

## Major

### M1. Three of six walkthrough frames are Postgres introspection — the section sags on infra evidence

- **Ref:** `docs/videos/v3-presentation-plan.md` §2 items 1, 5, 6 (user row,
  round-trip rows, constraint catalog line).
- **Expectation violated:** the video bar's pacing requirement — "complete
  unhurried walkthrough of ACTUAL behavior" means product behavior, not
  database internals. Roughly 3 of the 6 walkthrough minutes are spent on
  `users.preferred_language` rows and catalog introspection, which is
  dev-register content in a board pitch. A cold viewer can absorb the Marathi
  fix in one frame ("`mr` registrations work — verified on live Postgres")
  instead of three.
- **Required:** collapse items 1/5/6 into a single 45–60 s "the Marathi fix
  is real" beat.

### M2. The cook's dish-listing flow — the onboarding-friction beat the MVP scoreboard depends on — is never shown

- **Ref:** `docs/milestones.md` MVP done criteria ("Cook lists a dish with
  photo + ingredients in < 5 minutes, unassisted"); `docs/how-to/cooks-first-day.md`
  (cook's first-day flow).
- **Expectation violated:** PM rubric (b) — cover onboarding friction, don't
  skip it. §2 "What it PROVES" claims "(a) cook menu flow with photo +
  ingredients + description," but the on-screen evidence (menu listing frame)
  shows the menu as the *customer* received it — the output, not the flow.
  The viewer never sees the cook typing a dish name, entering a price, adding
  a photo + ingredients, and getting the live confirmation — the single
  highest-friction moment in the MVP (smartphone literacy is a named MVP
  risk in milestones § Risks).
- **Required:** show the listing flow once (the cook's side), held long
  enough to read, before the customer-side menu frame.

## Minor

### m1. Intro states who it's for but not who pays

- **Ref:** `docs/videos/v3-presentation-plan.md` §1 (Intro, target 2:00);
  `docs/business-plan.md` §1 ("Who pays" / "Who does NOT pay").
- **Expectation violated:** the plan's own §1 v2 analysis flags "no
  who-pays framing" as a v2 failure; the v3 intro still leaves it out. The
  viewer learns the customer pays nothing and the cook pays eventually only
  in §4 (~minute 9). One sentence in the intro ("customers order for free;
  cooks use it free in the pilot — the platform monetizes the cook side
  later") closes it.
- **Fix:** add the one-liner to §1's "Must say."

### m2. Stale "Still open (v3 round)" in milestones.md

- **Ref:** `docs/milestones.md`, final section ("Still open (v3 round)").
- **Expectation violated:** document currency — the section lists
  `docs/business-plan.md` and the v3 pitch video as open items, but both
  artifacts exist and are dated 2026-09-07 (business-plan.md v1;
  `docs/videos/v3-presentation-plan.md`). A reviewer cannot tell which parts
  of the doc reflect the current package.
- **Fix:** update the section to reflect what's actually still open (board
  review itself).

---

## Rubric coverage summary

- **(a) 60-second clarity — PASS (with m1).** The §1 intro states the product
  category, the zero-client thesis, the audience (home cooks + customers,
  seniors included), and the honest boundary ("pilot-grade build, not
  hardened production") before any terminal or chat appears. A cold viewer
  can state what BiteFlow is within 60 seconds.
- **(b) Day-one flows — FAIL (B1, M2).** The walkthrough covers localization
  and inventory evidence completely but skips the first-order flow entirely
  and the cook-listing flow partially.
- **(c) Pacing — MIXED.** Section totals (2 + 6 + 1.5 + 2.5 + 1 + 1 ≈ 14 min)
  sit inside the 13–15 min target; §3 (Transitions) and §4 (Business model)
  are well-budgeted — disclosures get spoken airtime, the money-flow diagram
  and contribution table appear with assumption labels. But the flagship
  walkthrough sags on three DB-introspection frames (M1).
- **(d) Milestones — PASS.** MVP "First real kitchen" is genuinely minimal:
  the `mr`/Postgres fix, minimum webhook hardening, live Meta API +
  templates, trust-based payments with explicit daily human reconciliation,
  status updates, and a dashboard that reuses the already-implemented owner
  addendum. Out-of-scope exclusions (verified payments, delivery, multi-cook
  marketplace, ratings, cook subscriptions) are correctly drawn. v1.2
  properly follows from measured data: the growth gates (repeat ≥40%,
  positive contribution margin *after* reconciliation labor, 10 cooks at
  <1 day support each, billing model chosen from data) gate the
  commission-vs-subscription decision on pilot measurement, not opinion.
