# BiteFlow 🍛

[![CI](https://github.com/sanjaysane/biteflow/actions/workflows/ci.yml/badge.svg)](https://github.com/sanjaysane/biteflow/actions/workflows/ci.yml)
[![CodeQL](https://github.com/sanjaysane/biteflow/actions/workflows/codeql.yml/badge.svg)](https://github.com/sanjaysane/biteflow/actions/workflows/codeql.yml)
[![Python 3.11–3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/sanjaysane/biteflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Zero-client WhatsApp micro-commerce for home cooks and their customers.
Nobody installs an app — cooks broadcast menus and customers order dinner
entirely inside plain WhatsApp chats, using single-digit replies (`Reply 1`),
👍/👎 confirmations, and short localized text. English, Spanish, and Hindi
are built in; the language can be switched mid-chat with one word.

Built on the **Meta WhatsApp Business Cloud API** + **PostgreSQL**
(Supabase-ready), deployable for (almost) free on **Render** or **Vercel**.

> ⚠️ **Not production-hardened.** This is a working pilot with real CI,
> real migrations, and measured load numbers — but it does not verify
> webhook signatures, dedupe inbound messages, or rate-limit the webhook.
> See [Operational cautions](#operational-cautions) before real traffic.

## Quick start (one command)

```bash
docker compose up --build
# → app http://localhost:8000 (GET /health), Postgres on :5432
```

That's it: the image runs migrations automatically and boots the API.
Then expose it to Meta with ngrok (see
[docs/how-to/local-dev-with-ngrok.md](docs/how-to/local-dev-with-ngrok.md)).

Local Python dev:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env        # fill in values
./run.sh                    # → http://localhost:8000  (GET /health)
python -m pytest tests/ -q  # → 49 passed
```

The app boots without credentials: no `DATABASE_URL` → in-memory fake DB,
no WhatsApp token → fake client that logs instead of sending.

## Documentation

| Doc | What it covers |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design notes + deliberate simplifications |
| [docs/SCALE.md](docs/SCALE.md) | Measured load-test results (18.3 req/s, p95 990 ms) + how to reproduce |
| [docs/FAQ.md](docs/FAQ.md) | Common questions |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Fix-it recipes for the usual failures |
| [How-to guides](docs/how-to/) | ngrok local dev, Supabase setup, Meta app setup, Render deploy, Vercel deploy, cook's first day |
| [Video scripts](docs/videos/) | Three presenter scripts: local setup, Render deploy, cook's first day |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Ground rules, branch discipline, migration rules |
| [SECURITY.md](SECURITY.md) | Threat model, reporting, known gaps |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |

## CI & quality gates

Every push runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

- **Tests** on Python 3.11 / 3.12 / 3.13 against a real PostgreSQL 16
  service (migrations applied, locale parity checked, coverage ≥ 60%)
- **Ruff** lint + format check
- **Docker** build + Compose boot + `/health` check
- **CodeQL** and **Dependabot** run separately (see badges above)

A manual [**Load test** workflow](.github/workflows/loadtest.yml) runs the
Locust workload from [docs/SCALE.md](docs/SCALE.md) against Compose and
fails on any `[biteflow] handler error` — HTTP 200 alone is not success.

## Repository layout

```
biteflow/
├── src/
│   ├── main.py            # FastAPI app: GET /webhook (verify), POST /webhook, GET /health
│   ├── state_machine.py   # declarative ROUTES table: (role, state) → handler
│   ├── config.py          # env-based settings
│   ├── models.py          # roles, states, enums, language commands
│   ├── db.py              # PostgresDatabase + FakeDatabase (same interface)
│   ├── i18n.py            # JSON locale tables, EN fallback
│   ├── whatsapp.py        # MetaWhatsAppClient + FakeWhatsAppClient
│   ├── payments.py        # COD / P2P totals, proof submission, state helpers
│   ├── context.py         # Ctx: reply/send_to/set_state + safe parsers
│   ├── handlers/
│   │   ├── customer.py    # welcome → browse → cart → pay → track
│   │   └── cook.py        # home → menu broadcast → inbound → payment/status
│   └── owner/             # business-owner addendum (kitchen economics +
│                          # marketing); new app code lives ONLY here
│       ├── handlers.py    # O_* / M_* conversational loops
│       ├── states.py      # owner state names (O_HOME… / M_HOME…)
│       ├── economics.py   # recipes, margins, stock, procurement, P&L
│       ├── marketing.py   # referrals, offers, campaigns, win-back
│       └── digest.py      # daily P&L WhatsApp digest builder
├── locales/               # en.json, es.json, hi.json (identical key sets)
├── sql/schema.sql         # base schema (frozen)
├── sql/migrations/        # additive migrations only (002–004)
├── tests/                 # 49 pytest tests (see Testing)
├── docs/                  # architecture, scale, FAQ, troubleshooting, how-tos, video scripts
├── Dockerfile             # multi-stage, non-root
├── docker-compose.yml     # app + Postgres
├── .github/workflows/     # ci.yml, loadtest.yml, codeql.yml
├── render.yaml            # Render blueprint (web + Postgres)
├── vercel.json            # Vercel serverless function
├── requirements.txt       # runtime deps
├── requirements-dev.txt   # test/lint/load deps
├── .env.example
└── run.sh                 # local dev server
```

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | prod | Postgres connection string (Supabase pooler for serverless) |
| `WHATSAPP_TOKEN` | prod | Meta Cloud API permanent access token |
| `WHATSAPP_PHONE_NUMBER_ID` | prod | Meta phone number ID for the business |
| `WEBHOOK_VERIFY_TOKEN` | yes | Shared secret for `GET /webhook` verification |
| `DEFAULT_LANGUAGE` | no | `en` (default) / `es` / `hi` for brand-new chats |
| `WHATSAPP_API_BASE` | no | Graph API base (default `https://graph.facebook.com/v21.0`) |

## How a chat flows

**Customer:** `hello` → welcome + role pick → choose a cook (`1`) → menu →
`Reply 1` for a dish → quantity (`2`) → `0` checkout → confirm → Cash or
Phone-transfer → (P2P: send screenshot or reference) → live tracking
(`Cooking 🍳` … `Completed ✅`).

**Cook:** `hello` → register as cook → `1` set menu → dish name → price →
`1` add another / `2` done → menu is live. Incoming orders arrive as
`1 👍 Accept / 2 👎 Reject`; payment screenshots arrive as
`1 Approve / 2 Deny`; then `1 Cooking 🍳 → 2 Out 🚗 → 3 Done ✅` updates the
customer.

**Cook — business owner:** from the cook home, `3` opens 📊 Business
(inventory → recipes/BOM → procurement → finance) and `4` opens 📣 Marketing
(referrals → first-order offer → campaigns → win-back). Every decision is a
single digit or 👍/👎; free-form text appears only in setup moments (names,
prices, campaign copy). The paneer counterfactual is built in: double a
supplier price and the cook gets one WhatsApp alert listing every dish whose
margin fell below 20% — before the next menu broadcast.

**Language:** from anywhere, send `language`, `idioma`, or `भाषा` → pick
1/2/3 → the chat resumes exactly where it was, now in the new language.

## Testing

```bash
python -m pytest tests/ -q
```

49 tests, all green. The default run uses the in-memory fake DB (no external
services); `tests/test_postgres_smoke.py` runs the same flows against a real
PostgreSQL when `BITEFLOW_TEST_DATABASE_URL` is set (CI always sets it):

- `test_customer_flow.py` — invalid menu numbers / quantities rejected,
  polite re-prompt, state and basket untouched
- `test_cook_broadcast.py` — multi-item broadcast, price validation,
  rebroadcast replaces the old menu
- `test_language_switch.py` — mid-chat switch (EN→ES, EN→HI), invalid choice
  re-prompt, full loop in Spanish
- `test_payments.py` — COD, P2P screenshot → approve → verified, typed
  reference → deny → resend, accept → cooking → completed
- `test_webhook.py` — verify handshake (good/bad token), Meta payload
  parsing, image payloads, status-only receipts
- `test_locales.py` — en/es/hi key parity + every key referenced in code
  exists in every locale
- `test_owner_economics.py` — recipe food-cost & margin math, low-stock
  alert fires once per breach (latch), zero-threshold silence, stock
  consumption on accept, pre-broadcast margin warning, weekly purchase
  plan, daily P&L
- `test_owner_marketing.py` — referral apply/reject/self-reuse rules,
  dual-sided credit, first-order offer once-only, offer off switch,
  campaign opt-in filtering + cancel, 14-day win-back eligibility and
  30-day re-nudge suppression, customer opt-in ask + global STOP
- `test_owner_paneer.py` — the counterfactual end to end: paneer doubles →
  price persisted → affected recipes recomputed → sub-20% margins flagged →
  exactly one WhatsApp alert to the cook; unrelated recipes untouched;
  a benign price change stays silent; re-runs don't re-ping; and the chat
  trigger — logging a restock at the doubled price fires the alert inline
- `test_postgres_smoke.py` — real-PostgreSQL CRUD across every table plus a
  regression test for the new-user flow (caught two constraint bugs the
  fake DB hid; see [docs/SCALE.md](docs/SCALE.md))

## Migrating

`sql/schema.sql` is the base; changes ship as additive migrations in
`sql/migrations/` (never edit a shipped file):

| Migration | What it adds |
|---|---|
| `002_business_owner.sql` | Addendum tables + two nullable-with-default `orders` columns |
| `003_chat_sessions_nullable_role.sql` | `system_role` nullable until role pick |
| `004_chat_sessions_no_user_fk.sql` | Drop `chat_sessions → users` FK (sessions predate users) |

Apply with `scripts/apply_migrations.py` (runs in order, idempotent via
CREATE IF NOT EXISTS / IF NOT EXISTS guards):

```bash
python scripts/apply_migrations.py   # reads DATABASE_URL
```

Docker and CI apply migrations automatically at boot.

## Schedulers (not included)

Two rhythms are designed but need an external cron — the app exposes pure
functions for them:

- **Daily P&L digest** — `src/owner/digest.py::send_daily_digest(db, wa,
  i18n, cook_phone, day=None)`; run once per evening per cook (e.g. 9 PM local).
- **Low-stock sweep** — `src/owner/economics.py::check_low_stock(...)`;
  run hourly or after every purchase/order if you want alerts without the
  cook opening the chat. (The accept-order path already sweeps inline.)

## Operational cautions

This is a working pilot, not hardened production. Before real traffic:

- **Verify `X-Hub-Signature-256`** on inbound webhooks (not yet implemented) —
  without it anyone can forge messages to your endpoint.
- **Dedupe inbound `wamid`s** — Meta redelivers occasionally; today a retry
  would re-run the handler.
- **Add rate limiting** on `/webhook`.
- **Treat P2P screenshots as claims**, not settled funds.
- **Campaigns are not approved WhatsApp templates** — business-initiated
  messages need template approval from Meta or they won't deliver.
- **Pool your Postgres connections** — the app opens a new connection per
  DB operation (serverless-safe by design); measured ~750 ms avg webhook
  latency is mostly handshake. Run PgBouncer / the Supabase pooler in prod.
- See [SECURITY.md](SECURITY.md) and `docs/ARCHITECTURE.md` §9 for the full
  threat model and the list of deliberate simplifications.

## License

MIT — see `LICENSE`.
