"""Meta webhook contract: GET verification handshake and POST payload
parsing, using the real FastAPI app with fakes injected.
"""

import pytest
from fastapi.testclient import TestClient

from src import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "")
    monkeypatch.setenv("DATABASE_URL", "")
    main.settings.webhook_verify_token = "test-secret"
    with TestClient(main.app) as c:
        yield c
    main.settings.webhook_verify_token = ""


def _meta_payload(phone, body):
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": phone,
                                    "id": "wamid.1",
                                    "type": "text",
                                    "text": {"body": body},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }


def test_webhook_verify_success(client):
    r = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-secret",
            "hub.challenge": "challenge-42",
        },
    )
    assert r.status_code == 200
    assert r.text == "challenge-42"


def test_webhook_verify_wrong_token(client):
    r = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "challenge-42",
        },
    )
    assert r.status_code == 403


def test_webhook_post_drives_state_machine(client):
    from src.db import FakeDatabase
    from src.whatsapp import FakeWhatsAppClient

    main.app.state.db = FakeDatabase()
    main.app.state.wa = FakeWhatsAppClient()

    r = client.post("/webhook", json=_meta_payload("15550007777", "hello"))
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    sent = main.app.state.wa.sent
    assert sent, "no WhatsApp reply recorded"
    assert "Welcome to BiteFlow" in sent[0][1]
    session = main.app.state.db.get_session("+15550007777")
    assert session["state"] == "ask_role"


def test_webhook_post_image_payload(client):
    from src.db import FakeDatabase
    from src.whatsapp import FakeWhatsAppClient

    main.app.state.db = FakeDatabase()
    main.app.state.wa = FakeWhatsAppClient()

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "15550007777",
                                    "id": "wamid.2",
                                    "type": "image",
                                    "image": {"id": "media-1", "caption": "receipt"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    r = client.post("/webhook", json=payload)
    assert r.status_code == 200  # brand-new user + image → welcome flow, no crash


def test_webhook_post_status_only_payload(client):
    # Delivery receipts carry no "messages" key — must not crash.
    payload = {
        "entry": [
            {
                "changes": [
                    {"value": {"statuses": [{"id": "wamid.1"}]}, "field": "messages"}
                ]
            }
        ]
    }
    r = client.post("/webhook", json=payload)
    assert r.status_code == 200
    assert r.json() == {"ok": True}
