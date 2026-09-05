# How-to: deploy to Render

Render is the recommended low-cost host: the repo ships a blueprint that
provisions the web service and Postgres together.

## 1. Push to GitHub

Render deploys from your repo. Push `main` — CI must be green first.

## 2. Launch the blueprint

1. [dashboard.render.com](https://dashboard.render.com) → **New** →
   **Blueprint** → connect this repo.
2. Render reads `render.yaml` and proposes a web service + Postgres.
3. Fill in the secrets it can't know:
   - `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
   - `WEBHOOK_VERIFY_TOKEN` (must match what you type into Meta)
   - `DATABASE_URL` is wired automatically from the Render Postgres.
4. **Apply.** First deploy takes a few minutes.

## 3. Run migrations

The blueprint's web service runs `./run.sh`-equivalent via uvicorn, but
migrations are **not** automatic on Render (unlike the Docker entrypoint).
Run them once against the Render Postgres:

```bash
# from your laptop, with the Render DB external URL:
psql "$RENDER_DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f sql/schema.sql -f sql/migrations/002_business_owner.sql
```

Find the external URL under the Postgres service → **Connect**.

## 4. Point Meta at it

Webhook callback URL: `https://<your-service>.onrender.com/webhook`.
Subscribe to **messages**. Send `hello` from your phone.

## 5. Schedulers

Render's free tier has no cron. For the daily P&L digest and low-stock
sweep, either:

- add a **Render Cron Job** (paid tier) hitting a tiny wrapper, or
- run a GitHub Actions `schedule` workflow that calls a small script
  using `src/owner/digest.py` / `check_low_stock` against `DATABASE_URL`.

## Cost

Free tier: sleeps after inactivity (first message wakes it in ~30s — fine
for a pilot). Starter `$7/mo` keeps it always-on.
