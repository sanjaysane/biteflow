# Board Director Review — Walkthrough Videos v1

**Verdict: NEEDS WORK**

Two factual blockers, both in RoomLens: the two videos assert opposite facts about
the same business model, and both imply money moves through an app that has no
payment handling at all. Beyond that, the pack is unusually honest in places
(in-narration English-fallback disclosure, "preset compositing, not true AR" said
out loud and on the closing card) — the problems below are fixable, but the
blockers must be fixed before anything goes public.

Method: every narration script was read in full (`work/*/audio`, `work/*/narr`,
`work/*/scripts`), closing cards inspected frame-by-frame, and material claims
checked against `src/` in both repos, `SECURITY.md` in both repos, `BRIEF.md`,
`LEAKS.md`, and `manifest.json`. Timestamps are approximate (derived from
narration audio durations; ±a few seconds).

---

## Blockers

### B1. The two RoomLens videos contradict each other on the business model — one asserts a platform commission that does not exist in the code.

- **roomlens-prospect-mr.mp4 @ ~2:23** (narration n7, Marathi): *"बुकिंग झालं की
  डिझायनरची फी ठरते, आणि त्यावर प्लॅटफॉर्मचं कमिशन — हेच रूमलेन्सचं बिझनेस
  मॉडेल."* — "Once booked, the designer's fee is fixed, and on that, the
  platform's commission — that is RoomLens's business model."
- **roomlens-designer-en.mp4 @ ~2:33** (narration s8): *"There is no platform
  commission accounting in this version of the code, so I will not invent a
  cut — that is a business decision the team still has to make."*
- Code: `grep -rni commission` over the entire RoomLens repo (src, locales,
  docs) returns **zero hits**. There is no commission accounting, no fee
  field, no commission line in `quote_lines_text` (only line items, optional
  delivery, Total).

Reputational risk: a journalist or prospective designer watching both videos
gets two opposite answers to "how does RoomLens make money?" The Marathi
narration states as fact something the English narration explicitly disavows
and the code does not implement. This is the exact "estimate presented as
fact" failure class. The prospect-mr line must be re-recorded to match the
designer-en disclosure (no commission accounting exists yet).

### B2. Both RoomLens videos imply money moves through the app — the app has no payment handling whatsoever.

- **roomlens-designer-en.mp4 @ ~2:11** (narration s7): *"This is the
  business-model moment when money moves: the prospect's payment becomes the
  designer's fee."*
- **roomlens-prospect-mr.mp4 @ ~2:23** (narration n7, Marathi): *"इथंच पैशाचा
  क्षण येतो"* — "this is where the money moment comes."
- Code: RoomLens has no payments module, no payment handlers, no payment
  locales. Booking writes an order row and sends a chat notification; nothing
  collects or settles money. The designer's s8 disclaimer about commission
  makes it worse, not better: it acknowledges a money question while s7 has
  already told the viewer a payment happened.

Reputational risk: a viewer who tries RoomLens will ask "how do I pay?" and
get no answer. A regulator or press reader will read "the prospect's payment
becomes the designer's fee" as a claim about funds flow through an unlicensed
intermediary. Until a payment story exists (even "payment happens off-platform
directly with the designer"), the narration must not say money moves.

---

## Major findings

### M1. BiteFlow's premise — "real home kitchens, not restaurants" — is celebrated with zero food-safety framing.

- **biteflow-customer-en.mp4 @ ~0:48** (narration s03): *"Each cook here is a
  real home kitchen, not a restaurant, which is the whole premise of BiteFlow
  micro-commerce."*

This is the single most journalist-flammable line in the pack. The video
presents unlicensed home cooks selling prepared food over WhatsApp as the
value proposition, and nowhere — not in narration, not on a card — is there
any mention of food-handler certification, cottage-food law, kitchen
inspection, or allergen disclosure. A regulator does not need to look hard
to ask "who is liable when someone gets sick?" The line may be true as a
product premise, but shipping it publicly without a food-safety disclaimer
(or a stated operating model for cook vetting) invites exactly the story we
do not want. The demo also normalizes paying a stranger's personal number
(see m3).

### M2. BiteFlow's P2P "payment approved" flow is trust-based — the video never says so, and its own SECURITY.md warns against it.

- **biteflow-customer-en.mp4 @ ~2:06** (narration s07): *"the customer pays the
  cook over Zelle or UPI, then sends a screenshot for the cook to approve.
  Still no middleman."* The bot copy shown is *"✅ Payment approved by the
  cook!"*
- `biteflow/SECURITY.md` item 4: **"P2P payment 'verification' is
  trust-based.** A screenshot or typed reference is accepted as a claim;
  nothing is checked against a bank, and media bytes are never downloaded."
  Item 6 header: *"Do not handle real money-adjacent traffic until at least
  the first three are addressed"* (webhook signature, idempotency, rate
  limiting — all missing).

