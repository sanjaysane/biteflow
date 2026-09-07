# Senior Engineer Re-Review — Walkthrough Videos v2
**Reviewer role:** code & architecture fidelity (lighter v2 pass — confirm/reject each v2 fix, no new broad review)
**Scope:** 4 v2 videos, v2 narration scripts in `work/*/`, `~/workspace/biteflow/src`, `~/workspace/roomlens/src`
**Checklist source:** `reviews/CHANGELOG-v1-v2.md` + v1 report `reviews/v1/senior-engineer.md`
**Method:** every re-recorded claim re-traced to code; final mp4 durations cross-checked (all four match: 350.2s / 232.4s / 212.3s / 200.4s). Could not play video (no media playback); audio-segment inclusion verified via ffprobe duration arithmetic.

---

## Verdict: SIGN-OFF

The v1 blocker (RoomLens commission contradiction) is fixed: both videos now tell the same true story — zero commission accounting, no in-app payment — and it matches the code (`grep -ri commission` across both repos: **0 hits**). Of 36 checklist items claimed fixed in the changelog, **34 confirm fixed and 2 do not** (94.4% > the 90% bar). Both misses are v1-**minor**-class items whose changelog entries overclaim a reword that didn't happen (cutout language; digest "sends" language). No blocker or major remains. Recommended action for parent: correct those two changelog rows (A22) so they read "not changed — deferred" instead of "reworded".

---

## Per-item results

### A1 — RoomLens commission contradiction (v1 BLOCKER B1): CONFIRM FIXED ✓
- **prospect-mr n7 re-recorded** (`work/roomlens-prospect-mr/narr/n7.txt`; `audio/n7.mp3` regenerated Sep 6 05:04): "इथे ॲपमध्ये पैसे भरायची सोय नाही; या आवृत्तीत प्लॅटफॉर्म कमिशनचा हिशोब नाही — हा व्यवसाय निर्णय अजून बाकी आहे." Matches code (zero `commission` hits repo-wide; `roomlens/src/handlers/prospect.py:handle_order` writes `create_order(...)` + designer notification, no fee split, no payment rail).
- **designer-en s7 re-recorded** (new `audio/s7.mp3` 27.67s vs old 22.01s in `speak-backup/s7-v1.mp3`; final mp4 segment 6 runs 28.67s = 27.67 + 1.0 pad — the new audio is provably in the shipped video): "no money moves inside this app. The tap records the order and notifies the designer — there is no in-app payment; the designer is paid directly, off platform."
- **s8 kept** ("no platform commission accounting in this version of the code") — n7, s7, s8 now all agree with each other and with the code.
- Residual (minor, disclosed, not a reject): s8's "books the full order total as the designer's fee" is a gloss — the `orders` row holds only `total_cents`, no fee column — but s7 explicitly places settlement off-platform, so no false claim stands.

### A2 — Designer-EN money movement (v1 M1): CONFIRM FIXED ✓
- s7 money-movement line ("the prospect's payment becomes the designer's fee") removed; replaced by the no-money-moves correction above. `handle_order` collects nothing — true.
- prospect-mr money moment (A2): n7 "इंजिन ऑर्डरची नोंद लिहितं, आणि डिझायनरला नवीन ऑर्डरची सूचना आपोआप जाते... पैसे डिझायनरशी थेट ठरतात" ✓ matches `handle_order`.

### A3 — Cook-verified screenshot (v1 m6): CONFIRM FIXED ✓
- customer-en s07: "sends a screenshot for the cook to approve... Still no middleman." Code: `payments.py:submit_p2p_proof` stores `proof_ref`; `decide_payment` flips on cook's digit only — narration now says what the engine does and doesn't do.

### A4 — Synthetic-media disclosure: CONFIRM FIXED ✓
- prospect-mr n3 on-mic: "या डेमोमध्ये नमुना फोटो वापरले आहेत" + bilingual closing card ("Demo uses sample room & product photos"). designer-en s6 on-mic + end card. ✓

### A6 — Caption safe margins: CONFIRM (code evidence) ✓
- `build_v2.py` reserves a 180px caption band (`BAND_H=180`) with auto-fit ≤1000px; designer-en seg01 (Step 2) re-rendered per `build_v2.log`; customer-en closing card re-rendered. Could not visually inspect (no playback), accepted on build code.

