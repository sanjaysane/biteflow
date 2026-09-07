"""Declarative conversational state machine.

The whole dialogue lives in ROUTES: (role, state) -> handler function.
The webhook layer is stateless: every inbound message hydrates the session
(phone → chat_sessions row), dispatches through this table, and persists
the resulting session. No in-process memory is ever trusted.

Global pre-dispatch: the language command ("language"/"idioma"/"भाषा")
works from ANY state and returns to it afterwards.
"""

from __future__ import annotations

from . import models as M
from .context import Ctx, parse_choice
from .db import Database
from .handlers import cook, customer
from .i18n import I18n, resolve_language
from .owner import handlers as owner
from .owner import states as OW
from .whatsapp import WhatsAppClient

# ── The declarative route table ────────────────────────────────────
# (role, state) → handler(ctx) -> None  (handlers reply + persist state)
ROUTES = {
    # customer loop
    (M.ROLE_CUSTOMER, M.C_NEW): customer.handle_new,
    (M.ROLE_CUSTOMER, M.C_ASK_ROLE): customer.handle_ask_role,
    (M.ROLE_CUSTOMER, M.C_MENU_BROWSING): customer.handle_menu_browsing,
    (M.ROLE_CUSTOMER, M.C_QUANTITY): customer.handle_quantity,
    (M.ROLE_CUSTOMER, M.C_REVIEW): customer.handle_review,
    (M.ROLE_CUSTOMER, M.C_PAYMENT): customer.handle_payment,
    (M.ROLE_CUSTOMER, M.C_PROOF): customer.handle_proof,
    (M.ROLE_CUSTOMER, M.C_TRACKING): customer.handle_tracking,
    # cook loop
    (M.ROLE_COOK, M.K_HOME): cook.handle_home,
    (M.ROLE_COOK, M.K_MENU): cook.handle_menu_broadcast,
    (M.ROLE_COOK, M.K_INBOUND): cook.handle_inbound,
    (M.ROLE_COOK, M.K_STATUS): cook.handle_status,
    # ── business-owner addendum (cook role, O_* / M_* states) ──
    (M.ROLE_COOK, OW.O_HOME): owner.handle_owner_home,
    (M.ROLE_COOK, OW.O_INV): owner.handle_inventory,
    (M.ROLE_COOK, OW.O_INV_ADD_NAME): owner.handle_inv_add_name,
    (M.ROLE_COOK, OW.O_INV_ADD_UNIT): owner.handle_inv_add_unit,
    (M.ROLE_COOK, OW.O_INV_ADD_COST): owner.handle_inv_add_cost,
    (M.ROLE_COOK, OW.O_INV_ADD_STOCK): owner.handle_inv_add_stock,
    (M.ROLE_COOK, OW.O_INV_ADD_LOW): owner.handle_inv_add_low,
    (M.ROLE_COOK, OW.O_RESTOCK_PICK): owner.handle_restock_pick,
    (M.ROLE_COOK, OW.O_RESTOCK_QTY): owner.handle_restock_qty,
    (M.ROLE_COOK, OW.O_RESTOCK_PRICE): owner.handle_restock_price,
    (M.ROLE_COOK, OW.O_REC): owner.handle_recipes,
    (M.ROLE_COOK, OW.O_REC_DISH): owner.handle_rec_dish,
    (M.ROLE_COOK, OW.O_REC_ING): owner.handle_rec_ing,
    (M.ROLE_COOK, OW.O_REC_QTY): owner.handle_rec_qty,
    (M.ROLE_COOK, OW.O_SUP): owner.handle_procurement,
    (M.ROLE_COOK, OW.O_SUP_NAME): owner.handle_sup_name,
    (M.ROLE_COOK, OW.O_FIN): owner.handle_finance,
    (M.ROLE_COOK, OW.O_COST_LABEL): owner.handle_cost_label,
    (M.ROLE_COOK, OW.O_COST_AMOUNT): owner.handle_cost_amount,
    (M.ROLE_COOK, OW.M_HOME): owner.handle_marketing_home,
    (M.ROLE_COOK, OW.M_REF): owner.handle_referral,
    (M.ROLE_COOK, OW.M_REF_REWARD): owner.handle_referral_reward,
    (M.ROLE_COOK, OW.M_OFFER): owner.handle_offer,
    (M.ROLE_COOK, OW.M_OFFER_VALUE): owner.handle_offer_value,
    (M.ROLE_COOK, OW.M_CAMP_TITLE): owner.handle_camp_title,
    (M.ROLE_COOK, OW.M_CAMP_BODY): owner.handle_camp_body,
    (M.ROLE_COOK, OW.M_CAMP_CONFIRM): owner.handle_camp_confirm,
    (M.ROLE_COOK, OW.M_WINBACK): owner.handle_winback,
    # customer-side owner hooks
    (M.ROLE_CUSTOMER, OW.C_REFERRAL): owner.handle_referral_code,
    (M.ROLE_CUSTOMER, OW.C_OPTIN): owner.handle_optin,
    # role not yet chosen → same entry points as a fresh customer
    (None, M.C_NEW): customer.handle_new,
    (None, M.C_ASK_ROLE): customer.handle_ask_role,
}


