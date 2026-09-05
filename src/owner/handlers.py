"""Business-owner conversational loops (addendum).

Domain 1 — kitchen economics (O_* states): inventory, recipes, procurement,
finance. Domain 2 — marketing & growth (M_* states): referrals, freemium
offers, campaigns, win-back. Plus the customer-side referral-code state.

Contract: every decision is a single digit or an emoji; free-form text only
ever appears in setup moments (names, prices, campaign copy) that cannot be
digitized — the same split the core cook loop already uses.
"""

from __future__ import annotations

import re

from ..context import Ctx, parse_choice, parse_price
from ..payments import money
from . import digest as D
from . import economics as E
from . import marketing as MK
from . import states as S

_QTY_RE = re.compile(r"^\d{1,6}(\.\d{1,3})?$")


def _parse_qty(text: str | None) -> float | None:
    """Non-negative quantity with up to 3 decimals ('5', '2.5', '0')."""
    if not text:
        return None
    s = text.strip()
    if not _QTY_RE.fullmatch(s):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _back_home(ctx: Ctx) -> None:
    """Return to the plain cook home (stable K_HOME, owned by cook.py)."""
    from .. import models as M

    ctx.reply("cook_home")
    ctx.set_state(M.K_HOME)


# ═══════════════════════════════════════════════════════════════════
# Hub
# ═══════════════════════════════════════════════════════════════════
def show_owner_home(ctx: Ctx) -> None:
    ctx.reply("o_home")
    ctx.set_state(S.O_HOME)


def handle_owner_home(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 5)
    if choice is None:
        ctx.reply("o_home")
        return
    if choice == 0:
        _back_home(ctx)
    elif choice == 1:
        show_inventory(ctx)
    elif choice == 2:
        show_recipes(ctx)
    elif choice == 3:
        show_procurement(ctx)
    elif choice == 4:
        show_finance(ctx)
    else:
        show_marketing_home(ctx)


# ═══════════════════════════════════════════════════════════════════
# Domain 1 · inventory
# ═══════════════════════════════════════════════════════════════════
def show_inventory(ctx: Ctx) -> None:
    ings = ctx.db.get_ingredients(ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "o_inv_title")]
    if not ings:
        lines.append(ctx.i18n.t(ctx.lang, "o_inv_empty"))
    for n, ing in enumerate(ings, 1):
        lines.append(ctx.i18n.t(
            ctx.lang, "o_inv_line", n=n, name=ing["name"],
            stock=f"{float(ing['stock_qty']):g}", unit=ing["unit"],
            low=f"{float(ing['low_stock_threshold']):g}"))
    lines.append(ctx.i18n.t(ctx.lang, "o_inv_menu"))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_INV)


def handle_inventory(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 2)
    if choice is None:
        show_inventory(ctx)
        return
    if choice == 0:
        show_owner_home(ctx)
    elif choice == 1:
        ctx.reply("o_inv_add_name")
        ctx.set_state(S.O_INV_ADD_NAME)
    else:
        _restock_pick(ctx)


def handle_inv_add_name(ctx: Ctx) -> None:
    name = (ctx.text or "").strip()
    if not name or len(name) > 80:
        ctx.reply("o_inv_add_name")
        return
    ctx.reply("o_inv_add_unit", name=name)
    ctx.set_state(S.O_INV_ADD_UNIT, inv_name=name)


def handle_inv_add_unit(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 1, 3)
    if choice is None:
        ctx.reply("o_inv_add_unit",
                  name=ctx.session["data"].get("inv_name", ""))
        return
    unit = S.UNITS[choice - 1]
    ctx.reply("o_inv_add_cost", unit=unit)
    ctx.set_state(S.O_INV_ADD_COST, inv_unit=unit)


def handle_inv_add_cost(ctx: Ctx) -> None:
    cost = parse_price(ctx.text)
    if cost is None:
        ctx.reply("o_inv_add_cost",
                  unit=ctx.session["data"].get("inv_unit", ""))
        return
    data = ctx.session["data"]
    ctx.reply("o_inv_add_stock", name=data.get("inv_name", ""),
              unit=data.get("inv_unit", ""))
    ctx.set_state(S.O_INV_ADD_STOCK, inv_cost=cost)


