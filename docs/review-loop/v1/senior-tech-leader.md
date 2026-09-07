# Senior Technical Leader review — v1 walkthrough videos
## BiteFlow + RoomLens production-readiness & disclosure audit

Reviewer: Senior Technical Leader (swarm seat). Date: 2026-09-05.
Scope: `biteflow-customer-en.mp4` (319.5s), `biteflow-cook-mr.mp4` (213.7s),
`roomlens-prospect-mr.mp4` (191.8s), `roomlens-designer-en.mp4` (187.5s),
both repos' READMEs / SECURITY.md / docs, plus `LEAKS.md` and
`sharing-session/BRIEF.md` as the known-limitations checklist.

Method: narration scripts under `work/*/audio`, `work/*/narr` are the
verbatim spoken track; segment boundaries were measured with ffprobe and
cumulative durations, so timestamps below are ±1s. Code claims checked
against `src/`, `SECURITY.md`, and `docs/ARCHITECTURE.md` §10.

**Verdict: NEEDS WORK**

---

## Blockers

### B1 — RoomLens prospect (Marathi) asserts a platform-commission business model that does not exist in the code
- **Where:** `roomlens-prospect-mr.mp4` ≈ **2:22–2:44** (narration n7):
  "बुकिंग झालं की डिझायनरची फी ठरते, **आणि त्यावर प्लॅटफॉर्मचं कमिशन —
  हेच रूमलेन्सचं बिझनेस मॉडेल**" ("once booked, the designer's fee is
  fixed, and on top of it platform commission — that is RoomLens's
  business model").
- **Why it's a blocker:** The codebase has zero commission accounting, zero
  fee model, and zero payment processing — confirmed by grep: no
  `commission`, no `fee`, no `payment` anywhere in `roomlens/src`. Worse,
  this directly contradicts the *sibling* video: `roomlens-designer-en.mp4`
  ≈ **2:38–3:00** (s8) honestly states *"There is no platform commission
  accounting in this version of the code, so I will not invent a cut."*
  A prospect or investor who watches only the Marathi video walks away
  believing commission revenue exists; a viewer who watches both sees the
  company contradict itself on money.
