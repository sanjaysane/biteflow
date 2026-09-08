# v3 re-review sign-off — QA Analyst

Date: 2026-09-07. Scope: the 33 accepted fix IDs in
`docs/review-loop/reviews/v3/TRIAGE.md`, verified against the repo state on
`main` (commits `6a94dd5` F-23/F-24/F-25, `714fcf8` F-17, `faa8782` F-18
evidence, `07b0a60` doc fixes B, `4e67d27` plan fixes C). I ran the full
suite myself and read every changed line — I did not trust the triage
notes or the fix commits' summaries alone.

## Overall verdict: APPROVED

All 33 accepted fix IDs confirmed against the repo. Independent test run:
**69 passed, 4 skipped, 2 warnings** (`python3.12 -m pytest`, `.venv`;
the 4 skips are the env-gated live-Postgres smoke tests,
`BITEFLOW_TEST_DATABASE_URL` not set). Ruff clean. `check_locales.py`
passes (en/es/hi 162 keys; `mr` intentionally excluded as a documented
partial locale). One observation below the table, not a rejection.

## Per-fix-ID verification

| Fix ID | Verdict | Evidence |
|---|---|---|
| F-01 | confirmed | `docs/milestones.md` now reads "69 tests passing (2026-09-07), Ruff clean, CI green" — matches `docs/evidence/test-run-2026-09-07.txt` (`69 passed, 4 skipped, 2 warnings`) and my own run today. |
| F-02 | confirmed | Gap #1 moved into "Where we are (implemented)" with commit `1844781`, migration `006_allow_marathi_locale.sql`, and `postgres-mr-verification.txt` Steps 2→4→5 cites; removed from MVP "In scope"; done criteria carry a "Recorded verification (2026-09-07)" line. |
| F-03 | confirmed | `docs/business-plan.md` §5 now labels the $0 pilot stack "**sourced** as a documented deployment option", consistent with the line-7 label key. |
| F-04 | confirmed | Milestones MVP scope item 4 rewritten as actual mechanics (customer pays cook directly off-platform; screenshot `photo:<media-id>` or `ref:<text>`; cook verifies with one digit; human reconciles daily; explicit "No UPI intent … anywhere in `src/`"). Business-plan §2 carries the cook's-own-VPA clarification. |
| F-05 | confirmed | Standing rule honored: "cook-verified, not bank-verified" appears in milestones scope item 4; "P2P proof is trust-based (a screenshot is a claim, not settled funds)" in business-plan §1; "P2P proof is trust-based" in ARCHITECTURE §10; plan §5 build notes reuse "cook-verified, not bank-verified". |
| F-06 | confirmed | Milestones MVP Risks now discloses: platform stores only the Meta `media_id`, never screenshot bytes — post-hoc audit impossible for the platform; disputes rely on the cook's device copy. Same disclosure in business-plan §7 risk 2. |
| F-07 | confirmed | Milestones "MVP approval condition (F-07)": board approval conditional — no real orders until `X-Hub-Signature-256`, `wamid` dedupe, and rate-limiting are implemented and covered by tests. Done criterion reworded to "hardening controls implemented and verified". |
| F-08 | confirmed | Plan §6 Ask states the condition out loud ("approval tonight is conditional — webhook hardening lands before the first real order"); §4 keeps the ₹3–8 reconciliation-labor line visibly uncertain with explicit "must not soften it (F-08)" note; the two OPEN gaps have spoken Transitions airtime. |
| F-09 | confirmed | Milestones "What must be true" += a documented read of Meta's WhatsApp Business Policy and Commerce Policy against the screenshot-verification flow, before pilot cook onboarding. |
| F-10 | confirmed | Milestones in-scope item 3 = rehearsed backup → restore → app boots, documented in `docs/TROUBLESHOOTING.md` ("I need to restore the database" runbook, explicitly marked **unrehearsed**); plan §3 Transitions and §6 Ask both disclose "no restore has been rehearsed yet". |
| F-11 | confirmed | v1.2 growth gates += "multi-worker + pooled-DB load test at 10x pilot traffic with zero handler errors"; plan §3 Transitions disclose "the 18.3 requests-per-second figure is a single-worker baseline, not a capacity claim"; milestones gate carries the same parenthetical. |
| F-12 | confirmed | Business-plan §3 carries the currency note: single-currency schema ⇒ this plan assumes per-market deployments (doubled ops); the currency-column migration is explicitly not v1.2 scope. |
| F-13 | confirmed | Milestones "Pilot ops floor" section (alert on `[biteflow] handler error`, daily reconciliation report, named human on-call); v1.2 gate += alerting/SLO definition; plan §3 speaks "Ops today is grep-the-logs" with the silent-outage consequence. |
| F-14 | confirmed | SECURITY.md § "Secret rotation and custody": rotation policy for `WHATSAPP_TOKEN` / `WEBHOOK_VERIFY_TOKEN` (incl. after staff/contractor changes), per-environment separation, Meta app admin custody. |
| F-15 | confirmed | Business-plan §8 gate names "minutes per reconciled order" explicitly as the pilot's **#1 business metric**. |
| F-16 | confirmed | v1.2 in-scope: "campaign outreach on approved WhatsApp templates with batching and per-second rate control"; growth gates: "Campaign work requires approved WhatsApp templates + batching/per-second rate control". |
| F-17 | confirmed | `src/config.py` adds `BITEFLOW_MODE` / `BITEFLOW_FAKE_DB`; `src/main.py` `build_runtime()` raises `RuntimeError` for pilot/demo modes on the fake DB without `BITEFLOW_FAKE_DB=1`. New `tests/test_startup_guard.py` (4 tests) — all pass standalone and in the full suite. |
| F-18 | confirmed | Plan §2 restructured: items 1/5/6 collapsed into a single 45–60 s "Marathi fix is real" beat; "at least 3:00 of the 6:00" is one real customer order end-to-end; the payment beat (item 4) is held until narration finishes with the exact must-say line; the cook's dish-listing flow (item 2) precedes the customer menu frame (item 3) and is "held long enough to read". Evidence transcript `docs/evidence/order-loop-marathi-2026-09-07.txt` Parts 1–5 exists and matches. |
| F-19 | confirmed | Plan §1 "Must say": "customers order for free; cooks use it free in the pilot — the platform monetizes the cook side later." |
| F-20 | confirmed | Milestones "Still open (v3 round)" now names the board review itself; notes business-plan and v3 video exist dated 2026-09-07 and are under review, not open work. |
| F-21 | confirmed | "Owner addenda" bullet now cites commit `b244696` (verified to exist: "BiteFlow: WhatsApp micro-commerce for seniors + business-owner addendum"). |
| F-22 | confirmed | Plan §1 retired the old line; the must-say now reads "the engine and database path are the real production code; the WhatsApp transport in this demo is a local adapter, not the live Meta Cloud API". |
| F-23 | confirmed | `locales/mr.json` `cook_home` → "2️⃣ चालू ऑर्डरी पहा 📦". The "उघड्या" joke is gone. |
| F-24 | confirmed | `locales/mr.json` `cook_registered` → "चला, तुमचं स्वयंपाकघर सुरू करूया." |
| F-25 | confirmed | Marathi `p2p_instructions` → "…UPI ने पाठवा" and `payment_title` → "फोनवरून पेमेंट (UPI)"; no Zelle/Venmo/Pix in either. `en.json` keeps the multi-rail list (US context) as required. |
| F-26 | confirmed | Plan §5 build notes carry register guidance: warm non-technical Marathi for UI-quoting beats; no "डेटाबेस/स्टेट मशीन/बॅकएंड" where a senior would hear it. |
| F-27 | confirmed | Business-plan §2 states the decision rule (commission iff repeat ≥ 40%, AOV ≥ ₹150, orders/cook/month ≥ 100, AND a cook-accepted collection mechanism passes its acceptance test; otherwise subscription by default) and names the asymmetry ("not symmetric, not a coin flip"; "subscription wins by default"). Milestones v1.2 in-scope and growth gates reference the rule; plan §4 presents commission as "boundary-crossing candidate" and subscription as "wins by default". |
| F-28 | confirmed | §6 F-28 note: ₹150 AOV ⇒ ~2-item basket; evidence-price re-run at ₹85: 10% → ₹8.50 gross vs ₹5–14 variable = "≈ −₹6 to +₹4, underwater before the pilot starts". My arithmetic agrees (−₹5.50 to +₹3.50). |
| F-29 | confirmed | §6 subscription table contribution row → "≈ −₹3 to +₹5". Arithmetic: ₹9.99 − ₹13 = −₹3.01; ₹9.99 − ₹5 = +₹4.99. Correct. |
| F-30 | confirmed | §6 commission table models both: 10% → "≈ ₹1–9"; 8% → "≈ −₹2 to +₹7" with "negative in the high-cost case" noted. Arithmetic: 8% × 150 = ₹12; −₹2 to +₹7 correct. |
| F-31 | confirmed | Business-plan §9 "Defensibility — the honest version": no network effect in scope, near-zero switching cost, technology not defensible; the bet is execution depth (locale/voice UX, margin-alert intelligence, referral relationships, speed). |
| F-32 | confirmed | Business-plan §8 and milestones done-criteria preamble label MVP as **demand validation**, name the v1.2 contribution-margin gate as the first genuine business test; milestones "What must be true" += the directional ₹999/month WTP probe with each pilot cook. |
| F-33 | confirmed | v1.2 growth gates += subscription kill criterion: median orders/cook/month ≥ 100 AND median cook GMV ≥ ₹15,000/month to hold ₹999 pricing; below that the price is repriced or the model is abandoned. |

**Deferred D-01:** not a fix-ID verdict — see external-user report for the one
caveat (the deferral's milestones-gating condition isn't explicit).

## Observation (not a rejection)

- The triage's F-01 verification note claimed the evidence showed "zero
  skips"; the actual evidence file and my run both show **4 skips** (the
  env-gated live-Postgres smoke tests). The doc fix itself ("69 tests
  passing (2026-09-07), Ruff clean, CI green") is accurate and the plan's
  claim-to-evidence map correctly documents the 4 skips. No fix required.

Rejected fix IDs: **none** (33/33 confirmed).