def handle_inv_add_stock(ctx: Ctx) -> None:
    qty = _parse_qty(ctx.text)
    if qty is None:
        ctx.reply("o_qty_invalid")
        return
    data = ctx.session["data"]
    ctx.reply("o_inv_add_low", name=data.get("inv_name", ""),
              unit=data.get("inv_unit", ""))
    ctx.set_state(S.O_INV_ADD_LOW, inv_stock=qty)


def handle_inv_add_low(ctx: Ctx) -> None:
    low = _parse_qty(ctx.text)
    if low is None:
        ctx.reply("o_qty_invalid")
        return
    data = ctx.session["data"]
    ing = ctx.db.add_ingredient(
        ctx.phone, data.get("inv_name", ""), data.get("inv_unit", "kg"),
        data.get("inv_cost", 0.0), data.get("inv_stock", 0.0), low)
    ctx.reply("o_inv_added", name=ing["name"],
              stock=f"{float(ing['stock_qty']):g}", unit=ing["unit"],
              cost=money(ing["unit_cost"]), low=f"{low:g}")
    show_inventory(ctx)


def _restock_pick(ctx: Ctx) -> None:
    ings = ctx.db.get_ingredients(ctx.phone)
    if not ings:
        show_inventory(ctx)
        return
    lines = [ctx.i18n.t(ctx.lang, "o_restock_pick")]
    for n, ing in enumerate(ings, 1):
        lines.append(f"{n}️⃣ {ing['name']} ({float(ing['stock_qty']):g} "
                     f"{ing['unit']})")
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_RESTOCK_PICK)


def handle_restock_pick(ctx: Ctx) -> None:
    ings = ctx.db.get_ingredients(ctx.phone)
    choice = parse_choice(ctx.text, 0, len(ings))
    if choice is None or not ings:
        _restock_pick(ctx)
        return
    if choice == 0:
        show_inventory(ctx)
        return
    ing = ings[choice - 1]
    ctx.reply("o_restock_qty", name=ing["name"], unit=ing["unit"])
    ctx.set_state(S.O_RESTOCK_QTY, restock_id=ing["id"])


def handle_restock_qty(ctx: Ctx) -> None:
    qty = _parse_qty(ctx.text)
    ing_id = ctx.session["data"].get("restock_id")
    ing = ctx.db.get_ingredient(ing_id) if ing_id else None
    if qty is None or qty <= 0 or ing is None:
        if ing is None:
            show_inventory(ctx)
        else:
            ctx.reply("o_qty_invalid")
        return
    # A changed supplier price is the counterfactual trigger: ask what was
    # paid so a price shock can recompute recipes and alert immediately.
    ctx.reply("o_restock_price", name=ing["name"], unit=ing["unit"],
              old=money(float(ing["unit_cost"])))
    ctx.set_state(S.O_RESTOCK_PRICE, restock_id=ing["id"],
                  restock_qty=qty)


def handle_restock_price(ctx: Ctx) -> None:
    data = ctx.session["data"]
    ing = ctx.db.get_ingredient(data.get("restock_id"))
    qty = data.get("restock_qty")
    if ing is None or qty is None:
        show_inventory(ctx)
        return
    text = (ctx.text or "").strip()
    if text == "0":
        price = float(ing["unit_cost"])  # keep last price
    else:
        price = parse_price(text)
        if price is None:
            ctx.reply("o_restock_price", name=ing["name"], unit=ing["unit"],
                      old=money(float(ing["unit_cost"])))
            return
    old_cost = float(ing["unit_cost"])
    if price != old_cost:
        # Supplier price changed → recompute recipes, flag sub-20% margins,
        # alert the cook now (before the next menu broadcast).
        E.apply_ingredient_price_change(ctx.db, ctx.wa, ctx.i18n, ctx.phone,
                                       ing["id"], price)
    ctx.db.log_purchase(ctx.phone, ing["id"], qty, price)
    ing = ctx.db.get_ingredient(ing["id"])
    assert ing is not None
    ctx.reply("o_restock_done", name=ing["name"],
              stock=f"{float(ing['stock_qty']):g}", unit=ing["unit"])
    show_inventory(ctx)