- **Disclosure demanded:** Replace the n7 claim with an on-screen +
  narration line aligned with the designer video's honest note, e.g.:
  "या आवृत्तीत कमिशन गणना नाही — फी आणि पेमेंट सध्या हाताने हाताळली जातात"
  ("This version has no commission accounting — fees and payments are
  handled manually"). Do not rely on the closing card; the misleading claim
  must be corrected at the point where money is discussed.
- **Not covered by closing card:** the closing card only discloses the
  simulated client and preset compositing — nothing about money.

### B2 — BiteFlow cook video labels trust-based P2P approvals "verified"
- **Where:** `biteflow-cook-mr.mp4` ≈ **2:32–3:07** (step7, COD vs P2P
  screen), bot message: *"🤝 COD vs P2P (completed, last 7 days): •
  COD: $17.00 collected, $0.00 still out • **P2P: $0.00 verified**,
  $0.00 awaiting proof review"*.
- **Why it's a blocker:** `SECURITY.md` #4 and `docs/ARCHITECTURE.md` §10
  state plainly: *"P2P proof is trust-based: a screenshot is accepted as
  evidence, and `media_id`s are not downloaded/inspected"* / *"Media bytes
  are never downloaded."* The engine's own label — "verified" — will make
  a cook believe the system verified settlement against a bank. This is a
  mislabeled-state problem, not just a video problem; the video must not
  ship showing it unannotated.
- **Disclosure demanded:** On-screen text during step7: "P2P 'verified' =
  the cook approved a screenshot on trust; nothing is checked against a
  bank" (matches README: "Treat P2P screenshots as claims, not settled
  funds").
- **Not covered by closing card:** nothing about payments on any closing card.

---

## Major

### M1 — No video discloses the webhook hardening gaps; the release branding actively invites a production-safe misread
- **Where:** all four videos, esp. closing cards at ≈ 5:22 (customer),
  3:33 (cook), 3:10 (prospect), 3:00 (designer).
- **The gaps:** no `X-Hub-Signature-256` validation on inbound webhooks
  (biteflow `SECURITY.md` #1: "the single most important thing to fix
  before going live"; roomlens `SECURITY.md` "Known gap"), no
  idempotency/dedup on inbound `wamid`s (a redelivered "accept" is processed
  twice), no rate limiting on `/webhook`, no auth on endpoints beyond the
  verify token. Both READMEs carry an "Operational cautions" /
  "Deliberate simplifications" section saying do not run real traffic yet.
- **The misleading surface:** the closing cards say "Simulated WhatsApp
  client · local run · not the live Meta API" — which a viewer reads as
  "the product itself is fine, only the client was simulated." Combined
  with `BRIEF.md`'s note that the BiteFlow v0.1.0 release is titled
  **"Enterprise-hardened pilot"** and the GitHub proof shots showing green
  CI/CodeQL, a viewer can reasonably conclude this is production-hardened.
  None of the nine BRIEF-known limitations (no signature validation, no
  dedup/rate limiting, trust-based payment screenshots, single currency,
  flat cook discovery, media-not-persisted, simplified P&L, exact-name
  recipe matching, external scheduling) appear in any video.
- **Disclosure demanded:** Append to **all four** closing cards:
  "Demo build — webhook signature validation, message dedup, and rate
  limiting not yet implemented. Do not handle real money-adjacent traffic."
  The "Enterprise-hardened pilot" framing must not stand next to these
  videos without that caveat.

### M2 — RoomLens designer video says "money moves" when no payment processing exists
- **Where:** `roomlens-designer-en.mp4` ≈ **2:16–2:38** (s7):
  *"This is the business-model moment when money moves: the prospect's
  payment becomes the designer's fee."*
- **Why it matters:** No payment is processed, collected, or routed by
  RoomLens — the order row is a record; settlement happens entirely
  outside the product. A viewer could infer the platform moves money.
  The s8 honest note (no commission accounting) does not cover this.
- **Disclosure demanded:** On-screen line during s7: "No payments are
  processed in-app in this version — settlement happens outside the product."

### M3 — BiteFlow customer video implies geo-nearby cook discovery; it is a flat list
- **Where:** `biteflow-customer-en.mp4` ≈ **0:49–1:10** (s03):
  *"Then the bot lists every cook **nearby** with a live menu."*
- **Why it matters:** `docs/ARCHITECTURE.md` §10: *"Cook discovery is a
  plain list; no search, geo, ratings, or scheduling."* The demo list shows
  a single cook identified by raw phone number. At 100x cooks this is an
  unusable phone-book list, and "nearby" is a claim about proximity
  filtering the code does not implement.
- **Disclosure demanded:** On-screen during s03: "Cook discovery is a flat
  list in this version — no search, distance, or ratings."

### M4 — BiteFlow customer video describes P2P screenshot approval without saying it is trust-based
- **Where:** `biteflow-customer-en.mp4` ≈ **2:10–2:46** (s07):
  *"Phone transfer works the same way — the customer pays the cook over
  Zelle or UPI, then sends a screenshot for the cook to approve. Still no
  middleman."*
- **Why it matters:** Accurate about the flow, silent about verification.
  A viewer can infer BiteFlow verifies the Zelle/UPI payment before the
  cook approves. It does not — nothing is checked against any bank.
- **Disclosure demanded:** On-screen during s07: "P2P payments are verified
  on trust only — BiteFlow does not confirm funds." (Same README line as
  B2: "Treat P2P screenshots as claims, not settled funds.")

### M5 — RoomLens prospect video implies the preview pipeline is instantaneous; renders are synchronous in the webhook path
- **Where:** `roomlens-prospect-mr.mp4` ≈ **0:47–1:14** (n3):
  *"इमिडिएटली"* / "The engine quality-checks the photo, stores it, and
  **immediately** pushes a notification to the designer's phone."
- **Why it matters:** `docs/SCALE.md` (measured 2026-09-05, 50 concurrent
  users): webhook p99 2.2s / max 8.7s, single uvicorn worker, fresh DB
  connection per call, no pool — and *"the composite/render path (Pillow +
  ffmpeg)… will be the bottleneck if many visualizations render
  concurrently — pre-warm or queue renders."* At 100x concurrent renders,
  they serialize behind one worker. "Immediately" is true at demo scale,
  misleading at product scale.
