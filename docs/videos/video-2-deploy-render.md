# Video 2 script: Deploy BiteFlow to Render

**Format:** screencast with voiceover. **Length:** ~10–12 min.
**Audience:** a junior developer with the repo cloned. **Goal:** a public
URL taking real WhatsApp orders.

---

## Scene 1 — Cold open (0:00–0:30)

**On screen:** Title card — "BiteFlow on Render: from repo to real orders."

**Say:** "Local works. Now let's put BiteFlow on the public internet with
Render's blueprint — web service plus Postgres in a few clicks — then wire
Meta's webhook and take a real order from a real phone."

## Scene 2 — Push and blueprint (0:30–3:00)

**On screen:** Push `main` to GitHub (CI green badge visible). Render
dashboard → New → Blueprint → select repo. Show `render.yaml` in the
editor briefly.

**Say:** "The blueprint provisions both services. You only fill in the
secrets Render can't know: your WhatsApp token, phone number ID, and the
webhook verify token — which must match what you'll type into Meta."

**On-screen text:** `render.yaml → web + Postgres` · `secrets: WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN`

## Scene 3 — Migrate (3:00–5:00)

**On screen:** Terminal:

```bash
psql "$RENDER_DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f sql/schema.sql -f sql/migrations/002_business_owner.sql
```

Then show the tables in Render's Postgres dashboard.

**Say:** "Migrations don't run automatically on Render, so we apply them
once from the laptop. Schema is frozen; the addendum is a numbered
migration — this is the pattern for every future change."

**On-screen text:** `schema.sql frozen → migrations only`

## Scene 4 — Wire the Meta webhook (5:00–7:30)

**On screen:** Meta App Dashboard → WhatsApp → Configuration. Paste
`https://<service>.onrender.com/webhook`, the verify token, Verify and
save, subscribe to **messages**.

**Say:** "This is the handshake from video one's ngrok guide, but with a
stable URL. If verification fails, it's almost always whitespace in the
env var — check the troubleshooting doc."

**On-screen text:** `callback → https://<service>.onrender.com/webhook` · `subscribe: messages`

## Scene 5 — First real order (7:30–10:30)

**On screen:** Split screen — phone (customer) and laptop logs. Send
`hello`, order a dish, pay cash. Then the cook phone: accept, mark
cooking, mark done. Show the customer receiving each update.

**Say:** "Watch the logs: every message hydrates the session from
Postgres, routes through the state machine, and persists. Kill the
service mid-order and it resumes — that's the stateless design earning
its keep."

**On-screen text:** `stateless: session in Postgres, not memory`

## Scene 6 — Outro (10:30–11:00)

**On screen:** Title card — "Next: a cook's first day → video 3." Plus a
honest footer: "Pilot, not hardened — see SECURITY.md before real money."

**Say:** "It's live. Before real customers, read SECURITY.md — webhook
signature verification is the first hardening job. Next video is for the
cook: menus, orders, and the business hub."
