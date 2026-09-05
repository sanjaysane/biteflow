"""Daily P&L WhatsApp digest: formatted, sent once to the cook.

Called from the cook's WhatsApp home ("Business" → "Today's P&L") and from a
scheduler/cron (one cron entry per cook, idempotency enforced by the caller
recording the send time — see docs/ARCHITECTURE.md).
"""

from __future__ import annotations

from datetime import datetime

from ..db import Database
from ..i18n import I18n
from ..payments import money
from ..whatsapp import WhatsAppClient
from .economics import daily_pnl


def send_daily_digest(
    db: Database,
    wa: WhatsAppClient,
    i18n: I18n,
    cook_phone: str,
    day: datetime | None = None,
) -> dict:
    """Compute today's P&L and WhatsApp it to the cook. Returns the P&L."""
    pnl = daily_pnl(db, cook_phone, day=day)
    user = db.get_user(cook_phone) or {}
    lang = user.get("preferred_language", "en")

    lines = [i18n.t(lang, "o_digest_title")]
    lines.append(i18n.t(lang, "o_digest_rev", rev=money(pnl["revenue"])))
    lines.append(i18n.t(lang, "o_digest_food", cost=money(pnl["food_cost"])))
    lines.append(i18n.t(lang, "o_digest_opex", opex=money(pnl["opex"])))
    lines.append(i18n.t(lang, "o_digest_capex", capex=money(pnl["capex"])))
    lines.append(i18n.t(lang, "o_digest_net", net=money(pnl["net"])))
    for d in pnl["dishes"]:
        m = f"{d['margin'] * 100:.0f}" if d["margin"] is not None else "–"
        lines.append(
            i18n.t(
                lang,
                "o_digest_dish",
                dish=d["dish"],
                qty=d["qty"],
                rev=money(d["revenue"]),
                margin=m,
            )
        )
    wa.send_text(cook_phone, "\n".join(lines))
    return pnl
