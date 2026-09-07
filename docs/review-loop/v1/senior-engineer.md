# Senior Engineer Review — Walkthrough Videos v1
**Reviewer role:** code & architecture fidelity — does the narration tell the truth about what the code does?
**Scope:** 4 videos, their narration scripts, `~/workspace/biteflow/src`, `~/workspace/roomlens/src`.
**Method:** every narrated backend claim traced to a file/function. `grep -ri commission` across both repos returns **zero hits** — that fact drives the top finding.

**Timestamps:** derived from per-segment narration-audio durations (ffprobe), assuming segments play back-to-back in script order. Approximate ±5s. Video totals cross-checked against manifest.json durations.

---

## Verdict: NEEDS WORK

One blocker: the two RoomLens videos make directly contradictory factual claims about platform commission on the same codebase. One of them is false against the code. Additionally, the designer-EN video narrates real-money movement ("the prospect's payment becomes the designer's fee") where the code collects no payment at all. Fix or re-record those two segments before shipping.

---

## Blockers

### B1. RoomLens prospect-MR claims platform commission exists; the code has no commission anywhere, and the designer-EN video says the opposite
- **Video:** `roomlens-prospect-mr.mp4` — Step 7, **~02:23–02:44** (narr/n7.txt → audio/n7.mp3)
- **Claim (Marathi):** "बुकिंग झालं की डिझायनरची फी ठरते, आणि त्यावर प्लॅटफॉर्मचं कमिशन — हेच रूमलेन्सचं बिझनेस मॉडेल." ("At booking the designer's fee is set, and on it the platform's commission — that is RoomLens's business model.")
- **Code evidence:**
  - `roomlens/src/db.py:1044-1053` (`PostgresDatabase.create_order`) — `INSERT INTO orders (prospect_phone, designer_id, quote_id, total_cents, currency)`. No fee column, no commission column.
  - `roomlens/src/db.py:521-539` (`FakeDatabase.create_order`) — same: only `total_cents`/`currency` stored.
  - `roomlens/src/pricing.py` (`build_quote`) — computes line totals/subtotal/delivery/total only. No fee split.
  - `roomlens/src/handlers/prospect.py:handle_order` — calls `create_order(...)`, marks viz `ordered`, notifies designer. No fee computation, no commission accounting, no payment collection.
  - Repo-wide `grep -ri "commission"` on both `biteflow/src` and `roomlens/src`: **zero matches**.
- **Contradiction:** `roomlens-designer-en.mp4` Step 8 (**~02:33**, narration.txt) says the exact opposite: "There is no platform commission accounting in this version of the code, so I will not invent a cut." Both statements cannot be true of the same repo. The Marathi one is the false one.
- **Fix:** re-record Step 7 of the prospect-MR video to match the designer-EN disclosure (no commission accounting in this build).

---

## Major findings

### M1. Designer-EN Step 7 narrates real-money movement that the code cannot perform
- **Video:** `roomlens-designer-en.mp4` — Step 7, **~02:11–02:33** (audio/s7.mp3)
- **Claim:** "This is the business-model moment when money moves: the prospect's payment becomes the designer's fee."
- **Code evidence:** `roomlens/src/handlers/prospect.py:handle_order` — the order path writes `db.create_order(...)` and sends notifications. There is **no `payment_type`, no `payment_status`, no payment rail, no payout function** anywhere in the roomlens repo. No money moves; nothing is collected from the prospect and nothing is disbursed to the designer. Step 8 then says "this build books the full order total as the designer's fee" — but nothing is booked *as a fee* either; the `orders` row holds only `total_cents`. The honest statement is: "the order records a total the prospect owes the designer; settlement happens entirely outside this build."
- **Why major:** implies real-money settlement + fee accounting with no code behind either.

### M2. No webhook signature validation — forged inbound messages accepted (both repos)
- **Code evidence:** `biteflow/src/main.py:106-140` (`receive_webhook`) and `roomlens/src/main.py` (same shape) — `POST /webhook` parses JSON and dispatches to `process_incoming`. Only the `GET /webhook` handshake checks `hub.verify_token`. Neither file reads the `X-Hub-Signature-256` header or validates an HMAC. Anyone who can reach the endpoint can inject orders, payment approvals, and status updates as any phone number.
- **Narration:** never claims webhook security, so this is a skipped failure mode, not a false claim — but it's the highest-risk gap in what's shown.

