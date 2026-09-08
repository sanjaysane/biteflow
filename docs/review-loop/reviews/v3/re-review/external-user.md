# v3 re-review sign-off — External User (harshest critic)

Date: 2026-09-07. Role: the external user who caught the shipped Marathi
regressions (v1's "उघड्या ऑर्डरी" joke; Zelle/Venmo/Pix on a Marathi
pilot). My findings in this round were EU B1/B2/M1/M2 + minors; the
triage accepted F-18/F-19/F-23/F-24/F-25/F-26 and deferred D-01. I do not
fix anything — I verify. Everything below was checked against the repo
state on `main`, not against the triage's summaries.

## Overall verdict: APPROVED, with one open note

The Marathi strings I flagged are genuinely fixed — natural, correct
Marathi, and I traced them through the locale file into the actual
evidence transcript the video will narrate. The video plan no longer
starts mid-thought on schema and now walks the money loop first, with
the who-pays framing up front and the honest disclosures spoken. One
note below on the D-01 deferral condition — it does not change this
verdict, but it needs a line in milestones before the pilot, not after.

## Per-fix-ID verification (my findings only)

| Fix ID | Verdict | Evidence |
|---|---|---|
| F-18 | confirmed | Plan §2 is restructured the way I demanded: the six schema frames are gone, replaced by a single 45–60 s "Marathi fix is real" beat; ≥3:00 of the 6:00 is one real customer order end-to-end from `docs/evidence/order-loop-marathi-2026-09-07.txt`; the cook's dish-listing flow (name → price → photo → ingredients → live confirmation) is shown BEFORE the customer menu frame and is "held long enough to read"; the payment beat holds "💳 ऑर्डर #4 साठी पेमेंटचा पुरावा … 1️⃣ पेमेंट मान्य करा 👍" until narration finishes with the exact honest line — "the cook approves only when the money is really in their account — screenshot is a claim, not settled funds." The claim-to-evidence map backs every narrated beat. |
| F-19 | confirmed | Plan §1 must-say carries the one-liner verbatim: "customers order for free; cooks use it free in the pilot — the platform monetizes the cook side later." |
| F-23 | confirmed | `locales/mr.json` `cook_home` now reads "2️⃣ चालू ऑर्डरी पहा 📦" — "चालू" (ongoing) is the natural word; the "उघड्या" (uncovered/naked) joke I caught in v1 is gone. The evidence transcript (Part 4) shows the corrected string on the real engine path. |
| F-24 | confirmed | `cook_registered` now reads "🎉 स्वयंपाकी म्हणून नोंदणी झाली! चला, तुमचं स्वयंपाकघर सुरू करूया." — "स्वयंपाकघर" is what a real person writes, not "किचन". The transcript (Part 1) shows it verbatim. |
| F-25 | confirmed | Marathi `p2p_instructions`: "कृपया {cook} ला {total} UPI ने पाठवा" — UPI only, no Zelle/Venmo/Pix anywhere in the Marathi payment strings. `payment_title`: "2️⃣ फोनवरून पेमेंट (UPI) 📱". `en.json` keeps the multi-rail list for the US context (verified, unchanged). The register is natural — "स्क्रीनशॉटचा फोटो पाठवा" mirrors how the English string and real users both phrase it. |
| F-26 | confirmed | Plan §5 build notes: warm, non-technical Marathi for UI-quoting beats; explicit ban on "डेटाबेस/स्टेट मशीन/बॅकएंड" in voiceover where a senior would hear it ("सिस्टीम" or plain words instead). This is the register guidance I asked for. |
| D-01 | partially honored (deferred) | The spoken Transitions disclosure IS in the plan §3: "The owner and business-hub screens are still English-first — the Marathi-first pass for the pilot is MVP scope." And the current state is disclosed in milestones "Where we are" ("Marathi partial (missing keys fall back to English)") and in the plan's claim map (70 of 162 keys). **The unhonored half:** the deferral requires "pilot-cook readiness in milestones must gate on it" — but `docs/milestones.md` has no explicit gate or "what must be true" line tying pilot cook onboarding to the business-hub Marathi-first pass. The done criterion "dish listed in < 5 min, unassisted" covers the cook listing flow (already Marathi), not the English-first `o_*`/`m_*` hub. This is the same class of drift that let the v1 regressions ship: a disclosure in the plan without a milestone gate. One line in milestones fixes it. Not a rejected fix ID (D-01 is deferred, not accepted), and not a verdict-changer — but it should land before the pilot, not after. |

## Things I checked that turned out fine

- The F-18 evidence transcript is real engine output (`src/state_machine.py` + FakeDatabase + FakeWhatsAppClient + real `mr.json`), and every corrected Marathi string (`चालू ऑर्डरी` × 4, `स्वयंपाकघर`, UPI-only payment screens) appears in it — the video will narrate the strings I verified, not new ones.
- No Zelle/Venmo/Pix leakage anywhere in `locales/mr.json` (grepped; zero hits).
- The plan's explicit non-goal #5 ("No full Marathi parity — 'Partial — English fallback' is stated") means the video cannot over-claim Marathi coverage the way v1 did.

Rejected fix IDs: **none** (all 6 of my accepted fix IDs confirmed). One open
note on D-01's milestones gating, above.
