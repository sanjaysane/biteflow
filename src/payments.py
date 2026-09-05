"""Zero-friction payment workflow: COD + P2P (Zelle/Venmo/UPI/Pix).

Flow:
  1. Customer picks 1 = COD or 2 = P2P_TRANSFER at order review.
  2. COD → order created unpaid; cash collected on delivery; cook marks
     completed at drop-off.
  3. P2P → customer sends a payment screenshot PHOTO or a reference
     name/ID as text → payment_status = 'pending_approval', proof stored.
  4. Cook receives a single-digit prompt: 1 = approve 👍, 2 = deny 👎.
  5. Approve → 'verified' (customer notified); deny → back to 'unpaid'
     (customer asked to resend proof).

All functions are pure workflow steps: they mutate the DB and return the
order dict. Message text comes from the i18n layer in the handlers.
"""

from __future__ import annotations

from .db import Database


def money(value: float | str) -> str:
    """Format a numeric value as 2-decimal money for chat display."""
    return f"{float(value):.2f}"


def cart_total(cart: list[dict]) -> float:
    return round(sum(float(i["price"]) * int(i["qty"]) for i in cart), 2)


def create_order_from_cart(
    db: Database,
    customer_phone: str,
    cook_phone: str,
    cart: list[dict],
    payment_type: str,
) -> dict:
    """Snapshot the cart into an order row (JSONB) and return it."""
    items = [
        {"item": c["item_name"], "quantity": int(c["qty"]), "price": float(c["price"])}
        for c in cart
    ]
    return db.create_order(
        customer_phone=customer_phone,
        cook_phone=cook_phone,
        ordered_items=items,
        total_sum=cart_total(cart),
        payment_type=payment_type,
    )


def submit_p2p_proof(db: Database, order_id: int, proof_ref: str) -> dict | None:
    """Flag an order as pending_approval with the customer's proof reference.

    proof_ref is either 'photo:<media-id>' for a screenshot upload or
    'ref:<text>' for a typed reference name/ID.
    """
    return db.update_order(
        order_id, payment_status="pending_approval", payment_proof_ref=proof_ref[:300]
    )


def decide_payment(db: Database, order_id: int, approved: bool) -> dict | None:
    """Cook's single-digit verdict on a P2P proof."""
    if approved:
        return db.update_order(order_id, payment_status="verified")
    return db.update_order(order_id, payment_status="unpaid", payment_proof_ref="")


def describe_proof(proof_ref: str) -> str:
    """Human-readable proof description for the cook's chat."""
    if proof_ref.startswith("photo:"):
        return "📸 photo screenshot"
    if proof_ref.startswith("ref:"):
        return proof_ref[4:] or "—"
    return proof_ref or "—"
