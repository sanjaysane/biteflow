"""Shared fixtures: in-memory DB, fake WhatsApp, real i18n, and a
`send` driver that pushes messages through the state machine exactly
like the webhook layer does.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.db import FakeDatabase
from src.i18n import I18n
from src.state_machine import process_incoming
from src.whatsapp import FakeWhatsAppClient

COOK = "+15550001111"
CUST = "+15550002222"
CUST_ES = "+15550003333"


@pytest.fixture
def db():
    return FakeDatabase()


@pytest.fixture
def wa():
    return FakeWhatsAppClient()


@pytest.fixture
def i18n():
    return I18n(str(ROOT / "locales"))


@pytest.fixture
def send(db, wa, i18n):
    def _send(phone, text=None, msg_type="text", media_id=None):
        process_incoming(
            db, wa, i18n, phone, text, msg_type=msg_type, media_id=media_id
        )

    return _send


@pytest.fixture
def cook_with_menu(db, wa, i18n, send):
    """Register COOK and broadcast a 2-item menu. Returns the cook phone."""
    send(COOK, "hello")
    send(COOK, "2")  # register as cook
    send(COOK, "1")  # cook home → set menu
    send(COOK, "Veg Pulao")  # dish name
    send(COOK, "8.50")  # price
    send(COOK, "0")  # skip photo
    send(COOK, "0")  # skip ingredients
    send(COOK, "0")  # skip description
    send(COOK, "1")  # add another
    send(COOK, "Dal Tadka")  # dish name
    send(COOK, "7")  # price
    send(COOK, "0")  # skip photo
    send(COOK, "0")  # skip ingredients
    send(COOK, "0")  # skip description
    send(COOK, "2")  # menu done
    return COOK


@pytest.fixture
def customer_at_menu(db, wa, i18n, send, cook_with_menu):
    """Register CUST as customer and land on the cook's menu listing."""
    send(CUST, "hello")
    send(CUST, "1")  # register as customer → cook list
    send(CUST, "1")  # pick the cook → menu shown
    return CUST