### A7 — Tofu emoji (customer s12–13): ACCEPT on build evidence ✓
- changelog claims re-render through working emoji path; no contrary evidence found; visual-only item, no code claim involved.

### A8 — Step 8 narration (no phantom second chat): CONFIRM FIXED ✓
- customer-en s08 narrates only customer-side status pushes + opt-in, matching `transcripts/s08-accepted.json`. ✓

### A9 — "Every cook nearby" (v1 M4): CONFIRM FIXED ✓
- s03 now "the bot lists every cook with an active menu". Code: `db.py:get_cooks_with_menus` — no geo anywhere ✓.

### A10/A11 — Disclosures: CONFIRM FIXED ✓
- customer-en closing card (`render_frames.py:66-71`): "Simulated WhatsApp client / local run, not the live Meta API", "Demo only — a real deployment needs cottage-food / food-safety compliance", "Pilot build: webhook signature validation, idempotency, and rate limiting not yet implemented." designer-en end card carries the webhook line too (narration.txt). ✓

### A12 — Approved Meta templates: CONFIRM FIXED ✓
- customer-en s08: "business-initiated broadcasts need approved Meta templates". designer-en end card: "Production business-initiated messages need approved Meta templates." ✓

### A13 — Money moment, both BiteFlow videos: CONFIRM FIXED ✓
- customer s07: "BiteFlow takes no commission in this build... business-owner addendum — daily P and L, food-cost math, marketing broadcasts — is the planned paid layer; pricing is not set." cook-mr step6 (Marathi): "या आवृत्तीत बाइटफ्लो कोणतंही कमिशन घेत नाही... पुढे पैसे मिळवण्याचा मार्ग ठरलेला आहे... पण त्याची किंमत अजून ठरलेली नाही." ✓ Zero commission hits in code.

### A14 — P&L reframed as demo data: CONFIRM FIXED ✓
- cook-mr step5 v2: "हे आकडे या डेमो सत्रातल्या पूर्ण झालेल्या एकाच ऑर्डरवरून आलेले आहेत; प्रत्यक्ष विक्री नाही" ✓ (vs v1 "खऱ्या पूर्ण झालेल्या ऑर्डरवरून" — correctly scoped down). `daily_pnl` sums completed orders — numbers true of the session.

### A15 — Plain-Marathi jargon: CONFIRM FIXED (spot) ✓
- cook-mr step7 reworded to plain Marathi; step5/step6 Marathi is plain. Prospect-mr n-scripts likewise.

### A16 — Bilingual closing cards: CONFIRM FIXED ✓
- prospect-mr closing card: EN + Marathi line pairs (`render_frames.py:196-208`) ✓. cook-mr closing card bilingual (per changelog; script change accepted).

### A17 — USD disclosure: CONFIRM FIXED ✓
- prospect-mr closing card: "Prices shown in USD (real engine behavior)" + Marathi line ✓.

### A18 — Cook-number privacy: CONFIRM FIXED ✓
- customer-en s04: "these are test numbers; a real pilot needs a design that keeps cooks' personal numbers private" ✓.

### A19 — Honest timing language: CONFIRM FIXED ✓
- prospect-mr n3: "फोटो आल्या आल्या दोन कामं होतात... डिझायनरला आपोआप सूचना जाते" — describes the synchronous local-run push, no false immediacy claim.

### A20 — New branches driven through the real engine: CONFIRM ALL THREE ✓
1. **Empty-cart checkout guard** (customer-en s06b): transcript `s06b-emptycart.json` is verbatim engine output — `0` at menu with empty cart → `item_invalid` ("Hmm, that's not on the menu…") + menu re-render, no order written. Code: `handlers/customer.py:114-118` (`choice == 0`, `if not cart: reply("item_invalid"); _show_menu(...)`). Narration ("checkout rejected, menu re-rendered, no order written") is behaviorally accurate. Locale string matches `biteflow/locales/en.json` verbatim.
2. **STOP opt-out** (customer-en s08b): transcript `s08b-stop.json` verbatim `c_stop_done` locale string. Code: `state_machine.py:170-174` — STOP checked pre-dispatch for any customer state; `db.optout_everywhere` touches only `marketing_optins`. `handle_status` pushes to the customer without an optin check — so "tracking is transactional, so status pushes keep working" is true.
3. **Talk-to-designer** (prospect-mr, option 4): transcript `f6b-talk-designer.json` verbatim `d_prospect_wants_talk` locale string ("💬 +15550005555 wants to talk to you directly."). Code: `prospect.py:156,181-185` — `parse_choice(text,1,4)`, choice 4 → `_notify_designer(ctx, "d_prospect_wants_talk")`, state `P_WAITING`, reply `p_change_noted`. Real engine branch.

