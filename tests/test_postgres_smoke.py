"""Postgres-backed smoke test: proves PostgresDatabase works against a REAL
PostgreSQL (not just FakeDatabase). Runs only when BITEFLOW_TEST_DATABASE_URL
is set (CI sets it against the postgres:16 service container); otherwise it
skips so local `pytest` stays dependency-free.

The CI job applies sql/schema.sql + sql/migrations/*.sql before running, so
this test also proves the migrations produce a schema the code can use.
"""

from __future__ import annotations

import os
import uuid

import pytest

DB_URL = os.environ.get("BITEFLOW_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DB_URL, reason="needs BITEFLOW_TEST_DATABASE_URL (real PostgreSQL)"
)

from src.db import PostgresDatabase


def _phone() -> str:
    return f"+1555{8000000 + uuid.uuid4().int % 999999:07d}"[:12]


def test_postgres_smoke_crud():
    db = PostgresDatabase(DB_URL)
    phone = _phone()

    user = db.upsert_user(phone, "customer", "en")
    assert user["phone_number"] == phone
    assert user["system_role"] == "customer"

    assert db.get_session(phone) is None
    db.save_session(
        phone, {"state": "C_MENU", "language": "en", "role": "customer", "data": {}}
    )
    session = db.get_session(phone)
    assert session["state"] == "C_MENU"

    ing = db.add_ingredient(phone, "Paneer", "kg", 4.0, 10.0, 2.0)
    assert ing["name"] == "Paneer"
    assert db.get_ingredient(ing["id"])["stock_qty"] == 10.0

    updated = db.update_ingredient(ing["id"], stock_qty=9.0)
    assert float(updated["stock_qty"]) == 9.0

    recipe = db.add_recipe(phone, "Paneer Tikka")
    db.add_recipe_item(recipe["id"], ing["id"], 0.5)
    items = db.get_recipe_items(recipe["id"])
    assert len(items) == 1
    assert float(items[0]["qty_per_dish"]) == 0.5

    supplier = db.add_supplier(phone, "Fresh Farms", "555-0100")
    assert supplier["name"] == "Fresh Farms"

    order = db.create_order(
        phone, phone, [{"item_name": "X", "qty": 1, "price": 5.0}], 5.0, "COD"
    )
    assert order["payment_status"] == "unpaid"
    fetched = db.get_order(order["id"])
    assert fetched["id"] == order["id"]


def test_postgres_brand_new_chat_flow():
    """Regression test: a brand-new chat has role=None until the user picks
    one. Real PostgreSQL used to reject that first save_session because
    chat_sessions.system_role was NOT NULL (FakeDatabase never enforced it,
    so the suite stayed green while production broke on message one)."""
    from pathlib import Path

    from src import models as M
    from src.i18n import I18n
    from src.state_machine import process_incoming
    from src.whatsapp import FakeWhatsAppClient

    db = PostgresDatabase(DB_URL)
    wa = FakeWhatsAppClient()
    i18n = I18n(str(Path(__file__).resolve().parent.parent / "locales"))
    phone = _phone()

    process_incoming(db, wa, i18n, phone, "hello")
    session = db.get_session(phone)
    assert session is not None
    assert session["state"] == M.C_ASK_ROLE
    assert session["role"] is None

    process_incoming(db, wa, i18n, phone, "1")
    user = db.get_user(phone)
    assert user is not None
    assert user["system_role"] == "customer"
    assert db.get_session(phone)["role"] == "customer"


def test_postgres_marathi_locale_accepted():
    """Regression: the users.preferred_language CHECK must accept 'mr'.

    models.SUPPORTED_LANGUAGES includes 'mr' and the chat language menu
    offers option 4 = Marathi, but the original schema.sql CHECK allowed
    only ('en', 'es', 'hi') — a user selecting Marathi crashed
    set_user_language with a check_violation (schema.sql fixed, plus
    migration 006 for existing databases). This test proves 'mr' round-
    trips on a REAL PostgreSQL, including Marathi UTF-8 strings.
    """
    import psycopg

    db = PostgresDatabase(DB_URL)
    phone = _phone()

    # 1. upsert with 'mr' directly (this exact call used to 500 on Postgres)
    user = db.upsert_user(phone, "customer", "mr")
    assert user["preferred_language"] == "mr"

    # 2. switch back and forth through the real set_user_language path
    db.set_user_language(phone, "en")
    assert db.get_user(phone)["preferred_language"] == "en"
    db.set_user_language(phone, "mr")
    assert db.get_user(phone)["preferred_language"] == "mr"

    # 3. Marathi UTF-8 display name round-trips byte-identical
    db.set_display_name(phone, "संजय साने")
    assert db.get_user(phone)["display_name"] == "संजय साने"

    # 4. the CHECK constraint itself names 'mr' (guards against a future
    #    schema.sql edit re-breaking this without touching any data)
    with psycopg.connect(DB_URL) as c, c.cursor() as cur:
        cur.execute(
            """
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'users'::regclass
              AND conname = 'users_preferred_language_check'
            """
        )
        definition = cur.fetchone()[0]
    assert "'mr'" in definition, f"CHECK missing 'mr': {definition}"


def test_postgres_inventory_seed_accepts_gram_unit():
    """Regression: ingredients_unit_check must accept 'g' (grams).

    seed_default_inventory() seeds spice rows in grams and
    test_phase_a asserts unit == 'g', but the original CHECK allowed only
    ('kg', 'L', 'pcs') — on real Postgres the seed crashed with a
    CheckViolation while the FakeDatabase suite stayed green.
    (002 migration fixed, plus migration 007 for existing databases.)
    """
    from src.owner import economics as E

    db = PostgresDatabase(DB_URL)
    phone = _phone()
    db.upsert_user(phone, "cook", "en")

    ings = E.seed_default_inventory(db, phone, "mr")
    assert len(ings) == 10
    units = {i["unit"] for i in ings}
    assert "g" in units, f"expected gram-unit rows, got {units}"
    assert all(float(i["stock_qty"]) > 0 for i in ings)
    haldi = next(i for i in ings if i["name"] == "Turmeric (Haldi)")
    assert haldi["unit"] == "g" and float(haldi["stock_qty"]) == 500.0
