# CHANGELOG — v1 → v2 walkthrough videos

Every change mapped to the persona finding that caused it (finding IDs from
`reviews/v1/*.md`, triage IDs from `reviews/TRIAGE.md`). v1 files kept
untouched; v2 files are `*-v2.mp4`.

## biteflow-customer-en (v1 319.5s → v2 350.2s)

| Change | Finding → Triage |
|---|---|
| Step 8 narration rewritten: removed the "switch to the cook's phone / second chat on the right" lines; now describes only the customer-side status pushes actually shown | QA M2 → A8 |
| All step captions re-rendered with safe margins (no longer cover the chat header) | QA M3 → A6 |
| Steps 12–13 frames re-rendered through the working emoji path (tofu boxes fixed) | QA M5 → A7 |
| Payment step: added "the cook approves a screenshot — cook-verified, not bank-verified" | TechLead B2, Board M2, VC M1 → A3 |
| "Every cook nearby" → "every cook with an active menu" | SrEng → A9 |
| Added food-safety disclosure: demo only; real deployment needs cottage-food / food-safety compliance | Board M1 → A10 |
| Closing card: "webhook signature validation, idempotency, and rate limiting not yet implemented" | TechLead M1 → A11 |
| Broadcast opt-in: "production broadcasts need approved Meta templates" | TechLead M6, Board m4 → A12 |
| Money moment: "no commission in this build; the business-owner addendum (P&L, marketing hub) is the planned paid layer — pricing not set" | VC B2 → A13 |
| Cook-number clause: "test numbers shown; a real pilot needs a privacy design" | Board m3, PM M4 → A18 |
| NEW branches driven through the real engine: empty-cart checkout guard; STOP opt-out demo | QA m1 → A20 |
| Reworded "cutout image", digest "sends" (no cron in repo), gross-vs-net reconciliation | SrEng minors → A22 — PARTIAL: gross-vs-net and "cutout" rewords applied where re-recorded; v2 re-review found the designer-en "cutout image" line (Step 2, s2 not re-recorded) and the cook-mr digest "sends" opening ("रोजचा नफा-तोटा पाठवतं") unchanged. Corrected 2026-09-06 via surgical narration patch (audio re-synthesized with the exact v1 voice, video frames untouched): roomlens-designer-en-v2.mp4 Step 2 now says the backend saves the raw photo as-is with no background removal; biteflow-cook-mr-v2.mp4 digest step now says the P&L report is generated on demand and a real deployment needs an external scheduler. Both v2 files re-verified same day. |

## biteflow-cook-mr (v1 213.7s → v2 232.4s)

| Change | Finding → Triage |
|---|---|
| All step captions re-rendered with safe margins (v1 yellow band covered menu options, price prompt, Finance items, order 🔔 line) | QA M3 → A6 |
| Money moment (Marathi): no commission in this build; business-owner addendum is the planned paid layer, pricing not set | VC B2 → A13 |
| P&L reframed: "demo data from this session's completed order" | VC M3 → A14 |
| Technical-jargon sentences re-recorded in plain Marathi (यादीत नोंद होते, संदेश आपोआप जातो…) | Ext M7 → A15 |
| Closing card bilingual (Marathi + English); added "Business/Finance section not yet in Marathi (English fallback)" | Board m1, Ext B1 → A16 |
| Emoji glyph re-render (🍳/👍/👎) where the pipeline allowed | QA m2 → A21 |

## roomlens-prospect-mr (v1 191.8s → v2 212.3s)

| Change | Finding → Triage |
|---|---|
| n7 re-recorded: commission-as-business-model claim REMOVED; now "या आवृत्तीत प्लॅटफॉर्म कमिशनचा हिशोब नाही — हा व्यवसाय निर्णय अजून बाकी आहे" (matches code + designer-en) | VC B1, Board B1, SrEng, TechLead B1, PM B1 → A1 |
| Money-moment re-recorded: booking writes the order + notifies the designer; no in-app payment — designer paid directly, off-platform | Board B2, SrEng, VC → A2 |
| Synthetic-media disclosure: on-mic line at photo step + closing-card "Demo uses sample room & product photos" | QA B1, Board M3, PM B2, Ext M5 → A4 |
| Captions re-rendered with safe margins; viz sub-caption no longer clipped | QA M3, QA m3 → A6 |
| Technical-jargon sentences re-recorded in plain Marathi | Ext M7 → A15 |
| Closing card bilingual; "सगळं मराठीत" boast softened | Board m1 → A16 |
| Closing card: "Prices shown in USD (real engine behavior)" (+ Marathi) | Board m2 → A17 |
| "Immediately pushes" → honest timing language | TechLead M5 → A19 |
| NEW branch: option 4 "talk to the designer" driven through the real engine | QA m1, PM M2 → A20 |
| Booking: "पैसे डिझायनरशी थेट ठरतात" (payment arranged directly with the designer) | Ext M6 → A23 |

## roomlens-designer-en (v1 187.5s → v2 200.4s)

| Change | Finding → Triage |
|---|---|
| s7 re-recorded: "money moves / prospect's payment becomes the designer's fee" REMOVED; now: the tap writes an order row and notifies the designer; no in-app payment — designer paid directly, off-platform. s8 no-commission line kept; both videos now agree | Board B2, SrEng, VC → A2 |
| Synthetic-media disclosure: on-mic line at viz step + closing card | QA B1, Board M3 → A4 |
| Bottom captions re-rendered with safe margins; step-8 clipped caption fixed | QA M3 → A6 |
| Closing card: webhook hardening gaps line | TechLead M1 → A11 |
| Marketing beat: approved-template clause | TechLead M6 → A12 |

## Deliberately NOT changed (see TRIAGE.md R1–R8)

- RoomLens viz inputs still synthetic (disclosed instead of faked) — R1
- Marathi locale strings untouched: "उघड्या ऑर्डरी", "Total", "received", "परफेक्ट", "किचन", "उत्पादन", "(COD)" — product backlog, verbatim-output rule — R2
- No commission/payment code added; no invented take rate or unit-economics numbers — R3, R4
- USD single currency kept, disclosed — R5; no live/offline toggle — R6
- "Enterprise-hardened pilot" release tag kept — recommended to owner — R7
- No designer SLA / feedback-loop ops design — R8
