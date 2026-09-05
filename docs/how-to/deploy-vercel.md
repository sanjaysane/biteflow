# How-to: deploy to Vercel

Vercel runs BiteFlow as a serverless Python function. Safe because session
state lives in Postgres, never in process memory.

## 1. Import the repo

1. [vercel.com](https://vercel.com) → **Add New** → **Project** → import
   this repo.
2. `vercel.json` routes all traffic to the Python function — no build
   settings to change.

## 2. Environment variables

Project → Settings → Environment Variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Supabase **pooler** URL (port 6543) — required |
| `WHATSAPP_TOKEN` | permanent token |
| `WHATSAPP_PHONE_NUMBER_ID` | from Meta API Setup |
| `WEBHOOK_VERIFY_TOKEN` | your secret |

⚠️ Use the pooler, not the direct connection string — serverless cold
starts open many short-lived connections.

## 3. Deploy and migrate

Deploy, then run the migrations once against Supabase (SQL editor or
`psql` from your laptop — see `supabase-setup.md`).

## 4. Point Meta at it

Webhook callback URL: `https://<project>.vercel.app/webhook`, subscribe to
**messages**.

## Caveats

- **Cold starts:** first message after idle takes a few seconds; after
  that it's warm. Fine for conversational traffic.
- **No background work:** the daily digest / low-stock sweep need an
  external cron (GitHub Actions schedule works well).
- **Logs:** Vercel function logs are the place to look for
  `[biteflow] handler error` lines.