### M3. No idempotency on webhook POSTs — Meta retries double-write
- **Code evidence:** neither `main.py` reads the WhatsApp message id (`wamid`) from the payload (`_extract_messages` yields only phone/text/type/media_id). `process_incoming` has no dedup. A retried delivery re-runs `handle_payment` → `create_order_from_cart` (`biteflow/src/handlers/customer.py`, `biteflow/src/payments.py:create_order_from_cart`) → a second order row for the same cart; re-runs `handle_status` → duplicate customer pushes.
- **Narration:** the customer-EN video presents order writes and status pushes as exactly-once with no mention of retry semantics. Skipped failure mode.

### M4. "Every cook nearby" — there is no proximity logic in BiteFlow
- **Video:** `biteflow-customer-en.mp4` — s03, **~00:48–01:08**
- **Claim:** "the bot lists every cook nearby with a live menu."
- **Code evidence:** `biteflow/src/db.py` (`get_cooks_with_menus`, FakeDatabase ~289, Postgres ~872) — `SELECT DISTINCT u.phone_number ... WHERE m.active_status = TRUE ORDER BY u.phone_number`. No latitude/longitude, no radius, no location input anywhere in the customer flow. The engine lists **all** cooks with active menus; "nearby" invents geo-filtering.

---

## Minor findings

### m1. manifest.json misdescribes the cook-MR video ("live/offline toggle")
- `manifest.json` describes `biteflow-cook-mr.mp4` as including a "live/offline toggle." The narration itself (step2, **~00:25**) explicitly corrects this: "इंजिनमध्ये किचन चालू-बंदचं वेगळं बटण नाही; मेनू जाहीर झाला की किचन लाइव्ह" (there is no separate kitchen on/off button; publish = live). Code confirms: `biteflow/src/handlers/cook.py:handle_home` offers only 1–4 (menu / orders / business / marketing); the only deactivation is `deactivate_menus` when a fresh broadcast starts. Manifest is wrong, narration is right — fix the manifest.

### m2. manifest.json misdescribes customer-EN payment options and "reorder"
- Manifest says "checkout with UPI/card/COD" — the engine offers exactly two options (`locales/en.json: payment_title`): 1 = Cash on delivery, 2 = Phone transfer (Zelle / Venmo / UPI / Pix). **No card option exists** (`handle_payment` maps choice → `COD` | `P2P_TRANSFER` only). Manifest also says "reorder" — no reorder flow exists in the customer loop.

