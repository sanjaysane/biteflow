"""Database access layer.

Two implementations share one interface:
  * PostgresDatabase — psycopg3, opens a short-lived connection per call.
    Serverless-safe (no persistent pool to leak between invocations).
  * FakeDatabase — in-memory dicts with identical semantics, used by tests
    and local development without a database.

Every query here mirrors sql/schema.sql exactly (table/column/enum names).
"""

from __future__ import annotations

import abc
import itertools
import json
import re
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Database(abc.ABC):
    # ── users ──────────────────────────────────────────────────
    @abc.abstractmethod
    def get_user(self, phone: str) -> dict | None: ...
    @abc.abstractmethod
    def upsert_user(self, phone: str, role: str, language: str) -> dict: ...
    @abc.abstractmethod
    def set_user_language(self, phone: str, language: str) -> None: ...

    # ── sessions (serverless state hydration) ──────────────────
    @abc.abstractmethod
    def get_session(self, phone: str) -> dict | None: ...
    @abc.abstractmethod
    def save_session(self, phone: str, session: dict) -> None: ...

    # ── menus ──────────────────────────────────────────────────
    @abc.abstractmethod
    def add_menu_item(self, cook_phone: str, item_name: str, description: str,
                      base_price: float, language_iso: str) -> dict: ...
    @abc.abstractmethod
    def get_active_menus(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def get_cooks_with_menus(self) -> list[dict]: ...
    @abc.abstractmethod
    def deactivate_menus(self, cook_phone: str) -> None: ...

    # ── orders ─────────────────────────────────────────────────
    @abc.abstractmethod
    def create_order(self, customer_phone: str, cook_phone: str,
                     ordered_items: list[dict], total_sum: float,
                     payment_type: str) -> dict: ...
    @abc.abstractmethod
    def get_order(self, order_id: int) -> dict | None: ...
    @abc.abstractmethod
    def update_order(self, order_id: int, **fields) -> dict | None: ...
    @abc.abstractmethod
    def get_open_orders_for_cook(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def get_open_orders_for_customer(self, customer_phone: str) -> list[dict]: ...

    # ── owner: ingredients ─────────────────────────────────────
    @abc.abstractmethod
    def add_ingredient(self, cook_phone: str, name: str, unit: str,
                       unit_cost: float, stock_qty: float,
                       low_threshold: float) -> dict: ...
    @abc.abstractmethod
    def get_ingredients(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def get_ingredient(self, ingredient_id: int) -> dict | None: ...
    @abc.abstractmethod
    def update_ingredient(self, ingredient_id: int, **fields) -> dict | None: ...

    # ── owner: recipes (bill of materials) ─────────────────────
    @abc.abstractmethod
    def add_recipe(self, cook_phone: str, dish_name: str,
                   menu_item_id: int | None = None) -> dict: ...
    @abc.abstractmethod
    def get_recipes(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def add_recipe_item(self, recipe_id: int, ingredient_id: int,
                        qty_per_dish: float) -> dict: ...
    @abc.abstractmethod
    def get_recipe_items(self, recipe_id: int) -> list[dict]: ...

    # ── owner: suppliers & purchases ───────────────────────────
    @abc.abstractmethod
    def add_supplier(self, cook_phone: str, name: str,
                     contact: str = "") -> dict: ...
    @abc.abstractmethod
    def get_suppliers(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def log_purchase(self, cook_phone: str, ingredient_id: int, qty: float,
                     unit_cost: float, supplier_id: int | None = None) -> dict: ...
    @abc.abstractmethod
    def get_purchases(self, cook_phone: str, since=None) -> list[dict]: ...

    # ── owner: capex / opex ledger ─────────────────────────────
    @abc.abstractmethod
    def add_business_cost(self, cook_phone: str, kind: str, label: str,
                          amount: float) -> dict: ...
    @abc.abstractmethod
    def get_business_costs(self, cook_phone: str, kind: str | None = None,
                           since=None) -> list[dict]: ...

    # ── owner: finance queries ─────────────────────────────────
    @abc.abstractmethod
    def get_completed_orders(self, cook_phone: str, since=None) -> list[dict]: ...
    @abc.abstractmethod
    def get_customer_last_order(self, cook_phone: str) -> dict: ...

    # ── marketing: referrals ───────────────────────────────────
    @abc.abstractmethod
    def create_referral(self, cook_phone: str, code: str, referrer_phone: str,
                        reward_amount: float) -> dict: ...
    @abc.abstractmethod
    def get_referral(self, referral_id: int) -> dict | None: ...
    @abc.abstractmethod
    def get_referral_by_code(self, code: str) -> dict | None: ...
    @abc.abstractmethod
    def get_referrals_for_cook(self, cook_phone: str) -> list[dict]: ...
    @abc.abstractmethod
    def set_referral_reward(self, referral_id: int,
                            reward_amount: float) -> dict | None: ...
    @abc.abstractmethod
    def record_redemption(self, referral_id: int, redeemer_phone: str,
                          order_id: int | None = None) -> bool: ...
    @abc.abstractmethod
    def get_referral_by_id(self, cook_phone: str,
                           referral_id: int) -> dict | None: ...
    @abc.abstractmethod
    def has_redeemed(self, referral_id: int, redeemer_phone: str) -> bool: ...
    @abc.abstractmethod
    def add_credit_ledger(self, cook_phone: str, phone: str, delta: float,
                          reason: str = "") -> dict: ...
    @abc.abstractmethod
    def get_credit_balance(self, cook_phone: str, phone: str) -> float: ...

    # ── marketing: offers ──────────────────────────────────────
    @abc.abstractmethod
    def set_offer(self, cook_phone: str, offer_type: str, value_text: str,
                  active: bool = True) -> dict: ...
    @abc.abstractmethod
    def get_active_offer(self, cook_phone: str) -> dict | None: ...
    @abc.abstractmethod
    def deactivate_offers(self, cook_phone: str) -> None: ...

    # ── marketing: campaigns & opt-ins ─────────────────────────
    @abc.abstractmethod
    def create_campaign(self, cook_phone: str, title: str, body: str) -> dict: ...
    @abc.abstractmethod
    def mark_campaign_sent(self, campaign_id: int, sent_count: int) -> None: ...
    @abc.abstractmethod
    def set_optin(self, cook_phone: str, customer_phone: str,
                  opted_in: bool) -> None: ...
    @abc.abstractmethod
    def get_opted_in_customers(self, cook_phone: str) -> list[str]: ...
    @abc.abstractmethod
    def get_last_winback_at(self, cook_phone: str,
                            customer_phone: str) -> str | None: ...
    @abc.abstractmethod
    def set_winback_sent(self, cook_phone: str, customer_phone: str) -> None: ...
    @abc.abstractmethod
    def optout_everywhere(self, customer_phone: str) -> int: ...


# ═══════════════════════════════════════════════════════════════════
# In-memory implementation (tests / local dev)
# ═══════════════════════════════════════════════════════════════════
class FakeDatabase(Database):
    def __init__(self) -> None:
        self.users: dict[str, dict] = {}
        self.sessions: dict[str, dict] = {}
        self.menus: dict[int, dict] = {}
        self.orders: dict[int, dict] = {}
        # owner addendum (Domain 1 + Domain 2)
        self.ingredients: dict = {}
        self.recipes: dict = {}
        self.recipe_items: dict = {}
        self.suppliers: dict = {}
        self.purchases: dict = {}
        self.business_costs: dict = {}
        self.referrals: dict = {}
        self.referral_redemptions: dict = {}
        self.credit_ledger: dict = {}
        self.marketing_offers: dict = {}
        self.campaigns: dict = {}
        self.marketing_optins: dict = {}  # keyed (cook_phone, customer_phone)
        self._ids = itertools.count(1)

    # users
    def get_user(self, phone: str) -> dict | None:
        return self.users.get(phone)

    def upsert_user(self, phone: str, role: str, language: str) -> dict:
        user = self.users.get(phone)
        if user is None:
            user = {
                "id": next(self._ids),
                "phone_number": phone,
                "system_role": role,
                "preferred_language": language,
                "registration_timestamp": utcnow(),
            }
            self.users[phone] = user
        else:
            user["system_role"] = role
        return user

    def set_user_language(self, phone: str, language: str) -> None:
        if phone in self.users:
            self.users[phone]["preferred_language"] = language

    # sessions
    def get_session(self, phone: str) -> dict | None:
        s = self.sessions.get(phone)
        return json.loads(json.dumps(s)) if s else None  # deep copy

    def save_session(self, phone: str, session: dict) -> None:
        self.sessions[phone] = json.loads(json.dumps(session))

    # menus
    def add_menu_item(self, cook_phone: str, item_name: str, description: str,
                      base_price: float, language_iso: str) -> dict:
        item = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "item_name": item_name,
            "description": description,
            "base_price": float(base_price),
            "language_iso": language_iso,
            "active_status": True,
            "created_at": utcnow(),
        }
        self.menus[item["id"]] = item
        return item

    def get_active_menus(self, cook_phone: str) -> list[dict]:
        return sorted(
            (m for m in self.menus.values()
             if m["cook_phone"] == cook_phone and m["active_status"]),
            key=lambda m: m["id"],
        )

    def get_cooks_with_menus(self) -> list[dict]:
        phones = sorted({m["cook_phone"] for m in self.menus.values()
                         if m["active_status"]})
        out = []
        for p in phones:
            user = self.users.get(p, {})
            out.append({"phone_number": p,
                        "preferred_language": user.get("preferred_language", "en")})
        return out

    def deactivate_menus(self, cook_phone: str) -> None:
        for m in self.menus.values():
            if m["cook_phone"] == cook_phone:
                m["active_status"] = False

    # orders
    def create_order(self, customer_phone: str, cook_phone: str,
                     ordered_items: list[dict], total_sum: float,
                     payment_type: str) -> dict:
        order = {
            "id": next(self._ids),
            "customer_phone": customer_phone,
            "cook_phone": cook_phone,
            "ordered_items": ordered_items,
            "total_sum": float(total_sum),
            "payment_type": payment_type,
            "payment_status": "unpaid",
            "payment_proof_ref": "",
            "order_status": "received",
            "delivery_target_time": None,
            "creation_time": utcnow(),
            "discount_total": 0.0,
            "discount_desc": "",
        }
        self.orders[order["id"]] = order
        return json.loads(json.dumps(order, default=str))

    def get_order(self, order_id: int) -> dict | None:
        o = self.orders.get(int(order_id))
        return json.loads(json.dumps(o, default=str)) if o else None

    def update_order(self, order_id: int, **fields) -> dict | None:
        order = self.orders.get(int(order_id))
        if order is None:
            return None
        order.update(fields)
        return self.get_order(order_id)

    def _open(self, rows: list[dict]) -> list[dict]:
        return sorted(
            (o for o in rows
             if o["order_status"] not in ("completed", "cancelled")),
            key=lambda o: o["creation_time"],
        )

    def get_open_orders_for_cook(self, cook_phone: str) -> list[dict]:
        return self._open([o for o in self.orders.values()
                           if o["cook_phone"] == cook_phone])

    def get_open_orders_for_customer(self, customer_phone: str) -> list[dict]:
        return self._open([o for o in self.orders.values()
                           if o["customer_phone"] == customer_phone])

    # ── owner: ingredients ─────────────────────────────────────
    def add_ingredient(self, cook_phone: str, name: str, unit: str,
                       unit_cost: float, stock_qty: float,
                       low_threshold: float) -> dict:
        ing = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "name": name,
            "unit": unit,
            "unit_cost": float(unit_cost),
            "stock_qty": float(stock_qty),
            "low_stock_threshold": float(low_threshold),
            "last_alert_at": None,
            "created_at": utcnow(),
        }
        self.ingredients[ing["id"]] = ing
        return ing

    def get_ingredients(self, cook_phone: str) -> list[dict]:
        return sorted(
            (i for i in self.ingredients.values()
             if i["cook_phone"] == cook_phone),
            key=lambda i: i["id"],
        )

    def get_ingredient(self, ingredient_id: int) -> dict | None:
        return self.ingredients.get(int(ingredient_id))

    def update_ingredient(self, ingredient_id: int, **fields) -> dict | None:
        ing = self.ingredients.get(int(ingredient_id))
        if ing is None:
            return None
        allowed = {"name", "unit", "unit_cost", "stock_qty",
                   "low_stock_threshold", "last_alert_at"}
        for k, v in fields.items():
            if k in allowed:
                ing[k] = v
        return ing

    # ── owner: recipes ─────────────────────────────────────────
    def add_recipe(self, cook_phone: str, dish_name: str,
                   menu_item_id: int | None = None) -> dict:
        recipe = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "dish_name": dish_name,
            "menu_item_id": menu_item_id,
            "created_at": utcnow(),
        }
        self.recipes[recipe["id"]] = recipe
        return recipe

    def get_recipes(self, cook_phone: str) -> list[dict]:
        return sorted(
            (r for r in self.recipes.values()
             if r["cook_phone"] == cook_phone),
            key=lambda r: r["id"],
        )

    def add_recipe_item(self, recipe_id: int, ingredient_id: int,
                        qty_per_dish: float) -> dict:
        item = {
            "id": next(self._ids),
            "recipe_id": int(recipe_id),
            "ingredient_id": int(ingredient_id),
            "qty_per_dish": float(qty_per_dish),
        }
        self.recipe_items[item["id"]] = item
        return item

    def get_recipe_items(self, recipe_id: int) -> list[dict]:
        out = []
        for it in self.recipe_items.values():
            if int(it["recipe_id"]) != int(recipe_id):
                continue
            ing = self.ingredients.get(int(it["ingredient_id"]), {})
            out.append({**it,
                        "ingredient_name": ing.get("name", "?"),
                        "unit": ing.get("unit", "?"),
                        "unit_cost": float(ing.get("unit_cost", 0))})
        return sorted(out, key=lambda i: i["id"])

    # ── owner: suppliers & purchases ───────────────────────────
    def add_supplier(self, cook_phone: str, name: str,
                     contact: str = "") -> dict:
        sup = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "name": name,
            "contact": contact,
            "created_at": utcnow(),
        }
        self.suppliers[sup["id"]] = sup
        return sup

    def get_suppliers(self, cook_phone: str) -> list[dict]:
        return sorted(
            (s for s in self.suppliers.values()
             if s["cook_phone"] == cook_phone),
            key=lambda s: s["id"],
        )

    def log_purchase(self, cook_phone: str, ingredient_id: int, qty: float,
                     unit_cost: float, supplier_id: int | None = None) -> dict:
        purchase = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "supplier_id": supplier_id,
            "ingredient_id": int(ingredient_id),
            "qty": float(qty),
            "unit_cost": float(unit_cost),
            "purchased_at": utcnow(),
        }
        self.purchases[purchase["id"]] = purchase
        ing = self.ingredients.get(int(ingredient_id))
        if ing is not None:
            ing["stock_qty"] = round(float(ing["stock_qty"]) + float(qty), 3)
            ing["unit_cost"] = float(unit_cost)  # last price wins
            if float(ing["stock_qty"]) > float(ing["low_stock_threshold"]):
                ing["last_alert_at"] = None  # recovered → may alert again
        return purchase

    def get_purchases(self, cook_phone: str, since=None) -> list[dict]:
        rows = [p for p in self.purchases.values()
                if p["cook_phone"] == cook_phone
                and (since is None or p["purchased_at"] >= since)]
        return sorted(rows, key=lambda p: p["purchased_at"], reverse=True)

    # ── owner: business costs ──────────────────────────────────
    def add_business_cost(self, cook_phone: str, kind: str, label: str,
                          amount: float) -> dict:
        entry = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "kind": kind,
            "label": label,
            "amount": float(amount),
            "logged_at": utcnow(),
        }
        self.business_costs[entry["id"]] = entry
        return entry

    def get_business_costs(self, cook_phone: str, kind: str | None = None,
                           since=None) -> list[dict]:
        rows = [c for c in self.business_costs.values()
                if c["cook_phone"] == cook_phone
                and (kind is None or c["kind"] == kind)
                and (since is None or c["logged_at"] >= since)]
        return sorted(rows, key=lambda c: c["logged_at"], reverse=True)

    # ── owner: finance queries ─────────────────────────────────
    def get_completed_orders(self, cook_phone: str, since=None) -> list[dict]:
        rows = [o for o in self.orders.values()
                if o["cook_phone"] == cook_phone
                and o["order_status"] == "completed"
                and (since is None or o["creation_time"] >= since)]
        return sorted(rows, key=lambda o: o["creation_time"])

    def get_customer_last_order(self, cook_phone: str) -> dict:
        last: dict[str, datetime] = {}
        for o in self.orders.values():
            if o["cook_phone"] != cook_phone or o["order_status"] != "completed":
                continue
            phone = o["customer_phone"]
            if phone not in last or o["creation_time"] > last[phone]:
                last[phone] = o["creation_time"]
        return {p: t.isoformat() for p, t in last.items()}

    # ── marketing: referrals ───────────────────────────────────
    def create_referral(self, cook_phone: str, code: str, referrer_phone: str,
                        reward_amount: float) -> dict:
        ref = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "code": code,
            "referrer_phone": referrer_phone,
            "reward_amount": float(reward_amount),
            "created_at": utcnow(),
        }
        self.referrals[ref["id"]] = ref
        return ref

    def get_referral(self, referral_id: int) -> dict | None:
        return self.referrals.get(int(referral_id))

    def get_referral_by_code(self, code: str) -> dict | None:
        for r in self.referrals.values():
            if r["code"] == (code or "").strip().upper():
                return r
        return None

    def get_referrals_for_cook(self, cook_phone: str) -> list[dict]:
        return sorted(
            (r for r in self.referrals.values()
             if r["cook_phone"] == cook_phone),
            key=lambda r: r["id"],
        )

    def set_referral_reward(self, referral_id: int,
                            reward_amount: float) -> dict | None:
        ref = self.referrals.get(int(referral_id))
        if ref is None:
            return None
        ref["reward_amount"] = float(reward_amount)
        return ref

    def record_redemption(self, referral_id: int, redeemer_phone: str,
                          order_id: int | None = None) -> bool:
        for red in self.referral_redemptions.values():
            # Mirrors Postgres: NULL order_ids never conflict with each other.
            if (red["referral_id"] == int(referral_id)
                    and order_id is not None
                    and red["order_id"] == order_id):
                return False  # already finalized for this order
        red = {
            "id": next(self._ids),
            "referral_id": int(referral_id),
            "redeemer_phone": redeemer_phone,
            "order_id": order_id,
            "rewarded_at": utcnow(),
        }
        self.referral_redemptions[red["id"]] = red
        return True

    def get_referral_by_id(self, cook_phone: str,
                           referral_id: int) -> dict | None:
        ref = self.referrals.get(int(referral_id))
        if ref is not None and ref["cook_phone"] != cook_phone:
            return None
        return ref

    def has_redeemed(self, referral_id: int, redeemer_phone: str) -> bool:
        return any(r["referral_id"] == int(referral_id)
                   and r["redeemer_phone"] == redeemer_phone
                   for r in self.referral_redemptions.values())

    def add_credit_ledger(self, cook_phone: str, phone: str, delta: float,
                          reason: str = "") -> dict:
        entry = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "phone": phone,
            "delta": float(delta),
            "reason": reason,
            "created_at": utcnow(),
        }
        self.credit_ledger[entry["id"]] = entry
        return entry

    def get_credit_balance(self, cook_phone: str, phone: str) -> float:
        return round(sum(e["delta"] for e in self.credit_ledger.values()
                         if e["cook_phone"] == cook_phone and e["phone"] == phone), 2)

    # ── marketing: offers ──────────────────────────────────────
    def set_offer(self, cook_phone: str, offer_type: str, value_text: str,
                  active: bool = True) -> dict:
        for o in self.marketing_offers.values():
            if o["cook_phone"] == cook_phone and o["offer_type"] == offer_type:
                o["value_text"] = value_text
                o["active"] = active
                return o
        offer = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "offer_type": offer_type,
            "value_text": value_text,
            "active": active,
            "created_at": utcnow(),
        }
        self.marketing_offers[offer["id"]] = offer
        return offer

    def get_active_offer(self, cook_phone: str) -> dict | None:
        actives = [o for o in self.marketing_offers.values()
                   if o["cook_phone"] == cook_phone and o["active"]]
        return sorted(actives, key=lambda o: o["id"])[-1] if actives else None

    def deactivate_offers(self, cook_phone: str) -> None:
        for o in self.marketing_offers.values():
            if o["cook_phone"] == cook_phone:
                o["active"] = False

    # ── marketing: campaigns & opt-ins ─────────────────────────
    def create_campaign(self, cook_phone: str, title: str, body: str) -> dict:
        camp = {
            "id": next(self._ids),
            "cook_phone": cook_phone,
            "title": title,
            "body": body,
            "sent_count": 0,
            "created_at": utcnow(),
        }
        self.campaigns[camp["id"]] = camp
        return camp

    def mark_campaign_sent(self, campaign_id: int, sent_count: int) -> None:
        camp = self.campaigns.get(int(campaign_id))
        if camp is not None:
            camp["sent_count"] = sent_count

    def set_optin(self, cook_phone: str, customer_phone: str,
                  opted_in: bool) -> None:
        key = (cook_phone, customer_phone)
        row = self.marketing_optins.get(key)
        if row is None:
            self.marketing_optins[key] = {
                "cook_phone": cook_phone,
                "customer_phone": customer_phone,
                "opted_in": opted_in,
                "last_winback_at": None,
                "updated_at": utcnow(),
            }
        else:
            row["opted_in"] = opted_in
            row["updated_at"] = utcnow()

    def get_opted_in_customers(self, cook_phone: str) -> list[str]:
        return sorted(
            key[1] for key, row in self.marketing_optins.items()
            if key[0] == cook_phone and row["opted_in"])

    def get_last_winback_at(self, cook_phone: str,
                            customer_phone: str) -> str | None:
        row = self.marketing_optins.get((cook_phone, customer_phone))
        if row is None or row.get("last_winback_at") is None:
            return None
        return row["last_winback_at"].isoformat()

    def set_winback_sent(self, cook_phone: str, customer_phone: str) -> None:
        key = (cook_phone, customer_phone)
        row = self.marketing_optins.get(key)
        if row is None:
            self.set_optin(cook_phone, customer_phone, True)
            row = self.marketing_optins[key]
        row["last_winback_at"] = utcnow()
        row["updated_at"] = utcnow()

    def optout_everywhere(self, customer_phone: str) -> int:
        count = 0
        for key, row in self.marketing_optins.items():
            if key[1] == customer_phone and row["opted_in"]:
                row["opted_in"] = False
                row["updated_at"] = utcnow()
                count += 1
        return count


