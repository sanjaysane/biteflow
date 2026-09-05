# BiteFlow Architecture

BiteFlow is a zero-client WhatsApp micro-commerce platform for home cooks
and their customers. Nobody installs anything: every interaction is a plain
WhatsApp chat driven by single-digit replies, 👍/👎 confirmations, and short
localized text.

## 1. Request flow

```
Meta Cloud API ──POST /webhook──▶ FastAPI (src/main.py)
                                      │
                                      │ 1. parse payload → (phone, text, image?)
                                      │ 2. hydrate chat_sessions row (Postgres)
                                      │ 3. dispatch (role, state) → handler
                                      │ 4. handler replies via WhatsAppClient
                                      │ 5. persist updated session
                                      ▼
                                   Postgres (Supabase) + WhatsApp replies
```

The server process holds **no conversation state**. Every inbound message
rehydrates the session from `chat_sessions` and persists it before returning,
so the app is safe on serverless platforms (Vercel) and multi-worker hosts
(Render) alike.

## 2. The state machine

`src/state_machine.py` owns a single declarative table:

```python
ROUTES = {
    ("customer", "menu_browsing"): customer.handle_menu_browsing,
    ("cook",     "order_inbound_queue"): cook.handle_inbound,
    ...
}
```

`process_incoming(db, wa, i18n, phone, text, …)` builds a `Ctx` (the shared
handler context: db, WhatsApp client, i18n, phone, user row, session dict,
incoming text) and calls the handler for `(role, state)`.

### Global language command
Before dispatch, the strings `"language"`, `"idioma"`, and `"भाषा"` open the
language menu **from any state**. The current `(state, data)` is stashed, and
after a choice the chat resumes exactly where it was — re-rendered in the new
language (`state_machine._handle_language_select`).

### Unknown state
A corrupt/unknown `(role, state)` falls back to a safe hub instead of
crashing: `cook_home` for cooks, fresh cook-browsing for customers.

### Business-owner states (addendum)
The cook home gained two digits: `3` → the 📊 Business hub, `4` → the
📣 Marketing hub. Their states live in `src/owner/states.py` (`O_HOME…`
for kitchen economics, `M_HOME…` for marketing, plus `C_REFERRAL` on the
customer side) and their handlers in `src/owner/handlers.py`, registered in
the same declarative `ROUTES` table. The accessibility contract is
unchanged: single digits and 👍/👎; free-form text appears only in setup
moments (ingredient names, prices, campaign copy) that cannot be digitized.

## 3. Handler context (`src/context.py`)

`Ctx` gives handlers small, safe primitives:

- `reply(key, **vars)` — localized template send to the chat's user
- `send_to(phone, key, lang, **vars)` — cross-chat send (cook ⇄ customer),
  resolved in the *recipient's* language
- `set_state(state, **data)` / `set_state_for(phone, …)` — persist session
- `parse_choice(text, lo, hi)` — bare digits only; `"9"` works, `"nine"` and
  `"1; DROP TABLE"` do not
- `parse_price(text)` — bounded `0.01–999.99` with `Decimal` rounding

## 4. Data model (`sql/schema.sql`)

- `users(phone PK, display_name, system_role, preferred_language, …)`
- `chat_sessions(phone PK, role, state, lang, data JSONB)` — the rehydratable
  conversation cursor; `data` holds cart, pending items, broadcast progress
- `menus(cook_phone FK, item_name, base_price, active)` — only one active
  menu per cook (partial unique index)
- `orders(…, items JSONB, total_sum, payment_type, payment_status,
  payment_proof_ref, order_status, …)` — `items` is a frozen snapshot so
  later menu edits never rewrite history

Two database backends implement the same interface (`src/db.py`):
`PostgresDatabase` (psycopg 3, Supabase) and `FakeDatabase` (in-memory,
drives the entire pytest suite). `sql/schema.sql` is frozen; the addendum's
tables arrive via `sql/migrations/002_business_owner.sql` (ingredients,
recipes + BOM lines, suppliers, purchases, business costs, referrals +
redemptions + credit ledger, offers, campaigns, opt-ins, plus
`orders.discount_total/discount_desc`).

## 5. Payments (`src/payments.py`)

- **COD** — order placed unpaid; customer pays cash at handoff.
- **P2P** — customer uploads a screenshot (WhatsApp image → `photo:<media-id>`)
  or types a reference (`ref:<text>`); order flips to `pending_approval`;
  the cook sees a 1/2 approve-or-deny prompt; approval → `verified`,
  denial → back to `unpaid` with a resend request.