def _is_language_command(text: str | None) -> bool:
    return bool(text) and text.strip().lower() in M.LANGUAGE_COMMANDS


def _enter_language_select(ctx: Ctx) -> None:
    ctx.session["data"]["return_state"] = ctx.session["state"]
    ctx.session["data"]["return_data"] = dict(ctx.session["data"])
    ctx.reply("language_menu")
    ctx.set_state(M.C_LANGUAGE)


def _handle_language_select(ctx: Ctx) -> None:
    choice = parse_choice(ctx.text, 1, len(M.LANGUAGE_OPTIONS))
    if choice is None:
        ctx.reply("language_invalid")
        return
    lang = M.LANGUAGE_OPTIONS[choice - 1][1]
    ctx.db.set_user_language(ctx.phone, lang)
    if ctx.user:
        ctx.user["preferred_language"] = lang
    ctx.session["lang"] = lang
    ctx.lang = lang
    ctx.reply("language_changed")
    # Return to wherever the chat was, now in the new language.
    data = ctx.session["data"]
    ret_state = data.pop("return_state", None)
    ret_data = data.pop("return_data", None) or {}
    ret_data.pop("return_state", None)
    ret_data.pop("return_data", None)
    if not ret_state:
        ctx.set_state(M.C_MENU_BROWSING, cooks=[], cook_phone=None, items=[], cart=[])
        return
    ctx.set_state(ret_state, **ret_data)
    # Re-dispatch with no input: every state's invalid-input branch politely
    # re-renders its prompt — now in the newly chosen language.
    process_incoming(
        ctx.db,
        ctx.wa,
        ctx.i18n,
        ctx.phone,
        None,
        msg_type="text",
        default_lang=ctx.default_lang,
    )


def fresh_session(phone: str, default_lang: str) -> dict:
    return {"role": None, "state": M.C_NEW, "lang": default_lang, "data": {}}


def process_incoming(
    db: Database,
    wa: WhatsAppClient,
    i18n: I18n,
    phone: str,
    text: str | None,
    msg_type: str = "text",
    media_id: str | None = None,
    default_lang: str = "en",
    profile_name: str | None = None,
) -> None:
    """Single entry point for every inbound WhatsApp message."""
    user = db.get_user(phone)
    session = db.get_session(phone)
    if session is None:
        session = fresh_session(phone, default_lang)
        # Brand-new chats start unregistered; language comes from default.
    lang = resolve_language(user, session, default_lang)

    # Nickname capture: the WhatsApp profile name becomes the display name
    # shown on every customer-facing surface (menus, order pings) instead
    # of the raw phone number. Never overwrites an explicitly set name.
    if profile_name:
        if user is not None and not user.get("display_name"):
            db.set_display_name(phone, profile_name)
            user = db.get_user(phone)
        elif user is None:
            session.setdefault("data", {}).setdefault(
                "profile_name", profile_name[:80]
            )

    ctx = Ctx(
        db=db,
        wa=wa,
        i18n=i18n,
        phone=phone,
        user=user,
        session=session,
        text=text,
        msg_type=msg_type,
        media_id=media_id,
        lang=lang,
        default_lang=default_lang,
    )

    # Language switch works from any state (but not while selecting one).
    if session["state"] != M.C_LANGUAGE and _is_language_command(text):
        _enter_language_select(ctx)
        return
    if session["state"] == M.C_LANGUAGE:
        _handle_language_select(ctx)
        return

    role = session.get("role") or (user["system_role"] if user else None)

    # STOP works from any customer state: leave every marketing list.
    if role == M.ROLE_CUSTOMER and (text or "").strip().upper() == "STOP":
        db.optout_everywhere(phone)
        ctx.reply("c_stop_done")
        return

    handler = ROUTES.get((role, session["state"]))
    if handler is None:
        # Unknown/corrupt state → safe reset to a known hub.
        if role == M.ROLE_COOK:
            ctx.set_state(M.K_HOME)
            cook.show_home(ctx)
        else:
            ctx.set_state(
                M.C_MENU_BROWSING, cooks=[], cook_phone=None, items=[], cart=[]
            )
            customer.handle_menu_browsing(ctx)
        return
    handler(ctx)
