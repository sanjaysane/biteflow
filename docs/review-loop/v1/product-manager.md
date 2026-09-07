# Product Manager Review — Walkthrough Videos v1

**Verdict: NEEDS WORK**

Reviewed as a first-time viewer: all 4 videos end-to-end, frames every ~20s, full narration scripts.

---

## BLOCKERS (must fix before showing to anyone outside the team)

### B1 — RoomLens: the two videos contradict each other on the business model
- **Where:** `roomlens-prospect-mr.mp4` Step 7 (~2:35–2:50) vs `roomlens-designer-en.mp4` Step 8 (~2:40–2:55).
- **What a viewer experiences:** In the prospect video the narrator says, in Marathi: the designer's fee is set "आणि त्यावर प्लॅटफॉर्मचं कमिशन — हेच रूमलेन्सचं बिझनेस मॉडेल" ("and platform commission on it — that's RoomLens's business model"). In the designer video the narrator says the opposite: "this build books the full order total as the designer's fee. There is no platform commission accounting in this version of the code... that is a business decision the team still has to make."
- **What they should experience:** one story about how money flows. A viewer who watches both videos walks away with two different business models. Pick the actual truth, make both narrations say it.

### B2 — RoomLens: the money-shot preview looks broken, which kills the product promise
- **Where:** `roomlens-prospect-mr.mp4` Step 5 (~1:45–2:05); also `roomlens-designer-en.mp4` Step 5–6 (~1:50–2:30).
- **What a viewer experiences:** "तुमच्याच खोलीत एरिया चेअर" ("the Aria Chair in YOUR room") — and on screen is a crudely drawn brown rectangle with the text "Aria Chair" stamped on it, sitting on what reads as TV static, not a room. It looks like a placeholder that escaped into production, not a product.
- **What they should experience:** the whole pitch is "see beautiful furniture in YOUR OWN room before you buy." If the demo render can't look even mildly plausible, the viewer concludes the product doesn't work and stops believing everything after it. Use a real room photo and a real product cutout for this one frame — nothing else in the video matters if this frame fails.

### B3 — BiteFlow cook has no way to go offline (missing day-one flow)
- **Where:** `biteflow-cook-mr.mp4` Step 2 (~0:45); the narrator is honest about it: "इंजिनमध्ये किचन चालू-बंदचं वेगळं बटण नाही; मेनू जाहीर झाला की किचन लाइव्ह" ("the engine has no separate on/off button; once the menu is announced the kitchen is live").
- **What a viewer experiences:** a home cook's kitchen is permanently open once announced. What happens at 10 PM when she's done cooking? What if she goes on a trip?
- **What they should experience:** a real viewer immediately asks "how do I stop orders tonight?" — and there is no answer. Either build the toggle or change the demo to show the only workaround (un-publish the menu) explicitly. As shown, the product looks unfinished for the exact person it's sold to.

---

## MAJOR (fix before calling this a product story)

### M1 — Manifest advertises a "reorder" flow that was dropped from the build
- **Where:** `manifest.json` for `biteflow-customer-en.mp4` claims "cancel, reorder, and unknown-input fallback." The 13 narration segments cover welcome→cancel; there is no reorder segment (`work/biteflow-customer-en/drive_journey.py` line 17: "DROPPED: reorder-from-history — the engine has no such command").
- **What a viewer experiences:** the manifest promises reorder; the video never shows it; the engine can't do it.
- **What they should experience:** the manifest must describe what's actually in the video. Fix the one-word manifest, not the product.

### M2 — RoomLens: the prospect↔designer feedback loop is claimed but never closed
- **Where:** `roomlens-prospect-mr.mp4` Step 6 (~2:05): prospect replies "2", narrator says the request "डिझायनरच्या फोनवर जाते" ("goes to the designer's phone"). The video moves on; we never see the designer receive or act on it. The designer video shows no change request arriving either.
- **What a viewer experiences:** a loop is described but demonstrated only halfway — the video keeps narrating as if it worked.
- **What they should experience:** either show the designer's phone receiving the request and re-rendering, or don't claim the loop. Related gap: no timing expectation anywhere — the prospect sends a photo at ~1:15 and is told "तयार झाला की लगेच कळवू" ("we'll tell you when ready") with no SLA. A human designer is in the critical path and the viewer is given no idea whether the wait is 5 minutes or 5 days. That's the single biggest bounce risk in the prospect journey.