# ═══════════════════════════════════════════════════════════════════
# Domain 1 · recipes (bill of materials)
# ═══════════════════════════════════════════════════════════════════
def show_recipes(ctx: Ctx) -> None:
    recipes = ctx.db.get_recipes(ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "o_rec_title")]
    if not recipes:
        lines.append(ctx.i18n.t(ctx.lang, "o_rec_empty"))
    for recipe in recipes:
        items = ctx.db.get_recipe_items(recipe["id"])
        cost = E.dish_food_cost(items)
        price = E.menu_price_for_dish(ctx.db, ctx.phone, recipe["dish_name"])
        m = E.margin(price, cost) if price else None
        if m is None:
            lines.append(ctx.i18n.t(ctx.lang, "o_rec_line_noprice",
                                    dish=recipe["dish_name"], cost=money(cost)))
        else:
            lines.append(ctx.i18n.t(ctx.lang, "o_rec_line",
                                    dish=recipe["dish_name"], cost=money(cost),
                                    margin=f"{m * 100:.0f}"))
    lines.append(ctx.i18n.t(ctx.lang, "o_rec_menu"))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_REC)


def handle_recipes(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 1)
    if choice is None:
        show_recipes(ctx)
        return
    if choice == 0:
        show_owner_home(ctx)
        return
    items = ctx.db.get_active_menus(ctx.phone)
    if not items:
        ctx.reply("o_rec_empty")
        show_recipes(ctx)
        return
    lines = [ctx.i18n.t(ctx.lang, "o_rec_dish")]
    for n, item in enumerate(items, 1):
        lines.append(f"{n}️⃣ {item['item_name']} (${money(item['base_price'])})")
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_REC_DISH)


def handle_rec_dish(ctx: Ctx) -> None:
    items = ctx.db.get_active_menus(ctx.phone)
    choice = parse_choice(ctx.text, 1, len(items)) if items else None
    if choice is None:
        handle_recipes(ctx)
        return
    dish = items[choice - 1]["item_name"]
    # Replace any existing recipe for this dish (re-entry is an edit).
    for r in ctx.db.get_recipes(ctx.phone):
        if r["dish_name"] == dish:
            recipe = r
            break
    else:
        recipe = ctx.db.add_recipe(ctx.phone, dish,
                                   items[choice - 1]["id"])
    _rec_ing_prompt(ctx, recipe, dish)


def _rec_ing_prompt(ctx: Ctx, recipe: dict, dish: str) -> None:
    ings = ctx.db.get_ingredients(ctx.phone)
    if not ings:
        ctx.reply("o_inv_empty")
        show_recipes(ctx)
        return
    lines = []
    for n, ing in enumerate(ings, 1):
        lines.append(f"{n}️⃣ {ing['name']} (${money(ing['unit_cost'])}/"
                     f"{ing['unit']})")
    ctx.reply("o_rec_ing", items="\n".join(lines))
    ctx.set_state(S.O_REC_ING, recipe_id=recipe["id"], dish=dish)


def handle_rec_ing(ctx: Ctx) -> None:
    data = ctx.session["data"]
    recipe_id, dish = data.get("recipe_id"), data.get("dish", "")
    ings = ctx.db.get_ingredients(ctx.phone)
    choice = parse_choice(ctx.text, 0, len(ings)) if ings else None
    if choice is None:
        recipe = {"id": recipe_id}
        _rec_ing_prompt(ctx, recipe, dish)
        return
    if choice == 0:
        items = ctx.db.get_recipe_items(recipe_id)
        if not items:
            ctx.reply("o_rec_need_one")
            _rec_ing_prompt(ctx, {"id": recipe_id}, dish)
            return
        cost = E.dish_food_cost(items)
        price = E.menu_price_for_dish(ctx.db, ctx.phone, dish)
        m = E.margin(price, cost) if price else None
        ctx.reply("o_rec_done", dish=dish, cost=money(cost),
                  margin=f"{m * 100:.0f}" if m is not None else "–")
        show_recipes(ctx)
        return
    ing = ings[choice - 1]
    ctx.reply("o_rec_qty", name=ing["name"], dish=dish, unit=ing["unit"])
    ctx.set_state(S.O_REC_QTY, rec_ing_id=ing["id"])


