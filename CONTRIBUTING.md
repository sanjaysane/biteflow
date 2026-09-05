# Contributing to BiteFlow

Thanks for wanting to make BiteFlow better. This project is deliberately
small and readable — a weekend-scale codebase a junior dev can hold in
their head. Please keep contributions in that spirit: boring technology,
explicit code, no cleverness.

## Ground rules

1. **Addendum discipline.** New product code lives under `src/owner/`;
   new SQL goes in `sql/migrations/` as a new numbered file. `sql/schema.sql`
   is frozen — never edit it, migrate it.
2. **Senior-accessible UX.** Every new conversational step must work with
   single-digit replies or 👍/👎. No free-form typing in core loops, no
   searching, no menus deeper than two levels.
3. **Three languages, always.** Every user-facing string needs an `en`, `es`,
   and `hi` entry. `scripts/check_locales.py` (and CI) enforces exact key
   parity and placeholder consistency.
4. **Tests for behavior.** New flows get pytest scenarios that drive the
   state machine like the webhook does (see `tests/conftest.py`'s `send`
   fixture). The full suite must stay green, ruff must stay clean, and
   total coverage must stay above the CI floor.
5. **Honest docs.** If your change has a known limitation, write it in
   `docs/ARCHITECTURE.md` §10 and/or the README's cautions — don't let the
   next person discover it in production.

## Local setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # fill in what you have; blanks boot with fakes
./run.sh               # → http://localhost:8000  (GET /health)
```

Or the whole stack at once (Postgres included):

```bash
docker compose up --build
```

## Running checks

```bash
python -m pytest tests/ -q            # full suite (fake DB)
ruff check src tests scripts locustfile.py
ruff format --check src tests scripts locustfile.py
python scripts/check_locales.py       # en/es/hi parity
```

To also run the real-PostgreSQL smoke test:

```bash
# with a Postgres reachable, migrations applied:
BITEFLOW_TEST_DATABASE_URL=postgresql://user:pass@host:5432/db \
  python -m pytest tests/ -q
```

## Pull request process

1. Fork, branch from `main` (`feat/…`, `fix/…`, `docs/…`).
2. Keep PRs small and single-purpose; one workflow per PR.
3. Fill in `.github/pull_request_template.md` — especially the
   "How I tested it" section. CI must be green.
4. A maintainer reviews for the ground rules above, not just correctness.
   Expect questions about accessibility and multilingual coverage.
5. Squash-merge; the commit message should read like a changelog line.

## Release process

Maintainers tag annotated releases (`vX.Y.Z`) with `gh release create`,
writing release notes that summarize behavior changes **and** restate the
current known limitations. See the `v0.1.0` notes for the template.

## Recommended repository settings

(Not enabled by automation — a maintainer flips these in Settings.
Documented here so the intent is public.)

- **Branch protection on `main`:** require pull request before merging,
  require status checks `lint`, `test (3.11)`, `test (3.12)`, `test (3.13)`,
  `docker` to pass; require conversation resolution; dismiss stale reviews.
- **No direct pushes to `main`** except automated dependency updates after
  CI passes.
- **CodeQL:** default setup or the `codeql.yml` workflow — keep the weekly
  scan on.
- **Dependabot:** weekly pip + GitHub Actions updates (already configured).
- **Secret scanning + push protection:** on. Webhook verify tokens and
  WhatsApp tokens must never appear in code, issues, or logs.
