"""Phase A (Sanjay's video feedback): dish photos/ingredients/descriptions,
nickname display with phone fallback, realistic inventory seed, and
locale-aware currency (₹ for hi/mr, $ for en/es).
"""

from src.payments import currency_symbol, money
from src.state_machine import process_incoming
from tests.conftest import COOK, CUST


# ── 1. dish listings: photo + ingredients + description ──────────────
def test_cook_can_attach_photo_ingredients_description(db, wa, i18n, send):
    send(COOK, "hello")
    send(COOK, "2")  # register as cook
    send(COOK, "1")  # set menu
    send(COOK, "Veg Pulao")
    send(COOK, "8.50")
    assert "photo" in wa.last_to(COOK).lower()
    send(COOK, None, msg_type="image", media_id="wamid.abc123")  # attach photo
    send(COOK, "rice, peas, carrots, ghee")  # ingredients
    send(COOK, "Slow-cooked in ghee, just like home")  # description
    send(COOK, "2")  # menu done

    items = db.get_active_menus(COOK)
    assert len(items) == 1
    assert items[0]["photo_ref"] == "photo:wamid.abc123"
    assert items[0]["ingredients"] == "rice, peas, carrots, ghee"
    assert items[0]["description"] == "Slow-cooked in ghee, just like home"


def test_photo_step_reprompts_on_unexpected_text(db, wa, i18n, send):
    send(COOK, "hello")
    send(COOK, "2")
    send(COOK, "1")
    send(COOK, "Samosa")
    send(COOK, "3")
    send(COOK, "nice pic")  # neither a photo nor 0 → re-prompt
    assert db.get_session(COOK)["data"]["menu_step"] == "photo"
    assert "photo" in wa.last_to(COOK).lower()
    send(COOK, "0")  # skip
    send(COOK, "0")
    send(COOK, "0")
    send(COOK, "2")
    assert db.get_active_menus(COOK)[0]["photo_ref"] is None


def test_customer_menu_shows_photo_ingredients_description(db, wa, i18n, send):
    send(COOK, "hello")
    send(COOK, "2")
    db.add_menu_item(
        COOK,
        "Veg Pulao",
        "Slow-cooked in ghee, just like home",
        8.50,
        "en",
        photo_ref="sample:veg_pulao.jpg",  # clearly-labeled sample data
        ingredients="rice, peas, carrots, ghee",
    )
    send(CUST, "hello")
    send(CUST, "1")  # register as customer → cook list
    wa.clear()
    send(CUST, "1")  # pick the cook → menu

    body = wa.last_to(CUST)
    assert "rice, peas, carrots, ghee" in body
    assert "Slow-cooked in ghee" in body
    assert "8.50" in body
    # the photo goes out as an image message, not buried in text
    assert wa.images, "expected an image message for the dish photo"
    to, ref, caption = wa.images[0]
    assert to == CUST and ref == "sample:veg_pulao.jpg"
    assert "Veg Pulao" in caption


# ── 2. nicknames with phone fallback ─────────────────────────────────
def test_nicknames_shown_instead_of_phone(db, wa, i18n, send, cook_with_menu):
    db.set_display_name(COOK, "Meena Kaki")  # cook registered by the fixture
    send(CUST, "hello")
    send(CUST, "1")  # register → cook list shows the nickname
    assert "Meena Kaki" in wa.last_to(CUST)
    assert COOK not in wa.last_to(CUST)
    db.set_display_name(CUST, "Ravi")  # customer now registered

    wa.clear()
    send(CUST, "1")  # pick cook → menu title uses the nickname
    assert "Meena Kaki" in wa.last_to(CUST)

    # order it; the cook's NEW ORDER ping names the customer, not a number
    send(CUST, "1")  # item 1
    send(CUST, "2")  # qty 2
    send(CUST, "0")  # checkout → review
    send(CUST, "1")  # confirm
    send(CUST, "1")  # cash on delivery
    ping = wa.last_to(COOK)
    assert "Ravi" in ping
    assert CUST not in ping


def test_phone_fallback_when_no_nickname(db, wa, i18n, send, cook_with_menu):
    send(CUST, "hello")
    send(CUST, "1")
    body = wa.last_to(CUST)
    assert COOK in body  # no nickname set → raw phone is the fallback


