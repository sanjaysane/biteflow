"""Domain constants: states, roles, and statuses.

The conversational state machine is declarative: STATE_ROUTES in
state_machine.py maps (role, state) -> handler. The state names below are
the contract between the dispatcher, the handlers, and the tests.
"""

from __future__ import annotations

# ── Roles ──────────────────────────────────────────────────────────
ROLE_CUSTOMER = "customer"
ROLE_COOK = "cook"

# ── Customer states ────────────────────────────────────────────────
C_NEW = "new"  # first contact / welcome
C_ASK_ROLE = "ask_role"  # "Reply 1 = customer, 2 = cook"
C_MENU_BROWSING = "menu_browsing"  # pick cook, then pick item (0 = checkout)
C_QUANTITY = "quantity_selection"  # "Reply 1-9"
C_REVIEW = "order_review"  # 1 = confirm -> payment, 2 = cancel
C_PAYMENT = "payment_method"  # 1 = COD, 2 = P2P transfer
C_PROOF = "payment_proof"  # screenshot photo OR reference name
C_TRACKING = "active_tracking"  # live order status
C_LANGUAGE = "language_select"  # 1 = en, 2 = es, 3 = hi (any state)

# ── Cook states ────────────────────────────────────────────────────
K_HOME = "cook_home"  # hub: 1 = menu broadcast, 2 = open orders
K_MENU = "menu_broadcast"  # guided add-item loop (name/price/more?)
K_INBOUND = "order_inbound_queue"  # 1 = accept/approve, 2 = reject/deny
K_STATUS = "status_update_broadcast"  # 1 = cooking, 2 = on the way, 3 = done

# ── Order / payment statuses (mirror the SQL enums) ────────────────
OPEN_ORDER_STATUSES = ("received", "accepted", "cooking", "out_for_delivery")

SUPPORTED_LANGUAGES = ("en", "es", "hi")
LANGUAGE_OPTIONS = (("1", "en"), ("2", "es"), ("3", "hi"))

# Words (any supported language) that open the language menu mid-chat.
LANGUAGE_COMMANDS = {"language", "idioma", "भाषा", "lang", "lenguaje"}
