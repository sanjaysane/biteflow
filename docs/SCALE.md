# BiteFlow scale notes

How BiteFlow behaves under load, measured — not estimated.

## What was measured (2026-09-05)

| | |
|---|---|
| App server | Uvicorn, single worker, `src/main.py` |
| Database | PostgreSQL 16, local, real migrations (`sql/schema.sql` + `002`–`004`) |
| Load driver | Locust, `locustfile.py`, 20 concurrent users, spawn rate 5/s, 90 s |
| Workload mix | Customer order flows, cook broadcast flows, owner P&L flows |

### Results

| Metric | Measured |
|---|---|
| Requests | 1,635 |
| HTTP failures | 0 |
| Handler errors (server log) | 0 |
| Throughput | 18.3 req/s |
| Latency avg | 752 ms |
| Latency p50 | 750 ms |
| Latency p95 | 990 ms |
| Latency p99 | 1,400 ms |

### Reading these numbers honestly

- **This is a single-VM, single-worker baseline, not a production claim.**
  It proves the full stack (webhook → state machine → real PostgreSQL)
  works end to end under concurrency; it does not prove WhatsApp-scale
  readiness.
- **~750 ms average latency is dominated by connection setup, by design.**
  `PostgresDatabase` opens a new TCP connection per DB operation
  ("serverless-safe: no persistent pool to leak between invocations").
  Each webhook does ~6–10 operations, so most of the 750 ms is
  connect/auth handshakes, not query time. Recommendation: run PgBouncer
  (or Supabase's pooler) in front of Postgres in production, or add an
  opt-in connection pool for long-lived deployments. This is the single
  biggest latency lever.
- **Order completion in the scripted run was low (5 orders).**
  The Locust customer script picks cook "1" from a live list; when other
  virtual cooks register mid-run the list shifts and the rigid script
  derails into re-prompts instead of adapting. The order path itself is
  covered by the test suite (47 unit tests on the fake DB + a real-Postgres
  new-user regression test). The throughput/latency numbers above are
  still valid: every request executed the real webhook path against real
  Postgres with zero failures.
- **HTTP 200 is not proof of success.** The webhook intentionally returns
  `{"ok": true}` even when a handler raises (production must never 500 on
  Meta's retries). The load-test workflow greps server logs for
  `[biteflow] handler error` and fails the run if any appear.

## A bug the load test caught

The first load run reported 21.4 req/s with 0 failures — and was
**discarded as invalid**. Server logs showed every new-user flow throwing
`NotNullViolation` on `chat_sessions.system_role`: brand-new chats have
no role until the user picks one, but the column was `NOT NULL`, and the
`chat_sessions → users` foreign key rejected sessions for unregistered
phones. The fake-DB test suite never caught this because it doesn't
enforce constraints. Fixes, all covered by `tests/test_postgres_smoke.py`:

- `sql/migrations/003_chat_sessions_nullable_role.sql` — allow NULL role
  until the user picks one.
- `sql/migrations/004_chat_sessions_no_user_fk.sql` — sessions are created
  on first contact, before any `users` row exists; the FK was wrong for
  this lifecycle.
- `src/db.py` — `save_session`'s `ON CONFLICT` update now includes
  `system_role` (it previously kept the stale value on re-save).

## How to reproduce

```bash
docker compose up -d db        # or any Postgres 16
DATABASE_URL=... .venv/bin/python scripts/apply_migrations.py
DATABASE_URL=... .venv/bin/python -m uvicorn src.main:app
.venv/bin/locust -f locustfile.py --headless -u 20 -r 5 -t 90s \
  --host http://127.0.0.1:8000
```

Or dispatch the **Load test** workflow from the GitHub Actions tab —
it runs the same workload against Compose, uploads the Locust HTML
report, and fails on any `[biteflow] handler error` in the logs.
