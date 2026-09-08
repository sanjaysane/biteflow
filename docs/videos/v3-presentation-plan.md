# BiteFlow — v3 pitch video presentation plan (for 7-persona board review)

Date: 2026-09-07. Status: **plan** — input to the v3 review package.
Video bar (non-negotiable): intro → complete unhurried walkthrough of ACTUAL
behavior → transitions → business model → summary → ask, never starting
mid-thought. Every on-screen product pixel is real engine output from the
Phase-1 evidence files below. Total target: **13–15 minutes, unhurried.**

---

## 1. v2 script analysis (what the v2 scripts get wrong for a pitch)

The v2 scripts are *how-to tutorials*, not a pitch. They were written for
three different audiences (junior dev, deployer, cook) and assume prior
context. Against the video bar, each fails on structure and pacing:

### video-1-local-setup.md (10 scenes in ~8.5 min)

| Issue | Detail |
|---|---|
| **Starts mid-thought** | Scene 1 cold-opens with "from zero to a working local server" — no problem statement, no who-pays framing, no intro to what BiteFlow *is* for a viewer who hasn't seen the product. A board member joining cold learns the stack before the reason it exists. |
| **Rushed** | Scenes 2–5 (clone/tour → boot → docker → green tests) compress a full dev loop into ~7.5 min with six `Say:` blocks — narration never lingers on any one real behavior. The test-suite scene runs `pytest`, `ruff`, and `check_locales` back-to-back in 2 minutes with no pause to explain what the tests prove. |
| **Stale claim** | "Forty-seven tests drive the state machine" — evidence (`docs/evidence/test-run-2026-09-07.txt`) shows **69 passed** as of 2026-09-07. The script under-claims and is out of date. |
| **Outdated language claim** | "three languages built in … '158 keys × 3 languages'" — the product now has a fourth locale (Marathi, partial; 69-test suite includes `test_mr_*` tests and `mr` round-trips on live Postgres per `docs/evidence/postgres-mr-verification.txt`). v2 either over-claims (Marathi parity) or under-claims (three, not four). |
| **No summary / no ask** | Scene 6 outro hands off to "video 2" — there is no recap of what was shown, no business moment, no ask. A pitch needs all three. |
| **Dev-audience only** | A pitch audience (board, VC, external user) never needs to see `pip install` — v2's center of gravity is setup mechanics, not product behavior. |

### video-2-deploy-render.md (~11 min)

| Issue | Detail |
|---|---|
| **Starts mid-thought** | Scene 1: "Local works. Now let's put BiteFlow on the public internet" — explicitly depends on video 1. As a standalone pitch it is incoherent. |
| **Rushed** | Scenes 2–5 cover blueprint → manual migration → Meta webhook handshake → full real-order loop (customer + cook phones) in ~10 min. Scene 5's "split screen — phone (customer) and laptop logs" compresses the entire money-adjacent flow (order, accept, cooking, done, notifications) into 3 minutes. |
| **Claim not backed by engine output** | Scene 5 narration: "Kill the service mid-order and it resumes — that's the stateless design earning its keep." No evidence artifact in `docs/evidence/` shows a kill-and-resume run. Statelessness is *tested* (stateless round trips in SCALE-style tests) but the kill mid-order demonstration is unproven — v3 must drop it or prove it. |
| **Security disclosure is a footer, not a section** | Webhook signature verification gap gets one on-screen footer line at 10:30. The Board Director seat (FRAMEWORK.md rubric: "claim audit; disclosure sufficiency") needs this as a spoken disclosure with target duration, not a flash frame. |
| **No summary / no ask** | Outro hands off to video 3. |

### video-3-cooks-first-day.md (~9.5 min)

| Issue | Detail |
|---|---|
| **Wrong audience for a pitch** | Written for the cook (senior-friendly, "every step shown twice"). That's a training video, not a pitch — it contains zero business framing, zero investor content, and its "say" lines can't be reused verbatim for a board audience. |
| **Rushed despite "slow pace"** | The script *says* slow pace but Scene 3 packs dish-name typing, price entry, add-another, and the live confirmation into 2.5 min; Scene 5 packs P2P screenshot approval AND the entire business-hub tour (recipes, food cost, margins, weekly buys, nightly earnings) into 2 min. The business hub — the actual monetization-adjacent feature — is the most rushed beat in all three scripts. |
| **Ambiguity on money** | "reply one to approve — but only when the money is really in your account" is the correct disclosure, but the script never says *whose* account, *which* rail (UPI/Zelle/cash), or that there is no verified rail. The v2 review-loop fixes (CHANGELOG A3/A13: "cook-verified, not bank-verified", "no commission in this build") have not been absorbed into this script. |
| **No intro / summary / ask** | Cold title card; outro is a well-wish. |

