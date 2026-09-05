"""Business-owner conversational states (addendum).

Two workflow domains, both driven from the cook's WhatsApp chat under the
same senior-accessible contract (single-digit replies, emoji confirmations,
no free-form typing in core loops):

  Domain 1 — kitchen economics & operations (O_* states)
  Domain 2 — marketing & growth            (M_* states)

Plus one customer-side state (C_REFERRAL) for typing a referral code at
order review — the only typed input in the customer loop, mirroring the
existing P2P reference-name precedent.
"""

from __future__ import annotations

# ── Domain 1 · kitchen economics ─────────────────────────────────────
O_HOME = "owner_home"  # hub: 1 inventory 2 recipes 3 procurement 4 finance 0 back
# inventory
O_INV = "owner_inventory"  # list; 1 add ingredient, 2 log restock, 0 back
O_INV_ADD_NAME = "owner_inv_add_name"
O_INV_ADD_UNIT = "owner_inv_add_unit"  # 1 kg, 2 L, 3 pcs
O_INV_ADD_COST = "owner_inv_add_cost"  # price per unit
O_INV_ADD_STOCK = "owner_inv_add_stock"  # opening qty
O_INV_ADD_LOW = "owner_inv_add_low"  # low-stock threshold
O_RESTOCK_PICK = "owner_restock_pick"  # 1..n ingredient, 0 cancel
O_RESTOCK_QTY = "owner_restock_qty"  # qty received
O_RESTOCK_PRICE = "owner_restock_price"  # price paid, 0 = keep last
# recipes
O_REC = "owner_recipes"  # list w/ food cost; 1 add recipe, 0 back
O_REC_DISH = "owner_rec_dish"  # pick menu item 1..n to attach BOM to
O_REC_ING = "owner_rec_ing"  # pick ingredient 1..n, 0 = done
O_REC_QTY = "owner_rec_qty"  # qty of ingredient per dish
# procurement
O_SUP = "owner_procurement"  # 1 add supplier, 2 weekly purchase plan, 0 back
O_SUP_NAME = "owner_sup_name"
# finance
O_FIN = "owner_finance"  # 1 P&L 2 weekly projection 3 capex 4 opex 5 recon 0 back
O_COST_LABEL = "owner_cost_label"  # free text (kind carried in session data)
O_COST_AMOUNT = "owner_cost_amount"

# ── Domain 2 · marketing & growth ────────────────────────────────────
M_HOME = "marketing_home"  # hub: 1 referrals 2 first-order offer 3 campaign 4 win-back 0 back
M_REF = "marketing_referral"  # shows code+reward; 1 set reward, 0 back
M_REF_REWARD = "marketing_referral_reward"
M_OFFER = "marketing_offer"  # 1 %off 2 free item 3 free delivery 4 disable 0 back
M_OFFER_VALUE = "marketing_offer_value"
M_CAMP_TITLE = "marketing_camp_title"
M_CAMP_BODY = "marketing_camp_body"
M_CAMP_CONFIRM = "marketing_camp_confirm"  # 1 send 👍, 2 cancel 👎
M_WINBACK = "marketing_winback"  # shows inactive count; 1 send nudges, 0 back

# ── customer-side hook ───────────────────────────────────────────────
C_REFERRAL = "referral_code"  # typed referral code at order review
C_OPTIN = "marketing_optin"  # one-time menu-update opt-in after accept

# Ingredient units offered as single-digit picks (order is the contract).
UNITS = ("kg", "L", "pcs")

# Margin floor that triggers the price-shock alert (counterfactual path).
MARGIN_FLOOR = 0.20

# Win-back inactivity threshold (days).
WINBACK_DAYS = 14
