"""Owner addendum — Domain 2: marketing & growth.

Covers: referral discount application (typed code at review), single-use
enforcement, dual-sided referrer credit, freemium first-order offers,
campaign opt-in filtering, the 14-day win-back, and the opt-in/STOP flow.
"""

from datetime import timedelta

from tests.conftest import COOK, CUST

from src.db import utcnow
from src.owner import marketing as MK


CUST_B = "+15550004444"
CUST_C = "+15550005555"


def _to_payment(send, db, cust):
    """Drive a fresh customer: hello → cook → item → qty → checkout →
    review → confirm → COD. Returns the created order id."""
    send(cust, "hello")
    send(cust, "1")   # register as customer → cook list
    send(cust, "1")   # pick the cook → menu
    send(cust, "1")   # Veg Pulao × …
    send(cust, "1")   # … qty 1 → back to menu
    send(cust, "0")   # checkout → review ($8.50)
    assert db.get_session(cust)["state"] == "order_review"
    send(cust, "1")   # confirm → payment
    send(cust, "1")   # COD → tracking
    return db.get_session(cust)["data"]["order_id"]


def _cook_to(db, send, *choices):
    """Walk the cook through menu choices; returns nothing."""
    for c in choices:
        send(COOK, c)


# ── referrals ────────────────────────────────────────────────────────
def test_referral_discount_application(db, wa, send, cook_with_menu):
    ref = MK.get_or_create_referral(db, COOK, COOK, reward_amount=2.00)
    # fresh customer → review → 5 → code → confirm → COD
    send(CUST, "hello")
    send(CUST, "1")   # register as customer
    send(CUST, "1")   # pick the cook
    send(CUST, "1")   # Veg Pulao × …
    send(CUST, "1")   # … qty 1 → back to menu
    send(CUST, "0")   # checkout → review
    assert db.get_session(CUST)["state"] == "order_review"
    wa.clear()
    send(CUST, "5")
    assert "referral code" in wa.last_to(CUST).lower()
    send(CUST, ref["code"].lower())   # codes are case-insensitive
    assert "−$2.00" in wa.last_to(CUST)
    send(CUST, "1")                   # confirm
    send(CUST, "1")                   # COD
    order_id = db.get_session(CUST)["data"]["order_id"]
    order = db.get_order(order_id)
    assert order["discount_total"] == 2.00
    assert "Referral" in order["discount_desc"]
    # Dual-sided: the referrer (cook) earned $2 credit.
    assert MK.referrer_credit_available(db, COOK, COOK) == 2.00
    # The cook's NEW ORDER ping shows the NET total ($8.50 − $2.00).
    assert "Total: $6.50" in wa.last_to(COOK)


def test_referral_reuse_rejected(db, wa, send, cook_with_menu):
    ref = MK.get_or_create_referral(db, COOK, COOK, reward_amount=2.00)
    MK.apply_referral(db, COOK, CUST, ref["code"], 8.50)
    db.record_redemption(ref["id"], CUST, order_id=None)
    result = MK.apply_referral(db, COOK, CUST, ref["code"], 8.50)
    assert result == {"ok": False, "discount": 0.0, "desc": "",
                      "referral_id": None, "reason": "already_used"}


def test_referral_unknown_and_own_code(db):
    ref = MK.get_or_create_referral(db, COOK, COOK, reward_amount=2.00)
    assert MK.apply_referral(
        db, COOK, CUST, "NOPE-1234", 8.50)["reason"] == "unknown_code"
    assert MK.apply_referral(
        db, COOK, COOK, ref["code"], 8.50)["reason"] == "own_code"


def test_referrer_credit_auto_applies(db, wa, send, cook_with_menu):
    # CUST_B refers CUST; CUST's order earns CUST_B $2 credit …
    ref = MK.get_or_create_referral(db, COOK, CUST_B, reward_amount=2.00)
    order = db.create_order(customer_phone=CUST, cook_phone=COOK,
                            ordered_items=[{"item": "Veg Pulao",
                                            "quantity": 1, "price": 8.50}],
                            total_sum=8.50, payment_type="COD")
    MK.finalize_referral(db, COOK, ref["id"], CUST, order["id"])
    assert MK.referrer_credit_available(db, COOK, CUST_B) == 2.00
    # … which auto-applies to CUST_B's own next order.
    order_id = _to_payment(send, db, CUST_B)
    order2 = db.get_order(order_id)
    assert order2["discount_total"] == 2.00
    assert "Referral credit" in order2["discount_desc"]
    assert MK.referrer_credit_available(db, COOK, CUST_B) == 0.00


