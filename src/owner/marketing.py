"""Marketing & growth engine: referrals, freemium offers, win-back.

Pure-ish workflow helpers shared by the conversational handlers and by
tests. WhatsApp sends stay in the handlers; this module computes who gets
what and records it.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from ..db import Database
from ..payments import money
from . import states as S


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── referrals ────────────────────────────────────────────────────────
def get_or_create_referral(
    db: Database, cook_phone: str, referrer_phone: str, reward_amount: float = 2.00
) -> dict:
    """One code per referrer per cook; idempotent."""
    for ref in db.get_referrals_for_cook(cook_phone):
        if ref["referrer_phone"] == referrer_phone:
            return ref
    base = "BITE-" + re.sub(r"\D", "", cook_phone)[-4:]
    code, suffix = base, 2
    while db.get_referral_by_code(code) is not None:
        code = f"{base}-{suffix}"
        suffix += 1
    return db.create_referral(cook_phone, code, referrer_phone, reward_amount)


def apply_referral(
    db: Database,
    cook_phone: str,
    redeemer_phone: str,
    code: str,
    order_total: float,
    lang: str = "en",
) -> dict:
    """Validate a typed code and compute the discount.

    Returns {"ok", "discount", "desc", "referral_id", "reason"}.
    One redemption per (code, customer). The referrer earns credit at
    order-creation time (see finalize_referral below), not here.
    """
    code = (code or "").strip().upper()
    ref = db.get_referral_by_code(code)
    if ref is None or ref["cook_phone"] != cook_phone:
        return {
            "ok": False,
            "discount": 0.0,
            "desc": "",
            "referral_id": None,
            "reason": "unknown_code",
        }
    if ref["referrer_phone"] == redeemer_phone:
        return {
            "ok": False,
            "discount": 0.0,
            "desc": "",
            "referral_id": None,
            "reason": "own_code",
        }
    if db.has_redeemed(int(ref["id"]), redeemer_phone):
        return {
            "ok": False,
            "discount": 0.0,
            "desc": "",
            "referral_id": None,
            "reason": "already_used",
        }
    discount = round(min(float(ref["reward_amount"]), float(order_total)), 2)
    return {
        "ok": True,
        "discount": discount,
        "desc": f"Referral {code} −{money(discount, lang)}",
        "referral_id": int(ref["id"]),
        "reason": "",
    }


def finalize_referral(
    db: Database, cook_phone: str, referral_id: int, redeemer_phone: str, order_id: int
) -> None:
    """Called once the discounted order is created: record redemption and
    credit the referrer (dual-sided reward). Idempotent per order."""
    ref = db.get_referral_by_id(cook_phone, referral_id)
    if ref is None:
        return
    if db.record_redemption(referral_id, redeemer_phone, order_id):
        db.add_credit_ledger(
            cook_phone,
            ref["referrer_phone"],
            float(ref["reward_amount"]),
            f"referral {ref['code']} used by {redeemer_phone}",
        )


def referrer_credit_available(db: Database, cook_phone: str, phone: str) -> float:
    return round(max(0.0, db.get_credit_balance(cook_phone, phone)), 2)


def consume_referrer_credit(
    db: Database, cook_phone: str, phone: str, order_total: float, lang: str = "en"
) -> dict:
    """Auto-apply earned credit to the referrer's own order review."""
    balance = referrer_credit_available(db, cook_phone, phone)
    if balance <= 0:
        return {"discount": 0.0, "desc": ""}
    use = round(min(balance, order_total), 2)
    db.add_credit_ledger(cook_phone, phone, -use, "credit applied to own order")
    return {"discount": use, "desc": f"Referral credit −{money(use, lang)}"}


# ── freemium first-order offers ──────────────────────────────────────
def is_first_order(db: Database, cook_phone: str, customer_phone: str) -> bool:
    """True when the customer has no completed order with this cook."""
    for order in db.get_completed_orders(cook_phone):
        if order["customer_phone"] == customer_phone:
            return False
    return True


def first_order_offer(
    db: Database,
    cook_phone: str,
    customer_phone: str,
    cart_total: float,
    cart: list[dict],
    lang: str = "en",
) -> dict:
    """Auto-applied freemium for first-time customers. {"discount", "desc"}."""
    if not is_first_order(db, cook_phone, customer_phone):
        return {"discount": 0.0, "desc": ""}
    offer = db.get_active_offer(cook_phone)
    if offer is None:
        return {"discount": 0.0, "desc": ""}
    otype = offer["offer_type"]
    if otype == "first_order_percent_off":
        try:
            pct = max(0.0, min(100.0, float(offer["value_text"])))
        except ValueError:
            return {"discount": 0.0, "desc": ""}
        discount = round(cart_total * pct / 100.0, 2)
        return {
            "discount": discount,
            "desc": f"First-order {pct:g}% off −{money(discount, lang)}",
        }
    if otype == "first_order_free_item":
        # value_text holds the menu item name; cheapest cart line free.
        if not cart:
            return {"discount": 0.0, "desc": ""}
        cheapest = min(float(c["price"]) for c in cart)
        return {
            "discount": round(cheapest, 2),
            "desc": f"First order: free {offer['value_text']} 🎁",
        }
    if otype == "first_order_free_delivery":
        try:
            flat = max(0.0, float(offer["value_text"] or 2.0))
        except ValueError:
            flat = 2.0
        discount = round(min(flat, cart_total), 2)
        return {
            "discount": discount,
            "desc": f"First order: free delivery −{money(discount, lang)} 🛵",
        }
    return {"discount": 0.0, "desc": ""}


# ── win-back ─────────────────────────────────────────────────────────
def find_winback_candidates(
    db: Database, cook_phone: str, days: int = S.WINBACK_DAYS
) -> list[dict]:
    """Opted-in customers whose last completed order is ≥ `days` old and
    who have not been nudged in the last 30 days."""
    cutoff = utcnow() - timedelta(days=days)
    renudge_cutoff = utcnow() - timedelta(days=30)
    opted_in = set(db.get_opted_in_customers(cook_phone))
    cands = []
    for phone, last_iso in db.get_customer_last_order(cook_phone).items():
        if phone not in opted_in:
            continue
        try:
            last = datetime.fromisoformat(last_iso)
        except (ValueError, TypeError):
            continue
        if last.replace(tzinfo=timezone.utc) > cutoff:
            continue
        cands.append({"phone": phone, "last_order": last_iso})
    # filter recent nudges
    fresh = []
    for c in cands:
        if db.get_last_winback_at(cook_phone, c["phone"]) is None:
            fresh.append(c)
        else:
            try:
                sent = datetime.fromisoformat(
                    db.get_last_winback_at(cook_phone, c["phone"])
                )
                if sent.replace(tzinfo=timezone.utc) <= renudge_cutoff:
                    fresh.append(c)
            except (ValueError, TypeError):
                fresh.append(c)
    return fresh
