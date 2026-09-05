"""Mid-chat language handoff: the word 'language' (or 'idioma'/'भाषा')
opens the language menu from ANY state; after choosing, the chat resumes
where it was — now in the new language.
"""

from tests.conftest import CUST


def test_language_switch_mid_menu_browsing(db, wa, send, customer_at_menu):
    # customer is looking at the cook's menu (English)
    assert db.get_session(CUST)["state"] == "menu_browsing"
    assert db.get_session(CUST)["lang"] == "en"

    wa.clear()
    send(CUST, "language")
    assert db.get_session(CUST)["state"] == "language_select"
    assert "Choose your language" in wa.last_to(CUST)

    # invalid choice → polite re-prompt, still selecting
    send(CUST, "5")
    assert "1, 2, or 3" in wa.last_to(CUST)
    assert db.get_session(CUST)["state"] == "language_select"

    # pick Spanish → confirmation in Spanish, state restored, menu re-shown
    # in Spanish
    wa.clear()
    send(CUST, "2")
    assert db.get_user(CUST)["preferred_language"] == "es"
    session = db.get_session(CUST)
    assert session["lang"] == "es"
    assert session["state"] == "menu_browsing"
    assert session["data"]["cook_phone"] is not None  # cart/context kept

    bodies = [b for to, b in wa.sent if to == CUST]
    assert any("Idioma actualizado" in b for b in bodies)
    # the re-rendered menu prompt is Spanish now
    assert any("no está en el menú" in b or "Pagar" in b for b in bodies)


def test_spanish_customer_full_loop(db, wa, send, cook_with_menu):
    phone = "+15550003333"
    send(phone, "hola")
    send(phone, "language")
    send(phone, "2")  # Español from the start
    send(phone, "1")  # register as customer (state was restored to ask_role)
    last = wa.last_to(phone)
    assert "Elige un cocinero" in last  # cook list in Spanish
    send(phone, "1")
    assert "Menú de" in wa.last_to(phone)  # menu in Spanish


def test_language_command_in_hindi(db, wa, send, customer_at_menu):
    send(CUST, "भाषा")
    assert db.get_session(CUST)["state"] == "language_select"
    send(CUST, "3")
    assert db.get_session(CUST)["lang"] == "hi"
    assert db.get_user(CUST)["preferred_language"] == "hi"
