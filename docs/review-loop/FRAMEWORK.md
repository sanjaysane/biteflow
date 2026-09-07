# Product Review Swarm — the mini-company loop

A reusable framework for shipping demo-grade work like a tiny company:
build → independent review → triage → iterate → re-review → release,
with evidence at every milestone. Created 2026-09-05 after the
BiteFlow + RoomLens walkthrough-video v1 needed a real self-improvement loop.

## The loop

```
BUILD v1 → REVIEW SWARM → TRIAGE → REBUILD v2 → RE-REVIEW → RELEASE
```

1. **Build v1.** Ship the best honest version you can. Iron rule for demos:
   every pixel of "product" on screen must be real output of the real system
   (no hand-written chat text, no mock screenshots presented as product).
   Narration/scripts are written first, then synthesized, then assembled.
2. **Review swarm.** 7 persona reviewers, spawned in parallel, each with a
   distinct voice and rubric, each writing a structured report to
   `reviews/v1/<persona>.md`. They review independently — no shared draft,
   no anchoring. Every report has: **Verdict: SHIP** or **Verdict: NEEDS
   WORK**, findings ordered blocker / major / minor, each with a timestamp
   or frame reference and the exact expectation violated.
3. **Triage.** One owner reads all seven and writes `reviews/TRIAGE.md`:
   every finding → **accepted** (fix in v2, with fix ID) or
   **rejected/deferred** (with the reason stated plainly). Real code/product
   limitations get honest in-product disclosure, never silent fixes and never
   faked output.
4. **Rebuild v2.** One builder per artifact, each with its fix-ID list.
   v1 is kept untouched; v2 is a new file. Every change must be re-verified
   (durations, spot frames, script diffs).
5. **Re-review (lighter).** A subset of personas (at minimum QA + the
   harshest v1 critic) gets `CHANGELOG-v1-v2.md` as a checklist and confirms
   or rejects each fix. Sign-offs land in `reviews/v2/`.
6. **Release.** `reviews/RELEASE.md`: what "released", known issues carried
   forward, what the next milestone would address — including material
   findings deliberately not fixed and why.

## The 7 seats

| # | Persona | Rubric in one line |
|---|---|---|
| 1 | QA Analyst | Verify every claim; entry/exit coverage; caption/frame accuracy |
| 2 | Senior Engineer | Narration vs. code fidelity; dishonest simplifications; skipped failure modes |
| 3 | Senior Technical Leader | Production readiness; scale/security/compliance/ops gaps to disclose |
| 4 | Product Manager | 60-second clarity; onboarding friction; pacing; missing day-one flows |
| 5 | External User | Non-technical real user; language naturalness; trust moments |
| 6 | VC | Monetization, unit economics, money-movement honesty, moat |
| 7 | Board Director | Claim audit; public-embarrassment test; disclosure sufficiency |

Keep the seats fixed across milestones so verdicts are comparable. Reviewers
never fix — they report. The triage owner never overrules a blocker silently;
a rejected blocker needs a written reason.

## Evidence required per milestone

- `reviews/v1/<persona>.md` — 7 structured reports
- `reviews/TRIAGE.md` — accept/reject per finding, with reasons
- `reviews/CHANGELOG-v1-v2.md` — every change mapped to the finding that caused it
- `reviews/v2/<persona>.md` — re-review sign-offs
- `reviews/RELEASE.md` — milestone note: released, known issues, next milestone
- `reviews/LEAKS.md` (or equivalent) — any honesty audit the domain needs

## Lessons from the first run (walkthrough videos, Sep 2026)

- The swarm caught a cross-video contradiction (two business models for one
  product) that no single reviewer role was guaranteed to catch — the value
  is in the *overlap* of rubrics, not just their union.
- "Fix in v2 what the video can fix; disclose what the code can't" resolved
  every triage dispute. The only rejected fixes were ones that would have
  required faking output or inventing numbers.
- The External User found what the engineers couldn't: a main-menu string
  that reads as a joke in Marathi ("उघड्या ऑर्डरी"), and a money screen no
  Marathi reader can use. Always seat a real-user voice.
- Narration re-records are cheaper than frame re-renders; caption safe
  margins should be a v1 checklist item, not a v2 fix.
- The Board Director's "claim audit" table is the artifact the final page's
  "How this was reviewed" section is built from — write reviews so their
  findings are quotable.
