"""Owner addendum — the paneer counterfactual, end to end.

"If paneer's supplier price doubles": the new price is persisted, every
affected recipe is recomputed, dishes whose margin falls below 20% are
flagged, and the cook gets exactly one WhatsApp alert — before the next
menu broadcast. A benign price change stays silent.
"""

from src.owner import economics as E
from tests.conftest import COOK


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


def test_paneer_price_doubling_end_to_end(db, wa, i18n):
    ing = _kitchen(db)
    wa.clear()
    flagged = E.apply_ingredient_price_change(
        db, wa, i18n, COOK, ing["paneer"]["id"], 16.00
    )
    # 1. The new unit cost is persisted.
    assert db.get_ingredient(ing["paneer"]["id"])["unit_cost"] == 16.00
    # 2. All affected recipe costs are recomputed …
    recipe = next(r for r in db.get_recipes(COOK) if r["dish_name"] == "Paneer Pulao")
    assert E.dish_food_cost(db.get_recipe_items(recipe["id"])) == 4.30
    # … while the rice-only dish is untouched.
    jr = next(r for r in db.get_recipes(COOK) if r["dish_name"] == "Jeera Rice")
    assert E.dish_food_cost(db.get_recipe_items(jr["id"])) == 0.40
    # 3. Dishes now under the 20% margin floor are flagged …
    assert [f["dish_name"] for f in flagged] == ["Paneer Pulao"]
    assert flagged[0]["margin"] < 0.20
    # 4. … and the cook gets ONE WhatsApp alert before the next broadcast.
    alert = wa.last_to(COOK)
    assert alert is not None
    assert "Paneer" in alert and "Paneer Pulao" in alert
    assert "20%" in alert
    assert "Jeera Rice" not in alert


def test_price_change_with_no_margin_breach_stays_quiet(db, wa, i18n):
    ing = _kitchen(db)
    wa.clear()
    flagged = E.apply_ingredient_price_change(
        db, wa, i18n, COOK, ing["peas"]["id"], 3.50
    )
    assert flagged == []
    assert wa.sent == []


def test_price_change_alert_is_idempotent(db, wa, i18n):
    ing = _kitchen(db)
    wa.clear()
    E.apply_ingredient_price_change(db, wa, i18n, COOK, ing["paneer"]["id"], 16.00)
    assert len(wa.sent) == 1
    # Re-running with the same price (e.g. a retried cron) must not re-ping.
    E.apply_ingredient_price_change(db, wa, i18n, COOK, ing["paneer"]["id"], 16.00)
    assert len(wa.sent) == 1


def test_restock_at_doubled_price_alerts_cook(db, wa, send, cook_with_menu):
    """The chat trigger: the cook logs paneer at double the last price and
    the margin alert fires before the next broadcast."""
    ing = _kitchen(db)
    wa.clear()
    send(COOK, "3")  # Business hub
    send(COOK, "1")  # Inventory
    send(COOK, "2")  # log a restock
    send(COOK, "1")  # pick Paneer
    send(COOK, "5")  # 5 kg arrived
    assert db.get_session(COOK)["state"] == "owner_restock_price"
    send(COOK, "16")  # paid $16/kg — double the last $8
    assert db.get_ingredient(ing["paneer"]["id"])["unit_cost"] == 16.00
    alerts = [
        b for to, b in wa.sent if to == COOK and "Paneer Pulao" in b and "20%" in b
    ]
    assert len(alerts) == 1, [b[:60] for to, b in wa.sent if to == COOK]


def test_restock_keep_price_stays_quiet(db, wa, send, cook_with_menu):
    ing = _kitchen(db)
    wa.clear()
    send(COOK, "3")
    send(COOK, "1")
    send(COOK, "2")
    send(COOK, "1")
    send(COOK, "5")
    send(COOK, "0")  # keep the last price
    assert db.get_ingredient(ing["paneer"]["id"])["unit_cost"] == 8.00
    assert wa.sent == [] or "20%" not in (wa.last_to(COOK) or "")
