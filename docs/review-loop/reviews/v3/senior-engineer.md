# Senior Engineer Review — v3 Milestone Package (BiteFlow)

**Verdict: NEEDS WORK**

Persona: Senior Engineer. Rubric: narration vs. code fidelity; dishonest
simplifications; skipped failure modes. Method: read `docs/milestones.md`,
`docs/business-plan.md`, `docs/videos/v3-presentation-plan.md`, plus
`docs/ARCHITECTURE.md`; spot-checked `src/payments.py`, `src/owner/handlers.py`,
`src/whatsapp.py`, `sql/migrations/006_allow_marathi_locale.sql`,
`docs/SCALE.md`, `docs/FAQ.md`, and `docs/evidence/*`. Verified ground truths:
69 tests passed per `docs/evidence/test-run-2026-09-07.txt`; no signature
verification in `src/main.py`; no dedupe/rate-limiting on `/webhook`.

Blockers: **none.** The engineering is honestly described in ARCHITECTURE.md
§10 ("Deliberate simplifications") — exemplary. All findings below are
places where the *milestone/planning docs* diverge from the code, not places
where the code is broken.

---

## Blockers

None. Nothing found that misrepresents a shipped engineering capability as
working when it is not.

## Major

### M1 — Milestones MVP scope item 4 says "UPI intent/collect"; no such capability exists in code

- **Doc + section:** `docs/milestones.md`, MVP "In scope" item 4: "Payments: UPI intent/collect + screenshot reconciliation, with explicit in-chat trust framing."
- **What the code does:** `src/payments.py` implements exactly two flows — COD, and P2P where the customer submits either `photo:<media-id>` (a screenshot) or `ref:<text>` (a typed reference); the order flips to `pending_approval` and the cook approves/denies with one digit (`submit_p2p_proof`, `decide_payment`). A grep for UPI across `src/` returns only a docstring mention ("P2P (Zelle/Venmo/UPI/Pix)") — there is no UPI intent (deep link) generation and no collect-request integration anywhere.
- **Expectation violated:** a milestone's in-scope item must describe engineering work that is actually planned to be built. "UPI intent/collect" is payment-rail terminology implying the platform generates UPI payment links or issues collect requests — which would mean touching money movement. That directly contradicts the business plan's own stated architecture: `docs/business-plan.md` §1–§2: "No money moves through BiteFlow; it tracks payment state only" and "No money-movement rails are built or operated by BiteFlow in MVP."
- **Why it matters:** a board approving this milestone, or an engineer scoping it, would budget for UPI link generation — a materially different (and payment-licensing-adjacent) build than "customer pays cook directly off-platform, sends a screenshot/reference, cook verifies." Rewrite item 4 to name the actual mechanics: "customer pays cook directly off-platform (cash/UPI); submits screenshot or typed reference; cook verifies with one digit; human reconciles daily."

## Minor

### m1 — milestones.md "Where we are" cites stale test counts

- **Doc + section:** `docs/milestones.md`, "Where we are": "65 tests passing, 2 skipped; Ruff clean; CI green."
- **Evidence:** `docs/evidence/test-run-2026-09-07.txt` (same date): `69 passed, 2 warnings`, zero skipped. The v3 presentation plan's §3 claim map cites 69. The milestones doc was not updated after the suite grew.
- **Expectation violated:** the milestone doc should not under/over-claim a number that the repo's own same-day evidence file contradicts. Fix: "69 passed, 2 warnings."

### m2 — Same-day docs disagree on whether gap #1 (mr/Postgres) is open or closed

- **Doc + section:** `docs/milestones.md`, Known gaps #1: "Fix + test against live Postgres **before pilot**" (still listed as a gap to close); vs. `docs/videos/v3-presentation-plan.md` §3 (same date, 2026-09-07): "`mr`/Postgres constraint — **FIXED, migration 006 verified**", citing `docs/evidence/postgres-mr-verification.txt` Step 4.
- **Code check:** `sql/migrations/006_allow_marathi_locale.sql` exists and correctly widens `users_preferred_language_check` to `('en','es','hi','mr')`. The verification evidence exists. The truth is "fixed" — the milestones doc is stale.
- **Expectation violated:** two documents in the same review package, dated the same day, must agree on whether a named gap is open or closed. Mark gap #1 resolved in milestones.md with the migration + evidence reference.

