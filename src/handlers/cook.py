"""Cook conversational loop.

States: cook_home → menu_broadcast (guided name/price/photo/ingredients/
                     description/add-more loop)
                 → order_inbound_queue (1 = accept/approve, 2 = reject/deny)
                 → status_update_broadcast (1/2/3 status push to customer)

Menu setup intentionally allows brief free-form text (dish names and
descriptions can't be picked from digits); every price and decision
stays single-digit. Dish photos ride as WhatsApp image messages; a cook
may also skip with 0 at each enrichment step.
"""

from __future__ import annotations

from .. import models as M
from .. import payments as pay
from ..context import Ctx, parse_choice, parse_price
from ..payments import currency_symbol


def _price_example(ctx: Ctx) -> str:
    return "140" if currency_symbol(ctx.lang) == "₹" else "8.50"


# ── home hub ───────────────────────────────────────────────────────
def show_home(ctx: Ctx) -> None:
    ctx.reply("cook_home")
    ctx.set_state(M.K_HOME)


def handle_home(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 1, 4)
    if choice is None:
        ctx.reply("cook_home")
        return
    if choice == 1:
        start_broadcast(ctx)
    elif choice == 2:
        show_open_orders(ctx)
    else:
        # Business-owner addendum: lazy import avoids a hard cook↔owner cycle.
        from ..owner import handlers as owner

        if choice == 3:
            owner.show_owner_home(ctx)
        else:
            owner.show_marketing_home(ctx)


def show_open_orders(ctx: Ctx) -> None:
    orders = ctx.db.get_open_orders_for_cook(ctx.phone)
    if not orders:
        ctx.wa.send_text(ctx.phone, ctx.i18n.t(ctx.lang, "tracking_none"))
        return
    order = orders[0]
    lines = [f"{i['item']} × {i['quantity']}" for i in order["ordered_items"]]
    ctx.send_to(
        ctx.phone,
        "cook_new_order",
        ctx.lang,
        order_id=order["id"],
        customer=ctx.db.display_name(order["customer_phone"]),
        items="\n".join(lines) if lines else "—",
        total=ctx.money(order["total_sum"]),
        payment=order["payment_type"],
    )
    ctx.set_state(M.K_INBOUND, order_id=order["id"], pending_kind="new_order")


# ── menu broadcast ─────────────────────────────────────────────────
def start_broadcast(ctx: Ctx) -> None:
    # A fresh broadcast replaces yesterday's menu — one live menu per cook.
    ctx.db.deactivate_menus(ctx.phone)
    ctx.reply("cook_menu_name")
    ctx.set_state(M.K_MENU, menu_step="name")


def handle_menu_broadcast(ctx: Ctx) -> None:
    step = ctx.session["data"].get("menu_step", "name")
    data = ctx.session["data"]
    if step == "name":
        name = (ctx.text or "").strip()
        if not name or len(name) > 120:
            ctx.reply("cook_menu_name")
            return
        ctx.reply(
            "cook_menu_price", item=name, cur=ctx.currency(), ex=_price_example(ctx)
        )
        ctx.set_state(M.K_MENU, menu_step="price", pending_name=name)
    elif step == "price":
        price = parse_price(ctx.text)
        if price is None:
            ctx.reply("cook_menu_price_invalid", ex=_price_example(ctx))
            return
        name = data["pending_name"]
        ctx.reply("cook_menu_photo", item=name)
        ctx.set_state(M.K_MENU, menu_step="photo", pending_price=price)
    elif step == "photo":
        # A real WhatsApp photo arrives as an image message; "0" skips.
        # Anything else re-prompts — a photo step that silently swallowed
        # text would lose the cook's next answer.
        photo_ref: str | None = None
        if ctx.msg_type == "image" and ctx.media_id:
            photo_ref = f"photo:{ctx.media_id}"
        elif (ctx.text or "").strip() != "0":
            ctx.reply("cook_menu_photo", item=data["pending_name"])
            return
        ctx.reply("cook_menu_ingredients", item=data["pending_name"])
        ctx.set_state(M.K_MENU, menu_step="ingredients", pending_photo=photo_ref)
    elif step == "ingredients":
        text = (ctx.text or "").strip()
        ingredients = "" if text == "0" or not text else text[:300]
        ctx.reply("cook_menu_desc")
        ctx.set_state(M.K_MENU, menu_step="description", pending_ingredients=ingredients)
    elif step == "description":
        text = (ctx.text or "").strip()
        description = "" if text == "0" or not text else text[:300]
        item = ctx.db.add_menu_item(
            ctx.phone,
            data["pending_name"],
            description,
            data["pending_price"],
            ctx.lang,
            photo_ref=data.get("pending_photo"),
            ingredients=data.get("pending_ingredients", ""),
        )
        ctx.reply("cook_menu_another", item=item["item_name"], price=ctx.money(item["base_price"]))
        ctx.set_state(M.K_MENU, menu_step="another")
    elif step == "another":
        choice = parse_choice(ctx.text, 1, 2)
        if choice is None:
            ctx.reply("generic_invalid")
            return
        if choice == 1:
            ctx.reply("cook_menu_name")
            ctx.set_state(M.K_MENU, menu_step="name")
        else:
            ctx.reply("cook_menu_done")
            # Business-owner addendum: margin sweep BEFORE the menu goes live.
            from ..owner import economics as E

            E.check_menu_margins(ctx.db, ctx.wa, ctx.i18n, ctx.phone)
            show_home(ctx)


