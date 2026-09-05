# BiteFlow 🍛

Zero-client WhatsApp micro-commerce for home cooks and their customers.
Nobody installs an app — cooks broadcast menus and customers order dinner
entirely inside plain WhatsApp chats, using single-digit replies (`Reply 1`),
👍/👎 confirmations, and short localized text. English, Spanish, and Hindi
are built in; the language can be switched mid-chat with one word.

Built on the **Meta WhatsApp Business Cloud API** + **Supabase/PostgreSQL**,
deployable for (almost) free on **Render** or **Vercel**.

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
│   └── handlers/
│       ├── customer.py    # welcome → browse → cart → pay → track
│       └── cook.py        # home → menu broadcast → inbound → payment/status
│   ├── owner/             # business-owner addendum (kitchen economics +
│   │                      # marketing); new app code lives ONLY here
│   │   ├── handlers.py    # O_* / M_* conversational loops
│   │   ├── states.py      # owner state names (O_HOME… / M_HOME…)
│   │   ├── economics.py   # recipes, margins, stock, procurement, P&L
│   │   ├── marketing.py   # referrals, offers, campaigns, win-back
│   │   └── digest.py      # daily P&L WhatsApp digest builder
├── locales/               # en.json, es.json, hi.json (identical key sets)
├── sql/schema.sql         # users, chat_sessions, menus, orders (frozen)
├── sql/migrations/002_business_owner.sql  # addendum tables + order discounts
├── tests/                 # 43 pytest tests (see Testing)
├── docs/ARCHITECTURE.md   # design notes + deliberate simplifications
├── render.yaml            # Render blueprint (web + Postgres)
├── vercel.json            # Vercel serverless function
├── .github/workflows/ci.yml
├── requirements.txt
├── .env.example
└── run.sh                 # local dev server
```

## Quick start (local)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in values
./run.sh                   # → http://localhost:8000  (GET /health)
python -m pytest tests/ -q # → 22 passed
```

The app boots without credentials: no `DATABASE_URL` → in-memory fake DB,
no WhatsApp token → fake client that logs instead of sending.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | prod | Postgres connection string (Supabase) |
| `WHATSAPP_TOKEN` | prod | Meta Cloud API permanent access token |
| `WHATSAPP_PHONE_NUMBER_ID` | prod | Meta phone number ID for the business |
| `WEBHOOK_VERIFY_TOKEN` | yes | Shared secret for `GET /webhook` verification |
| `DEFAULT_LANGUAGE` | no | `en` (default) / `es` / `hi` for brand-new chats |
| `WHATSAPP_API_BASE` | no | Graph API base (default `https://graph.facebook.com/v21.0`) |

## Wiring Meta webhooks (ngrok)

1. `./run.sh`, then in another terminal `ngrok http 8000`.
2. In the [Meta App Dashboard](https://developers.facebook.com) → WhatsApp →
   Configuration: set the callback URL to `https://<ngrok-id>.ngrok.io/webhook`
   and the verify token to your `WEBHOOK_VERIFY_TOKEN`.
3. Subscribe the webhook to the **messages** field.
4. Message your business number from a personal WhatsApp account.

## Supabase setup

1. Create a project at supabase.com → copy the Postgres connection string
   (use the connection pooler for serverless/Vercel).
2. Open the SQL editor and run `sql/schema.sql` verbatim.
3. Set `DATABASE_URL` to the pooler URL (it starts with `postgresql://`).

## Deploy

**Render (recommended low-cost):** push to GitHub → Render → New → Blueprint,
select this repo. `render.yaml` provisions the web service + Postgres; set the
secret env vars in the dashboard. Free tier sleeps when idle — fine for a
pilot; `$7/mo` starter keeps it always-on.

**Vercel:** `vercel import` this repo; `vercel.json` routes everything to the
Python function. Set env vars in the project settings. Because sessions live
in Postgres (never in process memory), serverless cold starts are safe.

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

43 tests, all green, no external services:

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

## Migrating (addendum)

`sql/schema.sql` is frozen. New tables live in
`sql/migrations/002_business_owner.sql` — apply once per database:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f sql/migrations/002_business_owner.sql
```

The migration only *adds* tables plus two nullable-with-default columns on
`orders` (`discount_total`, `discount_desc`); existing rows stay valid.

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

- verify `X-Hub-Signature-256` on inbound webhooks (not yet implemented);
- dedupe inbound `wamid`s — Meta redelivers occasionally;
- add rate limiting on `/webhook`;
- treat P2P screenshots as claims, not settled funds;
- see `docs/ARCHITECTURE.md` §9 for the full list of deliberate simplifications.

## License

MIT — see `LICENSE`.
