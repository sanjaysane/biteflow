# QA Analyst — v2 Re-review (strict checklist against CHANGELOG-v1-v2.md)

**Reviewer:** QA Analyst subagent (5-persona swarm)
**Date:** 2026-09-06 (PDT)
**Method:** CHANGELOG-v1-v2.md read in full → every item re-verified in the final v2 MP4s (ffprobe durations: customer-en 350.200s, cook-mr 232.411s, prospect-mr 212.300s, designer-en 200.367s), the build scripts/narration sources, and frame extractions from the final files (timestamps below are positions inside the final v2 MP4s).
**Strictness:** per brief, a fix that is "90% there" is REJECTED. Marking is per-changelog-item, not per-sub-claim; a bundled item with any unaddressed sub-claim is REJECTED.

---

## Overall verdict: **REJECT**

31 of 32 changelog items are CONFIRMED with frame/script/audio evidence. One bundled item — **A22 under biteflow-customer-en ("cutout image" / digest "sends" / gross-vs-net rewords)** — is REJECTED: none of the three rewords were applied anywhere, and the changelog misattributes them to customer-en, a video that never contained any of the three phrases. That item was triaged as minor (SrEng minors). If the owner accepts A22 as-is, everything else in v2 is shippable; otherwise this needs a v2.1 pass.

---

## biteflow-customer-en-v2.mp4 (350.200s)

| Changelog item | Verdict | Evidence (final MP4 unless noted) |
|---|---|---|
| A8 Step 8 narration rewritten — no visible second phone | **CONFIRMED** | Script `narr/s07.txt`: "your customer phone, the only view in this video". Frame @203s ("Step 9 · Order accepted"): single phone only, no split-screen second phone. |
| A6 Captions re-rendered with safe margins | **CONFIRMED** | Frames @55s (Step 3), @141s (Step 7), @203s (Step 9), @227s (Step 10), @310s (Step 14), @340s (Step 15): captions sit in the top dark area, never overlapping the chat header or bubbles. |
| A7 Steps 12–13 tofu emoji fixed | **CONFIRMED** | Frames @310s, @318s (Step 14 · Fallback) and @340s (Step 15 · Cancel): 📋 🍛 0️⃣ 🔢 🧾 ✅ ❌ 👍 👎 💰 🎉 👩‍🍳 all render — no tofu boxes. (Steps renumbered 12–13 → 14–15 after the two new branch steps; same frames.) |
| A3 Payment step "cook-verified, not bank-verified" | **CONFIRMED** | Script `narr/s07.txt`: "the customer pays the cook over Zelle or UPI, then sends a screenshot for the cook to approve. Still no middleman." The exact phrase "cook-verified, not bank-verified" is not used, but the substance is: verification is by the cook (screenshot approval), not by any bank. |
| A9 "every cook nearby" → "every cook with an active menu" | **CONFIRMED** | Script `narr/s03.txt`: "matches her with every cook with an active menu." |
| A10 Food-safety disclosure on closing card | **CONFIRMED** | Frame @347s: "Demo only — a real deployment needs cottage-food / food-safety compliance for home kitchens." Legible. |
| A11 Webhook hardening disclosure on closing card | **CONFIRMED** | Frame @347s: "Pilot build: webhook signature validation, idempotency, and rate limiting not yet implemented." Legible. |
| A12 Broadcast opt-in: approved Meta templates | **CONFIRMED** | Script `narr/s08.txt`: "those business-initiated broadcasts need approved Meta templates." |
| A13 Money moment: no-commission + business-owner addendum | **CONFIRMED** | Script `narr/s07.txt`: "BiteFlow takes no commission in this build: payment moves directly from customer to cook, peer to peer… The business-owner addendum … is the planned paid layer; pricing is not set." |
| A18 Cook-number privacy / test-number caveat | **CONFIRMED** | Script `narr/s04.txt`: "That number is a test number in this simulation; the list reveals only cooks with active menus." |
| A20 Empty-cart guard + STOP opt-out branches | **CONFIRMED** | Frames @141s ("Step 7 · Empty-cart guard": 0 on empty basket → guard re-renders menu) and @227s ("Step 10 · Opt-out": STOP → "You've been opted out of menu updates"). Scripts `narr/s06b.txt`, `narr/s08b.txt` present; transcripts `s06b-emptycart.json`, `s08b-stop.json` drive the real engine. |
| A22 Reworded "cutout image", digest "sends", gross-vs-net reconciliation | **REJECTED** | None of the three phrases exist in customer-en v1 or v2 — the changelog misattributes the item. The actual offending lines live in other videos and were NOT reworded: (1) `roomlens-designer-en/audio/s2.txt` still says "The backend saves the cutout image to local storage" (v1 segment reused; s2.mp3 unchanged, seg01.mp4 duration 24.33s = old mp3 + pad); (2) `biteflow-cook-mr/v2/scripts/step5.txt` still says "बाइटफ्लो रोजचा नफा-तोटा पाठवतं" ("sends the daily P&L" — implies a cron that does not ship in this repo); (3) cook-mr step5/step6 gained no gross-vs-net distinction (recon "एकूण" vs P&L "निव्वळ" unaddressed in narration). |