The narration describes the mechanics accurately, but "Payment approved by
the cook!" reads as verified settlement when it is an eyeball check of an
unvalidated screenshot — a trivially forgeable instrument. The video should
carry the same honesty the cook-mr video shows elsewhere (cf. its on-mic
fallback disclosure): one line that payment proof is cook-verified, not
bank-verified. As narrated, a fraud victim's first exhibit would be this
video.

### M3. RoomLens presents synthetic test fixtures as "your own room" with no in-video disclosure.

- **roomlens-prospect-mr.mp4 @ ~1:55** (narration n5, Marathi): *"आणि हे आहे
  प्रीव्यू — तुमच्याच खोलीत एरिया चेअर"* — "this is the preview — the Aria
  Chair in your own room." @ ~0:46 (n3): the narration instructs the viewer to
  "send a clear photo of your room," implying a real prospect photo.
- Reality (BRIEF.md honest notes): room and chair are synthetic samples from
  the repo test toolkit (`make_test_room`, `make_placeholder_cutout`). The
  mid-video frame (~1:35) shows a gray-noise rectangle room and a brown
  rounded rectangle labeled "Aria Chair" — a placeholder, not furniture.
- The compositing *engine* claim is fair ("पिलो आणि नमपाय वापरून… कोणताही
  हातचा फोटोशॉप नाही" — Pillow/NumPy, no hand Photoshop — verified in
  `src/composite.py`). What is not fair is letting the viewer believe the
  inputs are real. BRIEF.md discloses this only in a sidecar file; nothing
  in the video does. One on-screen or narrated line ("sample photos used")
  fixes it.

### M4. manifest.json — the published description of these videos — contains two claims the code and the narrations themselves refute.

- **biteflow-customer-en.mp4** description: *"checkout with UPI/card/COD."*
  The engine offers exactly two options (`payment_title` locale):
  1️⃣ Cash on delivery, 2️⃣ Phone transfer (Zelle/Venmo/UPI/Pix). There is no
  card flow anywhere in the repo. "card" is invented.
- **biteflow-cook-mr.mp4** description: *"live/offline toggle."* There is no
  live/offline toggle in the code (`src/handlers/cook.py` has none), and the
  video's own narration at ~1:08 (step2) explicitly says so: *"इंजिनमध्ये किचन
  चालू-बंदचं वेगळं बटण नाही; मेनू जाहीर झाला की किचन लाइव्ह"* ("the engine
  has no separate on/off button; once the menu is announced, the kitchen is
  live"). The manifest contradicts the video it describes.

The manifest is what a viewer reads before pressing play. Fix the two
descriptions; they are small edits with outsized misrepresentation risk.

---

## Minor findings

### m1. Closing cards and section banners are in English on the Marathi videos — the Marathi audience cannot read the disclaimers.

- Both Marathi videos end with English-only closing cards
  (prospect-mr @ ~3:04; cook-mr end card). The cook-mr card adds the USD
  note; the prospect-mr card does not (see m2).
- **roomlens-prospect-mr.mp4**: all on-screen step banners are English
  ("Step 4 · Draft preview", visible ~1:35) — an English-in-video-chrome leak
  that `LEAKS.md` does not count (it audits chat bubbles only).
- **roomlens-prospect-mr.mp4 @ ~3:04** (closing narration n10, Marathi):
  *"सगळं व्हॉट्सॲपवर, सगळं मराठीत"* — "all on WhatsApp, all in Marathi."
  Overbroad: the banners are English, the closing card is English, and the
  chat itself contains the documented English leaks ("Total" @ order summary,
  "received" @ tracking per LEAKS.md). The closing boast should be softened
  or the leaks disclosed in-video.

### m2. USD prices are shown to Marathi viewers with uneven in-video disclosure.