# ═══════════════════════════════════════════════════════════════════
# Postgres implementation (Supabase / production)
# ═══════════════════════════════════════════════════════════════════
class PostgresDatabase(Database):
    """Short-lived connections per call: safe on serverless runtimes
    (Render, Vercel) where a persistent pool would leak across freezes."""

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise RuntimeError("DATABASE_URL is not set")
        self._url = database_url

    def _conn(self):
        import psycopg
        from psycopg.rows import dict_row
        return psycopg.connect(self._url, row_factory=dict_row)

    @staticmethod
    def _one(cur) -> dict | None:
        row = cur.fetchone()
        return dict(row) if row else None

    # ── users ──
    def get_user(self, phone: str) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE phone_number = %s", (phone,))
            return self._one(cur)

    def upsert_user(self, phone: str, role: str, language: str) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO users (phone_number, system_role, preferred_language)
                   VALUES (%s, %s::system_role, %s)
                   ON CONFLICT (phone_number)
                   DO UPDATE SET system_role = EXCLUDED.system_role
                   RETURNING *""",
                (phone, role, language),
            )
            return self._one(cur)  # type: ignore[return-value]

    def set_user_language(self, phone: str, language: str) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE users SET preferred_language = %s WHERE phone_number = %s",
                (language, phone),
            )

    # ── sessions ──
    def get_session(self, phone: str) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT phone_number, system_role, state, language, data
                   FROM chat_sessions WHERE phone_number = %s""",
                (phone,),
            )
            row = self._one(cur)
            if row is None:
                return None
            return {
                "role": row["system_role"],
                "state": row["state"],
                "lang": row["language"],
                "data": row["data"] or {},
            }

    def save_session(self, phone: str, session: dict) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO chat_sessions
                     (phone_number, system_role, state, language, data, updated_at)
                   VALUES (%s, %s::system_role, %s, %s, %s::jsonb, now())
                   ON CONFLICT (phone_number) DO UPDATE SET
                     state = EXCLUDED.state,
                     language = EXCLUDED.language,
                     data = EXCLUDED.data,
                     updated_at = now()""",
                (phone, session["role"], session["state"],
                 session.get("lang", "en"), json.dumps(session.get("data", {}))),
            )

    # ── menus ──
    def add_menu_item(self, cook_phone: str, item_name: str, description: str,
                      base_price: float, language_iso: str) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO menus
                     (cook_phone, item_name, description, base_price, language_iso)
                   VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                (cook_phone, item_name, description, base_price, language_iso),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_active_menus(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT * FROM menus
                   WHERE cook_phone = %s AND active_status = TRUE
                   ORDER BY id""",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_cooks_with_menus(self) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT DISTINCT u.phone_number, u.preferred_language
                   FROM users u JOIN menus m ON m.cook_phone = u.phone_number
                   WHERE m.active_status = TRUE
                   ORDER BY u.phone_number""",
            )
            return [dict(r) for r in cur.fetchall()]

    def deactivate_menus(self, cook_phone: str) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE menus SET active_status = FALSE WHERE cook_phone = %s",
                (cook_phone,),
            )

    # ── orders ──
    def create_order(self, customer_phone: str, cook_phone: str,
                     ordered_items: list[dict], total_sum: float,
                     payment_type: str) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO orders
                     (customer_phone, cook_phone, ordered_items, total_sum,
                      payment_type)
                   VALUES (%s, %s, %s::jsonb, %s, %s::payment_type)
                   RETURNING *""",
                (customer_phone, cook_phone, json.dumps(ordered_items),
                 total_sum, payment_type),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_order(self, order_id: int) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            return self._one(cur)

    def update_order(self, order_id: int, **fields) -> dict | None:
        if not fields:
            return self.get_order(order_id)
        allowed = {"ordered_items", "total_sum", "payment_type", "payment_status",
                   "payment_proof_ref", "order_status", "delivery_target_time",
                   "discount_total", "discount_desc"}
        cols = [k for k in fields if k in allowed]
        if not cols:
            return self.get_order(order_id)
        set_clause = ", ".join(f"{k} = %s" for k in cols)
        params: list = [json.dumps(fields[k]) if k == "ordered_items" else fields[k]
                        for k in cols]
        # cast enum columns explicitly
        set_clause = (set_clause
                      .replace("payment_type = %s", "payment_type = %s::payment_type")
                      .replace("payment_status = %s", "payment_status = %s::payment_status")
                      .replace("order_status = %s", "order_status = %s::order_status"))
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                f"UPDATE orders SET {set_clause} WHERE id = %s RETURNING *",
                (*params, order_id),
            )
            return self._one(cur)

    def get_open_orders_for_cook(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT * FROM orders
                   WHERE cook_phone = %s
                     AND order_status NOT IN ('completed', 'cancelled')
                   ORDER BY creation_time""",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_open_orders_for_customer(self, customer_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT * FROM orders
                   WHERE customer_phone = %s
                     AND order_status NOT IN ('completed', 'cancelled')
                   ORDER BY creation_time""",
                (customer_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    # ── owner: ingredients ─────────────────────────────────────
    def add_ingredient(self, cook_phone: str, name: str, unit: str,
                       unit_cost: float, stock_qty: float,
                       low_threshold: float) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO ingredients
                     (cook_phone, name, unit, unit_cost, stock_qty, low_stock_threshold)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
                (cook_phone, name, unit, unit_cost, stock_qty, low_threshold),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_ingredients(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT * FROM ingredients WHERE cook_phone = %s ORDER BY id",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_ingredient(self, ingredient_id: int) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT * FROM ingredients WHERE id = %s",
                        (int(ingredient_id),))
            return self._one(cur)

    def update_ingredient(self, ingredient_id: int, **fields) -> dict | None:
        if not fields:
            return self.get_ingredient(int(ingredient_id))
        allowed = {"name", "unit", "unit_cost", "stock_qty",
                   "low_stock_threshold", "last_alert_at"}
        cols = [k for k in fields if k in allowed]
        if not cols:
            return self.get_ingredient(int(ingredient_id))
        set_clause = ", ".join(f"{k} = %s" for k in cols)
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                f"UPDATE ingredients SET {set_clause} WHERE id = %s RETURNING *",
                [fields[k] for k in cols] + [int(ingredient_id)],
            )
            return self._one(cur)

    # ── owner: recipes ─────────────────────────────────────────
    def add_recipe(self, cook_phone: str, dish_name: str,
                   menu_item_id: int | None = None) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO recipes (cook_phone, dish_name, menu_item_id)
                   VALUES (%s, %s, %s) RETURNING *""",
                (cook_phone, dish_name, menu_item_id),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_recipes(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT * FROM recipes WHERE cook_phone = %s ORDER BY id",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def add_recipe_item(self, recipe_id: int, ingredient_id: int,
                        qty_per_dish: float) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO recipe_items (recipe_id, ingredient_id, qty_per_dish)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (recipe_id, ingredient_id)
                   DO UPDATE SET qty_per_dish = EXCLUDED.qty_per_dish
                   RETURNING *""",
                (int(recipe_id), int(ingredient_id), qty_per_dish),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_recipe_items(self, recipe_id: int) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT ri.*, i.name AS ingredient_name, i.unit,
                          i.unit_cost
                   FROM recipe_items ri
                   JOIN ingredients i ON i.id = ri.ingredient_id
                   WHERE ri.recipe_id = %s ORDER BY ri.id""",
                (int(recipe_id),),
            )
            return [dict(r) for r in cur.fetchall()]

    # ── owner: suppliers & purchases ───────────────────────────
    def add_supplier(self, cook_phone: str, name: str,
                     contact: str = "") -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO suppliers (cook_phone, name, contact)
                   VALUES (%s, %s, %s) RETURNING *""",
                (cook_phone, name, contact),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_suppliers(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT * FROM suppliers WHERE cook_phone = %s ORDER BY id",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def log_purchase(self, cook_phone: str, ingredient_id: int, qty: float,
                     unit_cost: float, supplier_id: int | None = None) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO purchases
                     (cook_phone, supplier_id, ingredient_id, qty, unit_cost)
                   VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                (cook_phone, supplier_id, int(ingredient_id), qty, unit_cost),
            )
            purchase = self._one(cur)
            # last price wins; recovery above threshold clears the alert latch
            cur.execute(
                """UPDATE ingredients
                   SET stock_qty = stock_qty + %s,
                       unit_cost = %s,
                       last_alert_at = CASE
                         WHEN stock_qty + %s > low_stock_threshold THEN NULL
                         ELSE last_alert_at END
                   WHERE id = %s""",
                (qty, unit_cost, qty, int(ingredient_id)),
            )
            return purchase  # type: ignore[return-value]

    def get_purchases(self, cook_phone: str, since=None) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            if since is None:
                cur.execute(
                    """SELECT * FROM purchases WHERE cook_phone = %s
                       ORDER BY purchased_at DESC""",
                    (cook_phone,),
                )
            else:
                cur.execute(
                    """SELECT * FROM purchases WHERE cook_phone = %s
                         AND purchased_at >= %s
                       ORDER BY purchased_at DESC""",
                    (cook_phone, since),
                )
            return [dict(r) for r in cur.fetchall()]

    # ── owner: business costs ──────────────────────────────────
    def add_business_cost(self, cook_phone: str, kind: str, label: str,
                          amount: float) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO business_costs (cook_phone, kind, label, amount)
                   VALUES (%s, %s, %s, %s) RETURNING *""",
                (cook_phone, kind, label, amount),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_business_costs(self, cook_phone: str, kind: str | None = None,
                           since=None) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            query = ("SELECT * FROM business_costs WHERE cook_phone = %s")
            params: list = [cook_phone]
            if kind is not None:
                query += " AND kind = %s"
                params.append(kind)
            if since is not None:
                query += " AND logged_at >= %s"
                params.append(since)
            query += " ORDER BY logged_at DESC"
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    # ── owner: finance queries ─────────────────────────────────
    def get_completed_orders(self, cook_phone: str, since=None) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            if since is None:
                cur.execute(
                    """SELECT * FROM orders WHERE cook_phone = %s
                         AND order_status = 'completed'
                       ORDER BY creation_time""",
                    (cook_phone,),
                )
            else:
                cur.execute(
                    """SELECT * FROM orders WHERE cook_phone = %s
                         AND order_status = 'completed'
                         AND creation_time >= %s
                       ORDER BY creation_time""",
                    (cook_phone, since),
                )
            return [dict(r) for r in cur.fetchall()]

    def get_customer_last_order(self, cook_phone: str) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT customer_phone, max(creation_time) AS last_ts
                   FROM orders
                   WHERE cook_phone = %s AND order_status = 'completed'
                   GROUP BY customer_phone""",
                (cook_phone,),
            )
            return {r["customer_phone"]: r["last_ts"].isoformat()
                    for r in cur.fetchall()}

    # ── marketing: referrals ───────────────────────────────────
    def create_referral(self, cook_phone: str, code: str, referrer_phone: str,
                        reward_amount: float) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO referrals
                     (cook_phone, code, referrer_phone, reward_amount)
                   VALUES (%s, %s, %s, %s) RETURNING *""",
                (cook_phone, code, referrer_phone, reward_amount),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_referral(self, referral_id: int) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT * FROM referrals WHERE id = %s",
                        (int(referral_id),))
            return self._one(cur)

    def get_referral_by_code(self, code: str) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT * FROM referrals WHERE code = %s",
                        ((code or "").strip().upper(),))
            return self._one(cur)

    def get_referrals_for_cook(self, cook_phone: str) -> list[dict]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT * FROM referrals WHERE cook_phone = %s ORDER BY id",
                (cook_phone,),
            )
            return [dict(r) for r in cur.fetchall()]

    def set_referral_reward(self, referral_id: int,
                            reward_amount: float) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """UPDATE referrals SET reward_amount = %s
                   WHERE id = %s RETURNING *""",
                (reward_amount, int(referral_id)),
            )
            return self._one(cur)

    def record_redemption(self, referral_id: int, redeemer_phone: str,
                          order_id: int | None = None) -> bool:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO referral_redemptions
                     (referral_id, redeemer_phone, order_id)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (referral_id, order_id) DO NOTHING
                   RETURNING id""",
                (int(referral_id), redeemer_phone, order_id),
            )
            return cur.fetchone() is not None

    def get_referral_by_id(self, cook_phone: str,
                           referral_id: int) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "SELECT * FROM referrals WHERE id = %s AND cook_phone = %s",
                (int(referral_id), cook_phone),
            )
            return self._one(cur)

    def has_redeemed(self, referral_id: int, redeemer_phone: str) -> bool:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT 1 FROM referral_redemptions
                   WHERE referral_id = %s AND redeemer_phone = %s""",
                (int(referral_id), redeemer_phone),
            )
            return cur.fetchone() is not None

    def add_credit_ledger(self, cook_phone: str, phone: str, delta: float,
                          reason: str = "") -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO referral_credit_ledger
                     (cook_phone, phone, delta, reason)
                   VALUES (%s, %s, %s, %s) RETURNING *""",
                (cook_phone, phone, delta, reason),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_credit_balance(self, cook_phone: str, phone: str) -> float:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(delta), 0) AS bal
                   FROM referral_credit_ledger
                   WHERE cook_phone = %s AND phone = %s""",
                (cook_phone, phone),
            )
            return float(self._one(cur)["bal"])  # type: ignore[index]

    # ── marketing: offers ──────────────────────────────────────
    def set_offer(self, cook_phone: str, offer_type: str, value_text: str,
                  active: bool = True) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO marketing_offers
                     (cook_phone, offer_type, value_text, active)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (cook_phone, offer_type)
                   DO UPDATE SET value_text = EXCLUDED.value_text,
                                 active = EXCLUDED.active
                   RETURNING *""",
                (cook_phone, offer_type, value_text, active),
            )
            return self._one(cur)  # type: ignore[return-value]

    def get_active_offer(self, cook_phone: str) -> dict | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT * FROM marketing_offers
                   WHERE cook_phone = %s AND active ORDER BY id DESC LIMIT 1""",
                (cook_phone,),
            )
            return self._one(cur)

    def deactivate_offers(self, cook_phone: str) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE marketing_offers SET active = FALSE WHERE cook_phone = %s",
                (cook_phone,),
            )

    # ── marketing: campaigns & opt-ins ─────────────────────────
    def create_campaign(self, cook_phone: str, title: str, body: str) -> dict:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO campaigns (cook_phone, title, body)
                   VALUES (%s, %s, %s) RETURNING *""",
                (cook_phone, title, body),
            )
            return self._one(cur)  # type: ignore[return-value]

    def mark_campaign_sent(self, campaign_id: int, sent_count: int) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE campaigns SET sent_count = %s WHERE id = %s",
                (sent_count, int(campaign_id)),
            )

    def set_optin(self, cook_phone: str, customer_phone: str,
                  opted_in: bool) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO marketing_optins
                     (cook_phone, customer_phone, opted_in)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (cook_phone, customer_phone)
                   DO UPDATE SET opted_in = EXCLUDED.opted_in,
                                 updated_at = now()""",
                (cook_phone, customer_phone, opted_in),
            )

    def get_opted_in_customers(self, cook_phone: str) -> list[str]:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT customer_phone FROM marketing_optins
                   WHERE cook_phone = %s AND opted_in ORDER BY customer_phone""",
                (cook_phone,),
            )
            return [r["customer_phone"] for r in cur.fetchall()]

    def get_last_winback_at(self, cook_phone: str,
                            customer_phone: str) -> str | None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT last_winback_at FROM marketing_optins
                   WHERE cook_phone = %s AND customer_phone = %s""",
                (cook_phone, customer_phone),
            )
            row = self._one(cur)
            if row is None or row.get("last_winback_at") is None:
                return None
            return row["last_winback_at"].isoformat()

    def set_winback_sent(self, cook_phone: str, customer_phone: str) -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO marketing_optins
                     (cook_phone, customer_phone, opted_in, last_winback_at)
                   VALUES (%s, %s, TRUE, now())
                   ON CONFLICT (cook_phone, customer_phone)
                   DO UPDATE SET last_winback_at = now(),
                                 updated_at = now()""",
                (cook_phone, customer_phone),
            )

    def optout_everywhere(self, customer_phone: str) -> int:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """UPDATE marketing_optins
                   SET opted_in = FALSE, updated_at = now()
                   WHERE customer_phone = %s AND opted_in""",
                (customer_phone,),
            )
            return cur.rowcount


PHONE_RE = re.compile(r"^\+[1-9][0-9]{6,14}$")


def normalize_phone(raw: str) -> str | None:
    """Meta sends digits only; normalize to E.164. Returns None if invalid."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    phone = "+" + digits
    return phone if PHONE_RE.match(phone) else None
