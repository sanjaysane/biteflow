# Board Director Re-review — Walkthrough Videos v2

**Verdict: SIGN-OFF (with one noted soft spot)**

Both v1 blockers are fixed and the fixes are in the actual video files, not just
the scripts. Every disclosure I flagged as missing is now in-video (narration
and/or closing card). One item — the trust-based P2P payment disclosure (M2) —
is weaker than the changelog claims: the exact "cook-verified, not bank-verified"
line is not in the video. It does not rise to a blocker (nothing false is
asserted now), but it is the softest point left, and the changelog overstates it.

Method: read the v2 narration scripts in `work/*/` (all regenerated during the
Sep 6 ~05:00–05:05 rebuild; the audio mp3s were re-recorded immediately after
their corresponding scripts, so scripts ≈ spoken audio), extracted closing-card
frames from all four v2 mp4s with ffmpeg (durations match manifest.json v2:
350.2 / 232.4 / 212.3 / 200.4s), and diffed the manifest descriptions against the
v1 findings. Timestamps are approximate, derived from cumulative audio segment
durations (±~10s).

---

## Blockers — re-checked

### B1. RoomLens commission contradiction — CONFIRMED FIXED

Both videos now state the same code truth, in near-parallel phrasing:

- **roomlens-prospect-mr-v2.mp4 @ ~3:08** (narration n7, Marathi): *"या
  आवृत्तीत प्लॅटफॉर्म कमिशनचा हिशोब नाही — हा व्यवसाय निर्णय अजून बाकी आहे"*
  — "in this version there is no platform commission accounting — that
  business decision is still pending." The v1 commission-as-business-model
  claim is gone entirely.
- **roomlens-designer-en-v2.mp4 @ ~3:03** (narration s8): *"There is no
  platform commission accounting in this version of the code, so I will not
  invent a cut — that is a business decision the team still has to make."*
  (unchanged from v1, now corroborated rather than contradicted.)

A viewer watching both videos now gets one consistent answer: no commission
accounting exists; the business model is undecided. This matches the code
(zero `commission` hits) and R3/R4 (no invented take rate).

### B2. RoomLens money-movement implication — CONFIRMED FIXED

Both videos now say, explicitly, that no payment happens in the app:

- **roomlens-prospect-mr-v2.mp4 @ ~3:08** (n7): *"लक्षात घ्या — इथे ॲपमध्ये
  पैसे भरायची सोय नाही … पैसे डिझायनरशी थेट ठरतात"* — "note: there is no
  in-app payment here … payment is settled directly with the designer." The
  v1 "पैशाचा क्षण" ("money moment") line is gone.
- **roomlens-designer-en-v2.mp4 @ ~2:33** (s7, re-recorded; audio file mtime
  05:02, immediately after the script edit): *"An important correction: no
  money moves inside this app. The tap records the order and notifies the
  designer — there is no in-app payment; the designer is paid directly, off
  platform."* The v1 line "the prospect's payment becomes the designer's fee"
  is removed.

The regulator's "where does the prospect's payment go?" question now has a
true answer on-mic: nowhere through the app — off-platform, directly.

---

## Major findings — re-checked

### M1. Food-safety disclosure — CONFIRMED FIXED

**biteflow-customer-en-v2.mp4 closing card** (verified frame from the actual
video): *"Demo only — a real deployment needs cottage-food / food-safety
compliance for home kitchens."* (amber highlight). The "real home kitchen"
premise now ships with the journalist-flammable question answered in-video.

### M2. Trust-based P2P verification — PARTIALLY FIXED (changelog overstates)

The v2 narration at the payment step
(**biteflow-customer-en-v2.mp4 @ ~2:43**, s07) says: *"the customer pays the
cook over Zelle or UPI, then sends a screenshot for the cook to approve.
Still no middleman."*

The CHANGELOG claims the added line was "the cook approves a screenshot —
cook-verified, not bank-verified." The actual script and (per duration math,
37.9s for 99 words ≈ normal TTS rate) the actual audio contain the first half
but **not the "not bank-verified" qualifier**, and the closing card has no
payment-trust line either. What a viewer hears is: cook approves a screenshot
— which implies cook-verification and is not false — but the explicit
disclaimer that nothing is bank-checked (the part a fraud victim's lawyer
would care about) is missing.

Why not reject: nothing asserted is false; the mechanics are described
accurately ("cook to approve" = eyeball check, matching `SECURITY.md` item 4).
But this is the single weakest v2 fix relative to its changelog claim, and a
fraud story would still read "✅ Payment approved by the cook!" against it.
**Recommendation: one 10-second re-record inserting "…an eyeball check —
not bank-verified" into s07 before any public launch.**

### M3. Synthetic-inputs disclosure — CONFIRMED FIXED

- On-mic at the photo step (**roomlens-prospect-mr-v2.mp4 @ ~0:52**, n3):
  *"एक प्रामाणिक नोंद — या डेमोमध्ये नमुना फोटो वापरले आहेत; तुमचा स्वतःचा
  फोटो इथे दिसेल"* ("an honest note — this demo uses sample photos; your own
  photo would appear here"). (The n5 "in your own room" line survives, but it
  now follows this disclosure, so it reads as demo framing, not deception.)
- On closing cards of **both** RoomLens videos (frames verified):
  *"Demo uses sample room & product photos"* (+ Marathi on prospect-mr).