### M3 — RoomLens: order numbers don't match between the two videos
- **Where:** prospect video Step 7 confirms "ऑर्डर #9"; designer video Step 7–8 confirms "new order number ten" / moves "order ten from received to preparing."
- **What a viewer experiences:** these are presented as the same marketplace loop, but the transaction identifiers disagree.
- **What they should experience:** one coherent product story. If the two runs can't share state, at least align the identifiers (or don't frame them as one loop).

### M4 — BiteFlow: the customer sees cooks as phone numbers
- **Where:** `biteflow-customer-en.mp4` Step 4 (~1:10): the menu header reads "+15550001111's menu:" — a bare phone number, no name, no photo, no location, no rating.
- **What a viewer experiences:** "who am I buying food from?" The answer is a phone number. For a product whose audience includes seniors ordering food from strangers, this fails the trust test on screen one.
- **What they should experience:** a cook name/kitchen name at minimum. (The demo data is at fault more than the engine, but the video is the product story — fix the fixture.)

### M5 — BiteFlow cook: the money screen falls back to English for a Marathi user
- **Where:** `biteflow-cook-mr.mp4` Step 6 (~2:40); the narration admits it: "हा भाग अजून मराठीत भाषांतरित झालेला नाही, म्हणून संदेश इंग्रजीत येतात" ("this part isn't translated to Marathi yet, so the messages come in English").
- **What a viewer experiences:** the single most important screen — the payout/reconciliation screen — is in the wrong language for the audience this video is aimed at.
- **What they should experience:** honesty in narration is good, but the money moment is the one screen where partial localization is not acceptable to demo. Finish the locale or cut the flow from this cut of the video.

### M6 — "Type language" is a hidden command both products depend on but never teach
- **Where:** `biteflow-customer-en.mp4` Step 2 (~0:30), `biteflow-cook-mr.mp4` Step 1 (~0:10), `roomlens-prospect-mr.mp4` Step 1 (~0:15).
- **What a viewer experiences:** every video's multilingual story hinges on the user spontaneously typing the word "language" — a command that appears in no menu, hint, or button. The narration presents it as discoverable; in the product it isn't.
- **What they should experience:** a real user would never find this. Add it to the welcome message (e.g., "Reply LANGUAGE anytime to switch languages") or acknowledge the discovery gap in the video.

---

## MINOR (polish)

1. **Quantity capped at single digits, silently.** `biteflow-customer-en.mp4` Step 5: "the reply must be a single digit, one through nine." A family ordering 12 portions hits a wall with no explanation. Minor for the demo, real friction in the product.
2. **"Live tracking" is status pushes, not tracking.** `biteflow-customer-en.mp4` Step 9: cooking → out-for-delivery → completed is a push notification model, and a good one. Calling it "live tracking" invites comparison with map-based tracking and slightly overclaims.
3. **Referral code option is unexplained.** `biteflow-customer-en.mp4` Step 6: the review screen offers "enter a referral code" — never explained anywhere. Dead menu item in the hero flow.
4. **"On the wall" is a placement preset for a chair.** `roomlens-designer-en.mp4` Step 5 (~2:00): options include "On the wall." A viewer notices; it reads as untested copy.
5. **Frame-render overlap glitch.** `biteflow-customer-en.mp4` at ~3:20 (frame f010): the "Step 9 · Order accepted" and "Step 9 · Live tracking" title cards render on top of each other mid-transition. Cosmetic, but it's the tracking moment — the one place visual clarity matters most.
6. **Prospect tips opt-in arrives before the preview.** `roomlens-prospect-mr.mp4` Step 3: the user is asked to subscribe to design tips while still waiting for their first preview. Ask after delivering value, not before.
7. **Two phones in the BiteFlow customer video can confuse.** Step 8 switches to "the cook's phone" mid-journey with a brief overlay label. It works, but the transition is fast; a first-time viewer may not register whose phone they're looking at. The cook-mr video's Step 3 handles the same two-phone moment more clearly.

---

## Rubric scores

