"""Customer conversational loop.

States: new → ask_role → menu_browsing → quantity_selection → order_review
        → payment_method → payment_proof → active_tracking
(plus language_select, handled globally before dispatch).

Every numeric input goes through parse_choice(): bare digits only, range
checked, polite re-prompt otherwise. No free-form typing in the core loop.
"""

from __future__ import annotations

from .. import models as M
from ..context import Ctx, cart_lines, parse_choice
from ..payments import cart_total, create_order_from_cart, money, submit_p2p_proof


# ── new / welcome ──────────────────────────────────────────────────
def handle_new(ctx: Ctx) -> None:
    ctx.reply("welcome")
    ctx.reply("ask_role")
    ctx.set_state(M.C_ASK_ROLE)


def handle_ask_role(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 1, 2)
    if choice is None:
        ctx.reply("role_invalid")
        return
    role = M.ROLE_CUSTOMER if choice == 1 else M.ROLE_COOK
    user = ctx.db.upsert_user(ctx.phone, role, ctx.lang)
    ctx.user = user
    ctx.session["role"] = role
    ctx.session["lang"] = user.get("preferred_language", ctx.lang)
    ctx.lang = ctx.session["lang"]
    if role == M.ROLE_CUSTOMER:
        ctx.reply("customer_registered")
        _show_cooks(ctx)
    else:
        from . import cook as cook_handlers
        ctx.reply("cook_registered")
        cook_handlers.show_home(ctx)


def _show_cooks(ctx: Ctx) -> None:
    cooks = ctx.db.get_cooks_with_menus()
    if not cooks:
        ctx.reply("cook_list_empty")
        ctx.set_state(M.C_MENU_BROWSING)
        return
    options = "\n".join(f"{i}. 👩‍🍳 {c['phone_number']}"
                        for i, c in enumerate(cooks, 1))
    ctx.reply("choose_cook", options=options)
    ctx.set_state(M.C_MENU_BROWSING, cooks=[c["phone_number"] for c in cooks],
                  cook_phone=None, cart=[])


# ── menu browsing ──────────────────────────────────────────────────
def _show_menu(ctx: Ctx, cook_phone: str) -> None:
    items = ctx.db.get_active_menus(cook_phone)
    if not items:
        ctx.reply("menu_empty")
        return
    lines = [ctx.i18n.t(ctx.lang, "menu_title", cook=cook_phone)]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. 🍛 {item['item_name']} — ${money(item['base_price'])}")
        if item.get("description"):
            lines.append(f"   {item['description']}")
    ctx.reply("menu_prompt", items="\n".join(lines))
    ctx.set_state(M.C_MENU_BROWSING,
                  cooks=ctx.session["data"].get("cooks", []),
                  cook_phone=cook_phone,
                  items=[{"id": it["id"], "item_name": it["item_name"],
                          "price": float(it["base_price"])} for it in items],
                  cart=ctx.session["data"].get("cart", []))


def handle_menu_browsing(ctx: Ctx) -> None:
    data = ctx.session["data"]
    # Step 1: choose a cook (no cook picked yet)
    if not data.get("cook_phone"):
        cooks = data.get("cooks") or [c["phone_number"]
                                      for c in ctx.db.get_cooks_with_menus()]
        choice = parse_choice(ctx.text, 1, len(cooks)) if cooks else None
        if choice is None:
            ctx.reply("cook_choice_invalid")
            _show_cooks(ctx)
            return
        _show_menu(ctx, cooks[choice - 1])
        return
    # Step 2: choose an item, or 0 to checkout
    items = data.get("items", [])
    choice = parse_choice(ctx.text, 0, len(items))
    if choice is None:
        ctx.reply("item_invalid")
        _show_menu(ctx, data["cook_phone"])
        return
    if choice == 0:
        cart = data.get("cart", [])
        if not cart:
            ctx.reply("item_invalid")
            _show_menu(ctx, data["cook_phone"])
            return
        show_review(ctx)
        return
    item = items[choice - 1]
    ctx.reply("ask_quantity", item=item["item_name"])
    ctx.set_state(M.C_QUANTITY, pending_item=item,
                  **{k: v for k, v in data.items() if k != "pending_item"})


# ── quantity ───────────────────────────────────────────────────────
def handle_quantity(ctx: Ctx) -> None:
    qty = parse_choice(ctx.text, 1, 9)
    if qty is None:
        ctx.reply("quantity_invalid")
        return
    data = ctx.session["data"]
    item = data["pending_item"]
    cart = data.get("cart", [])
    cart.append({"item_name": item["item_name"], "price": item["price"],
                 "qty": qty})
    ctx.reply("menu_added", item=item["item_name"], qty=qty)
    ctx.reply("checkout_hint")
    ctx.set_state(M.C_MENU_BROWSING,
                  cooks=data.get("cooks", []), cook_phone=data["cook_phone"],
                  items=data.get("items", []), cart=cart)


