# VC Review — v1 Walkthrough Videos
**Role:** Business case (monetization, unit economics, moat, market)
**Reviewer verdict:** ❌ **NEEDS WORK**
**Date:** 2026-09-05
**Files reviewed:** `biteflow-customer-en.mp4`, `biteflow-cook-mr.mp4`, `roomlens-prospect-mr.mp4`, `roomlens-designer-en.mp4`, narration scripts under `work/*/`, `~/workspace/biteflow` (README, docs, `src/payments.py`, `src/owner/economics.py`, `SECURITY.md`), `~/workspace/roomlens` (README, `docs/FAQ.md`, `src/pricing.py`, `src/handlers/`)

---

## The one-line money story per video (rubric test 1)

| Video | "How does the company make money?" after watching |
|---|---|
| BiteFlow — customer (EN) | **No answer.** Explicitly disavows: "BiteFlow takes no commission and touches no money." (~2:06) No alternative revenue stream is named. |
| BiteFlow — cook (MR) | **No answer.** Reaffirms: "या इंजिनमध्ये प्लॅटफॉर्म कमिशन नाही" — no platform commission (~2:32). Still no revenue stream named. |
| RoomLens — prospect (MR) | **Claims:** "बुकिंग झालं की डिझायनरची फी ठरते, आणि त्यावर प्लॅटफॉर्मचं कमिशन — हेच रूमलेन्सचं बिझनेस मॉडेल" (~2:30) = platform takes commission on the designer's fee; that IS the business model. |
| RoomLens — designer (EN) | **Contradicts the above:** "There is no platform commission accounting in this version of the code, so I will not invent a cut — that is a business decision the team still has to make." (~2:32) |

Two videos, two companies, two money stories — and the RoomLens pair directly contradicts itself. Repo code confirms zero commission logic exists anywhere (`src/pricing.py` computes quotes only; README/FAQ silent on revenue). The honest video is the English designer one; the Marathi prospect video asserts a business model the code doesn't implement.

---

## BLOCKERS

### B1. RoomLens: the two videos tell investors two different business models
- **Timestamps:** `roomlens-prospect-mr.mp4` ~2:30–2:52 (Step 7, `work/roomlens-prospect-mr/narr/n7.txt`); `roomlens-designer-en.mp4` ~2:32–2:54 (Step 8, `work/roomlens-designer-en/audio/s8.txt`).
- **What happens:** The Marathi prospect narration states as fact: *"बुकिंग झालं की डिझायनरची फी ठरते, आणि त्यावर प्लॅटफॉर्मचं कमिशन — हेच रूमलेन्सचं बिझनेस मॉडेल"* ("once booked, the designer's fee is set, and on that the platform's commission — this is RoomLens's business model"). Twenty seconds later in the English designer video, the narrator explicitly says no commission exists in the code and "I will not invent a cut."
- **Business question:** What is the take rate? If it's undecided, neither video may present one as settled. An investor doing diligence against the repo (there is no `commission` in `src/`, README, or FAQ) will conclude the Marathi video invented a revenue model — a credibility hit on everything else it says.
- **Evidence:** `grep -ri commission src/ --include='*.py'` in `~/workspace/roomlens` → zero hits. `docs/FAQ.md` Q6 ("How do pricing and quotes work?") describes quote math with no mention of any platform cut.