### m3 — DB state named `verified` is cook-verified, not bank-verified

- **Doc + section:** `docs/ARCHITECTURE.md` §5 and `docs/business-plan.md` §2 describe payment states `unpaid → pending_approval → verified`; the qualifier "cook-verified, not bank-verified" appears in the business plan (§1) and ARCHITECTURE §10, but the raw state name `verified` in code and doc tables can be misread by a board member as settlement confirmation.
- **Expectation violated:** none of the three docs — the qualifier is present where it counts. This is hygiene only: keep the "cook-verified" qualifier attached every time the state name appears in board-facing material, or consider renaming the state. No code change required for the milestone.

### m4 — Screenshot auditability limitation is under-named (failure-mode sharpening)

- **Code fact:** `docs/ARCHITECTURE.md` §10 discloses "Media handling stores only the Meta `media_id`, never the file bytes" and "P2P proof is trust-based … `media_id`s are not downloaded/inspected." Correct and honest.
- **Unstated consequence:** because BiteFlow never persists the screenshot bytes, post-hoc audit of a disputed payment is impossible even for the human reconciler — the screenshot exists only on the cook's phone. The business plan §7 risk 2 ("Payment fraud on trust-based verification") is disclosed, but the docs never say the evidence itself is non-retained. Add one sentence to milestones risk 2 or business-plan §7: disputes rely on the cook's device copy; the platform cannot re-inspect proof.

---

## Rubric checklist

- **(a) Business-plan cost/infra story vs. architecture:** MATCHES. Business-plan §5 pilot cost ("≈ $0/month Supabase free + Render free; $7–12/month always-on") is accurately sourced from `docs/FAQ.md` (lines 35–37: "Near-zero for a pilot … A small always-on setup is roughly $7–12/month") and explicitly flagged "recheck at pilot time." The binding unknown — Meta per-conversation price — is called out as *not in this repo* and must be read from the rate card; no rate-card number is quoted anywhere. ARCHITECTURE §8 deployment options (Render / Vercel / local+ngrok) are consistent with the cost story.
- **(b) Presentation plan vs. actual code behavior:** FIDELITY HOLDS. The claim-to-evidence map (§3) verified against evidence files: 69 passed ✓, mr/Postgres fix ✓ (migration 006 real), locale currency ✓, inventory seed ✓, nickname ✓. No scale number is claimed in the BiteFlow plan (correct — BiteFlow's measured number is 18.3 req/s single-worker per `docs/SCALE.md`, not 35; the plan does not borrow RoomLens's number). Non-goals (§4) are honest: no live Meta API, no verified rail, no kill-mid-order demo (correctly dropped as unproven), no commission numbers as fact. Two OPEN gaps (webhook hardening, live Meta API) get spoken disclosure per the plan's own duration rule.
- **(c) Skipped failure modes:** disclosed where they exist — inbound dedupe/signature/rate-limit gaps (ARCHITECTURE §10, milestones gap #2, README flag), screenshot-fraud trust model (ARCHITECTURE §10, business-plan §7 risk 2), campaign fan-out with no batching/rate control (ARCHITECTURE §10 — this disclosure is present in BiteFlow and absent in RoomLens; see that repo's report), human-reconciliation labor not scaling (business-plan §7 risk 6). One sharpening: m4 above.
- **(d) Dishonest simplifications in milestones:** one real instance — M1 ("UPI intent/collect"). The rest of the milestones doc's label discipline (implemented / assumption / gap) holds up against the code.

---

*Reviewed 2026-09-07. Independent review; no coordination with other personas.*