# ── order review ───────────────────────────────────────────────────
def _discounts_total(ctx: Ctx) -> tuple[list[dict], float]:
    """(discount lines, total discount) stashed in session data."""
    discounts = ctx.session["data"].get("discounts", [])
    total = round(sum(float(d.get("discount", 0)) for d in discounts), 2)
    return discounts, total


def show_review(ctx: Ctx) -> None:
    cart = ctx.session["data"].get("cart", [])
    lines = [ctx.i18n.t(ctx.lang, "review_title")]
    for n, c in enumerate(cart, 1):
        lines.append(ctx.i18n.t(ctx.lang, "review_line", n=n,
                                item=c["item_name"], qty=c["qty"],
                                price=money(float(c["price"]) * int(c["qty"]))))
    total = cart_total(cart)
    discounts, disc_total = _discounts_total(ctx)
    lines.append(ctx.i18n.t(ctx.lang, "review_total",
                            total=money(total)))
    if discounts:
        for d in discounts:
            lines.append(ctx.i18n.t(ctx.lang, "c_review_discount",
                                    desc=d.get("desc", ""),
                                    discount=money(d.get("discount", 0))))
        lines.append(ctx.i18n.t(ctx.lang, "c_review_total_after",
                                total=money(round(total - disc_total, 2))))
    lines.append(ctx.i18n.t(ctx.lang, "review_prompt"))
    ctx.wa.send_text(ctx.phone, "\n".join(lines))
    ctx.set_state(M.C_REVIEW)


def handle_review(ctx: Ctx) -> None:
    # Business-owner addendum: 5️⃣ enters a typed referral code, then
    # returns here. Everything else keeps the original 1/2 contract.
    if (ctx.text or "").strip() == "5":
        ctx.reply("c_referral_prompt")
        from ..owner import states as OW

        ctx.set_state(OW.C_REFERRAL)
        return
    choice = parse_choice(ctx.text, 1, 2)
    if choice is None:
        ctx.reply("review_invalid")
        return
    if choice == 2:
        ctx.reply("order_cancelled")
        ctx.set_state(M.C_MENU_BROWSING, cooks=[], cook_phone=None,
                      items=[], cart=[])
        _show_cooks(ctx)
        return
    ctx.reply("payment_title")
    ctx.set_state(M.C_PAYMENT)


# ── payment ────────────────────────────────────────────────────────
def handle_payment(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 1, 2)
    if choice is None:
        ctx.reply("payment_invalid")
        return
    data = ctx.session["data"]
    cart = data.get("cart", [])
    cook_phone = data.get("cook_phone")
    if not cart or not cook_phone:
        ctx.reply("generic_invalid")
        ctx.set_state(M.C_MENU_BROWSING, cooks=[], cook_phone=None,
                      items=[], cart=[])
        return
    payment_type = "COD" if choice == 1 else "P2P_TRANSFER"
    order = create_order_from_cart(ctx.db, ctx.phone, cook_phone, cart,
                                   payment_type)
    order_id = order["id"]
    # Business-owner addendum: stack the discounts. A typed referral code
    # (from 5️⃣ at review) is already in session data; the freemium
    # first-order offer and any earned referrer credit apply automatically.
    from ..owner import marketing as MK

    total = cart_total(cart)
    # Stack discounts sequentially against the remaining total so the
    # aggregate can never exceed the order total (no negative nets).
    discounts: list[dict] = []
    remaining = round(total, 2)

    def _take(kind: str, amount: float, desc: str, **extra) -> None:
        nonlocal remaining
        amt = round(min(float(amount), remaining), 2)
        if amt > 0:
            discounts.append({"kind": kind, "discount": amt,
                              "desc": desc, **extra})
            remaining = round(remaining - amt, 2)

    for d in data.get("discounts", []):
        if d.get("kind") == "referral":
            _take("referral", d["discount"], d["desc"],
                  referral_id=d.get("referral_id"))
    auto = MK.first_order_offer(ctx.db, cook_phone, ctx.phone, total, cart)
    if auto["discount"] > 0:
        _take("offer", auto["discount"], auto["desc"])
    credit = MK.consume_referrer_credit(ctx.db, cook_phone, ctx.phone,
                                        remaining)
    if credit["discount"] > 0:
        discounts.append({"kind": "credit", "discount": credit["discount"],
                          "desc": credit["desc"]})
        remaining = round(remaining - credit["discount"], 2)
    disc_total = round(total - remaining, 2)
    disc_desc = "; ".join(d["desc"] for d in discounts)
    if disc_total > 0:
        ctx.db.update_order(order_id, discount_total=disc_total,
                            discount_desc=disc_desc[:500])
        for d in discounts:
            if d.get("kind") == "referral" and d.get("referral_id"):
                MK.finalize_referral(ctx.db, cook_phone,
                                     int(d["referral_id"]), ctx.phone,
                                     order_id)
    net = round(total - disc_total, 2)
    if payment_type == "COD":
        ctx.reply("cod_confirmed", total=money(net))
    else:
        ctx.reply("p2p_instructions", total=money(net),
                  cook=cook_phone)
        ctx.set_state(M.C_PROOF, order_id=order_id,
                      cooks=[], cook_phone=None, items=[], cart=[])
    if payment_type == "COD":
        ctx.set_state(M.C_TRACKING, order_id=order_id,
                      cooks=[], cook_phone=None, items=[], cart=[])
    order = ctx.db.get_order(order_id) or order  # pick up discount_total
    _notify_cook_new_order(ctx, order)