def handle_rec_qty(ctx: Ctx) -> None:
    data = ctx.session["data"]
    qty = _parse_qty(ctx.text)
    ing = (ctx.db.get_ingredient(data.get("rec_ing_id"))
           if data.get("rec_ing_id") else None)
    if qty is None or qty <= 0 or ing is None:
        if ing is None:
            show_recipes(ctx)
        else:
            ctx.reply("o_qty_invalid")
        return
    ctx.db.add_recipe_item(data["recipe_id"], ing["id"], qty)
    _rec_ing_prompt(ctx, {"id": data["recipe_id"]}, data.get("dish", ""))


# ═══════════════════════════════════════════════════════════════════
# Domain 1 · procurement
# ═══════════════════════════════════════════════════════════════════
def show_procurement(ctx: Ctx) -> None:
    sups = ctx.db.get_suppliers(ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "o_sup_title")]
    if sups:
        lines.append(ctx.i18n.t(ctx.lang, "o_sup_list",
                                names=", ".join(s["name"] for s in sups)))
    lines.append(ctx.i18n.t(ctx.lang, "o_sup_menu"))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_SUP)


def handle_procurement(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 2)
    if choice is None:
        show_procurement(ctx)
        return
    if choice == 0:
        show_owner_home(ctx)
    elif choice == 1:
        ctx.reply("o_sup_name")
        ctx.set_state(S.O_SUP_NAME)
    else:
        _show_purchase_plan(ctx)


def handle_sup_name(ctx: Ctx) -> None:
    name = (ctx.text or "").strip()
    if not name or len(name) > 80:
        ctx.reply("o_sup_name")
        return
    ctx.db.add_supplier(ctx.phone, name)
    ctx.reply("o_sup_added", name=name)
    show_procurement(ctx)


def _show_purchase_plan(ctx: Ctx) -> None:
    plan = E.weekly_purchase_plan(ctx.db, ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "o_plan_title")]
    if not plan:
        lines.append(ctx.i18n.t(ctx.lang, "o_plan_empty"))
    for p in plan:
        lines.append(ctx.i18n.t(ctx.lang, "o_plan_line", item=p["ingredient"],
                                buy=f"{p['suggest_buy']:g}", unit=p["unit"],
                                need=f"{p['need_7d']:g}",
                                stock=f"{p['stock']:g}"))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    show_procurement(ctx)


# ═══════════════════════════════════════════════════════════════════
# Domain 1 · finance
# ═══════════════════════════════════════════════════════════════════
def show_finance(ctx: Ctx) -> None:
    lines = [ctx.i18n.t(ctx.lang, "o_fin_title"),
             ctx.i18n.t(ctx.lang, "o_fin_menu")]
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.O_FIN)


def handle_finance(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 5)
    if choice is None:
        show_finance(ctx)
        return
    if choice == 0:
        show_owner_home(ctx)
    elif choice == 1:
        D.send_daily_digest(ctx.db, ctx.wa, ctx.i18n, ctx.phone)
        show_finance(ctx)
    elif choice == 2:
        _show_projection(ctx)
    elif choice in (3, 4):
        kind = "capex" if choice == 3 else "opex"
        ctx.reply("o_cost_label", kind=kind.upper())
        ctx.set_state(S.O_COST_LABEL, cost_kind=kind)
    else:
        _show_reconciliation(ctx)


def handle_cost_label(ctx: Ctx) -> None:
    label = (ctx.text or "").strip()
    if not label or len(label) > 120:
        ctx.reply("o_cost_label",
                  kind=ctx.session["data"].get("cost_kind", "").upper())
        return
    ctx.reply("o_cost_amount", label=label)
    ctx.set_state(S.O_COST_AMOUNT, cost_label=label)


def handle_cost_amount(ctx: Ctx) -> None:
    amount = parse_price(ctx.text)
    data = ctx.session["data"]
    if amount is None:
        ctx.reply("o_cost_amount", label=data.get("cost_label", ""))
        return
    kind = data.get("cost_kind", "opex")
    ctx.db.add_business_cost(ctx.phone, kind, data.get("cost_label", ""),
                             amount)
    ctx.reply("o_cost_logged", kind=kind.upper(),
              label=data.get("cost_label", ""), amount=money(amount))
    show_finance(ctx)


