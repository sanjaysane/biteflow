## What

<!-- One paragraph: what changes and why. Link the issue if there is one. -->

## How I tested it

<!-- Be specific — reviewers will re-run this. -->

- [ ] `python -m pytest tests/ -q` — all green
- [ ] `ruff check src tests scripts locustfile.py` and `ruff format --check …` — clean
- [ ] `python scripts/check_locales.py` — en/es/hi parity (if strings changed)
- [ ] Manual walkthrough: <!-- paste the message-by-message chat transcript -->

## Checklists

- [ ] Senior-accessible: single-digit / 👍👎 only in core loops, no typing required
- [ ] Every new user-facing string exists in `en`, `es`, and `hi`
- [ ] No edits to `sql/schema.sql`; new tables are a numbered migration
- [ ] Docs updated (`README`, `docs/ARCHITECTURE.md` §10 if there are new limitations)
- [ ] No secrets, tokens, or phone numbers in code or logs