def _notify_cook_new_order(ctx: Ctx, order: dict) -> None:
    """Push the order into the cook's inbound queue with a 1/2 prompt."""
    cook_phone = order["cook_phone"]
    cook_user = ctx.db.get_user(cook_phone) or {}
    cook_lang = cook_user.get("preferred_language", "en")
    lines = [f"{i['item']} × {i['quantity']}" for i in order["ordered_items"]]
    net = round(float(order.get("total_sum", 0.0))
                - float(order.get("discount_total", 0.0)), 2)
    ctx.send_to(cook_phone, "cook_new_order", cook_lang,
                order_id=order["id"], customer=order["customer_phone"],
                items="\n".join(lines) if lines else "—",
                total=money(net), payment=order["payment_type"])
    ctx.set_state_for(cook_phone, M.ROLE_COOK, M.K_INBOUND, cook_lang,
                      order_id=order["id"], pending_kind="new_order")


def handle_proof(ctx: Ctx) -> None:
    """P2P verification loop: screenshot photo OR typed reference."""
    order_id = ctx.session["data"].get("order_id")
    if not order_id:
        ctx.reply("generic_invalid")
        ctx.set_state(M.C_MENU_BROWSING, cooks=[], cook_phone=None,
                      items=[], cart=[])
        return
    if ctx.msg_type == "image" and ctx.media_id:
        proof_ref = f"photo:{ctx.media_id}"
    elif ctx.text and ctx.text.strip():
        proof_ref = f"ref:{ctx.text.strip()}"
    else:
        ctx.reply("p2p_instructions",
                  total=money(ctx.db.get_order(order_id)["total_sum"]),
                  cook=ctx.db.get_order(order_id)["cook_phone"])
        return
    order = submit_p2p_proof(ctx.db, order_id, proof_ref)
    assert order is not None
    ctx.reply("payment_proof_received")
    ctx.set_state(M.C_TRACKING, order_id=order_id,
                  cooks=[], cook_phone=None, items=[], cart=[])
    # → cook's inbound queue: single-digit approve / deny
    from .. import payments as pay
    cook_phone = order["cook_phone"]
    cook_user = ctx.db.get_user(cook_phone) or {}
    cook_lang = cook_user.get("preferred_language", "en")
    ctx.send_to(cook_phone, "cook_payment_proof", cook_lang,
                order_id=order_id, customer=order["customer_phone"],
                total=money(order["total_sum"]),
                proof=pay.describe_proof(proof_ref))
    ctx.set_state_for(cook_phone, M.ROLE_COOK, M.K_INBOUND, cook_lang,
                      order_id=order_id, pending_kind="payment")


# ── tracking ───────────────────────────────────────────────────────
def _status_label(ctx: Ctx, status: str) -> str:
    return ctx.i18n.t(ctx.lang, f"status_{status}")


def handle_tracking(ctx: Ctx) -> None:
    order_id = ctx.session["data"].get("order_id")
    order = ctx.db.get_order(order_id) if order_id else None
    if order is None:
        opened = ctx.db.get_open_orders_for_customer(ctx.phone)
        order = opened[-1] if opened else None
    if order is None:
        ctx.reply("tracking_none")
        return
    ctx.reply("tracking_status", order_id=order["id"],
              status=_status_label(ctx, order["order_status"]),
              total=money(order["total_sum"]))