def _show_projection(ctx: Ctx) -> None:
    proj = E.project_weekly_food_cost(ctx.db, ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "o_proj_title")]
    if not proj["lines"]:
        lines.append(ctx.i18n.t(ctx.lang, "o_plan_empty"))
    for row in proj["lines"]:
        lines.append(ctx.i18n.t(ctx.lang, "o_proj_line", dish=row["dish"],
                                per_day=f"{row['per_day']:g}",
                                weekly=money(row["weekly"])))
    lines.append(ctx.i18n.t(ctx.lang, "o_proj_total",
                            total=money(proj["total"])))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    show_finance(ctx)


def _show_reconciliation(ctx: Ctx) -> None:
    from datetime import timedelta

    since = E.utcnow() - timedelta(days=7)
    orders = ctx.db.get_completed_orders(ctx.phone, since=since)
    lines = [ctx.i18n.t(ctx.lang, "o_recon_title")]
    if not orders:
        lines.append(ctx.i18n.t(ctx.lang, "o_recon_empty"))
        ctx.wa.send_text(ctx.phone, "\n".join(lines))
        show_finance(ctx)
        return
    cod = sum(float(o["total_sum"]) for o in orders
              if o["payment_type"] == "COD")
    cod_pending = sum(float(o["total_sum"])
                      for o in ctx.db.get_open_orders_for_cook(ctx.phone)
                      if o["payment_type"] == "COD")
    p2p_ok = sum(float(o["total_sum"]) for o in orders
                 if o["payment_type"] == "P2P_TRANSFER"
                 and o.get("payment_status") == "verified")
    p2p_wait = sum(float(o["total_sum"]) for o in orders
                   if o["payment_type"] == "P2P_TRANSFER"
                   and o.get("payment_status") != "verified")
    lines.append(ctx.i18n.t(ctx.lang, "o_recon_cod", collected=money(cod),
                            pending=money(round(cod_pending, 2))))
    lines.append(ctx.i18n.t(ctx.lang, "o_recon_p2p", confirmed=money(p2p_ok),
                            awaiting=money(p2p_wait)))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    show_finance(ctx)


# ═══════════════════════════════════════════════════════════════════
# Domain 2 · marketing & growth
# ═══════════════════════════════════════════════════════════════════
def show_marketing_home(ctx: Ctx) -> None:
    ctx.reply("m_home")
    ctx.set_state(S.M_HOME)


def handle_marketing_home(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 4)
    if choice is None:
        show_marketing_home(ctx)
        return
    if choice == 0:
        show_owner_home(ctx)
    elif choice == 1:
        show_referrals(ctx)
    elif choice == 2:
        show_offer(ctx)
    elif choice == 3:
        ctx.reply("m_camp_title")
        ctx.set_state(S.M_CAMP_TITLE)
    else:
        show_winback(ctx)


# ── referrals ──────────────────────────────────────────────────────
def show_referrals(ctx: Ctx) -> None:
    ref = MK.get_or_create_referral(ctx.db, ctx.phone, ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "m_ref_title"),
             ctx.i18n.t(ctx.lang, "m_ref_info", code=ref["code"],
                        reward=money(ref["reward_amount"])),
             ctx.i18n.t(ctx.lang, "m_ref_menu")]
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.M_REF)


def handle_referral(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 1)
    if choice is None:
        show_referrals(ctx)
        return
    if choice == 0:
        show_marketing_home(ctx)
        return
    ctx.reply("m_ref_reward")
    ctx.set_state(S.M_REF_REWARD)


def handle_referral_reward(ctx: Ctx) -> None:
    reward = _parse_qty(ctx.text)
    if reward is None or reward > 20:
        ctx.reply("m_ref_reward")
        return
    ref = MK.get_or_create_referral(ctx.db, ctx.phone, ctx.phone)
    ctx.db.set_referral_reward(int(ref["id"]), reward)
    ctx.reply("m_ref_saved", reward=money(reward), code=ref["code"])
    show_referrals(ctx)


# ── freemium first-order offers ──────────────────────────────────────
OFFER_TYPES = ("first_order_percent_off", "first_order_free_item",
               "first_order_free_delivery")


