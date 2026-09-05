"""Kitchen economics engine: food-cost math, margins, stock, planning.

Pure functions take plain dicts (DB rows); the few WhatsApp-touching paths
(price-shock alert, low-stock sweep) take (db, wa, i18n, cook_phone) and are
designed to be called from handlers AND from a scheduler/cron.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..db import Database
from ..i18n import I18n
from ..payments import money
from ..whatsapp import WhatsAppClient
from . import states as S


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── food cost & margin ───────────────────────────────────────────────
def dish_food_cost(recipe_items: list[dict]) -> float:
    """Sum over BOM lines: qty_per_dish × ingredient unit_cost.

    Each item is a joined row: {"qty_per_dish", "unit_cost", ...}.
    """
    total = sum(float(i["qty_per_dish"]) * float(i["unit_cost"]) for i in recipe_items)
    return round(total, 2)


def margin(sell_price: float, food_cost: float) -> float | None:
    """Gross margin ratio. None when the price is not positive."""
    if sell_price <= 0:
        return None
    return round((sell_price - food_cost) / sell_price, 4)


def _recipes_by_dish(db: Database, cook_phone: str) -> dict[str, dict]:
    """dish_name → {"recipe": row, "food_cost": float}."""
    out = {}
    for recipe in db.get_recipes(cook_phone):
        items = db.get_recipe_items(recipe["id"])
        out[recipe["dish_name"]] = {
            "recipe": recipe,
            "food_cost": dish_food_cost(items),
        }
    return out


def menu_price_for_dish(db: Database, cook_phone: str, dish_name: str) -> float | None:
    """Current menu price for a dish (active menu), else None."""
    for item in db.get_active_menus(cook_phone):
        if item["item_name"] == dish_name:
            return float(item["base_price"])
    return None


def check_menu_margins(
    db: Database, wa: WhatsAppClient, i18n: I18n, cook_phone: str
) -> list[dict]:
    """Pre-broadcast sweep: warn about on-menu dishes under the margin floor.

    Called when the cook finishes setting the menu (before it goes live) and
    reusable from a scheduler. Returns the flagged dishes.
    """
    lang = _cook_lang(db, cook_phone)
    by_dish = _recipes_by_dish(db, cook_phone)
    flagged = []
    for dish_name, info in by_dish.items():
        price = menu_price_for_dish(db, cook_phone, dish_name)
        if not price:
            continue
        m = margin(price, info["food_cost"])
        if m is not None and m < S.MARGIN_FLOOR:
            flagged.append(
                {
                    "dish_name": dish_name,
                    "food_cost": info["food_cost"],
                    "price": price,
                    "margin": m,
                }
            )
    if flagged:
        lines = [i18n.t(lang, "o_margin_alert_title")]
        for f in flagged:
            lines.append(
                i18n.t(
                    lang,
                    "o_price_alert_line",
                    dish=f["dish_name"],
                    cost=money(f["food_cost"]),
                    margin=f"{f['margin'] * 100:.1f}",
                )
            )
        lines.append(i18n.t(lang, "o_margin_alert_hint"))
        wa.send_text(cook_phone, "\n".join(lines))
    return flagged


# ── counterfactual: supplier price shock ────────────────────────────
def apply_ingredient_price_change(
    db: Database,
    wa: WhatsAppClient,
    i18n: I18n,
    cook_phone: str,
    ingredient_id: int,
    new_unit_cost: float,
) -> list[dict]:
    """Supplier doubled a price overnight: recompute, flag, alert.

    1. Persists the new unit_cost on the ingredient.
    2. Recomputes food cost for every recipe using it.
    3. Flags dishes whose margin drops below MARGIN_FLOOR (20%).
    4. Pushes ONE WhatsApp alert to the cook — before the next menu
       broadcast — listing affected dishes, new food costs and margins.

    Returns the flagged dish dicts (for tests / schedulers).
    """
    ingredient = db.get_ingredient(int(ingredient_id))
    if ingredient is None or ingredient["cook_phone"] != cook_phone:
        return []
    old_cost = float(ingredient["unit_cost"])
    new_cost = float(new_unit_cost)
    price_changed = old_cost != new_cost
    db.update_ingredient(int(ingredient_id), unit_cost=new_cost)

    by_dish = _recipes_by_dish(db, cook_phone)
    flagged: list[dict] = []
    for dish_name, info in by_dish.items():
        items = db.get_recipe_items(info["recipe"]["id"])
        if not any(int(i["ingredient_id"]) == int(ingredient_id) for i in items):
            continue
        food_cost = dish_food_cost(items)
        price = menu_price_for_dish(db, cook_phone, dish_name)
        m = margin(price, food_cost) if price else None
        if m is not None and m < S.MARGIN_FLOOR:
            flagged.append(
                {
                    "dish_name": dish_name,
                    "food_cost": food_cost,
                    "price": price,
                    "margin": m,
                    "ingredient": ingredient["name"],
                    "old_unit_cost": old_cost,
                    "new_unit_cost": new_cost,
                }
            )

    if flagged and price_changed:
        lines = [
            i18n.t(
                _cook_lang(db, cook_phone),
                "o_price_alert_title",
                ingredient=ingredient["name"],
                old=money(old_cost),
                new=money(new_cost),
            )
        ]
        for f in flagged:
            lines.append(
                i18n.t(
                    _cook_lang(db, cook_phone),
                    "o_price_alert_line",
                    dish=f["dish_name"],
                    cost=money(f["food_cost"]),
                    margin=f"{f['margin'] * 100:.1f}",
                )
            )
        lines.append(i18n.t(_cook_lang(db, cook_phone), "o_price_alert_hint"))
        wa.send_text(cook_phone, "\n".join(lines))
    return flagged


def _cook_lang(db: Database, cook_phone: str) -> str:
    user = db.get_user(cook_phone) or {}
    return user.get("preferred_language", "en")


# ── low-stock sweep ──────────────────────────────────────────────────
def check_low_stock(
    db: Database, wa: WhatsAppClient, i18n: I18n, cook_phone: str
) -> list[dict]:
    """Alert once per breaching ingredient until its stock recovers.

    An ingredient alerts when stock_qty <= low_stock_threshold (> 0) and no
    alert has been sent since the last recovery. Recovery (stock pushed back
    above threshold by log_purchase) clears last_alert_at.
    """
    lang = _cook_lang(db, cook_phone)
    alerted = []
    for ing in db.get_ingredients(cook_phone):
        threshold = float(ing["low_stock_threshold"])
        if threshold <= 0 or ing.get("last_alert_at"):
            continue
        if float(ing["stock_qty"]) <= threshold:
            db.update_ingredient(ing["id"], last_alert_at=utcnow())
            wa.send_text(
                cook_phone,
                i18n.t(
                    lang,
                    "o_low_stock_alert",
                    item=ing["name"],
                    stock=f"{float(ing['stock_qty']):g}",
                    unit=ing["unit"],
                ),
            )
            alerted.append(ing)
    return alerted


def consume_stock_for_order(db: Database, order: dict) -> None:
    """Decrement ingredient stock from recipe BOMs when an order is accepted.

    Items without a matching recipe are skipped (documented simplification).
    Afterwards the low-stock sweep runs — the alert path needs (wa, i18n),
    so callers run check_low_stock themselves.
    """
    cook_phone = order["cook_phone"]
    by_dish = _recipes_by_dish(db, cook_phone)
    for line in order.get("ordered_items", []):
        info = by_dish.get(line.get("item", ""))
        if not info:
            continue
        qty = int(line.get("quantity", 0))
        for bom in db.get_recipe_items(info["recipe"]["id"]):
            ing = db.get_ingredient(int(bom["ingredient_id"]))
            if ing is None:
                continue
            new_stock = max(
                0.0, float(ing["stock_qty"]) - float(bom["qty_per_dish"]) * qty
            )
            db.update_ingredient(ing["id"], stock_qty=round(new_stock, 3))


# ── sales velocity & planning ────────────────────────────────────────
def sales_velocity(db: Database, cook_phone: str, days: int = 7) -> dict[str, float]:
    """Dish → average units sold per day over the trailing window."""
    since = utcnow() - timedelta(days=days)
    velocity: dict[str, float] = {}
    for order in db.get_completed_orders(cook_phone, since=since):
        for line in order.get("ordered_items", []):
            name = line.get("item", "")
            velocity[name] = velocity.get(name, 0.0) + int(line.get("quantity", 0))
    return {name: round(qty / days, 3) for name, qty in velocity.items()}


def project_weekly_food_cost(db: Database, cook_phone: str) -> dict:
    """Projected 7-day food cost from the recent sales mix."""
    by_dish = _recipes_by_dish(db, cook_phone)
    velocity = sales_velocity(db, cook_phone, days=7)
    lines = []
    total = 0.0
    for dish, per_day in sorted(velocity.items(), key=lambda kv: -kv[1]):
        info = by_dish.get(dish)
        if not info:
            continue  # no recipe → unknown cost, skipped honestly
        weekly = round(info["food_cost"] * per_day * 7, 2)
        total += weekly
        lines.append(
            {
                "dish": dish,
                "per_day": per_day,
                "food_cost": info["food_cost"],
                "weekly": weekly,
            }
        )
    return {"lines": lines, "total": round(total, 2)}


def weekly_purchase_plan(db: Database, cook_phone: str) -> list[dict]:
    """Suggested purchase quantities: 7-day ingredient need minus stock."""
    by_dish = _recipes_by_dish(db, cook_phone)
    velocity = sales_velocity(db, cook_phone, days=7)
    need: dict[int, dict] = {}
    for dish, per_day in velocity.items():
        info = by_dish.get(dish)
        if not info:
            continue
        for bom in db.get_recipe_items(info["recipe"]["id"]):
            ing_id = int(bom["ingredient_id"])
            entry = need.setdefault(ing_id, {"qty": 0.0, "ingredient": None})
            entry["qty"] += float(bom["qty_per_dish"]) * per_day * 7
            if entry["ingredient"] is None:
                entry["ingredient"] = db.get_ingredient(ing_id)
    plan = []
    for ing_id, entry in need.items():
        ing = entry["ingredient"]
        if ing is None:
            continue
        buy = round(max(0.0, entry["qty"] - float(ing["stock_qty"])), 2)
        plan.append(
            {
                "ingredient": ing["name"],
                "unit": ing["unit"],
                "need_7d": round(entry["qty"], 2),
                "stock": float(ing["stock_qty"]),
                "suggest_buy": buy,
            }
        )
    return sorted(plan, key=lambda p: -p["suggest_buy"])


# ── daily P&L ────────────────────────────────────────────────────────
def daily_pnl(db: Database, cook_phone: str, day: datetime | None = None) -> dict:
    """Revenue, food cost, opex, capex and net for one calendar day (UTC)."""
    day = day or utcnow()
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    by_dish = _recipes_by_dish(db, cook_phone)

    revenue = 0.0
    food_cost = 0.0
    dish_stats: dict[str, dict] = {}
    for order in db.get_completed_orders(cook_phone, since=start):
        revenue += float(order["total_sum"]) - float(order.get("discount_total", 0))
        for line in order.get("ordered_items", []):
            name = line.get("item", "")
            qty = int(line.get("quantity", 0))
            info = by_dish.get(name)
            if not info:
                continue
            cost = info["food_cost"] * qty
            food_cost += cost
            stat = dish_stats.setdefault(
                name, {"qty": 0, "revenue": 0.0, "food_cost": 0.0}
            )
            stat["qty"] += qty
            stat["revenue"] += float(line.get("price", 0)) * qty
            stat["food_cost"] += cost

    opex = sum(
        float(c["amount"])
        for c in db.get_business_costs(cook_phone, kind="opex", since=start)
    )
    capex = sum(
        float(c["amount"])
        for c in db.get_business_costs(cook_phone, kind="capex", since=start)
    )
    revenue, food_cost = round(revenue, 2), round(food_cost, 2)
    net = round(revenue - food_cost - opex - capex, 2)
    dishes = []
    for name, s in sorted(dish_stats.items(), key=lambda kv: -kv[1]["revenue"]):
        m = margin(s["revenue"], s["food_cost"])
        dishes.append(
            {
                "dish": name,
                "qty": s["qty"],
                "revenue": round(s["revenue"], 2),
                "food_cost": round(s["food_cost"], 2),
                "margin": m,
            }
        )
    return {
        "revenue": revenue,
        "food_cost": food_cost,
        "opex": round(opex, 2),
        "capex": round(capex, 2),
        "net": net,
        "dishes": dishes,
    }
