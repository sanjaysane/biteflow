# Review loop — walkthrough videos v1 → v2 (2026-09-06)

Evidence of the 7-persona review swarm for the narrated end-to-end walkthrough
videos, committed here so the GitHub history itself shows which persona gave
what input and what improvement resulted.

## Videos covered by this repo

- BiteFlow — Customer Journey (English): `biteflow-customer-en-v2.mp4` (5m50s)
- BiteFlow — Cook Journey (Marathi): `biteflow-cook-mr-v2.mp4` (3m55s)

(The RoomLens videos — prospect-mr, designer-en — are documented in the
sanjaysane/roomlens repo under the same `docs/review-loop/` path. The persona
review files cover all four videos; this README maps which findings apply to
BiteFlow.)

## Fix IDs applied to this repo's videos (from TRIAGE.md)

- biteflow-customer-en: A3, A5, A6, A7, A8, A9, A10, A11, A12, A13, A18, A20, A22
- biteflow-cook-mr: A5, A6, A13, A14, A15, A16, A21

## Files

- `FRAMEWORK.md` — the reusable 7-persona review loop
  (build → review → triage → rebuild → re-review → release)
- `v1/` — the 7 persona review reports; all 7 returned NEEDS WORK
- `TRIAGE.md` — accept/reject per finding, with reasons
  (23 accepted A1–A23, 8 rejected/deferred R1–R8)
- `CHANGELOG-v1-v2.md` — every v2 change mapped to the finding that caused it
- `v2/` — re-review sign-offs (senior-engineer, board-director)
- `RELEASE.md` — release notes and known issues carried forward

No code was changed by this loop. The v2 fixes are narration re-records,
caption re-renders, on-video disclosures, and corrected manifest descriptions —
the review swarm's rule was: fix in v2 what the video can fix; disclose what
the code can't; never fake engine output and never invent numbers.