### A21 — Cook-mr emoji re-render: ACCEPT on build evidence ✓
- Visual-only; no code claim involved.

### A22 — SrEng minors (cutout / digest-"sends" / gross-vs-net): 1 of 3 NOT fixed ✗✗/✓
1. **"cutout image" — REJECT (not fixed).** designer-en Step 2 still says "The backend saves the cutout image to local storage"; `audio/s2.mp3` is v1-era (04:46, not re-recorded). The seg01 re-render in `build_v2.log` was captions only. Code (`designer.py:handle_cat_photo`) saves raw uploaded bytes verbatim as `cutout_ref`; no background removal (`composite.py` docstring: out of scope). v1 rating was minor (narration hedges with "plain background"), but the changelog's "Reworded 'cutout image'" claim is false — the line is unchanged.
2. **Digest "sends" (no cron in repo) — REJECT (not fixed).** cook-mr step5 v2 still opens with "दिवस संपताना बाइटफ्लो रोजचा नफा-तोटा पाठवतं" (BiteFlow sends the daily P&L) — verbatim from v1. `owner/digest.py:send_daily_digest` exists but no scheduler ships in the repo (cron is the deployer's job per the docstring). Changelog's "Reworded digest 'sends'" claim is false.
3. **Gross-vs-net reconciliation — ACCEPT (no change needed).** No reconciliation-vs-P&L claim in v2 narration; narrated numbers ($17.00) are correct for the discount-free demo (v1 itself noted this).

### A23 — Direct-payment wording (Ext M6): CONFIRM FIXED ✓
- prospect-mr n7: "पैसे डिझायनरशी थेट ठरतात" (payment arranged directly with the designer) ✓.

---

## Summary table

| Item | v1 severity | v2 verdict |
|---|---|---|
| A1 RoomLens commission contradiction | Blocker | **FIXED** — n7/s7/s8 agree, match code (0 hits) |
| A2 designer money movement | Major | **FIXED** — s7 re-recorded, in final video |
| A9 "every cook nearby" | Major | **FIXED** — "every cook with an active menu" |
| A3/A4/A8/A10/A11/A12/A13/A14/A15/A16/A17/A18/A19/A23 | Major/minor | **FIXED** (traced above) |
| A6/A7/A21 captions/emoji | Minor (visual) | **ACCEPT** on build code |
| A20 empty-cart / STOP / talk-to-designer | Minor | **FIXED** — real engine output, locale-verbatim |
| A22 cutout reword | Minor | **NOT FIXED** — changelog overclaims |
| A22 digest "sends" reword | Minor | **NOT FIXED** — changelog overclaims |
| A22 gross-vs-net | Minor | **N/A** — no change needed |

**34/36 = 94.4% of claimed fixes confirmed. SIGN-OFF.**

### Caveats / follow-ups for the parent agent
1. Fix the two A22 changelog rows to say "not changed — deferred" (the current "Reworded" wording is itself inaccurate and would fail a future audit).
2. Optionally: the two residual items are both cheap one-line narration fixes if Sanjay wants 100% before public release — s2: "saves the product photo (used as the cutout as-is)"; cook-mr step5: "दिवस संपताना बाइटफ्लोचा नफा-तोटा हिशेब इथे पाहता येतो" (viewable on demand, not "sends").
3. Skipped failure modes from v1 (webhook HMAC, idempotency, swallow-exceptions, COD-collected assumption) are now disclosed on the closing cards as "not yet implemented" — appropriately closed as *disclosure* items rather than code claims.