### B2. BiteFlow: the video disavows monetization and names no alternative
- **Timestamps:** `biteflow-customer-en.mp4` ~2:06–2:41 (Step 7, `work/biteflow-customer-en/narr/s07.txt`); `biteflow-cook-mr.mp4` ~2:32–3:06 (Step 6, `work/biteflow-cook-mr/audio/scripts/step6.txt`).
- **What happens:** The English narration says, precisely: *"BiteFlow takes no commission and touches no money. Payment moves directly from customer to cook, peer to peer."* The Marathi cook narration agrees (*"या इंजिनमध्ये प्लॅटफॉर्म कमिशन नाही"*). Neither video ever names how BiteFlow itself earns anything — no subscription, no fee, no ads, no cost pass-through.
- **Business question:** Who pays BiteFlow and for what? The repo contains the answer's seed — the business-owner addendum (Business hub 📊: P&L, food-cost math; Marketing hub 📣: broadcast campaigns) — which is the natural SaaS/upsell layer, but the videos never connect it. The honest "we don't touch the money" moment (~2:06) was exactly where the monetization line belonged.
- **Compounding hole:** Both repos' docs acknowledge WhatsApp's per-24h-conversation billing from Meta (RoomLens `docs/FAQ.md` Q11; the marketing hub's broadcast campaigns generate exactly those charges). The videos never say who pays Meta. A VC will notice the platform's main variable cost is invisible in the money story.

---

## MAJORS

### M1. P2P "payment approval" is a claim, not verified funds — the video never says so
- **Timestamp:** `biteflow-customer-en.mp4` ~2:06–2:41 (Step 7).
- **What happens:** "The customer pays the cook over Zelle or UPI, then sends a screenshot for the cook to approve. Still no middleman." An investor watches a payments workflow where a screenshot tap = settlement.
- **Repo truth:** `~/workspace/biteflow/SECURITY.md` item 4: "P2P payment 'verification' is trust-based. A screenshot or typed reference is accepted as a claim; nothing is checked against a bank, and media bytes are never downloaded." The repo FAQ repeats it.
- **Business question:** What's the fraud surface? Fake screenshots, typed fake references, and no recourse are the single biggest unit-economics risk in a P2P food marketplace — and the video's money moment presents the flow without the caveat. (The video is otherwise admirably honest about what's simulated; this is the one money claim that isn't caveated.)
- **Note:** The COD moment (~3:30) is fine — "in a real kitchen, the cook is collecting those seventeen dollars in cash at the door right about now" correctly frames it as hypothetical.

### M2. No unit economics anywhere: no numbers, no costs, no CAC, no take rate
- **Across all four videos.** Not one gives a commission %, a fee per order, a per-conversation cost, CAC, or a margin. The only numbers in any video are order totals ($17, $189) — which are the *cook's/designer's* money, not the platform's.
- **What should have been said:** take rate (even as "planned: X%"), WhatsApp per-conversation cost as the main variable cost, contribution margin per order, and what the Marketing-hub broadcasts cost the cook. Every video has a natural slot (the money moment) and none uses it.

### M3. The daily P&L digest frames one demo order like live business data
- **Timestamp:** `biteflow-cook-mr.mp4` ~2:12–2:32 (Step 5).
- **What happens:** "दिवस संपताना बाइटफ्लो रोजचा नफा-तोटा पाठवतं. हे आकडे काल्पनिक नाहीत — खऱ्या पूर्ण झालेल्या ऑर्डरवरून काढलेले आहेत" ("at day's end BiteFlow sends the daily P&L. These numbers are not imaginary — they're from real completed orders"). Revenue $17, food cost $0, net profit $17.
- **Business question:** Is this traction or a demo fixture? "Real completed orders" is technically true (real engine rows from the simulated session) but an investor hears "real orders." The 100% margin exists only because food cost was never logged — disclosed, but buried mid-sentence, and "रोजचा" (daily) implies a cadence of real business. Calling it "demo data from this session's order" would defuse it.

### M4. Moat: neither video shows anything defensible — and the honest disclaimers prove it
- **BiteFlow:** The tech story (declarative state machine, strict digit parsers, locale parity, graceful fallbacks) is genuinely good engineering, but it's a weekend rebuild for any competent engineer. The actual hard parts of a home-cook marketplace — cottage-food licensing and health compliance (home kitchens selling food is regulated; California MEHKO and equivalents), cook acquisition and trust, delivery ops, P2P fraud — appear in neither video. A VC's first question will be "what's the regulatory story?" and the videos give them nothing.
- **RoomLens:** The videos are honest that compositing is "preset compositing, not true AR" (prospect-mr Step 4b; designer-en Step 5 + end card) — to its credit. But that honesty underscores that the IP is Pillow paste at four fixed presets: trivially rebuildable. The defensible part would be designer supply, catalog, and fulfillment relationships — none of which the videos demonstrate or even name.
- **Platform risk (both):** 100% WhatsApp dependency — per-conversation pricing changes and number bans are existential. The repo's own SECURITY.md notes Meta will rate-limit/ban numbers without approved templates. Not mentioned in any video; a VC will ask.

---

## MINORS

### m1. Manifest overclaims a payment method that doesn't exist
- **Location:** `walkthrough-videos/manifest.json`, biteflow-customer-en description: "checkout with UPI/card/COD."
- **Fact:** The video and repo (`src/payments.py`) support COD and P2P transfer (Zelle/Venmo/UPI/Pix) only — no card payment exists anywhere. Investor-facing copy should not invent payment rails.

### m2. "Free preview" without saying who pays
- **Timestamp:** `roomlens-prospect-mr.mp4` ~0:20 (Step 2): "हा प्रीव्यू अगदी मोफत आहे, किंमत फक्त वस्तूची" ("this preview is completely free, you only pay for the item").
- **Question:** Free to the prospect, but each message round-trip costs the *operator* a Meta conversation fee, and the designer's time is real labor. For the business case, "free preview" needs its cost-of-acquisition frame.

### m3. Currency context for the Marathi business story
- All money claims in the Marathi videos are in USD ($17 cook payout, $189 chair) — real engine behavior, disclosed on closing cards. But a commission-based business model asserted in USD to a Marathi audience muddles the market story: is the target market India (UPI, ₹) or the US diaspora? The business case needs a stated market; right now the money story floats between them.

---

## Market: "who pays and why" — verdict per product

- **BiteFlow / home cooks:** The cook's incentive is crystal clear (keep 100%, zero commission — the video's strongest honest line). The *company's* revenue is unexplained, so "who pays BiteFlow" has no answer. A cook-side SaaS (the Business/Marketing hubs) is the obvious story and the repo already builds it — but the video never says it. **Not credible as a business case until named.**
- **RoomLens / interior designers:** Incoherent across the two videos — one says the designer keeps the full $189 and commission is undecided; the other says commission on the designer's fee is the business model. An investor can't tell who pays RoomLens or how much. **Not credible until the contradiction is resolved.**
- Both products share one credible demand-side insight the videos *do* establish: zero-install WhatsApp flows remove the onboarding tax for non-tech-savvy users (seniors, Marathi-speaking cooks). That's a real wedge — but a wedge is not a business model.

## Bottom line

The videos are honest about what's simulated (end cards), honest about preset compositing, and honest that commission is undecided in the English RoomLens cut — which makes the two money-story failures (B1's cross-video contradiction, B2's monetization vacuum) the only things standing between these videos and a shippable investor narrative. Fix: decide the take rate (or explicitly label it "planned"), make both RoomLens videos tell the same story, and give BiteFlow one named revenue stream with one number. Nothing in the tech needs changing — this is a narration-only repair.
