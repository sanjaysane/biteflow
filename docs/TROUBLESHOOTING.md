# Troubleshooting

## "I messaged the business number and nothing happens"

1. Check the webhook subscription: Meta App Dashboard → WhatsApp →
   Configuration → the callback URL must be your public `/webhook` and the
   verify token must exactly match `WEBHOOK_VERIFY_TOKEN`.
2. Subscribe the webhook to the **messages** field — without it Meta never
   calls you.
3. Look at server logs for `[biteflow] handler error` lines.
4. Hit `GET /health` — if that fails, the app isn't up at all.

## "Meta says webhook verification failed"

`GET /webhook?hub.mode=subscribe&hub.verify_token=X&hub.challenge=Y` must
return `Y` verbatim when `X` equals your verify token. Common causes: extra
whitespace in the env var, or the app reading a different `.env` than you
edited. `./run.sh` sources `.env` from the repo root.

## "The bot repeats the welcome message / forgets where I was"

Sessions persist in `chat_sessions`. If `DATABASE_URL` is unset, the app
uses the in-memory fake — every restart wipes all conversations. Set a
real `DATABASE_URL` for anything beyond a quick local try.

## "Invalid choice" loops

The parser accepts bare digits only (`parse_choice`). "One", "1.", " 1 "
(with words around it) are rejected by design — seniors get a polite
re-prompt, not a crash. If *valid* digits are rejected, check that the
session row exists and the state matches what the user sees.

## "Menu shows but ordering fails"

The cook's menu items must be `active`. A rebroadcast deactivates the old
menu. If a customer is mid-order during a rebroadcast, their stashed item
IDs may no longer resolve — they get a re-prompt, not an error.

## "P2P screenshot sent, cook never got the approval prompt"

The cook must be in (or reachable from) the order-inbound state. The
approval goes to the cook's chat via `ctx.send_to` — if the cook's session
row is missing (fresh DB), the message still sends but the cook's *state*
won't show the queue until they say hello.

## "Tests fail on my machine but pass in CI"

- Python version: 3.11+ required (`str | None` unions, `tomllib`-era stdlib).
- Stale `.pyc` / old venv: recreate the venv and reinstall.
- The Postgres smoke test only runs with `BITEFLOW_TEST_DATABASE_URL` set;
  without it, it skips — that's expected, not a failure.

## "Docker build fails on pip install"

The builder stage needs network access to PyPI. Behind a corporate proxy,
pass `--build-arg` for `http_proxy`/`https_proxy`, or pre-build with
`docker build --network=host`.

## "Locust shows lots of failures"

The load test seeds one cook at test start; if seeding failed (app not
ready), every customer flow 500s. Wait for `/health` first. Also note the
webhook returns `{"ok": true}` even when a handler errors — Locust flags
only non-200 / `ok != true`, so check server logs for handler errors
behind a green-looking run.

## "Supabase connection drops on Vercel"

Use the Supabase **connection pooler** URL (port 6543), not the direct
5432 URL — serverless functions open many short-lived connections and
will exhaust the direct limit.

## "I need to restore the database" (backup → restore runbook, F-10)

Status: **unrehearsed** — this runbook is documented but no restore has been
rehearsed yet. The database holds orders, payment states, inventory, and
customer sessions; the v3 pitch discloses the unrehearsed state in the Ask.
Rehearse this before the first real order.

1. **Take the backup.** On Supabase free tier: Database → Backups →
   **Create backup** (daily automatic backups exist — a vendor feature, not
   an ops capability until you have restored one). Download the dump or note
   the point-in-time recovery timestamp.
2. **Provision a fresh database.** Create a new Supabase project (or a new
   database on the existing host). Record its new `DATABASE_URL`.
3. **Restore.** `pg_restore` / `psql` the dump into the fresh database, then
   run any pending migrations in `sql/migrations/` in order.
4. **Point the app at it.** Set the fresh `DATABASE_URL` in the deployment
   env, restart the app.
5. **Verify.** Check `/health` is green; then, in `psql` against the fresh
   database: `SELECT count(*) FROM orders;`, `SELECT count(*) FROM
   chat_sessions;`, and spot-check that a recent order's `payment_status`
   and the inventory rows match the pre-restore state.
6. **Acceptance:** backup taken → restored to a new database → app boots →
   orders/payment states intact. Record the date and who ran it.
