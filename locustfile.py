"""Load test: fires realistic Meta WhatsApp Cloud API webhook payloads at
POST /webhook, driving the same conversational flows a human would:

- CustomerUser: full order flow (welcome → cook → menu → qty → review →
  COD payment) against a seeded cook.
- CookUser: menu broadcast flow (hello → register → 2-item menu).
- OwnerUser: business hub (inventory/recipes/finance) + marketing hub
  (referrals/offer) walk-through.

Run against the compose stack:
    docker compose up --build -d
    locust -f locustfile.py --headless -u 20 -r 5 -t 2m --host http://localhost:8000
See docs/SCALE.md for method and measured numbers.
"""

from __future__ import annotations

import itertools
import time
import uuid

from locust import HttpUser, between, events, task

_phone_counter = itertools.count(1)


def _phone() -> str:
    return f"+1555{9000000 + next(_phone_counter):07d}"[:12]


def meta_payload(phone: str, text: str | None, msg_id: str) -> dict:
    """A minimal but shape-faithful Meta Cloud API inbound payload."""
    message: dict = {
        "from": phone.lstrip("+"),
        "id": msg_id,
        "timestamp": str(int(time.time())),
        "type": "text" if text else "unknown",
    }
    if text:
        message["text"] = {"body": text}
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "12345",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "999"},
                            "messages": [message],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }


class BiteFlowUser(HttpUser):
    wait_time = between(0.2, 0.8)

    def on_start(self):
        self.phone = _phone()

    def say(self, text: str, name: str):
        payload = meta_payload(self.phone, text, f"wamid.{uuid.uuid4().hex[:16]}")
        with self.client.post(
            "/webhook", json=payload, name=name, catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
            elif resp.json().get("ok") is not True:
                resp.failure(f"not ok: {resp.text[:80]}")

    # -- shared building blocks -------------------------------------
    def register_cook(self):
        for text, name in [
            ("hello", "cook: hello"),
            ("2", "cook: register"),
        ]:
            self.say(text, name)

    def broadcast_menu(self, tag: str):
        self.say("1", "cook: menu start")
        for dish, price in [("Veg Pulao", "8.50"), ("Dal Tadka", "7.00")]:
            self.say(dish, "cook: dish name")
            self.say(price, "cook: dish price")
            self.say("1", "cook: add another")
        # last "1" opened a third dish slot; finish it with a dish then done
        self.say(f"Raita {tag}", "cook: dish name")
        self.say("4.00", "cook: dish price")
        self.say("2", "cook: menu done")


@events.test_start.add_listener
def seed_cook(environment, **kwargs):
    """One shared cook with a live menu so CustomerUsers can order."""
    import requests

    host = environment.host
    phone = "+15550009999"
    script = [
        "hello",
        "2",
        "1",
        "Seed Thali",
        "9.99",
        "1",
        "Seed Curry",
        "7.50",
        "2",
        "Seed Done",
        "5.00",
        "2",
    ]
    for text in script:
        requests.post(
            f"{host}/webhook",
            json=meta_payload(phone, text, f"wamid.seed{uuid.uuid4().hex[:8]}"),
            timeout=10,
        )


class CustomerUser(BiteFlowUser):
    """End-to-end COD order against the seeded cook."""

    @task
    def order_flow(self):
        for text, name in [
            ("hello", "cust: hello"),
            ("1", "cust: register"),
            ("1", "cust: pick cook"),
            ("1", "cust: pick dish"),
            ("2", "cust: quantity"),
            ("0", "cust: checkout"),
            ("1", "cust: confirm"),
            ("1", "cust: COD"),
        ]:
            self.say(text, name)


class CookUser(BiteFlowUser):
    """Cook registration + two-item menu broadcast."""

    @task
    def cook_flow(self):
        self.register_cook()
        self.broadcast_menu(tag=uuid.uuid4().hex[:4])


class OwnerUser(BiteFlowUser):
    """Business-owner hubs: inventory → finance → referrals → offer."""

    @task
    def owner_flow(self):
        self.register_cook()
        for text, name in [
            ("3", "owner: business hub"),
            ("1", "owner: inventory"),
            ("0", "owner: back"),
            ("4", "owner: finance"),
            ("0", "owner: back"),
            ("5", "owner: marketing hub"),
            ("1", "owner: referrals"),
            ("0", "owner: back"),
            ("2", "owner: offer"),
            ("0", "owner: back"),
        ]:
            self.say(text, name)