- cook-mr: USD is disclosed **in-video** on the closing card ("Prices shown
  in USD (real engine behavior)") — good; it is also disclosed on-mic in
  narration (step2, ~0:25: "मग किंमत, डॉलरमध्ये").
- prospect-mr: `$189.00` appears throughout (price strip, quote, caption),
  and the closing card says only "simulated client / preset compositing" —
  **no USD note anywhere in the video**. LEAKS.md lists the USD pricing as
  disclosed, but for this video it is disclosed only in the sidecar. A
  Marathi viewer reasonably reads $189 as the price they would pay. Add the
  one-line USD note to the prospect-mr closing card, as was done for cook-mr.

### m3. The product UX exposes home cooks' personal phone numbers as menu titles and payee IDs — shown on screen, undisclosed as a privacy trade-off.

- **biteflow-customer-en.mp4 @ ~2:06** (payment screen): *"Please pay $17.00
  to +15550001111 via Zelle, Venmo, UPI or Pix."* @ ~2:42 (opt-in screen):
  *"Want +15550001111's menu updates on WhatsApp?"* The menu itself is titled
  "+15559876543's menu."
- These are test numbers, but the *design* is real: a customer's payee is a
  cook's personal phone number, displayed in-chat. For a home-kitchen
  marketplace this is a doxxing/harassment vector by design. Worth a privacy
  note in the repo's threat model before any pilot with real numbers; at
  minimum the video should not present it as unremarkable.

### m4. Business-initiated messaging (menu broadcasts, campaigns, win-back) is shown without noting WhatsApp's template/policy constraints.

- customer-en @ ~2:42 shows the menu-update broadcast opt-in; RoomLens
  designer flow includes marketing campaigns and win-back
  (`src/marketing.py`). `biteflow/SECURITY.md` item 6 notes these are
  one-shot chat messages, not approved templates — *"production
  business-initiated outreach needs approved templates or Meta will
  rate-limit/ban the number."* A viewer could conclude the demo's broadcast
  pattern is production-ready on the live API. One closing-card line or
  narration clause would cover it.

### m5. Small precision nits (noted for completeness; no action strictly required).

- customer-en @ ~0:00: *"That message hits BiteFlow's webhook"* — the demo
  drives `process_incoming` via `FakeWhatsAppClient`, not an HTTP webhook.
  The closing card ("local run") covers the substance; "webhook" is a mild
  gloss of the real entry point. Fine as-is, but "hands it to the state
  machine" would be the precise phrasing.
- customer-en @ ~3:31: *"the cook is collecting those seventeen dollars in
  cash at the door right about now"* — framed as hypothetical ("in a real
  kitchen"), acceptable.
- BRIEF.md notes BiteFlow v0.1.0 is released as **"Enterprise-hardened
  pilot"** while its own SECURITY.md lists webhook-signature validation,
  idempotency, and rate limiting as must-fix-before-money blockers. The label
  is on the GitHub release, not in the videos — but if the release notes or
  videos ever travel together, "enterprise-hardened" will be read against
  those three open gaps. Consider renaming the release tag.

---

## Rubric answers

**1. Claim audit.** Verdicts per video (timestamps approximate):

- *biteflow-customer-en.mp4*: webhook→state-machine flow (verified, m5 caveat);
  global language command (verified — `state_machine.py` pre-dispatch);
  user row keyed by phone (verified); live menu fetch per view (verified —
  `get_active_menus` on every render); single-digit qty parser (verified);
  "no commission, touches no money, P2P" (verified in code; **M2** caveat on
  trust-based verification); opt-in-gated broadcasts (verified); genuine push
  on status taps (verified, simulated-client caveat on closing card);
  cancel-at-review writes nothing (verified — `handle_review` returns before
  `create_order`); "real home kitchen" premise (**M1**); manifest "card"
  option (**M4** — does not exist).
- *biteflow-cook-mr.mp4*: Marathi selection flow incl. pre-selection English
  (verified, disclosed on-mic); dollar price entry with invalid-input
  re-prompt (verified); no on/off toggle — honest on-mic limitation
  (verified, contradicts manifest's "live/offline toggle" — **M4**); real
  new-order push (verified); status flow (verified); P&L from real completed
  order with zeroed food cost disclosed (verified, honest); **on-mic
  disclosure that Business/Finance is English-only fallback** (~2:32 —
  exemplary); "no platform commission" (verified); decline + fallback
  (verified); USD on closing card (verified, good).
- *roomlens-prospect-mr.mp4*: भाषा from any screen + persistence (verified —
  the fixed regression); graceful invalid input (verified); free preview
  (verified — engine copy says "free!"); photo quality gate, "a bad preview
  is never made" (verified — `assess_quality` rejects, retake guidance,
  counterfactual honored); tips opt-in (verified); preset compositing "not
  true AR" said on-mic (~1:30) and on closing card (verified, honest);
  "exact bytes" (verified); **synthetic inputs presented as "your own room"
  (M3)**; **commission-is-the-business-model claim (B1 — false)**;
  **money-moment claim (B2 — no payment rail)**; "all in Marathi" closing
  boast (overbroad — m1).
- *roomlens-designer-en.mp4*: designer row + catalog + photo to local storage
  (verified); gibberish re-prompt + product deactivation (verified); "real
  prospect — a second phone in this demo" (framed as demo, acceptable);
  photo quality check (verified); "genuine engine output, not a mock" ping
  (verified); Pillow/NumPy compositing + "not true augmented reality"
  (verified, honest); **"when money moves: the prospect's payment becomes the
  designer's fee" (B2 — false)**; "no platform commission accounting… I will
  not invent a cut" (verified, honest — and the direct contradiction of the
  prospect-mr video, B1).

