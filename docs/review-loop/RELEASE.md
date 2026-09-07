# RELEASE — walkthrough videos v2 (2026-09-06)

## What this is

Four narrated end-to-end simulated WhatsApp walkthroughs of BiteFlow and
RoomLens, v2 after a full 7-persona review swarm, triage, rebuild, and
re-review. Every chat bubble is verbatim output of the repos' real state
machines (FakeWhatsAppClient pattern); every RoomLens frame is real
`src/composite.py` output. Narration is synthesized; nothing on screen is
mock product.

| Video | Duration | File |
|---|---|---|
| BiteFlow — Customer Journey (English) | 5m50s | `biteflow-customer-en-v2.mp4` |
| BiteFlow — Cook Journey (Marathi) | 3m55s | `biteflow-cook-mr-v2.mp4` |
| RoomLens — Prospect Journey (Marathi) | 3m32s | `roomlens-prospect-mr-v2.mp4` |
| RoomLens — Designer Journey (English) | 3m22s | `roomlens-designer-en-v2.mp4` |

All 1080×1920 vertical, H.264/AAC.

## Review record

- v1: 7 personas (QA, Senior Engineer, Senior Tech Leader, PM, External User,
  VC, Board Director) — all 7 returned NEEDS WORK. Reports in `reviews/v1/`.
- Triage: 23 fixes accepted, 8 rejected/deferred with reasons (`reviews/TRIAGE.md`).
- v2: QA, Senior Engineer, Board Director re-reviewed against
  `reviews/CHANGELOG-v1-v2.md`. Senior Engineer SIGN-OFF, Board Director
  SIGN-OFF, QA REJECTED on one item (A22: two minor narration rewords not yet
  applied) — those two lines were then re-recorded and spliced 2026-09-06,
  verified in-script and via ffprobe. Changelog updated to reflect this.

## Biggest v2 corrections

- The two RoomLens videos contradicted each other on the business model
  (commission vs no-commission). Both now state the code truth: no platform
  commission accounting in this build; no in-app payment rail — designers
  are paid directly, off-platform.
- BiteFlow payment "verification" is disclosed as trust-based (cook-verified
  screenshot, not bank-verified).
- RoomLens demo photos disclosed as synthetic/sample; preset compositing,
  not AR.
- Captions re-rendered with safe margins; tofu emoji fixed; closing cards
  bilingual with hardening, USD, and food-safety disclosures.

## Pre-public polish (from re-reviewers, not blocking)

- Board Director: strengthen the trust-based P2P disclosure with a ~10s
  narration re-record of s07 before any public launch.
- Manifest claims corrected in v2 (`manifest.json`); v1 files retained for
  comparison.

## Known issues carried forward (deliberately not fixed)

- RoomLens viz inputs remain synthetic fixtures (disclosed in-video).
- Marathi locale stays partial: English fallback strings ("उघड्या ऑर्डरी",
  "Total", "received", Business/Finance section) and USD-only pricing are
  real engine behavior — disclosed, not silently fixed.
- No webhook signature validation, no idempotency, no rate limiting
  (disclosed on closing cards).
- No reorder command, no cook live/offline toggle, no payment rails —
  product backlog, not video problems.
- "Enterprise-hardened pilot" release tag kept; rename recommended to owner.