def _offer_desc(ctx: Ctx, offer: dict | None) -> str:
    if offer is None:
        return ctx.i18n.t(ctx.lang, "m_offer_none")
    otype, val = offer["offer_type"], offer["value_text"]
    if otype == "first_order_percent_off":
        return ctx.i18n.t(ctx.lang, "m_offer_desc_pct", pct=val)
    if otype == "first_order_free_item":
        return ctx.i18n.t(ctx.lang, "m_offer_desc_item", item=val)
    return ctx.i18n.t(ctx.lang, "m_offer_desc_delivery", value=money(val))


def show_offer(ctx: Ctx) -> None:
    offer = ctx.db.get_active_offer(ctx.phone)
    lines = [ctx.i18n.t(ctx.lang, "m_offer_title"),
             ctx.i18n.t(ctx.lang, "m_offer_current",
                        desc=_offer_desc(ctx, offer)),
             ctx.i18n.t(ctx.lang, "m_offer_menu")]
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.M_OFFER)


def handle_offer(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 4)
    if choice is None:
        show_offer(ctx)
        return
    if choice == 0:
        show_marketing_home(ctx)
    elif choice == 4:
        ctx.db.deactivate_offers(ctx.phone)
        ctx.reply("m_offer_off")
        show_offer(ctx)
    else:
        otype = OFFER_TYPES[choice - 1]
        prompt_key = {"first_order_percent_off": "m_offer_value_pct",
                      "first_order_free_item": "m_offer_value_item",
                      "first_order_free_delivery": "m_offer_value_delivery"}[otype]
        ctx.reply(prompt_key)
        ctx.set_state(S.M_OFFER_VALUE, offer_type=otype)


def handle_offer_value(ctx: Ctx) -> None:
    otype = ctx.session["data"].get("offer_type", "")
    if otype == "first_order_percent_off":
        pct = _parse_qty(ctx.text)
        if pct is None or not 1 <= pct <= 90:
            ctx.reply("m_offer_value_pct")
            return
        value = f"{pct:g}"
    elif otype == "first_order_free_item":
        value = (ctx.text or "").strip()
        if not value or len(value) > 120:
            ctx.reply("m_offer_value_item")
            return
    else:
        value_amt = parse_price(ctx.text)
        if value_amt is None:
            ctx.reply("m_offer_value_delivery")
            return
        value = f"{value_amt:.2f}"
    offer = ctx.db.set_offer(ctx.phone, otype, value, active=True)
    ctx.reply("m_offer_saved", desc=_offer_desc(ctx, offer))
    show_offer(ctx)


# ── campaigns (opted-in customers only) ──────────────────────────────
def handle_camp_title(ctx: Ctx) -> None:
    title = (ctx.text or "").strip()
    if not title or len(title) > 120:
        ctx.reply("m_camp_title")
        return
    ctx.reply("m_camp_body")
    ctx.set_state(S.M_CAMP_BODY, camp_title=title)


def handle_camp_body(ctx: Ctx) -> None:
    body = (ctx.text or "").strip()
    if not body or len(body) > 1000:
        ctx.reply("m_camp_body")
        return
    data = ctx.session["data"]
    n = len(ctx.db.get_opted_in_customers(ctx.phone))
    if n == 0:
        ctx.reply("m_camp_none")
        show_marketing_home(ctx)
        return
    ctx.reply("m_camp_confirm", n=n, title=data.get("camp_title", ""),
              body=body)
    ctx.set_state(S.M_CAMP_CONFIRM, camp_body=body)


def handle_camp_confirm(ctx: Ctx) -> None:
    text = (ctx.text or "").strip()
    data = ctx.session["data"]
    if text == "👍":
        choice = 1
    elif text == "👎":
        choice = 2
    else:
        choice = parse_choice(text, 1, 2)
    if choice is None:
        ctx.reply("m_camp_confirm", n=len(ctx.db.get_opted_in_customers(
            ctx.phone)), title=data.get("camp_title", ""),
            body=data.get("camp_body", ""))
        return
    if choice == 2:
        show_marketing_home(ctx)
        return
    camp = ctx.db.create_campaign(ctx.phone, data.get("camp_title", ""),
                                  data.get("camp_body", ""))
    sent = 0
    for cust in ctx.db.get_opted_in_customers(ctx.phone):
        cust_user = ctx.db.get_user(cust) or {}
        lang = cust_user.get("preferred_language", "en")
        ctx.wa.send_text(
            cust,
            f"📢 *{data.get('camp_title', '')}*\n"
            f"{data.get('camp_body', '')}"
            f"{ctx.i18n.t(lang, 'm_optout_footer')}")
        sent += 1
    ctx.db.mark_campaign_sent(camp["id"], sent)
    ctx.reply("m_camp_sent", n=sent)
    show_marketing_home(ctx)


