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
  the engine and database path are the real production code; the WhatsApp
  transport in this demo is a local adapter, not the live Meta Cloud API —
  and the pilot build has known gaps we'll name at the end." (F-22: the
  old "same code path as production" line is retired — the engine and DB
  path are production, the transport is not.)
- **Must say (who-pays, F-19):** "customers order for free; cooks use it
  free in the pilot — the platform monetizes the cook side later."

### Section 2 — Walkthrough (target 6:00)

- **Purpose:** show the *complete* product loop a real user would live
  through: cook lists a dish → customer orders → cook is notified →
  customer pays UPI → cook approves the payment → cook accepts →
  customer is updated → payment state is tracked. Unhurried: one behavior
  at a time, each shown to completion. At least **3:00 of the 6:00** is
  one real customer order end-to-end.
- **What it PROVES:** (a) cook menu flow with photo + ingredients +
  description (b) customer ordering with single-digit replies (c) the
  Marathi fix is real, end-to-end on live Postgres (d) nickname display,
  locale-aware currency, and realistic inventory seed (e) the money loop
  with the cook's payment verdict — all from evidence.
- **On screen, in order:**
  1. **The Marathi fix is real (45–60 s, one beat).** A single collapsed
     beat replacing the old frames 1/5/6: the `mr` user row from live
     Postgres, the Devanagari round-trip rows (संजय साने / पनीर टिक्का),
     and the CHECK-constraint catalog line
     (`ARRAY['en','es','hi','mr']`) — held together, narrated once.
     (`docs/evidence/product-experience-2026-09-07.txt`.)
  2. **The cook lists a dish (~60 s).** From
     `docs/evidence/order-loop-marathi-2026-09-07.txt` Part 1 — the real
     transcript: पदार्थाचं नाव → "व्हेज पुलाव"; price in ₹ ("85");
     photo prompt; ingredients ("तांदूळ, वाटाणे, गाजर, तूप"); one-line
     description; the live confirmation "✅ 'व्हेज पुलाव' जतन झालं —
     ₹85.00". Shown BEFORE the customer-side menu frame, held long
     enough to read.
  3. **The customer orders (~60 s).** The real menu frame the Marathi
     customer received (📋 +15550001111 चा मेनू, व्हेज पुलाव — ₹85.00,
     ingredients, description), then the transcript beats: item 1 →
     quantity 2 → checkout "0" → review screen (व्हेज पुलाव × 2 —
     ₹170.00) → confirm "1". (`order-loop-marathi-2026-09-07.txt` Part 2.)
  4. **The payment beat (~60 s, unhurried).** The Marathi payment screens
     as the customer actually saw them: "2️⃣ फोनवरून पेमेंट (UPI)" —
     UPI-only, no Zelle/Venmo/Pix; the UPI instructions ("₹170.00 UPI ने
     पाठवा", screenshot-or-reference); then the cook's screen, **held
     until the narration finishes**: "💳 ऑर्डर #4 साठी पेमेंटचा पुरावा …
     1️⃣ पेमेंट मान्य करा 👍". **Must say:** "the cook approves only when
     the money is really in their account — screenshot is a claim, not
     settled funds." The cook replies "1": customer gets "✅ स्वयंपाक्याने
     पेमेंट मान्य केलं!", cook gets "✅ पेमेंट मान्य केलं".
     (`order-loop-marathi-2026-09-07.txt` Part 3.)
  5. **Accept and status updates (~60 s).** The cook taps "2️⃣ चालू
     ऑर्डरी पहा", sees the open order, replies "1" (accept); the customer
     is told the order was accepted; the status prompt follows —
     "1️⃣ शिजत आहे 🍳" → customer sees "📦 ऑर्डर #4: शिजत आहे 🍳",
     "2️⃣ डिलिव्हरीसाठी निघाली 🛵", "3️⃣ पूर्ण झाली ✅" → customer
     tracking updated each time. (`order-loop-marathi-2026-09-07.txt`
     Parts 4–5.)
  6. **Locale-aware details (~30 s).** The nickname line
     (`display_name(+15550001111) -> Meena Kaki`) and the Indian-grouping
     currency line (`₹1,25,000.50`).
  7. **Inventory seed (~30 s).** The 10-raw-materials table (INR costs),
     held, not skimmed.
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
- **Spoken narration (not just the card):** every OPEN item gets spoken
  airtime, in plain language —
  - "Webhook hardening — signature verification, dedupe, rate limiting —
    is not implemented. Board approval tonight is conditional on it
    landing before the first real order."
  - "The demo runs the production engine and database path through a
    local WhatsApp adapter, not the live Meta Cloud API."
  - "No restore has been rehearsed yet — daily backups are a vendor
    feature until we have restored one."
  - "Ops today is grep-the-logs: a silent webhook outage during dinner
    service would lose orders nobody sees. The pilot ops floor is alert
    on handler errors, a daily reconciliation report, and a named human
    on-call."
  - "The 18.3 requests-per-second figure is a single-worker baseline, not
    a capacity claim."
  - "The owner and business-hub screens are still English-first — the
    Marathi-first pass for the pilot is MVP scope." (D-01 disclosure.)
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
  - The two v1.2 candidates, presented with their real asymmetry —
    commission is a **boundary-crossing candidate** (payments move
    cook↔customer off-platform, so the platform has no settlement point
    to deduct from; it requires a cook-accepted collection mechanism with
    its own acceptance test), subscription **wins by default**. The plan
    does not endorse either; the choice is gated on measured pilot data
    via the §2 decision rule (repeat ≥ 40%, AOV ≥ ₹150, orders/cook ≥ 100,
    collection mechanism accepted).
  - The contribution-per-order table (§6): 10% on a ₹150 order (assumption)
    minus WhatsApp conversation cost ₹2–5 and reconciliation labor
    ₹3–8 → **≈ ₹1–9 (assumption)**; 8% → **≈ −₹2 to +₹7**; subscription
    ₹999/100 orders → **≈ −₹3 to +₹5**. The reconciliation-labor line
    stays visibly uncertain on screen (₹3–8, assumption — "minutes per
    reconciled order" is the pilot's #1 measured metric); the video must
    not soften it (F-08).
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
  ≥30% repeat in 14 days, webhook hardening controls implemented and
  verified, recorded zero-failed `mr` registrations); (2) approve 1–2
  pilot cooks in the Marathi/India context with daily human payment
  reconciliation; (3) approve the v1.2 billing-model decision gate
  (commission vs subscription from measured data via the business-plan §2
  decision rule, not before).
- **Spoken condition (F-07/F-08):** "approval tonight is conditional —
  webhook hardening lands before the first real order." Say it out loud;
  it must not be readable as approving unhardened money-adjacent traffic.
- **Spoken disclosure (F-10):** "no backup restore has been rehearsed yet
  — the runbook is written, the rehearsal is pilot-gating."

---

## 3. Claim-to-evidence map

Every factual claim the video will make, mapped to its backing. Nothing
in §2 is said without a row here.

| Claim (as narrated) | Evidence file / commit |
|---|---|
| One real customer order end-to-end in Marathi: cook lists a dish (name → price → photo → ingredients → description → live confirmation); customer orders (item → qty → checkout → confirm); cook is notified; customer sends UPI screenshot; cook approves payment; cook accepts via open orders; status updates cooking → out for delivery → completed | `docs/evidence/order-loop-marathi-2026-09-07.txt` Parts 1–5 — verbatim real engine output. State transitions: `payment_status` unpaid → pending_approval → verified; `order_status` received → accepted → cooking → out_for_delivery → completed |
| Cook's payment verdict is cook-verified, not bank-verified; narration: "the cook approves only when the money is really in their account — screenshot is a claim, not settled funds" | order-loop Part 3 (`cook_payment_proof` → "1️⃣ पेमेंट मान्य करा 👍"); `docs/business-plan.md` §1–§2; test `test_p2p_screenshot_approval_flow` |
| Marathi payment screens are UPI-only — no Zelle/Venmo/Pix for the India-pilot user | `locales/mr.json` `p2p_instructions` ("UPI ने पाठवा") / `payment_title` ("(UPI)"); `en.json` keeps the multi-rail list for the US context |
| Owner/business-hub screens are still English-first — Marathi-first is MVP scope | `locales/mr.json` covers 70 of 162 `en` keys (all `o_*`/`m_*` fall back to English); `docs/milestones.md` "Where we are"; disclosed in §3 Transitions |
| 69 tests pass (2 warnings, deprecation-only); the 4 skips are the live-Postgres smoke tests, env-gated on `BITEFLOW_TEST_DATABASE_URL` | `docs/evidence/test-run-2026-09-07.txt` (last line: `69 passed, 4 skipped, 2 warnings`); note supersedes the v2 script's "47 tests" |
| Menu, nickname, currency, inventory frames are real engine output on real Postgres | `docs/evidence/product-experience-2026-09-07.txt` — header states "All engine output above came from the real state machine + real PostgreSQL. No mocks, no hand-written values." |
| Marathi `mr` registration works on live Postgres (gap #1 closed) | `docs/evidence/postgres-mr-verification.txt` — Step 2 CHECK violation before migration 006; Step 4 insert succeeds after |
| `mr` locale accepted in `users_preferred_language_check` | `postgres-mr-verification.txt` + product-experience "CATALOG" section: `ARRAY['en','es','hi','mr']`; test `test_postgres_marathi_locale_accepted` in test-run log |
| Locale-aware currency: ₹ for mr (Indian grouping), $ for en | product-experience § FIX #3: `money(125000.5,'mr') = ₹1,25,000.50`; tests `test_money_locale_formatting`, `test_mr_customer_sees_inr_not_usd`, `test_en_customer_still_sees_usd` |
| Devanagari round-trips through Postgres | product-experience "mr ROUND-TRIP" rows (संजय साने / पनीर टिक्का); `test_postgres_marathi_locale_accepted` |
| Inventory seeded with realistic non-zero stock, INR costs for mr cook | product-experience § FIX #4 (10 materials table); tests `test_inventory_seeded_with_realistic_stock`, `test_inventory_seed_uses_inr_costs_for_mr_cook` |
| Dish photos + ingredients + description in menu | tests `test_cook_can_attach_photo_ingredients_description`, `test_customer_menu_shows_photo_ingredients_description`; milestone "Where we are" (commit `113881b`) |
| Nickname display with phone fallback | product-experience § FIX #2; tests `test_nicknames_shown_instead_of_phone`, `test_phone_fallback_when_no_nickname` |
| Payment tracking is cook-verified, not bank-verified; no commission in this build | `docs/business-plan.md` §1–§2; review-loop CHANGELOG A3/A13; tests `test_p2p_screenshot_approval_flow` |
| Billing model undecided: commission (boundary-crossing candidate — needs a cook-accepted collection mechanism) OR ₹999/$29 subscription (wins by default), chosen from pilot data via the §2 decision rule | `docs/milestones.md` v1.2 + `docs/business-plan.md` §2–§3 (all labeled **assumption**) |
| Contribution per order (assumption, both tails): commission 10% ≈ ₹1–9, 8% ≈ −₹2 to +₹7; subscription ≈ −₹3 to +₹5. Binding unknown = Meta per-conversation price | `docs/business-plan.md` §6 tables; §6 "Reading the table honestly" |
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

- **Narration register guidance (F-26):** board-register for the intro,
  business model, and Ask ("the engine and database path are the real
  production code"); **warm, non-technical Marathi for the UI-quoting
  beats** — when the narration quotes a screen ("पेमेंट मान्य करा"), it
  sounds like a person explaining to their neighbor, not a spec sheet.
  No "डेटाबेस", "स्टेट मशीन", or "बॅकएंड" in voiceover where a senior
  would hear it — say "सिस्टीम" or plain words instead.
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