### Cross-cutting v2 findings (from the v1→v2 review round, carried as plan constraints)

- The swarm caught two **cross-video business-model contradictions** in v1 (CHANGELOG-v1-v2.md) — v3 is a single script and single narrator, so this class of error is structurally prevented.
- The Board Director's **claim audit** must be a first-class plan section (it is — §3 below), not reconstructed after the fact.
- Narrations fixed via surgical re-record in v2 (A22 patch, 2026-09-06): "digest *sends*" → P&L "generated on demand"; "cutout image" → no background removal. v3 narration must use the **corrected** phrasing from the start.

---

## 2. v3 narrative structure (13–15 min, unhurried)

Sections follow the mandatory bar: Intro / Walkthrough / Transitions /
Business model / Summary / Ask. Durations are targets for the narration
build — slower than v2 (v2 averaged ~1.2 min/scene; v3 targets ~2.2
min/section).

### Section 1 — Intro (target 2:00)

- **Purpose:** a cold viewer knows what BiteFlow is, who it's for, and
  why it matters — before any terminal, chat, or demo appears.
- **What it PROVES:** the product category and the audience (home cooks +
  their customers, seniors included), the zero-client thesis (no app to
  install — everything inside plain WhatsApp), and the honest scope (a
  pilot-grade build, not a hardened production system).
- **On screen:** title card + three real engine-output frames from
  `docs/evidence/product-experience-2026-09-07.txt`: the Marathi menu
  listing ("📋 Meena Kaki चा मेनू", Veg Pulao ₹85.00), the locale-aware
  currency lines (`money(85,'mr') = ₹85.00` / `money(85,'en') = $85.00`),
  and the seeded inventory table (Atta 10 kg … Jeera 250 g). All real
  output, zero mockups.
- **Must say (slowly, once):** the honest boundary — "what you're about
  to see is real output of the real system talking to a real database;
  the WhatsApp side uses the same code path as production, but the pilot
  build has known gaps we'll name at the end."

### Section 2 — Walkthrough (target 6:00)

- **Purpose:** show the *complete* product loop a real user would live
  through: cook lists a dish → customer orders → cook accepts → customer
  is updated → money state is tracked. Unhurried: one behavior at a time,
  each shown to completion.
- **What it PROVES:** (a) cook menu flow with photo + ingredients +
  description (b) customer ordering with single-digit replies (c) Marathi
  locale end-to-end on live Postgres (d) nickname display, locale-aware
  currency, and realistic inventory seed — all from evidence.
- **On screen, in order:**
  1. The `mr` customer row from live Postgres (`docs/evidence/product-experience-2026-09-07.txt` § "user row on LIVE Postgres": phone +15550002222, `preferred_language: mr`) — proves the Marathi/Postgres fix (migration 006) is real.
  2. The actual menu listing the Marathi customer received (the 📋 Meena Kaki चा मेनू frame, photo caption, ₹ pricing) — full screen, held ≥20 s, nothing cropped.
  3. The nickname line (`display_name(+15550001111) -> Meena Kaki`) and the Indian-grouping currency line (`₹1,25,000.50`).
  4. The inventory seed table (10 raw materials, INR costs) — held, not skimmed.
  5. The Marathi round-trip rows from live Postgres (संजय साने / पनीर टिक्का / मसालेदार पनीर) — proves Devanagari reads back correctly.
  6. The CHECK constraint catalog line (`users_preferred_language_check … ARRAY['en','es','hi','mr']`).
- **Pacing rule for this section:** every frame that contains product text
  stays on screen until the narration has finished describing it — the
  single biggest v2 pacing flaw was cutting frames before the viewer
  finished reading them.

### Section 3 — Transitions (target 1:30)

- **Purpose:** the honest bridge between "what you just saw" and "what
  it would take to run this for real" — disclosures before the business
  model, so nothing in §4 reads as sandbagging.