**Notes (not verdict drivers):** the pre-existing minor 🍳→🔍 magnifier glyph (v1 m2) still appears at @203s ("…will start cooking soon. 🔍" while transcript says 🍳). The changelog never claimed this fix for customer-en (A21 was scoped to cook-mr), so it is noted, not counted. designer-en's 👍/👎 glyphs now render correctly as a bonus (wasn't claimed for designer-en).

---

## biteflow-cook-mr-v2.mp4 (232.411s)

| Changelog item | Verdict | Evidence |
|---|---|---|
| A6 Captions re-rendered with safe margins | **CONFIRMED** | Frames @15s (Step 1), @50s (Step 2), @100s (Step 4), @153s (Step 6), @190s (Step 7): caption is a yellow band at the bottom, chat content fully visible above it. @15s the language menu and @190s the Finance menu items (previously covered) are fully legible. |
| A13 Money moment in Marathi: no-commission + addendum | **CONFIRMED** | Script `step6.txt`: "या आवृत्तीत प्लॅटफॉर्म कमिशनचा हिशोब नाही… पैसे ग्राहकाकडून थेट स्वयंपाकीणीकडे. आणि मग बाइटफ्लो पैसे कुठून कमावणार? … व्यवसाय मालकांसाठीचा पूरक संच — दररोजचा नफा-तोटा, अन्नखर्चाचे गणित, मार्केटिंग प्रसारण — हीच भविष्यातली शुल्कावरची पातळी; किंमत अजून ठरलेली नाही." |
| A14 P&L reframed as demo data, not a live P&L | **CONFIRMED** | Script `step5.txt`: "हे आकडे या डेमो सत्रातल्या पूर्ण झालेल्या एकाच ऑर्डरवरून आलेले आहेत." Frame @153s shows the P&L bubble with correct Marathi and emoji. |
| A15 Plain spoken Marathi | **CONFIRMED** | No backend/media-store/compositing jargon in any step script (grep: 0 hits in `v2/scripts/*.txt`). |
| A16 Bilingual closing card | **CONFIRMED** | Frame @229s: three Marathi/English blocks — simulated client, USD prices, Business/Finance English fallback — all legible. |
| A21 Emoji glyph re-render (🍳/👍/👎) | **CONFIRMED** | Frame @100s: स्वीकारा 👍 / नकारा 👎 render as real thumbs; @50s: 🍳 renders as a proper pot. No pointing-hand or magnifier substitutions. |

**Notes:** closing-card line "हा डेमो आहे — खरं व्हॉट्सअँप नाही" has a small Devanagari shaping artifact on "व्हॉट्सअँप" (minor cosmetic, not checklist). The retained "रोजचा नफा-तोटा पाठवतं" wording (A22 sub-claim) still implies a daily automated send — see REJECT above.

---

## roomlens-prospect-mr-v2.mp4 (212.300s)

| Changelog item | Verdict | Evidence |
|---|---|---|
| A1 n7 re-recorded: commission claim removed | **CONFIRMED** | Script: "या आवृत्तीत प्लॅटफॉर्म कमिशनचा हिशोब नाही — हा व्यवसाय निर्णय अजून बाकी आहे." n7.mp3 rebuilt 05:04 UTC (24.05s); segment duration 24.57s = new mp3 + 0.5s hold. |
| A2/A23 Money moment: order row + notify; no in-app payment, paid directly off-platform | **CONFIRMED** | Script n7: "ऑर्डरची नोंद इंजिनमध्ये जाते… इथे ॲपमध्ये पैसे भरायची सोय नाही; …पैसे डिझायनरशी थेट ठरतात." |
| A4 Synthetic-media disclosure: on-mic at photo step + closing card | **CONFIRMED** | Script n3: "एक प्रामाणिक टीप — या डेमोमध्ये नमुना फोटो वापरले आहेत… तुमची स्वतःची खोली मात्र अगदी खरी." n3.mp3 rebuilt 05:04 UTC (34.13s, consistent with the longer script); segment 34.63s = new mp3 + hold. Frame @205s: closing card "Demo uses sample room & product photos / डेमोमध्ये नमुना खोली व उत्पादन फोटो वापरले आहेत." |
| A6 Captions safe margins; viz sub-caption legible | **CONFIRMED** | Frames @5s (Step 1), @62s (Step 3), @175s (Step 7): yellow band below header, no overlap. Frame @122s: sub-caption "rendered by src/composite.py · preset compositing, not AR" fully wrapped and legible inside the frame. |
| A15 Plain spoken Marathi | **CONFIRMED** | The only "backend/media-store/compositing-engine" hits are in the script file's header comment, not in narration. |
| A16 Bilingual closing; boast softened ("बहुतेक मराठीत") | **CONFIRMED** | Frame @205s: four EN/MR line pairs, all legible. Narration closing uses "बहुतेक मराठीत" (mostly in Marathi) instead of the absolute claim. |
| A17 USD disclosure on closing card | **CONFIRMED** | Frame @205s: "Prices shown in USD (real engine behavior) / किंमती डॉलरमध्ये दाखवल्या आहेत (इंजिनचं खरं वर्तन)." |
| A19 Honest timing: आपोआप instead of लगेच | **CONFIRMED** | Narration uses आपोआप throughout; the only लगेच hit is in the header comment. |
| A20 Option-4 "talk to the designer" branch | **CONFIRMED** | Frame @160s ("Step 6 · Designer notified"): designer's view "+15550005555 wants to talk to you directly." n6b1.mp3/n6b2.mp3 built; segments use f6b1/f6b2 frames. |

