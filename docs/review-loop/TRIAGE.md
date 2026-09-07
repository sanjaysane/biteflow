# TRIAGE — v1 reviews → v2 fixes

All 7 personas returned **NEEDS WORK**. 9 blockers, ~25 majors, ~25 minors.
Rule applied: fix in v2 what the video can fix (narration, captions, frames,
manifest, disclosures). Real code/product limitations get honest in-video
disclosure, never silent fixes and never faked engine output.

## Accepted — fixed in v2

| ID | Finding (personas) | Fix |
|---|---|---|
| A1 | RoomLens videos contradict each other on platform commission (VC B1, Board B1, SrEng blocker, TechLead B1, PM B1) | Re-record prospect-mr n7 to match code truth: no commission accounting in this build; business decision pending |
| A2 | "Money moves / prospect's payment" with no payment rail in RoomLens (Board B2, SrEng major, VC) | Re-record both RoomLens money segments: booking writes an order row + notification; designer is paid directly/off-platform; no in-app payment |
| A3 | P2P "verified / Payment approved" vs trust-based screenshots (TechLead B2, Board M2, VC M1) | One-line narration disclosure at BiteFlow payment step: cook-verified from screenshot, not bank-verified |
| A4 | Synthetic room/chair presented as "your own room" (QA B1, Board M3, PM B2, Ext M5) | In-video disclosure (on-mic + closing card): "demo uses sample photos"; compositing engine claim stays (verified true) |
| A5 | manifest.json overclaims: "card" checkout, "reorder", "live/offline toggle", "services/pricing" (QA M1, Board M4, PM M1, SrEng) | Correct all four descriptions to match engine reality |
| A6 | Step captions overlap/obscure chat content (QA M3) | Re-render all captions with safe margins; fix clipped captions (designer-en s8, prospect-mr viz sub-caption) |
| A7 | Tofu emoji boxes in customer-en steps 12–13 (QA M5) | Re-render those frames through the working emoji path |
| A8 | customer-en Step 8 narration describes a cook-side phone view that never appears (QA M2) | Rewrite narration to match the single-phone visual |
| A9 | "Every cook nearby" — no geo logic in code (SrEng) | Reword to "every cook with an active menu" |
| A10 | "Real home kitchens" with zero food-safety framing (Board M1) | One-line disclosure: demo only; real deployment needs cottage-food / food-safety compliance |
| A11 | Webhook hardening gaps undisclosed (TechLead M1, Board m5) | Closing-card line: signature validation, idempotency, rate limiting not yet implemented |
| A12 | Broadcast opt-in omits approved-template requirement (TechLead M6, Board m4) | One clause: production broadcasts need approved Meta templates |
| A13 | BiteFlow names no revenue stream (VC B2) | Honest line: no commission in this build; business-owner addendum (P&L, marketing hub) is the planned SaaS layer — pricing not set. No invented numbers |
| A14 | P&L "real completed orders" sounds like traction (VC M3) | Reframe: "demo data from this session's completed order" |
| A15 | Marathi narration uses technical jargon seniors won't know (Ext M7) | Re-record affected sentences in plain Marathi (यादीत नोंद, संदेश आपोआप जातो…) |
| A16 | Closing cards/banners English-only on Marathi videos; "सगळं मराठीत" overbroad (Board m1, Ext minor) | Bilingual closing cards; soften the boast |
| A17 | USD note missing from prospect-mr closing card (Board m2) | Add "Prices shown in USD (real engine behavior)" to that card |
| A18 | Cook phone numbers as menu titles/payee IDs, undisclosed privacy trade-off (Board m3, PM M4) | One narration clause: numbers shown are test numbers; real pilot needs privacy design |
| A19 | "Immediately pushes" vs measured webhook latency (TechLead M5) | Soften to honest timing language |
| A20 | Skipped cheap branches: empty-cart checkout, STOP demo, prospect "talk to designer" (QA m1, PM M2) | Add the engine-real branches: empty-cart guard, STOP opt-out demo, option-4 designer contact |
| A21 | Wrong emoji glyphs (🍳→magnifier, 👍→👆) (QA m2) | Re-render with correct emoji font where cheap |
| A22 | "Cutout image" overstates catalog flow; digest "sends" implies cron; gross-vs-net reconciliation (SrEng minors) | Reword each to match code |
| A23 | RoomLens booking never says how the prospect pays (Ext M6) | Covered by A2: "payment arranged directly with the designer" |

## Rejected / deferred — with reasons

| ID | Finding | Decision |
|---|---|---|
| R1 | Re-shoot viz with realistic photos (PM B2, Ext M5) | **Rejected.** Would misrepresent the demo. Disclosure (A4) is the honest fix; visual quality is a product-media backlog item |
| R2 | Fix Marathi locale strings in-repo: "उघड्या ऑर्डरी"→"चालू ऑर्डरी", "Total"→"एकूण", "received"→Marathi, "परफेक्ट"→"छान", "किचन"→"स्वयंपाकघर", "उत्पादन"→"वस्तू", "(COD)"→"(रोख)" (Ext M1–M4, minors) | **Deferred to product backlog.** v2 cannot show corrected text without violating the verbatim-engine-output rule. Filed in RELEASE.md next-milestone |
| R3 | Add commission/payment rails to the code | **Rejected.** Product/business decision, out of video scope. Videos now tell the truth about their absence |
| R4 | Name a take rate / unit-economics numbers (VC M2) | **Rejected.** Will not invent numbers. "Not yet set" disclosure (A13) instead |
| R5 | INR pricing (Ext B2) | **Rejected.** Single-currency USD is real engine behavior; disclosed (A17). Multi-currency is product backlog |
| R6 | Cook live/offline toggle (PM B3) | **Rejected.** No such feature in code; already disclosed on-mic. Product backlog |
| R7 | Rename "Enterprise-hardened pilot" release tag (Board m5) | **Recommended to owner, not done in v2.** Repo change outside video scope; flagged in RELEASE.md |
| R8 | Full human-designer SLA / feedback-loop closure (PM M2) | **Rejected.** Ops/product design question; noted as limitation in RELEASE.md |

## Net v2 work per video

- **biteflow-customer-en:** A5, A6, A7, A8, A9, A10, A11, A12, A13, A18, A20 (empty cart, STOP), A22
- **biteflow-cook-mr:** A5, A6, A13, A14, A15, A16, A21
- **roomlens-prospect-mr:** A1, A2, A4, A5, A6, A15, A16, A17, A19, A20 (option 4), A23
- **roomlens-designer-en:** A2, A4, A6, A11, A12
