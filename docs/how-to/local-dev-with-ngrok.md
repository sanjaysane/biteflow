# How-to: local development with ngrok

Develop against the real Meta WhatsApp API from your laptop: expose your
local server through ngrok and point Meta's webhook at it.

## 1. Start the app

```bash
cp .env.example .env   # set WEBHOOK_VERIFY_TOKEN to any secret string
./run.sh               # → http://localhost:8000
curl localhost:8000/health   # {"ok": true, ...}
```

## 2. Expose it

```bash
ngrok http 8000
```

Copy the `https://<id>.ngrok.io` forwarding URL.

## 3. Wire Meta

1. [Meta App Dashboard](https://developers.facebook.com) → your app →
   WhatsApp → Configuration.
2. Callback URL: `https://<id>.ngrok.io/webhook`
3. Verify token: the exact `WEBHOOK_VERIFY_TOKEN` from your `.env`.
4. Click **Verify and save**, then subscribe to the **messages** field.

## 4. Talk to it

Message your WhatsApp business number from a personal account. Say
`hello` — you should get the welcome + role picker. Server logs show each
inbound message; the fake WhatsApp client isn't used here because Meta
delivers real payloads (your `WHATSAPP_TOKEN` is only needed for *sending*,
which works as soon as the token + phone number ID are set).

## Tips

- ngrok free URLs change on every restart — re-paste the callback URL.
- Keep `ngrok http 8000 --region us` close to your Meta app region to cut
  latency.
- To test P2P screenshot approval end-to-end, use two phones: one as
  customer, one as cook.