### M4. manifest.json corrections — CONFIRMED FIXED

- customer-en description: now *"checkout with cash-on-delivery or phone
  transfer (Zelle/Venmo/UPI/Pix)"* — "card" is gone; matches the engine's two
  options.
- cook-mr description: now *"menu publish = going live (no separate toggle in
  this build)"* — matches both the code and the video's own on-mic line.

---

## Minor findings — re-checked

- **m1 (bilingual Marathi cards) — CONFIRMED FIXED.** Extracted frames from
  both v2 Marathi videos: every closing-card line is now bilingual
  (Marathi lead + English). Prospect-mr: simulated-client, preset-compositing,
  sample-photos, USD lines all bilingual. Cook-mr: demo/simulated, USD,
  English-fallback-for-Business-Finance lines all bilingual. The v1 closing
  narration boast is also softened: n10 now says *"बहुतेक मराठीत"* ("mostly in
  Marathi") instead of *"सगळं मराठीत"*.
- **m2 (USD on prospect-mr card) — CONFIRMED FIXED.** Closing card (frame
  verified): *"Prices shown in USD (real engine behavior)"* + Marathi
  translation.
- **m3 (cook phone-number privacy) — CONFIRMED FIXED.** Customer-en narration
  @ ~1:14 (s04): *"One privacy note: the header shows the cook's phone number —
  these are test numbers; a real pilot needs a design that keeps cooks'
  personal numbers private."*
- **m4 (broadcast template constraints) — CONFIRMED FIXED.** Customer-en
  narration (s08): *"those business-initiated broadcasts need approved Meta
  templates, not one-shot chat messages."* Designer-en closing card also
  carries *"Production business-initiated messages need approved Meta
  templates."*
- **Commission consistency across BiteFlow videos — CONFIRMED.** cook-mr
  money narration (Marathi): *"या इंजिनमध्ये प्लॅटफॉर्म कमिशन नाही"*; customer-en
  s07: *"BiteFlow takes no commission in this build … the business-owner
  addendum … is the planned paid layer; pricing is not set."* No invented
  numbers (R3/R4 respected).
- **Closing-card hardening lines — CONFIRMED.** Customer-en and designer-en
  cards both carry: *"Pilot build: webhook signature validation, idempotency,
  and rate limiting not yet implemented."*
- **"AI" — still absent.** Grep over all v2 narration scripts, captions,
  render code, and manifest.json: zero whole-word hits. "State machine,"
  "compositing engine," "Pillow and NumPy" remain the vocabulary. Keep it
  that way.

---

## Deliberately-not-changed items (R1–R8) — acknowledged

The changelog explicitly punts: synthetic viz inputs (disclosed instead —
fine), Marathi locale strings, no commission/payment code, USD-only, no
live/offline toggle, "Enterprise-hardened pilot" release tag (still on
GitHub; the m5 risk persists — the videos do not carry it, but if release
notes and videos travel together, the tag will be read against the open
webhook gaps — recommend owner action, unchanged from v1), no designer SLA.
These are documented decisions, not oversights.

---

## Rubric answers

**1. Claim audit (v2).** All v1 blockers resolved; all disclosures I asked for
are in-video. Nothing I checked against the code is now contradicted by the
narration. New v2 branches (empty-cart guard, STOP opt-out, "talk to the
designer") are driven through the real engine per the changelog.

**2. Public-embarrassment test.** The journalist's questions now have on-video
answers: food-safety compliance (closing card, M1 ✓); who verifies the payment
screenshot (narration says the cook approves — but see the M2 caveat, the one
remaining soft spot); the regulator's money-flow and commission questions
(B1/B2 ✓ — both videos agree, both on-mic); the Marathi viewer's dollar-price
and English-disclaimer questions (m1/m2 ✓ — bilingual cards).

**3. Disclosure sufficiency.** The closing-card pattern from v1's exemplary
cook-mr video has been replicated across all four videos, each with the
disclosures relevant to its content. Nothing material still lives only in a
sidecar.

**4. The word "AI."** Still nowhere. ✓

**5. LEAKS.md honesty.** Sidecar unchanged in status; v2 moves the material
items ("Total"/"received" remain English in-chat by design — the n10
"mostly in Marathi" softening and bilingual cards now carry the
transparency instead; synthetic inputs now on-card; USD now on-card).

---

## Verdict

**SIGN-OFF.** The v2 pack is ship-ready for public sharing from a board-risk
standpoint: the two blockers are genuinely fixed in the video files, every
disclosure flagged in v1 is now in-video, and both RoomLens videos agree on
commission and payment.

Caveats to hand to the parent agent:
1. **M2 soft spot (only open item):** the "cook-verified, not bank-verified"
   qualifier claimed in the changelog is not in the video — narration says
   only "the customer … sends a screenshot for the cook to approve."
   Recommend a ~10-second s07 re-record ("an eyeball check — not
   bank-verified") before public launch. Not a blocker; no falsehood.
2. The changelog slightly overstates the M2 fix (quotes a line that was not
   shipped) — the parent agent may want to correct `CHANGELOG-v1-v2.md` so it
   doesn't promise a review evidence trail that doesn't exist.
3. Residual punted risks, unchanged and acknowledged: "Enterprise-hardened
   pilot" GitHub release tag vs. open webhook gaps (owner action recommended);
   USD-only currency; no live/offline toggle; synthetic viz inputs (disclosed).