- **What it PROVES:** the team knows exactly what is and isn't built.
- **On screen:** a disclosure card listing the milestones "Known gaps"
  verbatim (`docs/milestones.md`): (1) `mr`/Postgres constraint —
  **FIXED, migration 006 verified** (cite `postgres-mr-verification.txt`
  Step 4: `mr` insert succeeds after migration); (2) webhook hardening —
  **not implemented** (signature verification, dedupe, rate limiting);
  (3) payments are trust-based (screenshot approval, no verified rail);
  (4) demo used fake/local WhatsApp adapters, not the live Meta Cloud
  API. Each item labeled FIXED or OPEN.
- **Duration rule:** the two OPEN items get spoken narration, not just a
  card flash (v2's footer-flash failure, see §1).

### Section 4 — Business model (target 2:30)

- **Purpose:** how BiteFlow becomes a business — who pays, how money
  moves, what the unit economics look like, what is unknown.
- **What it PROVES:** the money path is understood *honestly*, with every
  number labeled measured / sourced / assumption per `docs/business-plan.md`.
- **On screen:**
  - The MVP money-flow diagram (business-plan.md §2): customer → cook
    (cash/UPI, direct); cook → platform: **nothing in MVP** (free).
  - The two v1.2 candidates: 8–12% commission **OR** ₹999/mo (IN) /
    $29/mo (US) — **assumption**, chosen from measured pilot data, not
    before (milestones growth gates).
  - The contribution-per-order table (§6): ₹15 gross on a ₹150 order
    (assumption) minus WhatsApp conversation cost ₹2–5 and
    reconciliation labor ₹3–8 → **≈ ₹1–9 (assumption)**.
  - The binding unknown called out on screen: Meta's per-conversation
    price **must be read from Meta's rate card at pilot time** — no rate
    card number is quoted.
- **Must say:** "BiteFlow takes no commission in this build; money moves
  cook↔customer directly, off-platform. That's deliberate — it keeps us
  out of payment licensing while the pilot measures demand."

### Section 5 — Summary (target 1:00)

- **Purpose:** one-minute recap a board member can quote: what was shown,
  what it proves, what's open.
- **What it PROVES:** the walkthrough's claims are restatable without
  the demo in front of you.
- **On screen:** five bullets: (1) real state machine + real Postgres,
  69 tests green; (2) Marathi end-to-end on live Postgres; (3) money
  stays cook↔customer, platform takes nothing in MVP; (4) billing model
  undecided until pilot data; (5) two open gaps: webhook hardening, live
  Meta API.

### Section 6 — Ask (target 1:00)

- **Purpose:** say what the team needs from the board, plainly.
- **What it PROVES:** the pitch ends with a decision request, not a
  fade-out.
- **On screen / spoken:** (1) approve the MVP milestone scope and done
  criteria (`docs/milestones.md`: ≥50 paid orders, ≥85% completion,
  ≥30% repeat in 14 days, zero failed `mr` registrations, zero
  lost/duplicate orders); (2) approve 1–2 pilot cooks in the
  Marathi/India context with daily human payment reconciliation;
  (3) approve the v1.2 billing-model decision gate (commission vs
  subscription from measured data, not before).

---

## 3. Claim-to-evidence map

Every factual claim the video will make, mapped to its backing. Nothing
in §2 is said without a row here.

| Claim (as narrated) | Evidence file / commit |
|---|---|
| 69 tests pass (2 warnings, deprecation-only) | `docs/evidence/test-run-2026-09-07.txt` (last line: `69 passed … in 1.87s`); note supersedes the v2 script's "47 tests" |
| Menu, nickname, currency, inventory frames are real engine output on real Postgres | `docs/evidence/product-experience-2026-09-07.txt` — header states "All engine output above came from the real state machine + real PostgreSQL. No mocks, no hand-written values." |
| Marathi `mr` registration works on live Postgres (gap #1 closed) | `docs/evidence/postgres-mr-verification.txt` — Step 2 CHECK violation before migration 006; Step 4 insert succeeds after |
| `mr` locale accepted in `users_preferred_language_check` | `postgres-mr-verification.txt` + product-experience "CATALOG" section: `ARRAY['en','es','hi','mr']`; test `test_postgres_marathi_locale_accepted` in test-run log |
| Locale-aware currency: ₹ for mr (Indian grouping), $ for en | product-experience § FIX #3: `money(125000.5,'mr') = ₹1,25,000.50`; tests `test_money_locale_formatting`, `test_mr_customer_sees_inr_not_usd`, `test_en_customer_still_sees_usd` |
| Devanagari round-trips through Postgres | product-experience "mr ROUND-TRIP" rows (संजय साने / पनीर टिक्का); `test_postgres_marathi_locale_accepted` |
| Inventory seeded with realistic non-zero stock, INR costs for mr cook | product-experience § FIX #4 (10 materials table); tests `test_inventory_seeded_with_realistic_stock`, `test_inventory_seed_uses_inr_costs_for_mr_cook` |
| Dish photos + ingredients + description in menu | tests `test_cook_can_attach_photo_ingredients_description`, `test_customer_menu_shows_photo_ingredients_description`; milestone "Where we are" (commit `113881b`) |
| Nickname display with phone fallback | product-experience § FIX #2; tests `test_nicknames_shown_instead_of_phone`, `test_phone_fallback_when_no_nickname` |
| Payment tracking is cook-verified, not bank-verified; no commission in this build | `docs/business-plan.md` §1–§2; review-loop CHANGELOG A3/A13; tests `test_p2p_screenshot_approval_flow` |
| Billing model undecided: 8–12% commission OR ₹999/$29 subscription, chosen from pilot data | `docs/milestones.md` v1.2 + `docs/business-plan.md` §3 (all labeled **assumption**) |
| Contribution per order ≈ ₹1–9 (assumption), binding unknown = Meta per-conversation price | `docs/business-plan.md` §6 table; §6 "Reading the table honestly" |
| Webhook hardening NOT implemented (signature, dedupe, rate limiting) | `docs/milestones.md` Known gaps #2; README flag; review-loop CHANGELOG A11 (disclosure added to v2 closing card) |
| Demo used fake/local WhatsApp adapters, not live Meta Cloud API | `docs/milestones.md` Known gaps #4 |
| Pilot infra ≈ $0 on free tiers / ~$7–12 always-on (sourced, recheck at pilot time) | `docs/business-plan.md` §5 (sourced from FAQ) |
| Marathi is partial — missing keys fall back to English | `docs/milestones.md` "Where we are"; tests `test_mr_is_subset_of_en`, `test_mr_falls_back_to_english_for_missing_keys` |

---

## 4. Explicit non-goals (claim-audit hygiene)

v3 will NOT claim any of the following. The board's claim-audit table
stays clean because these stay out of the narration and off the screen:

1. **No live Meta WhatsApp Cloud API.** The demo runs the production
   code path through fake/local adapters. We will not say "works on
   WhatsApp today" without the adapter qualifier.
2. **No verified payment rail.** Screenshot/reference approval is
   trust-based (a screenshot is a claim, not settled funds). No
   "secure payments" language.
3. **No commission numbers as fact.** 8–12% and ₹999/$29 are
   **assumptions** labeled on screen; no unit-economics table is
   presented without the "assumption" label on every row.
4. **No Meta rate-card numbers.** WhatsApp per-conversation cost is
   explicitly "read the rate card at pilot time" — the video quotes no
   price.
5. **No full Marathi parity.** "Partial — English fallback" is stated;
   the menu frame shown is exactly the real output including fallback
   strings (verbatim-output rule from triage R2).
6. **No kill-mid-order resume demo.** v2 script's unproven
   "kill the service and it resumes" line is dropped until a test run
   proves it.
7. **No health/food-safety or regulatory clearance.** "Demo only — real
   deployment needs cottage-food / food-safety compliance" stays in the
   spoken disclosure (carried from v2 A10).
8. **No pricing decision.** The commission-vs-subscription choice is
   shown as gated on measured pilot data; the video endorses neither.

---

## 5. Build notes (for the narration/render pass)

- v3 is a **new script**, not a patch of video-1/2/3: single narrator,
  single audience (the board), single product story.
- Reuse corrected v2 phrasing (A22 patch, 2026-09-06): P&L "generated on
  demand" (no cron implied); payment "cook-verified, not bank-verified".
- Evidence frames are screen captures of the evidence text files and the
  v2-verified engine transcripts — never hand-written chat text, per the
  FRAMEWORK.md iron rule.
- Caption safe margins and emoji-glyph re-render lessons from v1→v2 (A6,
  A7, A21) apply to every new frame.
- Spot-check against the claim-to-evidence map (§3) before any render:
  every narrated sentence must trace to a row.