**1. 60-second test**
- BiteFlow customer: **PASS.** At 0:00: "Welcome to BiteFlow! Hot home-cooked meals, ordered right here in WhatsApp. No app needed." Product (home-cooked food via WhatsApp), audience (people who want home cooking, including cooks as sellers), and edge (no app, no commission, peer-to-peer payment — lands at the money moment ~2:45) are all clear.
- BiteFlow cook: **PASS.** At ~0:20 the Marathi narration frames it: register as a cook, list dishes, go live, get paid directly. The seller-side mirror of the same story.
- RoomLens prospect: **PASS on the pitch, FAIL on the proof.** At 0:00: "See beautiful furniture in YOUR OWN room before you buy" + "free room preview" — crystal clear. Then the preview itself (B2) destroys credibility.
- RoomLens designer: **WEAK PASS.** Onboarding is clear (studio name → catalog → studio → orders), but the "why better than the alternative" is never stated. Alternative to what — Instagram DMs? Shopify? The viewer is left to infer the value prop.

**2. Onboarding friction (steps from "hi" to first value)**
- BiteFlow customer: hi → role → (optional language) → cook → dish → qty → checkout → confirm → pay method = **~9 messages** to "Order placed." Very low. Bounce risks: M6 (hidden language command), minor #1 (qty cap).
- BiteFlow cook: hi → language → role → menu-name (free text) → price (free text) → repeat → publish = **~10 messages** to live menu. The two free-text entries (dish name, price in USD) are the only real friction; price validation with a polite Marathi re-prompt is well handled.
- RoomLens prospect: hi → language → role → designer → photo → **wait for a human** → preview → change → book. Everything before the wait is ~6 steps and smooth; the unbounded wait for the designer is the bounce point (M2).
- RoomLens designer: hi → role → studio name → per-product: name + price + size tag + photo = **~6 messages per catalog item.** Acceptable once, but cataloging 20 products is a grind — worth a bulk/catalog-import story later.

**3. Confusing steps**
- Numbered-reply UX is consistent across all four videos and the videos teach it well; the fallback demos ("banana" at cook-pick, gibberish at catalog, "abc" as a price, wrong number "9" at designer-pick) are genuinely reassuring. The weak spots are M6 (the one command that isn't numbered and isn't discoverable) and the BiteFlow review screen's referral-code option (minor #3).

**4. Missing day-one flows**
- BiteFlow: change/cancel an order **after** confirm but before cooking (no), wrong item delivered (no), cook going offline mid-order (B3 — can't even go offline at all), who delivers and how the customer knows them (never shown), reorder (advertised, doesn't exist — M1).
- RoomLens: prospect sends a bad photo (handled well — quality check, good), prospect sends photo of the wrong room (no), designer ignores a change request (no SLA — M2), commission accounting (contradicted — B1).

**5. Pacing**
- No dead 30-second stretches in any video; lengths (3.1–5.3 min) fit the content. Two places deserve *more* time, not less: the BiteFlow money moment (s07 — "no commission, no middleman" is the core differentiator and it passes quickly) and the RoomLens composite result (currently rushed past because, per B2, there's nothing good to look at — fix the frame, then linger on it).
- Both BiteFlow videos and both RoomLens videos each spend proportionate time on happy path vs. fallback demos — good balance; the fallback segments are the strongest trust-building minutes in the set.

**6. One coherent product story per pair?**
- **BiteFlow: YES.** The customer video and cook video show the two sides of one marketplace loop — the *same order #5* flows through both, in two languages, demonstrating the multilingual engine. This is the best thing about the set.
- **RoomLens: NO.** The prospect and designer videos describe the same loop but contradict the business model (B1), disagree on the order number (M3), and the feedback loop is shown from only one side (M2). They feel like two demos built on different days that were later declared a pair.

---

## Bottom line for the swarm
Ship the BiteFlow pair after fixing the manifest (M1), the hidden-language discovery (M6), and the cook phone-number fixture (M4); the offline toggle (B3) needs a product decision either way. Do not ship the RoomLens pair until the composite frame looks like a real product (B2) and both videos tell the same money story (B1). The honest-narration style ("this is preset compositing, not true AR," "no commission accounting in this build") is a strength — keep it; it's exactly why B1/B2 stand out as fixable rather than fatal.
