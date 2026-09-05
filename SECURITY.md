# Security Policy

## Reporting a vulnerability

**Do not open a public issue for a suspected vulnerability.**
Email the maintainer privately (see the repository owner's profile for
contact details) with:

- what you found and where (file/endpoint),
- steps to reproduce, ideally with a minimal payload,
- what you think the impact is (data exposure, spoofing, money movement).

We will acknowledge within 72 hours, keep you updated on the fix, and
credit you in the release notes unless you prefer anonymity.

## What is currently NOT hardened (read before deploying)

BiteFlow is a working pilot. The following are known gaps — see also
`docs/ARCHITECTURE.md` §10. Do not handle real money-adjacent traffic
until at least the first three are addressed:

1. **No `X-Hub-Signature-256` verification on inbound webhooks.** Anyone
   who knows your `/webhook` URL can inject fake customer/cook messages.
   This is the single most important thing to fix before going live.
2. **No idempotency on inbound `wamid`s.** Meta occasionally redelivers;
   today a redelivered "accept" or payment message is processed twice.
3. **No rate limiting on `/webhook`.** A flood of messages is processed
   synchronously and will queue behind the state machine.
4. **P2P payment "verification" is trust-based.** A screenshot or typed
   reference is accepted as a claim; nothing is checked against a bank,
   and media bytes are never downloaded.
5. **No authentication on app endpoints** beyond the webhook verify token;
   `/health` is intentionally public.
6. Campaign and win-back sends are one-shot chat messages, not WhatsApp
   template messages — production business-initiated outreach needs
   approved templates or Meta will rate-limit/ban the number.

## Safe harbor for researchers

If you follow this policy — private disclosure, no data exfiltration, no
service degradation, no social engineering of cooks/customers — we will
not pursue legal action for your good-faith research.
