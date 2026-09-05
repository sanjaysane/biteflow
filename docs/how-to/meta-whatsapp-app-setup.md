# How-to: Meta WhatsApp app setup

You need a Meta developer app with the WhatsApp product to get a business
number, an API token, and webhook delivery.

## 1. Create the app

1. Go to [developers.facebook.com](https://developers.facebook.com) →
   **My Apps** → **Create App** → choose the **Business** type.
2. In the app dashboard, **Add Product** → **WhatsApp** → **Set up**.

## 2. Get a test number working (5 minutes)

1. WhatsApp → **API Setup**: Meta gives you a free test phone number.
2. Add your personal WhatsApp number as a recipient (verify the code).
3. Note the **temporary access token** and the **Phone number ID**.
4. Send a test message from the API Setup page — it should arrive.

## 3. Connect BiteFlow

In your `.env` (or host dashboard):

```
WHATSAPP_TOKEN=<redacted>            # start with the temporary token
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WEBHOOK_VERIFY_TOKEN=<redacted>  # any secret you invent
```

Restart the app. Outbound messages (menus, order updates) now send for real.

## 4. Subscribe the webhook

Follow `docs/how-to/local-dev-with-ngrok.md` (local) or set the callback
URL to your deployed `https://<host>/webhook` (Render/Vercel). Subscribe
to the **messages** field.

## 5. Go production

1. **Permanent token:** the API Setup token expires in 24h. Create a
   system user (Business Settings → System users) with `whatsapp_business_
   messaging` permission and generate a permanent token.
2. **Your own number:** either port a real number (it can never be used in
   the WhatsApp mobile app again) or use Meta's managed number.
3. **Display name:** get it approved — it shows on every chat.
4. **Template messages:** business-initiated messages (campaigns, win-back)
   require approved templates. BiteFlow's campaigns currently send plain
   chat messages — fine for replies inside the 24h window, but get
   templates approved before any broadcast use (see `SECURITY.md`).

## Cost note

Meta charges per 24-hour conversation, not per message (free tier covers
1,000 service conversations/month). A cook replying to customer-initiated
chats stays in the cheapest category.