### m3. "Cutout image" overstates what the catalog photo flow does
- **Video:** `roomlens-designer-en.mp4` — Step 2, **~00:22–00:46**
- **Claim:** "send a product photo with a plain background. The backend saves the cutout image to local storage."
- **Code evidence:** `roomlens/src/handlers/designer.py:handle_cat_photo` saves the **raw uploaded bytes verbatim** as `cutout_ref` (also mislabeled with a `.png` extension regardless of actual bytes). No background removal happens — `composite.py` documents "Background removal is intentionally out of scope for v0.1.0." `place_cutout` converts RGB→RGBA, so an opaque JPEG pastes as a full rectangle, not a cutout. The narration hedges with "plain background" (designer's job), but "cutout" implies processed alpha. Suggest "saves the product image (used as the cutout as-is)".

### m4. COD vs P2P reconciliation uses gross totals, ignoring discounts
- **Video:** `biteflow-cook-mr.mp4` — Step 6, **~02:33–03:07** ("सीओडीमधून सतरा डॉलर जमा")
- **Code evidence:** `biteflow/src/owner/handlers.py:549` (`_show_reconciliation`) sums `total_sum` gross; `handle_payment` (`handlers/customer.py`) tells the customer the **net** total after discounts and stores `discount_total`. `daily_pnl` (`owner/economics.py:306`) correctly uses net. In this demo (no discounts) both are $17.00 so the narrated numbers are right, but the recon screen and the P&L disagree by construction once any referral/offer/credit applies.

### m5. Daily P&L "sends" implies automation that isn't wired up
- **Video:** `biteflow-cook-mr.mp4` — Step 5, **~02:12–02:33** ("दिवस संपताना बाइटफ्लो रोजचा नफा-तोटा पाठवतं" — BiteFlow sends the daily P&L at day's end)
- **Code evidence:** `biteflow/src/owner/digest.py:19` (`send_daily_digest`) — the docstring says "scheduler/cron (one cron entry per cook, idempotency enforced by the caller…)". The math is real (`daily_pnl` reads completed orders — verified), but **no scheduler ships in the repo**; the cron is the deployer's job. "Sends daily" is true only if someone wires the cron.

### m6. P2P "screenshot verification" is trust-based; the engine verifies nothing
- **Video:** `biteflow-customer-en.mp4` — s07, **~02:06–02:42** ("sends a screenshot for the cook to approve")
- **Code evidence:** `biteflow/src/payments.py:submit_p2p_proof` stores `proof_ref` (`photo:<media-id>` or `ref:<text>`); `decide_payment` flips status on the cook's digit alone. The engine never downloads the image, never matches an amount, never checks the reference. The narration is honest about the human-in-the-loop ("for the cook to approve"), but a viewer could read "verification" as engine-verified. Disclosed adequately; noting for completeness.

### m7. "Simulated client" disclosure is accurate but weakly placed
- **Verified present:** silent 5s end cards on all four videos ("Simulated WhatsApp client · local run · not the live Meta API" — confirmed in `biteflow-customer-en/render_frames.py:50-66`, `biteflow-cook-mr/frames/closing-card.png` viewed directly, `roomlens-prospect-mr/render_frames.py:186-189`, `roomlens-designer-en/narration.txt` end card) and in `manifest.json`'s global disclaimer. Mid-video, `biteflow-customer-en` s08 (**~02:42**) says "a second simulated chat," which helps.
- **Accuracy:** the claim is true of the demos — `FakeWhatsAppClient` (`whatsapp.py` in both repos) records instead of calling Meta. The real `MetaWhatsAppClient` (posts to `graph.facebook.com/v21.0`) exists in the code but is only constructed when `WHATSAPP_TOKEN`/`WHATSAPP_PHONE_NUMBER_ID` are set (`main.py:build_runtime`), which the demos don't do. Given the code genuinely integrates with the live Meta API when configured, the disclosure is accurate for what's shown.
- **Sufficiency:** a silent end card is easy to miss, and mid-video lines like "genuine engine output, not a mock" (designer-EN s4, **~01:04**) and "खरी नोटिफिकेशन धडकते" (cook-MR step3, **~01:08**) could leave a casual viewer thinking these ran on real WhatsApp. Recommend an opening card or persistent on-screen bug rather than end-card-only.

---

## Claims verified as TRUE (spot-checked, representative)

**BiteFlow customer-EN** (all timed from segment audio):
- s01 (~00:00) webhook → declarative state machine → two replies: `main.py:receive_webhook` → `state_machine.py:process_incoming` → `ROUTES`; `handlers/customer.py:handle_new` replies `welcome` + `ask_role`. ✓
- s02 (~00:23) language command works from any state, is saved: `state_machine.py:_is_language_command` checked pre-dispatch; `db.set_user_language`. ✓
- s03 (~00:48) user row keyed by phone: `handle_ask_role` → `db.upsert_user`. ✓ (except "nearby", M4)
- s04 (~01:08) menu fetched live per view: `_show_menu` → `db.get_active_menus` on every render. ✓
- s05 (~01:26) cart in chat session, qty 1–9: `handle_quantity` → `parse_choice(text, 1, 9)`; cart in session data. ✓
- s06 (~01:46) review → payment state: `handle_review` → `C_PAYMENT`. ✓
- s07 (~02:06) order row written, cook 1/2 alert, no commission, no money touched: `create_order_from_cart` → `db.create_order`; `_notify_cook_new_order` + `set_state_for(..., K_INBOUND)`; zero `commission` hits repo-wide; COD = cash at door, P2P = external Zelle/UPI + cook-approved screenshot (`handle_proof`, `payments.py`). ✓
- s08 (~02:42) accept → `accepted`, opt-in stored: `cook.py:handle_inbound` → `update_order(order_status="accepted")`, sends `order_accepted_customer` + `c_optin_ask`; `owner/handlers.py:handle_optin` → `db.set_optin`. Opted-in customers receive campaigns (`handle_camp_confirm` → `get_opted_in_customers`), so "broadcast future menus" is functionally true. ✓
- s09 (~03:10) push in customer's language: `handle_status` → `update_order` + `send_to(customer, ..., cust_lang)`. ✓
- s11–s13 (~03:53–05:15) fallbacks re-render; cancel at review writes nothing: `handle_review` choice 2 → reply only, no DB write. ✓

**BiteFlow cook-MR:**
- step1 (~00:00) register as cook, phone stored: `upsert_user` with role. ✓
- step2 (~00:25) "abc" price rejected, 8.50 accepted: `context.py:parse_price` (regex, positive amounts). No kitchen on/off toggle; publish = live (`start_broadcast` → `cook_menu_done` "Your menu is live!"). ✓
- step3 (~01:08) order #5 notification auto-pushed by engine: `_notify_cook_new_order` — not hand-written. ✓
- step4 (~01:43) statuses pushed in customer's language: `handle_status` uses `cust_lang`. ✓
- step5 (~02:12) P&L numbers from real completed orders: `daily_pnl` sums completed orders; food cost $0 because no recipes were recorded in the demo — the narration says exactly this. ✓
- step6 (~02:33) finance section untranslated → English: accurate — `locales/mr.json` has 66/158 keys and all `o_recon_*` keys are missing (fallback to English via `I18n.t`). ✓
- step7 (~03:07) reject → Marathi message; unknown input → home menu: `handle_inbound` choice 2 → `update_order(cancelled)` + `send_to(customer, "order_rejected_customer", cust_lang)`; `handle_home` invalid → re-reply `cook_home`. ✓

**RoomLens prospect-MR:**
- Step 1 (~00:00–00:22) language command from any state, saved to user record: `state_machine.py` pre-dispatch check; `set_user_language`. ✓
- Step 3 (~00:46) photo QC (brightness/blur/size) with retake instead of bad overlay: `composite.py:assess_quality` (`MIN_BRIGHTNESS=45.0`, `MIN_BLUR_SCORE=90.0`, `MIN_SIDE_PX=400`); saved to media store (`ctx.store.save`); designer notified in their language (`d_new_photo` via `d_lang`). ✓
- Step 4b (~01:22) "not true AR, preset compositing": accurate and matches `composite.py`'s own docstring ("This is NOT true AR… 2D presets"). ✓
- Step 5 (~01:55) "built by the compositing engine — Pillow and NumPy": `render_visualization` uses PIL + numpy; `handle_studio_preset` → `create_visualization` + stored `rendered_ref`. ✓
- Step 6 (~02:09) "2" → feedback to designer: `prospect.py:handle_review` choice 2 → `d_change_placement` push. ✓
- Step 7b (~02:44) cancel before persist: `handle_order` choice 2 → back to `P_PHOTO`, no `create_order` call. ✓
- Step 8 (~02:55) tracking lists orders: `handle_tracking` → `list_orders_for_prospect`. ✓ (Note per LEAKS.md: status word renders in English, e.g. `#9: received` — real engine fallback output, not a narration error.)

**RoomLens designer-EN:**
- Steps 1–6 (~00:00–02:11): onboarding, catalog add/remove (`set_product_active`), gibberish re-prompt, photo QC + designer ping, studio compositing with price strip, "exact bytes the prospect receives" (`handle_studio_adjust` loads `rendered_ref` from the store and `send_image`s it). ✓
- Step 8 (~02:33) commission disclaimer: **true** — no commission code exists. (This is what makes B1 a blocker: it's the correct one.)

---

## Skipped failure modes the narrations should have mentioned
1. **No webhook signature validation** (M2) — forged inbound messages accepted by both `POST /webhook`s.
2. **No idempotency / retry dedup** (M3) — Meta redelivery double-writes orders.
3. **P2P proofs are unverified trust tokens** (m6) — engine never inspects the screenshot or matches amounts.
4. **Webhook handler swallows all exceptions** (`main.py:receive_webhook` — `except Exception: print(...)`, always returns 200) — a handler bug silently drops the message with only a stdout line; no alerting, no dead-letter.
5. **COD "collected" is an assumption** — BiteFlow marks COD revenue on order *completion* (`daily_pnl`, `_show_reconciliation`); the engine never confirms cash actually changed hands. The narration's "cook is collecting those seventeen dollars at the door" (s10, ~03:31) is real-world color, but the finance screens present it as collected fact.

---

## Notes on method / limits
- I could not play the rendered videos (no media playback in this environment); timestamps are computed from narration-audio segment durations and script order, cross-checked against manifest durations. Wording of on-screen chat bubbles was verified against `work/*/transcripts/` and `audit_log.json` transcripts where available, and LEAKS.md's audit.
- Marathi scripts were read in the original; technical claims translated mentally. No Marathi wording issues found beyond what's noted (the Step 7 commission claim is a *factual* error, not a language error).
- I did not re-run the engines; code was read, not executed. Findings cite file + function/line-area, not runtime behavior.