- **Disclosure demanded:** On-screen during n4b1/n5 (≈ 1:24–2:13):
  "Renders run synchronously in the request path in this version — no render
  queue yet." (SCALE.md's own measured-limits line.)

### M6 — Menu-broadcast opt-in video omits that broadcasts need approved WhatsApp templates
- **Where:** `biteflow-customer-en.mp4` ≈ **2:46–3:14** (s08):
  *"That opt-in is stored in the database, and it is what lets the cook
  broadcast future menus to them."*
- **Why it matters:** `SECURITY.md` #6: *"Campaign and win-back sends are
  one-shot chat messages, not WhatsApp template messages — production
  business-initiated outreach needs approved templates or Meta will
  rate-limit/ban the number."* At 100x cooks broadcasting to 100x
  subscribers as shown, the business number gets banned. The opt-in story
  is told as complete; the template gate is hidden.
- **Disclosure demanded:** On-screen during s08: "Broadcasts need approved
  WhatsApp templates in production; the demo uses one-shot chat messages."

### M7 — "Menu fetched live on every view" has a hidden linear cost
- **Where:** `biteflow-customer-en.mp4` ≈ **1:10–1:28** (s04):
  *"Nothing is cached or stale — the menu is fetched live from the cook's
  menu table on every single view."*
- **Why it matters:** Presented as pure upside (freshness). The cost is
  hidden: the app opens a new Postgres connection per DB operation
  (serverless-safe by design), README measures ≈750ms avg webhook latency
  dominated by connection handshake, no connection pool, single worker.
  At 100x views this is linear connection-churn cost; "no cache" is a
  scalability tradeoff, not just a feature.
- **Disclosure demanded:** On-screen during s04 or on the closing card:
  "Live reads, no caching or DB pool in this version — measured baseline
  only, not load-tested beyond ~50 concurrent users." (RoomLens's SCALE.md
  already carries this honesty; BiteFlow's videos should match it.)

---

## Minor

- **N1 — Single-currency gap visible on BiteFlow, missing on RoomLens.**
  BiteFlow closing cards say "Prices shown in USD (real engine behavior)" —
  good. RoomLens shows `$189.00` throughout both videos with no currency
  note on its closing cards (prospect narration says "dollars" verbally).
  `ARCHITECTURE.md` §10 documents the single-currency assumption. Add
  "Prices in USD — single-currency model" to both RoomLens closing cards.
- **N2 — BiteFlow customer closing card lacks the USD line** that the
  cook closing card has. Same card, same fix as N1.
- **N3 — P&L digest simplification hidden.** `biteflow-cook-mr.mp4`
  ≈ 2:12–2:32 (step6): digest shows "उत्पन्न $17.00 / अन्नखर्च $0.00 /
  निव्वळ $17.00" with the honest note that recipe costs weren't logged.
  Still hidden: the P&L "treats discounts as contra-revenue and ignores
  payment fees, taxes, and waste" (ARCHITECTURE.md §10). Add on-screen:
  "Simplified P&L — excludes taxes, fees, waste."
- **N4 — "Daily P&L at day's end" implies a scheduler.** `biteflow-cook-mr.mp4`
  ≈ 2:12–2:32 (step5 narration): "दिवस संपताना बाइटफ्लो रोजचा नफा-तोटा
  पाठवतं." `src/owner/digest.py`: the digest is a pure function —
  "Called … from a scheduler/cron (one cron entry per cook, idempotency
  enforced by the caller)". No scheduler is bundled; external cron is
  required. Add to closing card: "Digest/payout scheduling needs an
  external cron — none bundled."
