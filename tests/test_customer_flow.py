"""Customer loop: invalid menu numbers are rejected with a polite
re-prompt, state is unchanged, and nothing lands in the basket.
"""

from tests.conftest import CUST


def test_invalid_menu_number_rejected(db, wa, send, customer_at_menu):
    assert db.get_session(CUST)["state"] == "menu_browsing"

    wa.clear()
    send(CUST, "9")  # only 2 items on the menu

    bodies = [b for to, b in wa.sent if to == CUST]
    assert any("not on the menu" in b for b in bodies)  # polite re-prompt …
    assert "Veg Pulao" in wa.last_to(CUST)              # … and menu re-shown

    session = db.get_session(CUST)
    assert session["state"] == "menu_browsing"  # state unchanged
    assert session["data"]["cart"] == []        # basket untouched


def test_invalid_menu_input_variants(db, wa, send, customer_at_menu):
    for bad in ["0x", "abc", "1; DROP TABLE menus", "👍", "  ", "-1"]:
        wa.clear()
        send(CUST, bad)
        bodies = [b for to, b in wa.sent if to == CUST]
        assert any("not on the menu" in b for b in bodies)
    assert db.get_session(CUST)["data"]["cart"] == []


def test_valid_choice_advances_to_quantity(db, wa, send, customer_at_menu):
    send(CUST, "1")
    assert db.get_session(CUST)["state"] == "quantity_selection"
    assert 'How many "Veg Pulao"?' in wa.last_to(CUST)


def test_invalid_quantity_rejected(db, wa, send, customer_at_menu):
    send(CUST, "1")
    wa.clear()
    send(CUST, "15")  # out of 1-9 range
    assert "1 to 9" in wa.last_to(CUST)
    assert db.get_session(CUST)["state"] == "quantity_selection"