**Notes:** the noise "room photo" is still shown (@62s) — deliberately retained per triage R1, now disclosed on-mic. A crossfade ghost frame ("RoomLens Studio"/"Casa Studio" double header) was caught at @160s — a transient transition artifact, not a defect.

---

## roomlens-designer-en-v2.mp4 (200.367s)

| Changelog item | Verdict | Evidence |
|---|---|---|
| A2 s7 re-recorded: money-moves removed | **CONFIRMED** | Script `s7.txt`: "Here's the honesty: no money moves inside the app here. The booking writes an order row… the designer's fee is a record… paid directly, off-platform." s7.mp3 rebuilt 05:02 UTC (27.67s); seg06.mp4 = 28.67s = new mp3 + 1.0s pad. |
| A4 Synthetic disclosure: on-mic at viz step + closing card | **CONFIRMED** | s6.mp3 rebuilt 05:02 UTC (18.89s); seg05.mp4 = 19.90s = new mp3 + pad. Script `s6.txt`: "An honesty note: the room photo and the chair here are sample images for this demo — the compositing engine itself is real." Frame @196s: "Demo uses sample room & product photos." |
| A6 Bottom captions safe margins; step-8 clip fixed | **CONFIRMED** | Frames @60s (Step 3) and @185s (Step 8): caption bar at bottom, chat above, no overlap. Step-8 caption "Step 8 · Booking confirmed — designer fee booked" is fully visible — the v1 right-edge clip ("designer fee booke…") is gone. |
| A11 Webhook hardening on closing card | **CONFIRMED** | Frame @196s: "Pilot build: webhook signature validation, idempotency, and rate limiting not yet implemented." |
| A12 Approved-template clause on closing card | **CONFIRMED** | Frame @196s: "Production business-initiated messages need approved Meta templates." |

**Note:** the A22 "cutout image" overstatement lives in this video's step 2 (`audio/s2.txt`: "The backend saves the cutout image to local storage") and was NOT reworded — see the REJECT row under customer-en.

---

## Fix ledger (for the record)

- **Confirmed fixes:** 31/32. Captions, emoji tofu/glyphs (customer-en, cook-mr), synthetic-media disclosures on-mic and on-card, commission claims removed, money moments honest (no in-app payment; paid directly off-platform), P&L reframed as demo data, plain-Marathi scripts, bilingual closing cards, USD disclosures, empty-cart/STOP/option-4 branches driven through the real engine, single-phone step 8, active-menu matching, cook-number privacy, Meta-template and webhook-gap lines on closing cards.
- **Rejected:** 1/32 — A22 (customer-en section): the three SrEng-minor rewords were never applied anywhere, and the item is misattributed to a video that never contained the phrases.
- **Bonus fixes not claimed in the changelog:** manifest.json rewritten for v2 (v1 M1 over-promising manifest resolved — now describes only what the videos contain); designer-en 👍/👎 glyphs now render correctly.
- **Still-present pre-existing minors, not claimed, not counted:** customer-en 🍳→🔍 glyph at @203s; small Devanagari shaping artifact in cook-mr closing card.

## Recommendation

Do not mark v2 as signed off. Either (a) accept A22 as a known-minor and ship v2 with that caveat recorded, or (b) run a v2.1 pass: reword designer-en s2's "saves the cutout image to local storage", change cook-mr step5's "रोजचा नफा-तोटा पाठवतं" to a pull/manual phrasing, and add a gross-vs-net note to cook-mr step5/step6 narration, then re-record those three narration segments. The rest of the package is ready.
