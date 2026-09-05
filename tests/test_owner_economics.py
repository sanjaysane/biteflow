"""Owner addendum — Domain 1: kitchen economics & operations.

Covers: recipe food-cost math, low-stock alert firing (once per breach),
stock consumption on accept, the weekly purchase plan, the daily P&L, and
the pre-broadcast margin warning. The paneer price-doubling counterfactual
lives in test_owner_paneer.py.
"""

from datetime import timedelta

from src.db import utcnow
from src.owner import economics as E
from tests.conftest import COOK, CUST


def _kitchen(db, cook=COOK):
    """Paneer Pulao kitchen: paneer $8/kg, peas $3/kg, menu price $5.00.

    Food cost = 0.25×8 + 0.10×3 = $2.30 → margin 54% (healthy).
    """
    paneer = db.add_ingredient(cook, "Paneer", "kg", 8.00, 10.0, 1.0)
    peas = db.add_ingredient(cook, "Peas", "kg", 3.00, 5.0, 0.5)
    rice = db.add_ingredient(cook, "Rice", "kg", 2.00, 20.0, 2.0)
    menu = db.add_menu_item(cook, "Paneer Pulao", "", 5.00, "en")
    db.add_menu_item(cook, "Jeera Rice", "", 4.00, "en")
    recipe = db.add_recipe(cook, "Paneer Pulao", menu["id"])
    db.add_recipe_item(recipe["id"], paneer["id"], 0.25)
    db.add_recipe_item(recipe["id"], peas["id"], 0.10)
    jr = db.add_recipe(cook, "Jeera Rice")
    db.add_recipe_item(jr["id"], rice["id"], 0.20)
    return {"paneer": paneer, "peas": peas, "rice": rice}


# ── recipe food-cost math ────────────────────────────────────────────
def test_recipe_food_cost_calculation(db):
    _kitchen(db)
    recipe = next(r for r in db.get_recipes(COOK) if r["dish_name"] == "Paneer Pulao")
    items = db.get_recipe_items(recipe["id"])
    assert E.dish_food_cost(items) == 2.30
    assert E.margin(5.00, 2.30) == round((5.00 - 2.30) / 5.00, 4)


def test_margin_none_without_price():
    assert E.margin(0, 2.30) is None


# ── low-stock alerts: once per breach ────────────────────────────────
def test_low_stock_alert_fires_once(db, wa, i18n):
    ing = db.add_ingredient(COOK, "Paneer", "kg", 8.00, 0.5, 1.0)
    alerted = E.check_low_stock(db, wa, i18n, COOK)
    assert [i["id"] for i in alerted] == [ing["id"]]
    assert "Paneer" in wa.last_to(COOK)
    # Second sweep: no repeat while the breach persists.
    wa.clear()
    assert E.check_low_stock(db, wa, i18n, COOK) == []
    # Restock above the threshold clears the latch; a new breach re-alerts.
    db.log_purchase(COOK, ing["id"], 5.0, 8.00)
    assert db.get_ingredient(ing["id"])["last_alert_at"] is None
    db.update_ingredient(ing["id"], stock_qty=0.2)
    assert [i["id"] for i in E.check_low_stock(db, wa, i18n, COOK)] == [ing["id"]]


def test_no_alert_when_threshold_zero(db, wa, i18n):
    db.add_ingredient(COOK, "Salt", "kg", 1.00, 0.0, 0.0)
    assert E.check_low_stock(db, wa, i18n, COOK) == []
    assert wa.sent == []


# ── stock consumption on accept + pre-broadcast warning ──────────────
def _order(
    db, cook=COOK, cust=CUST, days_ago=0, status="completed", items=None, total=10.00
):
    order = db.create_order(
        customer_phone=cust,
        cook_phone=cook,
        ordered_items=items or [{"item": "Paneer Pulao", "quantity": 2, "price": 5.00}],
        total_sum=total,
        payment_type="COD",
    )
    if days_ago:
        db.orders[order["id"]]["creation_time"] = utcnow() - timedelta(days=days_ago)
    if status != "received":
        db.update_order(order["id"], order_status=status)
    return db.get_order(order["id"])


def test_consume_stock_on_accept(db, wa, i18n, send, cook_with_menu):
    ing = _kitchen(db)
    # Cook home → Business hub (option 3) still routes correctly.
    send(COOK, "3")
    assert db.get_session(COOK)["state"] == "owner_home"
    # A dish with no recipe consumes nothing (honest skip, no crash).
    order = _order(
        db,
        status="received",
        items=[{"item": "Veg Pulao", "quantity": 1, "price": 8.50}],
    )
    before = db.get_ingredient(ing["paneer"]["id"])["stock_qty"]
    E.consume_stock_for_order(db, order)
    assert db.get_ingredient(ing["paneer"]["id"])["stock_qty"] == before
    # Paneer Pulao consumes 0.25 kg paneer + 0.10 kg peas per dish.
    order2 = _order(
        db,
        status="received",
        items=[{"item": "Paneer Pulao", "quantity": 2, "price": 5.00}],
    )
    E.consume_stock_for_order(db, order2)
    assert db.get_ingredient(ing["paneer"]["id"])["stock_qty"] == before - 0.5
    assert db.get_ingredient(ing["peas"]["id"])["stock_qty"] == 5.0 - 0.2


def test_menu_broadcast_warns_on_low_margin(db, wa, i18n, send, cook_with_menu):
    # Veg Pulao $8.50 with a $7.50 food cost → 11.8% margin → warn at done.
    cheap = db.add_ingredient(COOK, "Truffle", "kg", 75.00, 10.0, 1.0)
    r = db.add_recipe(COOK, "Veg Pulao")
    db.add_recipe_item(r["id"], cheap["id"], 0.10)
    wa.clear()
    flagged = E.check_menu_margins(db, wa, i18n, COOK)
    assert [f["dish_name"] for f in flagged] == ["Veg Pulao"]
    assert "Veg Pulao" in wa.last_to(COOK)


# ── weekly purchase plan & daily P&L ─────────────────────────────────
def test_weekly_purchase_plan(db):
    ing = _kitchen(db)
    # 14 Paneer Pulao sold over the last 7 days → 2/day → 14×0.25 = 3.5 kg.
    for _ in range(7):
        _order(
            db,
            items=[{"item": "Paneer Pulao", "quantity": 2, "price": 5.00}],
            total=10.00,
        )
    plan = {p["ingredient"]: p for p in E.weekly_purchase_plan(db, COOK)}
    assert plan["Paneer"]["suggest_buy"] == 0.0  # 10 kg in stock
    db.update_ingredient(ing["paneer"]["id"], stock_qty=1.0)
    plan = {p["ingredient"]: p for p in E.weekly_purchase_plan(db, COOK)}
    assert plan["Paneer"]["suggest_buy"] == 2.5  # 3.5 − 1.0


def test_daily_pnl(db):
    _kitchen(db)
    _order(
        db, items=[{"item": "Paneer Pulao", "quantity": 2, "price": 5.00}], total=10.00
    )
    db.add_business_cost(COOK, "opex", "Gas refill", 4.00)
    db.add_business_cost(COOK, "capex", "New kadhai", 30.00)
    pnl = E.daily_pnl(db, COOK)
    assert pnl["revenue"] == 10.00
    assert pnl["food_cost"] == 4.60
    assert pnl["opex"] == 4.00
    assert pnl["capex"] == 30.00
    assert pnl["net"] == round(10.00 - 4.60 - 4.00 - 30.00, 2)
    assert pnl["dishes"][0]["dish"] == "Paneer Pulao"
