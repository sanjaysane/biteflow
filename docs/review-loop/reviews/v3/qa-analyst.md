# QA Analyst review — BiteFlow v3 milestone package

Reviewer persona: QA Analyst (verify every claim; entry/exit coverage; caption/frame accuracy).
Date: 2026-09-07. Scope reviewed: `docs/milestones.md`, `docs/business-plan.md`,
`docs/videos/v3-presentation-plan.md`, spot-checked against `docs/evidence/`
(`test-run-2026-09-07.txt`, `product-experience-2026-09-07.txt`,
`postgres-mr-verification.txt`) and `git log`.

**Verdict: NEEDS WORK**

## Blocker findings

None.

## Major findings

### M1 — milestones.md "Where we are" cites a stale test count contradicted by evidence

- **The claim:** `docs/milestones.md` § "Where we are (implemented)": *"65 tests passing, 2 skipped; Ruff clean; CI green."*
- **Where it appears:** `docs/milestones.md`, line 17.
- **The evidence checked:** `docs/evidence/test-run-2026-09-07.txt` last line reads
  `======================== 69 passed, 2 warnings in 1.87s ========================`;
  a grep for `SKIPPED` across the whole log returns 0 lines. Suite = **69 passed / 0 skipped**.
- **Expectation violated:** every figure in the package must trace to its evidence artifact.
  The v3 presentation plan (§1 table) already flagged the v2 scripts' stale "47 tests" figure,
  but the milestones document — the authoritative milestone package, written the same day
  (2026-09-07) as the test rerun (commit `84938e0`) — still carries its own stale figure
  ("65 passing, 2 skipped"). Fix: refresh the line to "69 tests passing, 0 skipped" (or reword
  as a pointer to the evidence log).

### M2 — milestones.md "Known gaps #1" lists an already-fixed bug as still open

- **The claim:** `docs/milestones.md` § "Known gaps": *"1. **Marathi on Postgres**: `schema.sql`
  language constraint allows only `en/es/hi` — an `mr` registration could fail on live Postgres
  (SQLite tests pass). Fix + test against live Postgres before pilot."* MVP "In scope" #1 repeats:
  *"Fix the `mr`/Postgres language constraint; test full `mr` registration against live Postgres."*
- **Where it appears:** `docs/milestones.md`, "Known gaps" #1 and "MVP — In scope" #1.
- **The evidence checked:** fix commit `1844781` ("fix(i18n): allow Marathi 'mr' locale on
  users.preferred_language") and `sql/schema.sql` line 40 on HEAD already allows
  `('en', 'es', 'hi', 'mr')`. `docs/evidence/postgres-mr-verification.txt` Step 2 shows the CHECK
  violation on the old schema; Step 3 applies migration `006_allow_marathi_locale.sql`;
  Step 4's `mr` insert succeeds. The v3 presentation plan §3 claims this gap is **FIXED** and
  cites the same verification file.
- **Expectation violated:** the milestone package must be internally consistent and describe
  `main` as it is. The consequence is real: the board would gate the MVP on work that is already
  done (fix + live-Postgres verification), misallocating pilot scope. The milestones doc needs a
  "gap #1 closed" update and MVP scope #1 rewritten as verification/regression coverage, not a fix.
- **Note:** this is the one stale figure the v3 plan's §1 analysis does NOT flag — it flags the
  v2 scripts' "47 tests" and "three languages" figures, but misses that `docs/milestones.md`
  itself is stale.

## Minor findings

### m1 — "measured" label on pilot-infra cost stretches the label key

- **The claim:** `docs/business-plan.md` §5: *"Supabase free tier (Postgres) + Render free tier
  ≈ $0/month (**measured** as a documented deployment option...)"* and *"$7–12/month
  (**sourced** from the FAQ...)"*.
- **The evidence checked:** `docs/FAQ.md` lines 35–37 do document both figures ("Near-zero for a
  pilot: Supabase free tier (Postgres) + Render free tier", "$7–12/month" for always-on).
- **Expectation violated:** the label key defines **measured** = "verified in this repo/CI";
  a FAQ sentence is documentation, not measurement. The document qualifies it
  ("measured as a documented deployment option") and the numbers are accurate to the FAQ, so no
  numeric change is needed — but the honest label for a documented deployment option is
  **sourced**, not **measured**. One-word fix.

## What verified cleanly (for the record)

- **Milestones metrics are measurable / MVP gates are falsifiable.** ≥50 paid orders, ≥85%
  completion, ≥30% repeat in 14 days (explicitly labeled assumption), dish listing <5 min
  unassisted, zero failed `mr` registrations, zero lost/duplicate orders — all are countable and
  have clear fail states. Nothing in the done criteria is hand-wavy.
- **Business-plan figure labeling is otherwise disciplined.** §6 unit-economics table labels
  every row; §1–§3 correctly label pricing (8–12%, ₹999/$29) as assumptions; Meta rate-card
  numbers are explicitly *not* quoted (plan non-goal §3 #4). No invented numbers found —
  the one boundary case is m1 above.
- **Claim-to-evidence map (§3) spot-checks all pass.** 10 cited test names
  (`test_postgres_marathi_locale_accepted`, `test_money_locale_formatting`,
  `test_mr_customer_sees_inr_not_usd`, `test_en_customer_still_sees_usd`,
  `test_inventory_seeded_with_realistic_stock`, `test_cook_can_attach_photo_ingredients_description`,
  `test_nicknames_shown_instead_of_phone`, `test_p2p_screenshot_approval_flow`,
  `test_mr_is_subset_of_en`, `test_mr_falls_back_to_english_for_missing_keys`) each appear in
  the test log as PASSED. Product-experience strings verified verbatim: "📋 Meena Kaki चा मेनू",
  "Veg Pulao — ₹85.00", `₹1,25,000.50`, Devanagari round-trip rows, and the catalog output
  `CHECK ((preferred_language = ANY (ARRAY['en'::text, 'es'::text, 'hi'::text, 'mr'::text])))`.
  The file header states real engine + real Postgres output, no mocks.
- **Commit citations check out:** `113881b` (dish photos), `e936e28` (nickname/currency),
  `814e6c4` (inventory seed) all exist on `main`; `1844781` is the `mr` fix.
- **Locale-parity claim is exact:** `locales/en.json`, `es.json`, `hi.json` each hold 162 keys;
  `mr.json` holds 70 — matches the business plan's "full; Marathi partial" statement.
- **No v2-stale figures leak into the v3 narrated claims.** The claim map correctly supersedes
  "47 tests" → 69 and "three languages" → four-locale reality. The staleness problem is confined
  to `docs/milestones.md` (M1/M2), not the v3 plan.

## What needs to change before ship

1. Refresh `docs/milestones.md` "Where we are": 69 passed / 0 skipped (M1).
2. Mark "Known gaps #1" closed (fix commit `1844781`, migration 006, verified on live Postgres)
   and rewrite MVP scope #1 as verification coverage rather than a fix (M2).
3. Relabel the $0 pilot-infra line from **measured** to **sourced** (m1).
