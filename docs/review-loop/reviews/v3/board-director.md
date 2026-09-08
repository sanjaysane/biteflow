# Board Director Review — v3 Milestone Package (BiteFlow)

**Verdict: NEEDS WORK**

Method: read `docs/milestones.md`, `docs/business-plan.md`,
`docs/videos/v3-presentation-plan.md`; verified every public-facing claim
against `docs/evidence/*` (test-run-2026-09-07.txt, postgres-mr-verification.txt,
product-experience-2026-09-07.txt), `sql/schema.sql`, `sql/migrations/`,
and git history on `main`. The three docs are unusually honest in their
labeling discipline (measured / sourced / assumption; proposal status).
That discipline is what makes the two findings below real: they are
places where the docs contradict *themselves* or the repo's own evidence —
exactly what a journalist would print.

---

## Claim-audit table

| # | Claim (as a viewer would hear/read it) | Location | Evidence | Verdict |
|---|---|---|---|---|
| 1 | "65 tests passing, 2 skipped; Ruff clean; CI green" | milestones.md, "Where we are" | test-run-2026-09-07.txt last line: `69 passed, 2 warnings in 1.87s` — zero skips | **unsupported** (stale on both numbers) |
| 2 | "Known gap #1: mr/Postgres language constraint… an mr registration could fail on live Postgres" (+ MVP in-scope #1: "Fix the mr/Postgres language constraint"; done criterion: "Zero failed mr registrations") | milestones.md, Known gaps / MVP / Done criteria | **The gap is closed on main:** commit `1844781` ("fix(i18n): allow Marathi 'mr' locale"), `sql/schema.sql:40` CHECK now includes `'mr'`, `postgres-mr-verification.txt` Step 2 (rejected before migration) → Step 4 (`mr` insert succeeds) → Step 5 (app-level round-trip) | **unsupported as "open"** — the video plan's FIXED claim is the true one; milestones are stale |
| 3 | "mr/Postgres constraint — FIXED, migration 006 verified" | v3-presentation-plan.md §3 Transition card | Evidence above (commit, schema, verification transcript) | **supported** |
| 4 | "69 tests pass (2 warnings, deprecation-only)" | v3-presentation-plan.md §3 claim map | test-run log last line; warnings summary shows `StarletteDeprecationWarning` (httpx/starlette) — deprecation-only confirmed | **supported** |
| 5 | Menu/nickname/currency/inventory frames are "real engine output… No mocks, no hand-written values" | v3-presentation-plan.md §3 | product-experience-2026-09-07.txt header line 68: "No mocks, no hand-written values" | **supported** |
| 6 | "BiteFlow takes no commission in this build; money moves cook↔customer directly, off-platform" | v3-presentation-plan.md §4 must-say; business-plan.md §1–§2 | Plan's own §2 money-flow diagram; "No money moves through BiteFlow; it tracks payment state only" | **supported** |
| 7 | "Payments are trust-based: screenshot verification, no bank-verified rail" | milestones.md gap #3; v3 plan §3 card + §4 non-goal #2 | business-plan.md §1: "a screenshot is a claim, not settled funds" | **supported** (disclosed, not asserted falsely) |
| 8 | "Contribution per order ≈ ₹1–9" / commission "8–12%" / subscription "₹999/mo (IN) / $29/mo (US)" | business-plan.md §6; v3 plan §4 on-screen | Every row labeled **assumption**; business plan §6 "Reading the table honestly" + v3 plan non-goal #3 (assumptions labeled on screen) | **supported** — labeled as assumptions, never facts |
| 9 | "Meta per-conversation price must be read from the rate card at pilot time — no rate card number quoted" | business-plan.md §5; v3 plan §4 + non-goal #4 | Absence confirmed: no price appears anywhere in the three docs | **supported** (refusal-to-quote is itself the honest claim) |
| 10 | "the WhatsApp side uses the same code path as production" | v3-presentation-plan.md §2 §1 must-say | RoomLens-style qualifier ("sans network") is missing here; milestones gap #4: demo used **fake/local WhatsApp adapters, not the live Meta Cloud API** — i.e. the transport side is precisely what is *not* production | **needs disclosure** — rephrase before render (see M2) |
| 11 | "Marathi is partial — missing keys fall back to English" | milestones.md; v3 plan non-goal #5 | tests `test_mr_is_subset_of_en`, `test_mr_falls_back_to_english_for_missing_keys` (claim map) | **supported** |
| 12 | Milestones are a **proposal, not yet board-reviewed**; business plan is a **draft for board review**; video §6 Ask requests *approval* of the scope | milestones.md header; business-plan.md header; v3 plan §6 | Labels present at the top of both docs; Ask phrased as first approval, no prior-approval implication | **supported** — (c) satisfied |
| 13 | Pilot infra "≈ $0 on free tiers / ~$7–12 always-on" | business-plan.md §5 ("measured as a documented deployment option"); v3 plan §3 claim map ("sourced from FAQ") | FAQ-documented; both docs add "recheck at pilot time" | **supported with disclosure** — but the two docs label it differently ("measured" vs "sourced"); see minor m2 |

---

## Blocker

### B1. Milestones contradict the video plan on the #1 India-pilot gap

**Docs/sections:** `docs/milestones.md` — Known gaps #1; MVP In scope #1;
Done criteria ("Zero failed `mr` registrations against live Postgres");
vs `docs/videos/v3-presentation-plan.md` — §3 Transition card ("`mr`/Postgres
constraint — **FIXED, migration 006 verified**").

**What is true:** the fix is merged on `main` (commit `1844781`,
`sql/migrations/006_allow_marathi_locale.sql`, `sql/schema.sql:40` now
`CHECK (preferred_language IN ('en','es','hi','mr'))`) and verified against
live Postgres (`postgres-mr-verification.txt` Steps 2→4→5). The video plan's
FIXED claim is supported; the milestones' framing of it as still-open work is
not.

**Expectation violated:** claim audit — a proposal must not present as a
"known gap" something the repo's own evidence proves closed; public-embarrassment
test — a journalist comparing the two docs gets two answers on the single
gating item for the Marathi/India pilot, and it reads as either sloppy or
padded scope ("we asked the board to approve fixing something we already
fixed").

**Required before ship:** move gap #1 into milestones "Where we are
(implemented)" with the commit/evidence cite; remove it from MVP In scope;
convert the done criterion into a recorded verification (it is already
verified — `test_postgres_marathi_locale_accepted` + the verification
transcript). The video plan's §3 card ("listing the milestones Known gaps
verbatim… labeled FIXED or OPEN") then needs no reconciliation logic for
this item.

---

## Major findings

### M1. Stale test-count numbers in milestones.md

**Doc/section:** `docs/milestones.md`, "Where we are" — "65 tests passing,
2 skipped; Ruff clean; CI green."

**What is true:** `docs/evidence/test-run-2026-09-07.txt` (same date as the
milestones doc) ends `69 passed, 2 warnings in 1.87s` — **zero** skips.
The video plan (§3 claim map) correctly says 69. The milestones doc is wrong
on both numbers.

**Expectation violated:** claim audit — a fact-checker opens the repo's own
evidence directory and the headline test count doesn't match; Sanjay's
pre-ship verification standard (never present a stale number as current).

**Fix:** change to "69 tests passing (2026-09-07), Ruff clean, CI green."

### M2. "Same code path as production" overstates the WhatsApp transport

**Doc/section:** `docs/videos/v3-presentation-plan.md`, §2 §1 must-say:
"what you're about to see is real output of the real system talking to a real
database; **the WhatsApp side uses the same code path as production**, but the
pilot build has known gaps we'll name at the end."

**What is true:** the engine/state-machine path is real, but milestones gap #4
states the demo used **fake/local WhatsApp adapters, not the live Meta Cloud
API** — the transport side is precisely what is *not* production. RoomLens's
plan gets this phrasing right ("same code path as production, **sans
network**"); BiteFlow's must-say line doesn't.

**Expectation violated:** public-embarrassment test — the intro sentence is
the quotable one; "the WhatsApp side uses the same code path as production"
can be played against the plan's own gap #4 disclosure ("demo used fake/local
adapters"). Disclosure sufficiency requires the looser sentence to carry the
qualifier.

**Fix:** rephrase the must-say to: "the engine and database path are the real
production code; the WhatsApp transport in this demo is a local adapter, not
the live Meta Cloud API." (Non-goal #1 already says this correctly — align the
intro with it.)

---

## Minor findings

- **m1 — Infra-cost label drift between docs.** `business-plan.md` §5 calls
  the $0/$7–12 stack "**measured** as a documented deployment option"
  (its own key defines measured = verified in this repo/CI — a documented
  option is not that); the video plan's claim map (§3) correctly calls it
  "(sourced from FAQ)". Align the business-plan label to **sourced**.
  Expectation: claim audit — the label key is the docs' own contract.
- **m2 — Uneven evidence pointers in "Where we are."** Every implemented
  bullet cites a commit (`113881b`, `e936e28`, `814e6c4`) except "Owner
  addenda: kitchen economics, marketing/growth playbooks," which cites none.
  Add the commit(s) or mark the pointer. Expectation: claim audit — a
  commit-cited list with one uncited item reads as the unverified one.

---

## Rubric answers

1. **Claim audit.** One blocker (B1: gap #1 presented as open when the repo
   proves it fixed), one stale-number major (M1: 65+2 vs evidence's 69+0),
   plus the loose intro phrasing (M2). Everything else in the claim map
   traces to evidence — the assumption labeling in the business plan is
   exemplary and the "no rate-card number quoted" posture is the right call.
2. **Public-embarrassment test.** The journalist's hard questions all have
   on-plan answers: trust-based payments (disclosed as trust-based, no
   "secure payments" language), money never touches the platform
   (must-say, verbatim), food-safety compliance (non-goal #7 keeps it in the
   spoken disclosure), no live WhatsApp API (gap #4). After B1 and M2 are
   fixed, nothing in the three docs is quotable-against-itself.
3. **Disclosure sufficiency.** The Transition section (§3) correctly gives
   spoken time to the two OPEN items (webhook hardening, live Meta API);
   the v2 failure modes (footer-flash disclosure, mid-thought starts) are
   explicitly designed out. No material item lives only in a sidecar.
4. **Milestones-as-proposal honesty (c).** Satisfied: both docs label
   themselves proposal/draft-for-review at the top, and §6 asks the board
   to *approve* the scope — a first approval, never implied as a
   re-approval.
5. **Pilot-scale limits (b).** Carried: every unit-economics row is labeled
   assumption; the binding unknown (Meta rate card) is named and never
   quoted.