- **N5 — Absolute quality-gate claim.** `roomlens-prospect-mr.mp4`
  ≈ 0:47–1:14 (n3): "चुकीचं प्रीव्यू कधीच बनवलं जात नाही" ("a wrong
  preview is never made"). The gate is on-device heuristics only
  (brightness/focus/size; `assess_quality`, no third-party vision per
  SECURITY.md). "Never" overstates a heuristic. Soften to what it does.
- **N6 — Exact-name recipe matching not shown, no false impression.**
  ARCHITECTURE.md §10: recipe matching is by exact dish name; a renamed
  menu item silently skips stock consumption. Not in any video; nothing to
  retract. Candidate for a v2 disclosure card only.

---

## Compliance — checked, no false implication found

- **Food safety (BiteFlow):** the premise — "Each cook here is a real home
  kitchen, not a restaurant" (≈ 0:49–1:10, customer video) — describes the
  business model without claiming licensing, hygiene certification, or
  platform vetting. No transcript implies the digital flow satisfies a food-
  safety requirement. Caution for v2: keep it that way — never let a future
  video say "verified home cooks."
- **Payment compliance:** no video claims PCI / money-transmitter /
  regulated-payment status. The risk is omission (M2, M4), not false claims.
- **PII:** both apps log only phone + exception repr on handler errors
  (`main.py`); RoomLens SECURITY.md documents this. Video transcripts are
  synthetic fixtures (e.g. cook listed as `+15550001111`). No disclosure
  needed beyond M1's production-readiness card.

---

## BRIEF.md known-limitations checklist — visibility in the videos

| Limitation | Visible in any video? |
|---|---|
| No `X-Hub-Signature-256` validation | **Hidden** — see M1 |
| No inbound dedup / rate limiting | **Hidden** — see M1 |
| Trust-based payment screenshots | Partial: the *flow* is shown (s07 customer, step7 cook) but the *trust-based* nature is **hidden** — see B2, M4 |
| Single currency | Partial: USD shown on screen + BiteFlow closing card; **no closing-card line on RoomLens** — see N1 |
| Flat cook discovery | **Hidden** (implies "nearby") — see M3 |
| Media not persisted (BiteFlow stores only `media_id`, never bytes) | Neutral: no false impression created; P2P screenshot flow describes sending a screenshot, never claims bytes are stored |
| Simplified P&L | Partial: food-cost $0 honestly noted; tax/fee/waste exclusion **hidden** — see N3 |
| Exact-name recipe matching | Hidden but no false impression — see N6 |
| External scheduling needed | **Hidden** (implies automatic daily send) — see N4 |

The one bright spot: both videos already practice the right pattern.
`roomlens-designer-en` states the preset-compositing and no-commission
limits **in the narration at the point of claim** (s5 ≈ 1:29–2:04, s8 ≈
2:38–3:00) *and* on its closing card. `biteflow-cook-mr` honestly notes
the untranslated business menus and the missing kitchen on/off toggle in
the Marathi narration. The fixes demanded above are the same pattern
applied consistently: disclose at the claim, not only at the end.

## Recommended v2 disclosure set (closing cards + point-of-claim lines)

Per-video, minimal:
- **biteflow-customer-en:** closing card + M1 security line; s07 P2P trust
  line (M4); s03 flat-list line (M3); s04 scale line (M7); s08 template
  line (M6); add USD line (N2).
- **biteflow-cook-mr:** closing card + M1 security line; step7 "verified" →
  trust-based line (B2); step6 P&L simplification line (N3); external-cron
  line (N4).
- **roomlens-prospect-mr:** closing card + M1 security line + USD line
  (N1); **fix the n7 commission claim** (B1 — narration re-record, not just
  a card); n3 render-queue line (M5); soften "never" quality-gate claim (N5).
- **roomlens-designer-en:** closing card + M1 security line + USD line
  (N1); s7 no-payment-processing line (M2).
