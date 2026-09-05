"""Payment flows: COD, P2P screenshot upload → pending_approval →
cook single-digit approve/deny → both chats updated.
"""

from tests.conftest import COOK, CUST


def _build_cart_to_payment(send, db, wa):
    """Drive CUST to the payment-method prompt; returns nothing."""
    send(CUST, "1")  # menu item 1
    send(CUST, "2")  # qty 2
    send(CUST, "0")  # checkout
    send(CUST, "1")  # confirm order
    assert db.get_session(CUST)["state"] == "payment_method"


def _latest_order(db):
    orders = list(db.orders.values())
    assert orders, "no order created"
    return orders[-1]


def test_cod_flow(db, wa, send, customer_at_menu):
    _build_cart_to_payment(send, db, wa)
    wa.clear()
    send(CUST, "1")  # cash on delivery
    order = _latest_order(db)
    assert order["payment_type"] == "COD"
    assert order["payment_status"] == "unpaid"
    assert order["total_sum"] == 17.00  # 2 × 8.50
    assert "Pay $17.00 in cash" in wa.last_to(CUST)
    assert db.get_session(CUST)["state"] == "active_tracking"
    # cook got the inbound order with a 1/2 prompt
    assert "NEW ORDER" in wa.last_to(COOK)
    assert db.get_session(COOK)["state"] == "order_inbound_queue"


def test_p2p_screenshot_approval_flow(db, wa, send, customer_at_menu):
    _build_cart_to_payment(send, db, wa)
    send(CUST, "2")  # phone transfer
    assert db.get_session(CUST)["state"] == "payment_proof"
    order = _latest_order(db)
    assert order["payment_type"] == "P2P_TRANSFER"

    wa.clear()
    send(CUST, None, msg_type="image", media_id="media-abc-123")
    order = db.get_order(order["id"])
    assert order["payment_status"] == "pending_approval"
    assert order["payment_proof_ref"] == "photo:media-abc-123"
    assert "Payment proof received" in wa.last_to(CUST)
    # cook sees approve/deny prompt
    cook_msg = wa.last_to(COOK)
    assert "PAYMENT PROOF" in cook_msg and "Approve payment" in cook_msg
    assert db.get_session(COOK)["data"]["pending_kind"] == "payment"

    wa.clear()
    send(COOK, "1")  # approve 👍
    order = db.get_order(order["id"])
    assert order["payment_status"] == "verified"
    assert "Payment approved by the cook" in wa.last_to(CUST)
    assert any("Payment approved" in b for to, b in wa.sent if to == COOK)


def test_p2p_reference_name_and_deny_flow(db, wa, send, customer_at_menu):
    _build_cart_to_payment(send, db, wa)
    send(CUST, "2")  # phone transfer
    send(CUST, "Zelle ref JOHN-42")  # typed reference instead of photo
    order = _latest_order(db)
    assert order["payment_proof_ref"] == "ref:Zelle ref JOHN-42"
    assert "JOHN-42" in wa.last_to(COOK)  # cook sees the reference

    wa.clear()
    send(COOK, "2")  # deny 👎
    order = db.get_order(order["id"])
    assert order["payment_status"] == "unpaid"
    assert "couldn't verify" in wa.last_to(CUST)
    assert any("Payment denied" in b for to, b in wa.sent if to == COOK)


def test_cook_accept_and_status_flow(db, wa, send, customer_at_menu):
    _build_cart_to_payment(send, db, wa)
    send(CUST, "1")  # COD
    order = _latest_order(db)

    send(COOK, "1")  # accept 👍
    assert db.get_order(order["id"])["order_status"] == "accepted"
    # customer is told the order was accepted (an opt-in follow-up may come
    # after, so check all messages, not just the last)
    assert any("accepted your order" in b for to, b in wa.sent if to == CUST)
    assert "update the status" in wa.last_to(COOK)

    send(COOK, "1")  # cooking 🍳
    assert db.get_order(order["id"])["order_status"] == "cooking"
    assert "Cooking" in wa.last_to(CUST)  # customer tracking updated

    send(COOK, "3")  # completed ✅
    assert db.get_order(order["id"])["order_status"] == "completed"
    assert "Completed" in wa.last_to(CUST)