- No money moves through BiteFlow; it only tracks payment *state*.

## 6. Localization (`src/i18n.py`, `locales/`)

JSON tables per language (`en`, `es`, `hi` — mandatory). `I18n.t(lang, key,
**vars)` falls back to English on missing keys and leaves unknown keys
visible as `[key]`. CI asserts identical key sets across all three locales,
and `test_locales.py` asserts every key referenced in code exists.

## 7. WhatsApp client (`src/whatsapp.py`)

`MetaWhatsAppClient` posts to
`https://graph.facebook.com/v21.0/<phone-number-id>/messages` with a bearer
token. `FakeWhatsAppClient` records outbound messages for tests.

## 8. Deployment

- **Render**: `render.yaml` blueprint — web service + Postgres, free tier
  friendly, `/health` health check.
- **Vercel**: `vercel.json` — `@vercel/python` serverless function; sessions
  in Postgres make this stateless-safe.
- **Local**: `./run.sh` (loads `.env`, uvicorn with reload), or expose with
  ngrok for Meta webhook testing.

## 9. Business-owner addendum (`src/owner/`)

New application code lives **only** under `src/owner/`; new SQL **only** in
`sql/migrations/002_business_owner.sql`.

**Domain 1 — kitchen economics** (`economics.py` + `O_*` handlers):
inventory with low-stock latching alerts (one ping per breach until stock
recovers), recipes as bills of materials with food-cost/margin math,
suppliers + purchase logging, recent-sales velocity → weekly procurement
suggestions, daily P&L digest, capex/opex ledger, weekly food-cost
projection, and COD/P2P payment reconciliation. Accepting an order consumes
recipe-backed stock and sweeps low stock inline.

**Domain 2 — marketing & growth** (`marketing.py` + `M_*` handlers):
dual-sided referrals (redeemer discount + referrer credit ledger, capped at
the order total), cook-configurable first-order offers (percent / free item /
free delivery, once per customer), broadcast campaigns restricted to opted-in
recipients with explicit cook confirmation, and 14-day win-back with 30-day
re-nudge suppression. Customers get an opt-in ask after their first accepted
order; `STOP` opts out globally at any time.

**Counterfactual path** — `apply_ingredient_price_change()`: persists the new
supplier price, recomputes every affected recipe, flags dishes under the 20%
margin floor, and sends the cook exactly one WhatsApp alert (idempotent on
re-runs). It is wired into the restock flow — when the cook logs a purchase
at a changed price, the alert fires inline — and the same margin sweep runs
before every menu broadcast as a safety net.

**Schedulers (external cron required):** `digest.send_daily_digest()` for the
evening P&L ping and `economics.check_low_stock()` for alert sweeps — pure
functions, no cron bundled in this repo.

## 10. Deliberate simplifications (not production-hardened yet)

- **No signature verification** of Meta webhooks (`X-Hub-Signature-256`).
  Add it before handling real money-adjacent traffic.
- **No idempotency/dedup** on inbound `wamid`s; Meta may redeliver.
- **No rate limiting** on `/webhook`.
- **P2P proof is trust-based**: a screenshot is accepted as evidence, and
  `media_id`s are not downloaded/inspected.
- **No auth on endpoints** beyond the verify token; `/health` is public.
- Prices are `NUMERIC(10,2)` with no currency column — single-currency
  assumption per deployment.
- Cook discovery is a plain list; no search, geo, ratings, or scheduling.
- Media handling stores only the Meta `media_id`, never the file bytes.
- **Owner addendum, honestly:**
  - Discounts never stack above the order total (aggregate cap), but
    stacked first-order + referral + credit on one order is allowed by
    design — the cook cannot yet limit "one promo per order".
  - The free-item offer discounts the cheapest cart unit rather than
    validating the configured dish is in the cart.
  - Recipe matching to order items is by exact dish name; a renamed menu
    item silently skips stock consumption.
  - Low-stock alerts are per-cook WhatsApp pings with no quiet hours.
  - Campaigns send via the WhatsApp client in a loop — no batching,
    no per-second rate control, no delivery receipts.
  - Win-back and campaign sends are one-shot chat messages, not WhatsApp
    template messages; production would need approved templates for
    business-initiated outreach.
  - The P&L treats discounts as contra-revenue and ignores payment fees,
    taxes, and waste.
  - The migration was validated against PostgreSQL 16 (parses under
    libpg_query, applies cleanly, all owner code paths exercised); the
    pytest suite itself runs against `FakeDatabase`.