# ── inbound queue: new orders + payment proofs ─────────────────────
def handle_inbound(ctx: Ctx) -> None:
    data = ctx.session["data"]
    order_id = data.get("order_id")
    kind = data.get("pending_kind", "new_order")
    order = ctx.db.get_order(order_id) if order_id else None
    if order is None:
        show_home(ctx)
        return
    choice = parse_choice(ctx.text, 1, 2)
    if choice is None:
        ctx.reply("cook_payment_invalid" if kind == "payment" else "cook_order_invalid")
        return
    customer = order["customer_phone"]
    cust_user = ctx.db.get_user(customer) or {}
    cust_lang = cust_user.get("preferred_language", "en")

    if kind == "payment":
        # Single-digit verdict on the P2P screenshot / reference.
        updated = pay.decide_payment(ctx.db, order_id, approved=(choice == 1))
        assert updated is not None
        if choice == 1:
            ctx.send_to(customer, "payment_verified_customer", cust_lang)
            ctx.reply("cook_payment_approved")
        else:
            ctx.send_to(customer, "payment_denied_customer", cust_lang)
            ctx.reply("cook_payment_denied")
        show_home(ctx)
        return

    # kind == "new_order": accept → status loop; reject → cancel.
    if choice == 1:
        ctx.db.update_order(order_id, order_status="accepted")
        order = ctx.db.get_order(order_id)
        assert order is not None
        # Business-owner addendum: consume recipe stock, then run the
        # low-stock sweep (alerts fire once per breach, before the cook
        # needs to think about it).
        from ..owner import economics as E

        E.consume_stock_for_order(ctx.db, order)
        E.check_low_stock(ctx.db, ctx.wa, ctx.i18n, ctx.phone)
        ctx.send_to(customer, "order_accepted_customer", cust_lang, order_id=order_id)
        # Ask this customer once about menu-update opt-in, preserving
        # their tracking session data (order_id etc.).
        from ..owner import states as OW

        ctx.send_to(
            customer, "c_optin_ask", cust_lang, cook=ctx.db.display_name(ctx.phone)
        )
        cust_session = ctx.db.get_session(customer) or {}
        cust_data = dict(cust_session.get("data", {}))
        cust_data["cook_phone"] = ctx.phone
        ctx.set_state_for(customer, M.ROLE_CUSTOMER, OW.C_OPTIN, cust_lang, **cust_data)
        ctx.reply("cook_status_prompt", order_id=order_id)
        ctx.set_state(M.K_STATUS, order_id=order_id)
    else:
        ctx.db.update_order(order_id, order_status="cancelled")
        ctx.send_to(customer, "order_rejected_customer", cust_lang, order_id=order_id)
        show_home(ctx)


# ── status update broadcast ────────────────────────────────────────
STATUS_FLOW = (("1", "cooking"), ("2", "out_for_delivery"), ("3", "completed"))


def handle_status(ctx: Ctx) -> None:
    order_id = ctx.session["data"].get("order_id")
    order = ctx.db.get_order(order_id) if order_id else None
    if order is None:
        show_home(ctx)
        return
    choice = parse_choice(ctx.text, 1, 3)
    if choice is None:
        ctx.reply("cook_status_invalid")
        return
    status = STATUS_FLOW[choice - 1][1]
    ctx.db.update_order(order_id, order_status=status)
    label = ctx.i18n.t(ctx.lang, f"status_{status}")
    ctx.reply("cook_status_set", status=label)
    # Push to the customer's tracking chat in THEIR language.
    customer = order["customer_phone"]
    cust_user = ctx.db.get_user(customer) or {}
    cust_lang = cust_user.get("preferred_language", "en")
    ctx.send_to(
        customer,
        "tracking_status",
        cust_lang,
        order_id=order_id,
        status=ctx.i18n.t(cust_lang, f"status_{status}"),
        total=ctx.money(order["total_sum"]),
    )
    if status == "completed":
        show_home(ctx)
    else:
        ctx.reply("cook_status_prompt", order_id=order_id)
        ctx.set_state(M.K_STATUS, order_id=order_id)