# ── freemium first-order offers ──────────────────────────────────────
def test_stacked_discounts_capped_at_total(db, wa, send, cook_with_menu):
    ref = MK.get_or_create_referral(db, COOK, COOK, reward_amount=2.00)
    db.add_credit_ledger(COOK, CUST, 10.00, "test top-up")
    db.set_offer(COOK, "first_order_percent_off", "10")
    # review → 5 → referral code → confirm → COD
    send(CUST, "hello")
    send(CUST, "1")
    send(CUST, "1")
    send(CUST, "1")
    send(CUST, "1")
    send(CUST, "0")
    send(CUST, "5")
    send(CUST, ref["code"])
    send(CUST, "1")   # confirm → payment
    send(CUST, "1")   # COD
    order_id = db.get_session(CUST)["data"]["order_id"]
    order = db.get_order(order_id)
    # $2.00 referral + $0.85 offer + $5.65 credit = $8.50: never above total.
    assert order["discount_total"] == 8.50
    assert round(order["total_sum"] - order["discount_total"], 2) == 0.00
    # Only the applied credit left the ledger; the rest stays.
    assert MK.referrer_credit_available(db, COOK, CUST) == 4.35


def test_first_order_offer_auto_applies(db, wa, send, cook_with_menu):
    db.set_offer(COOK, "first_order_percent_off", "10")
    order_id = _to_payment(send, db, CUST)
    order = db.get_order(order_id)
    assert order["discount_total"] == 0.85   # 10% of $8.50
    assert "First-order" in order["discount_desc"]
    # Second order: no longer a first order → no offer.
    db.update_order(order_id, order_status="completed")
    assert MK.is_first_order(db, COOK, CUST) is False
    cart = [{"item_name": "Veg Pulao", "price": 8.50, "qty": 1}]
    assert MK.first_order_offer(db, COOK, CUST, 8.50, cart) == {
        "discount": 0.0, "desc": ""}


def test_offer_disabled_applies_nothing(db, send, cook_with_menu):
    db.set_offer(COOK, "first_order_percent_off", "10")
    db.deactivate_offers(COOK)
    order_id = _to_payment(send, db, CUST)
    assert db.get_order(order_id)["discount_total"] == 0.00


# ── campaigns: opted-in customers only ──────────────────────────────
def test_campaign_optin_filtering(db, wa, send, cook_with_menu):
    db.set_optin(COOK, CUST, True)
    db.set_optin(COOK, CUST_B, False)   # explicitly declined
    # CUST_C never asked → not opted in.
    wa.clear()
    _cook_to(db, send, "4", "3")        # Marketing → Campaign
    send(COOK, "Diwali Special")
    send(COOK, "20% off all thalis today!")
    assert "1 opted-in" in wa.last_to(COOK)
    send(COOK, "1")                     # confirm send
    got = {to for to, _ in wa.sent}
    assert CUST in got
    assert CUST_B not in got and CUST_C not in got
    assert "STOP" in wa.last_to(CUST)   # opt-out footer always attached


def test_campaign_cancel_sends_nothing(db, wa, send, cook_with_menu):
    db.set_optin(COOK, CUST, True)
    wa.clear()
    _cook_to(db, send, "4", "3")
    send(COOK, "Hello")
    send(COOK, "World")
    send(COOK, "👎")
    assert all(to != CUST for to, _ in wa.sent)


# ── win-back: 14+ days inactive, opted-in, not recently nudged ───────
def _completed_order(db, cust, days_ago):
    order = db.create_order(
        customer_phone=cust, cook_phone=COOK,
        ordered_items=[{"item": "Veg Pulao", "quantity": 1, "price": 8.50}],
        total_sum=8.50, payment_type="COD")
    db.orders[order["id"]]["creation_time"] = utcnow() - timedelta(
        days=days_ago)
    db.update_order(order["id"], order_status="completed")
    return order


def test_winback_candidates(db):
    _completed_order(db, CUST, 20)      # quiet 20d, will opt in
    _completed_order(db, CUST_B, 5)     # active recently
    _completed_order(db, CUST_C, 20)    # quiet but never opted in
    db.set_optin(COOK, CUST, True)
    db.set_optin(COOK, CUST_B, True)
    cands = MK.find_winback_candidates(db, COOK)
    assert [c["phone"] for c in cands] == [CUST]


def test_winback_send_and_no_renudge(db, wa, send, cook_with_menu):
    _completed_order(db, CUST, 20)
    db.set_optin(COOK, CUST, True)
    wa.clear()
    _cook_to(db, send, "4", "4")        # Marketing → Win-back
    assert "1 customers" in wa.last_to(COOK)
    send(COOK, "1")
    assert "10%" in wa.last_to(CUST)
    assert "STOP" in wa.last_to(CUST)
    # Nudged just now → no longer a candidate (30-day quiet period).
    assert MK.find_winback_candidates(db, COOK) == []


# ── opt-in ask on accept + STOP ──────────────────────────────────────
def test_optin_ask_and_stop(db, wa, send, cook_with_menu):
    order_id = _to_payment(send, db, CUST)
    # Cook's session was pushed to the inbound queue by the order.
    send(COOK, "1")                     # accept
    assert db.get_session(CUST)["state"] == "marketing_optin"
    assert "menu updates" in wa.last_to(CUST)
    wa.clear()
    send(CUST, "1")                     # yes please
    assert db.get_opted_in_customers(COOK) == [CUST]
    assert "STOP" in wa.last_to(CUST)
    # STOP works from any state afterwards.
    send(CUST, "STOP")
    assert db.get_opted_in_customers(COOK) == []
    assert "opted out" in wa.last_to(CUST).lower()