**2. Public-embarrassment test.** A journalist asks: who inspects these home
kitchens (M1); what stops a forged Zelle screenshot from marking an order
paid (M2); why is a cook's personal phone number the menu title (m3). A
regulator asks: where does the prospect's payment actually go (B2); what is
RoomLens's cut, since your own videos disagree (B1). A Marathi viewer asks:
why is the price in dollars, and why is the disclaimer in English (m1, m2).

**3. Disclosure sufficiency.** The closing-card line ("Simulated WhatsApp
client · local run · not the live Meta API") is necessary but not sufficient.
It covers the simulation question. It does not cover: USD prices on the
prospect-mr video (missing from that card entirely), synthetic input photos
(M3), trust-based payment verification (M2), or the English-fallback leaks
"Total"/"received" (LEAKS.md only). The cook-mr video is the model: it
discloses the English fallback **on-mic at the moment it appears** (~2:32)
and puts USD on its card. Replicate that pattern at each point of
misrepresentation rather than relying on a sidecar file.

**4. The word "AI."** It never appears — not in any narration script, not in
any on-screen banner I sampled, not in `manifest.json`, not in LEAKS.md.
The videos say "state machine," "compositing engine," "Pillow and NumPy,"
and explicitly *"preset compositing, not true augmented reality."* Every
use (and non-use) is defensible; the absence of AI-washing is a genuine
strength of this pack. Keep it that way.

**5. LEAKS.md honesty.** The audit itself is thorough and candid (it even
keeps the already-fixed lint failure in the GitHub screenshots — good). But
its disclosures live in a sidecar, and the claim "disclosed on the video's
closing card" is only true for the cook-mr video's USD note. In-video
disclosure status: English fallback in cook business section — disclosed
on-mic ✓; USD in cook-mr — on closing card ✓; USD in prospect-mr — **not in
the video** ✗; "Total"/"received" leaks — **not in any video** ✗; synthetic
inputs — **not in any video** ✗. A viewer never opens LEAKS.md. Move the
material ones into the videos.

---

## What must change before public sharing

1. **Re-record or re-cut roomlens-prospect-mr.mp4 @ ~2:23**: remove the
   platform-commission-as-business-model claim; align with the designer-en
   disclosure (no commission accounting in this build). (B1)
2. **Fix the money-movement language in both RoomLens videos** (~2:11
   designer-en, ~2:23 prospect-mr): no payment rail exists; say how the
   designer actually gets paid or say nothing. (B2)
3. **Add an in-video synthetic-inputs note** to roomlens-prospect-mr.mp4
   (sample room/product photos) — one line, on-mic or on-card. (M3)
4. **Fix the two manifest.json descriptions** ("card" checkout option;
   "live/offline toggle"). (M4)
5. **Decide the BiteFlow food-safety story** before public launch: either add
   a vetting/compliance disclosure to the video or accept the press risk
   explicitly. Do not ship M1 on accident. (M1)
6. **Disclose trust-based P2P verification in-video** (one line at the
   payment screen, ~2:06 customer-en). (M2)
7. Smaller: add the USD line to the prospect-mr closing card; translate (or
   at least subtitle) closing cards and step banners for the Marathi videos;
   soften "सगळं मराठीत." (m1, m2)

Nothing above requires re-running the demos — the engines are honest; it is
the narration and packaging that need the work.
