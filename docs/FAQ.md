# BiteFlow FAQ

## Product

**Who is BiteFlow for?**
Home cooks (tiffin services, home bakers, meal-prep sellers) and their
regular customers — especially senior citizens who find food-delivery apps
overwhelming. Nobody installs anything; everything happens in WhatsApp.

**How do customers order without typing?**
Every step is a single digit (`Reply 1`) or 👍/👎. The only free-form
moments are setup (cook's dish names and prices, a customer's name) — never
in the ordering loop.

**Which languages are supported?**
English, Spanish, and Hindi today. Any chat can switch mid-conversation by
sending `language`, `idioma`, or `भाषा`. Adding a language means adding one
JSON file in `locales/` with the same keys — see `scripts/check_locales.py`.

**How do payments work?**
Cash on Delivery, or peer-to-peer transfer (Zelle/Venmo/UPI/Pix). For P2P
the customer sends a screenshot or typed reference; the order goes to
`pending_approval` and the cook approves with a single digit. The screenshot
is a *claim*, not verified funds — see `SECURITY.md`.

**Does the cook get business tools, or just order notifications?**
Both. From the cook home, `3` opens the 📊 Business hub (inventory,
recipes with food-cost math, suppliers, procurement plan, daily P&L, capex/
opex) and `4` opens the 📣 Marketing hub (referrals, first-order offers,
broadcast campaigns to opted-in customers, win-back).

## Technical

**What does it cost to run?**
Near-zero for a pilot: Supabase free tier (Postgres) + Render free tier
(sleeps when idle) or Vercel hobby. A small always-on setup is roughly
$7–12/month.

**Why does the app work on serverless if WhatsApp is conversational?**
Conversation state lives in Postgres (`chat_sessions`), never in process
memory. Every webhook hydrates the session from the DB, handles one
message, and persists. Cold starts are harmless.

**How do scheduled things (daily P&L, low-stock sweeps) run?**
They don't, by themselves — the repo exposes pure functions
(`src/owner/digest.py::send_daily_digest`, `src/owner/economics.py::
check_low_stock`) and expects an external cron (Render cron job, GitHub
Actions schedule, or a phone alarm + a curl). See `docs/how-to/`.

**Can one deployment serve many cooks?**
Yes — cooks are just phone numbers with the `cook` role. Each cook has
their own menus, inventory, and customers. There is no multi-tenancy
isolation beyond the phone-number key; for unrelated businesses sharing one
deployment, consider separate databases.

**How do I add a fourth language?**
Copy `locales/en.json` to `locales/<iso>.json`, translate every value
(keeping `{placeholders}` identical), register the ISO code where languages
are listed (`src/models.py` and the language-select handler), and run
`python scripts/check_locales.py`.
