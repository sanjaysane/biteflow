"""Cook loop: guided multi-item menu broadcast updates the DB and the
state machine; invalid prices are rejected without losing progress.
"""

from tests.conftest import COOK


def test_cook_broadcast_two_items(db, wa, send, cook_with_menu):
    items = db.get_active_menus(COOK)
    assert len(items) == 2
    assert items[0]["item_name"] == "Veg Pulao"
    assert float(items[0]["base_price"]) == 8.50
    assert items[1]["item_name"] == "Dal Tadka"
    assert float(items[1]["base_price"]) == 7.00

    session = db.get_session(COOK)
    assert session["state"] == "cook_home"  # broadcast finished → hub
    assert any("menu is live" in b for to, b in wa.sent if to == COOK)


def test_invalid_price_rejected_keeps_progress(db, wa, send):
    send(COOK, "hello")
    send(COOK, "2")
    send(COOK, "1")
    send(COOK, "Samosa")
    wa.clear()
    send(COOK, "free")  # not a price
    assert "not a valid price" in wa.last_to(COOK)
    # still on the price step, dish name preserved
    session = db.get_session(COOK)
    assert session["data"]["menu_step"] == "price"
    assert session["data"]["pending_name"] == "Samosa"
    assert db.get_active_menus(COOK) == []
    # recover with a valid price → photo step
    send(COOK, "3.25")
    session = db.get_session(COOK)
    assert session["data"]["menu_step"] == "photo"
    assert db.get_active_menus(COOK) == []  # saved only after all steps
    send(COOK, "0")  # skip photo
    send(COOK, "rice, peas")  # ingredients
    send(COOK, "0")  # skip description
    items = db.get_active_menus(COOK)
    assert len(items) == 1 and float(items[0]["base_price"]) == 3.25
    assert items[0]["ingredients"] == "rice, peas"
    assert items[0]["photo_ref"] is None


def test_rebroadcast_replaces_old_menu(db, wa, send, cook_with_menu):
    assert len(db.get_active_menus(COOK)) == 2
    send(COOK, "1")  # start a new broadcast
    send(COOK, "Idli")  # (old menu deactivated at broadcast start)
    assert db.get_active_menus(COOK) == []
    send(COOK, "5")
    send(COOK, "0")  # skip photo
    send(COOK, "0")  # skip ingredients
    send(COOK, "0")  # skip description
    send(COOK, "2")  # done
    items = db.get_active_menus(COOK)
    assert len(items) == 1 and items[0]["item_name"] == "Idli"
