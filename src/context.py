"""Shared per-message context and input-parsing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .db import Database
from .i18n import I18n
from .payments import currency_symbol
from .payments import money as _money
from .whatsapp import WhatsAppClient


@dataclass
class Ctx:
    db: Database
    wa: WhatsAppClient
    i18n: I18n
    phone: str  # E.164 sender
    user: dict | None  # users row or None
    session: dict  # {"role","state","lang","data"}
    text: str | None  # message text (None for non-text)
    msg_type: str  # "text" | "image" | "other"
    media_id: str | None = None  # Meta media id for images
    lang: str = "en"
    default_lang: str = "en"

    # ── messaging ──
    def reply(self, key: str, **kwargs) -> None:
        self.wa.send_text(self.phone, self.i18n.t(self.lang, key, **kwargs))

    def send_to(self, phone: str, key: str, lang: str, **kwargs) -> None:
        self.wa.send_text(phone, self.i18n.t(lang, key, **kwargs))

    # ── locale-aware helpers ──
    def money(self, value: float | str) -> str:
        """Format money with the currency of the READER's locale
        (₹ for hi/mr, $ for en/es)."""
        return _money(value, self.lang)

    def currency(self) -> str:
        return currency_symbol(self.lang)

    # ── session ──
    def set_state(self, state: str, **data_updates) -> None:
        self.session["state"] = state
        self.session.setdefault("data", {}).update(data_updates)
        self.db.save_session(self.phone, self.session)

    def set_state_for(
        self, phone: str, role: str, state: str, lang: str, **data
    ) -> None:
        self.db.save_session(
            phone, {"role": role, "state": state, "lang": lang, "data": data}
        )


# ── Secure input parsing ───────────────────────────────────────────
# Senior-friendly AND injection-safe: only bare 1-2 digit replies are
# accepted as choices. Anything else → polite re-prompt, never a crash.

_CHOICE_RE = re.compile(r"^\d{1,2}$")
_PRICE_RE = re.compile(r"^\d{1,6}(\.\d{1,2})?$")


def parse_choice(text: str | None, low: int, high: int) -> int | None:
    """Parse '3' → 3 when low <= 3 <= high, else None. Rejects '3;',
    'three', '1 OR 1=1', emoji-mixed input, etc."""
    if not text:
        return None
    s = text.strip()
    if not _CHOICE_RE.fullmatch(s):
        return None
    value = int(s)
    return value if low <= value <= high else None


def parse_price(text: str | None) -> float | None:
    """Parse '8.50' → 8.5. Returns None for anything not a positive amount."""
    if not text:
        return None
    s = text.strip().lstrip("$₹")
    if not _PRICE_RE.fullmatch(s):
        return None
    try:
        value = float(s)
    except ValueError:
        return None
    return value if value > 0 else None


def cart_lines(cart: list[dict]) -> list[str]:
    return [f"{i['item_name']} × {i['qty']}" for i in cart]