# ── win-back (14+ days inactive, opted-in, not recently nudged) ──────
def show_winback(ctx: Ctx) -> None:
    cands = MK.find_winback_candidates(ctx.db, ctx.phone)
    if not cands:
        ctx.reply("m_winback_none")
        show_marketing_home(ctx)
        return
    lines = [ctx.i18n.t(ctx.lang, "m_winback_title", n=len(cands)),
             ctx.i18n.t(ctx.lang, "m_winback_menu")]
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(S.M_WINBACK)


def handle_winback(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 0, 1)
    if choice is None:
        show_winback(ctx)
        return
    if choice == 0:
        show_marketing_home(ctx)
        return
    cands = MK.find_winback_candidates(ctx.db, ctx.phone)
    sent = 0
    for c in cands:
        cust_user = ctx.db.get_user(c["phone"]) or {}
        lang = cust_user.get("preferred_language", "en")
        ctx.wa.send_text(
            c["phone"],
            ctx.i18n.t(lang, "m_winback_msg")
            + ctx.i18n.t(lang, "m_optout_footer"))
        ctx.db.set_winback_sent(ctx.phone, c["phone"])
        sent += 1
    ctx.reply("m_winback_sent", n=sent)
    show_marketing_home(ctx)


# ═══════════════════════════════════════════════════════════════════
# Customer-side hooks
# ═══════════════════════════════════════════════════════════════════
def handle_referral_code(ctx: Ctx) -> None:
    """Typed referral code at order review (5️⃣). 0 = skip."""
    from .. import models as M
    from ..payments import cart_total

    text = (ctx.text or "").strip()
    if text == "0":
        _reshow_review(ctx)
        return
    data = ctx.session["data"]
    cart = data.get("cart", [])
    total = cart_total(cart)
    result = MK.apply_referral(ctx.db, data.get("cook_phone", ""),
                               ctx.phone, text, total)
    if not result["ok"]:
        reason_key = {"unknown_code": "c_referral_reason_unknown",
                      "own_code": "c_referral_reason_own",
                      "already_used": "c_referral_reason_used"}.get(
                          result["reason"], "c_referral_reason_unknown")
        ctx.reply("c_referral_bad",
                  reason=ctx.i18n.t(ctx.lang, reason_key))
        return
    discounts = [d for d in data.get("discounts", [])
                 if d.get("kind") != "referral"]
    discounts.append({"kind": "referral", "discount": result["discount"],
                      "desc": result["desc"],
                      "referral_id": result["referral_id"]})
    ctx.set_state(M.C_REVIEW, discounts=discounts)
    ctx.reply("c_referral_ok", discount=money(result["discount"]))
    _reshow_review(ctx)


def _reshow_review(ctx: Ctx) -> None:
    from ..handlers import customer as cust_mod

    cust_mod.show_review(ctx)


def handle_optin(ctx: Ctx) -> None:
    """One-time marketing opt-in after the cook accepts the order."""
    from .. import models as M

    text = (ctx.text or "").strip().upper()
    if text == "STOP":
        _do_optout(ctx)
        return
    choice = parse_choice(ctx.text, 1, 2)
    if choice is None:
        cook = ctx.session["data"].get("cook_phone", "")
        ctx.reply("c_optin_ask", cook=cook)
        return
    cook_phone = ctx.session["data"].get("cook_phone", "")
    if cook_phone:
        ctx.db.set_optin(cook_phone, ctx.phone, opted_in=(choice == 1))
    ctx.reply("c_optin_yes" if choice == 1 else "c_optin_no")
    ctx.set_state(M.C_TRACKING)


def _do_optout(ctx: Ctx) -> None:
    from .. import models as M

    cook_phone = ctx.session["data"].get("cook_phone", "")
    if cook_phone:
        ctx.db.set_optin(cook_phone, ctx.phone, opted_in=False)
    ctx.reply("c_stop_done")
    ctx.set_state(M.C_TRACKING)