def test_profile_name_becomes_display_name(db, wa, i18n):
    process_incoming(db, wa, i18n, "+15550009999", "hello", profile_name="Meena Kaki")
    process_incoming(db, wa, i18n, "+15550009999", "2", profile_name="Meena Kaki")
    assert db.get_user("+15550009999")["display_name"] == "Meena Kaki"
    assert db.display_name("+15550009999") == "Meena Kaki"


def test_explicit_nickname_never_overwritten(db, wa, i18n):
    process_incoming(db, wa, i18n, "+15550008888", "hello", profile_name="Meena Kaki")
    process_incoming(db, wa, i18n, "+15550008888", "2", profile_name="Meena Kaki")
    db.set_display_name("+15550008888", "Aaji's Kitchen")
    process_incoming(db, wa, i18n, "+15550008888", "hello", profile_name="Someone Else")
    assert db.display_name("+15550008888") == "Aaji's Kitchen"


# ── 3. realistic inventory seed ──────────────────────────────────────
def _open_inventory(send):
    send(COOK, "3")  # cook home → Business
    send(COOK, "1")  # → Inventory


def test_inventory_seeded_with_realistic_stock(db, wa, i18n, send, cook_with_menu):
    wa.clear()
    _open_inventory(send)
    body = wa.last_to(COOK)
    assert "Starter pantry" in body

    ings = db.get_ingredients(COOK)
    assert len(ings) == 10
    assert all(float(i["stock_qty"]) > 0 for i in ings)
    names = {i["name"] for i in ings}
    assert {"Wheat flour (Atta)", "Basmati rice", "Sunflower oil"} <= names
    # plausible quantities: kilos of staples, grams of spices
    atta = next(i for i in ings if i["name"] == "Wheat flour (Atta)")
    assert float(atta["stock_qty"]) == 10.0 and atta["unit"] == "kg"
    haldi = next(i for i in ings if i["name"] == "Turmeric (Haldi)")
    assert float(haldi["stock_qty"]) == 500.0 and haldi["unit"] == "g"


def test_inventory_seed_does_not_duplicate(db, wa, i18n, send, cook_with_menu):
    _open_inventory(send)
    assert len(db.get_ingredients(COOK)) == 10
    send(COOK, "0")  # back
    send(COOK, "3")
    send(COOK, "1")  # inventory again
    assert len(db.get_ingredients(COOK)) == 10  # no re-seed


def test_inventory_seed_uses_inr_costs_for_mr_cook(db, wa, i18n, send, cook_with_menu):
    db.set_user_language(COOK, "mr")
    sess = db.get_session(COOK)
    sess["lang"] = "mr"
    db.save_session(COOK, sess)
    _open_inventory(send)
    atta = next(i for i in db.get_ingredients(COOK) if "Atta" in i["name"])
    assert float(atta["unit_cost"]) == 45.0  # INR-plausible, not USD


# ── 4. locale-aware currency ─────────────────────────────────────────
def test_money_locale_formatting():
    assert money(8.5, "en") == "$8.50"
    assert money(8.5, "es") == "$8.50"
    assert money(140, "mr") == "₹140.00"
    assert money(2500, "hi") == "₹2,500.00"
    assert money(100000, "mr") == "₹1,00,000.00"  # Indian digit grouping
    assert currency_symbol("mr") == "₹"
    assert currency_symbol("hi") == "₹"
    assert currency_symbol("en") == "$"
    assert currency_symbol("es") == "$"


def test_mr_customer_sees_inr_not_usd(db, wa, i18n, send, cook_with_menu):
    send(CUST, "hello")
    send(CUST, "1")  # register → cook list
    db.set_user_language(CUST, "mr")
    sess = db.get_session(CUST)
    sess["lang"] = "mr"
    db.save_session(CUST, sess)
    wa.clear()
    send(CUST, "1")  # pick cook → menu renders in Marathi
    body = wa.last_to(CUST)
    assert "₹" in body
    assert "$" not in body


def test_en_customer_still_sees_usd(db, wa, i18n, send, customer_at_menu):
    body = wa.last_to(CUST)
    assert "$8.50" in body
    assert "₹" not in body
