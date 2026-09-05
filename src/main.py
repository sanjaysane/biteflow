"""BiteFlow webhook orchestrator (FastAPI).

Endpoints:
  GET  /webhook  – Meta webhook verification handshake
                   (hub.mode / hub.verify_token / hub.challenge)
  POST /webhook  – inbound WhatsApp messages from the Meta Cloud API.
                   Parses the nested payload, hydrates the chat session,
                   dispatches through the state machine, always 200s.
  GET  /health   – liveness probe for Render/Vercel.

The process holds no conversation state: every POST hydrates from
Postgres (chat_sessions) and persists before returning.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse

from .config import settings
from .db import FakeDatabase, PostgresDatabase, normalize_phone
from .i18n import I18n
from .state_machine import process_incoming
from .whatsapp import FakeWhatsAppClient, MetaWhatsAppClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db, app.state.wa, app.state.i18n = build_runtime()
    yield


app = FastAPI(title="BiteFlow", version="0.1.0", lifespan=lifespan)


def build_runtime():
    """Construct (db, wa, i18n) from the environment.

    Falls back to in-memory fakes when env vars are absent so the app
    boots for local development and tests without credentials.
    """
    i18n = I18n(settings.locales_dir)
    if settings.database_url:
        db = PostgresDatabase(settings.database_url)
    else:
        db = FakeDatabase()
    if settings.whatsapp_token and settings.whatsapp_phone_number_id:
        wa = MetaWhatsAppClient(
            settings.whatsapp_token,
            settings.whatsapp_phone_number_id,
            api_base=settings.whatsapp_api_base,
        )
    else:
        wa = FakeWhatsAppClient()
    return db, wa, i18n


@app.get("/health")
def health():
    return {"ok": True, "service": "biteflow"}


# ── Meta webhook verification ──────────────────────────────────────
@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.webhook_verify_token:
        return PlainTextResponse(hub_challenge)
    return PlainTextResponse("forbidden", status_code=403)


# ── Inbound messages ───────────────────────────────────────────────
def _extract_messages(payload: dict):
    """Yield (from_phone, text, msg_type, media_id) from a Meta payload."""
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                raw_from = msg.get("from", "")
                phone = normalize_phone(raw_from)
                if not phone:
                    continue
                mtype = msg.get("type", "")
                text, media_id = None, None
                if mtype == "text":
                    text = (msg.get("text") or {}).get("body")
                elif mtype == "image":
                    media_id = (msg.get("image") or {}).get("id")
                    text = (msg.get("image") or {}).get("caption")
                elif mtype == "button":
                    text = (msg.get("button") or {}).get("text")
                yield (
                    phone,
                    text,
                    mtype if mtype in ("text", "image") else "other",
                    media_id,
                )


@app.post("/webhook")
async def receive_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001 - malformed body must not 500 a webhook
        return {"ok": False, "error": "invalid JSON"}
    if not isinstance(payload, dict):
        return {"ok": True}
    for phone, text, mtype, media_id in _extract_messages(payload):
        try:
            process_incoming(
                app.state.db,
                app.state.wa,
                app.state.i18n,
                phone,
                text,
                msg_type=mtype,
                media_id=media_id,
                default_lang=settings.default_language,
            )
        except Exception as exc:  # noqa: BLE001 - never 500 a webhook; log and continue
            print(f"[biteflow] handler error for {phone}: {exc!r}")
    return {"ok": True}
