-- ═══════════════════════════════════════════════════════════════════
-- BiteFlow · Migration 002 — business-owner domains
-- Kitchen economics & operations + marketing & growth, all driven from
-- the cook's WhatsApp chat. ADDENDUM ONLY: never edits sql/schema.sql.
--
-- Run: psql "$DATABASE_URL" -f sql/migrations/002_business_owner.sql
-- ═══════════════════════════════════════════════════════════════════

-- ── Small additive change to the existing orders table ──────────────
-- Discounts (referral / first-order offer / referrer credit) applied at
-- review time. Nullable-with-default so all existing rows stay valid.
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS discount_total NUMERIC(10, 2) NOT NULL DEFAULT 0
    CHECK (discount_total >= 0),
  ADD COLUMN IF NOT EXISTS discount_desc TEXT NOT NULL DEFAULT '';

-- ═══════════════════════════════════════════════════════════════════
-- DOMAIN 1 · Kitchen economics & operations
-- ═══════════════════════════════════════════════════════════════════

-- ── ingredients ────────────────────────────────────────────────────
-- unit: 'kg' | 'L' | 'pcs'. unit_cost = last purchase price per unit.
-- last_alert_at suppresses repeat low-stock pings until stock recovers.
CREATE TABLE IF NOT EXISTS ingredients (
  id                  BIGSERIAL PRIMARY KEY,
  cook_phone          TEXT NOT NULL REFERENCES users (phone_number)
                      ON DELETE CASCADE,
  name                TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 80),
  unit                TEXT NOT NULL CHECK (unit IN ('kg', 'L', 'pcs')),
  unit_cost           NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
  stock_qty           NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
  low_stock_threshold NUMERIC(12, 3) NOT NULL DEFAULT 0 CHECK (low_stock_threshold >= 0),
  last_alert_at       TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ingredients_cook ON ingredients (cook_phone);
-- Partial index: the low-stock sweep only reads breaching rows.
CREATE INDEX IF NOT EXISTS idx_ingredients_low_stock
  ON ingredients (cook_phone, id)
  WHERE stock_qty <= low_stock_threshold AND low_stock_threshold > 0;

-- ── recipes: bill of materials per dish ────────────────────────────
CREATE TABLE IF NOT EXISTS recipes (
  id            BIGSERIAL PRIMARY KEY,
  cook_phone    TEXT NOT NULL REFERENCES users (phone_number)
                ON DELETE CASCADE,
  dish_name     TEXT NOT NULL CHECK (char_length(dish_name) BETWEEN 1 AND 120),
  menu_item_id  BIGINT REFERENCES menus (id) ON DELETE SET NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (cook_phone, dish_name)
);
CREATE INDEX IF NOT EXISTS idx_recipes_cook ON recipes (cook_phone);

CREATE TABLE IF NOT EXISTS recipe_items (
  id            BIGSERIAL PRIMARY KEY,
  recipe_id     BIGINT NOT NULL REFERENCES recipes (id) ON DELETE CASCADE,
  ingredient_id BIGINT NOT NULL REFERENCES ingredients (id)
                ON DELETE RESTRICT,
  qty_per_dish  NUMERIC(12, 3) NOT NULL CHECK (qty_per_dish > 0),
  UNIQUE (recipe_id, ingredient_id)
);
CREATE INDEX IF NOT EXISTS idx_recipe_items_recipe ON recipe_items (recipe_id);

-- ── suppliers & purchases ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id          BIGSERIAL PRIMARY KEY,
  cook_phone  TEXT NOT NULL REFERENCES users (phone_number)
              ON DELETE CASCADE,
  name        TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 80),
  contact     TEXT NOT NULL DEFAULT '',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_suppliers_cook ON suppliers (cook_phone);

CREATE TABLE IF NOT EXISTS purchases (
  id            BIGSERIAL PRIMARY KEY,
  cook_phone    TEXT NOT NULL REFERENCES users (phone_number)
                ON DELETE CASCADE,
  supplier_id   BIGINT REFERENCES suppliers (id) ON DELETE SET NULL,
  ingredient_id BIGINT NOT NULL REFERENCES ingredients (id)
                ON DELETE RESTRICT,
  qty           NUMERIC(12, 3) NOT NULL CHECK (qty > 0),
  unit_cost     NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
  purchased_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_purchases_cook ON purchases (cook_phone, purchased_at DESC);

-- ── business costs: capex + opex in one ledger ─────────────────────
CREATE TABLE IF NOT EXISTS business_costs (
  id        BIGSERIAL PRIMARY KEY,
  cook_phone TEXT NOT NULL REFERENCES users (phone_number)
              ON DELETE CASCADE,
  kind      TEXT NOT NULL CHECK (kind IN ('capex', 'opex')),
  label     TEXT NOT NULL CHECK (char_length(label) BETWEEN 1 AND 120),
  amount    NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
  logged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_costs_cook ON business_costs (cook_phone, logged_at DESC);

-- ═══════════════════════════════════════════════════════════════════
-- DOMAIN 2 · Marketing & growth
-- ═══════════════════════════════════════════════════════════════════

-- ── referrals: dual-sided codes ────────────────────────────────────
CREATE TABLE IF NOT EXISTS referrals (
  id             BIGSERIAL PRIMARY KEY,
  cook_phone     TEXT NOT NULL REFERENCES users (phone_number)
                 ON DELETE CASCADE,
  code           TEXT NOT NULL UNIQUE,
  referrer_phone TEXT NOT NULL,
  reward_amount  NUMERIC(10, 2) NOT NULL CHECK (reward_amount >= 0),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_referrals_cook ON referrals (cook_phone);

CREATE TABLE IF NOT EXISTS referral_redemptions (
  id             BIGSERIAL PRIMARY KEY,
  referral_id    BIGINT NOT NULL REFERENCES referrals (id) ON DELETE CASCADE,
  redeemer_phone TEXT NOT NULL,
  order_id       BIGINT REFERENCES orders (id) ON DELETE SET NULL,
  rewarded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (referral_id, redeemer_phone),
  -- Supports idempotent re-finalize: ON CONFLICT (referral_id, order_id).
  UNIQUE (referral_id, order_id)
);

-- Referrer credit ledger: earned on each redemption, consumed when the
-- referrer's own order auto-applies credit. balance = SUM(delta).
CREATE TABLE IF NOT EXISTS referral_credit_ledger (
  id          BIGSERIAL PRIMARY KEY,
  cook_phone  TEXT NOT NULL REFERENCES users (phone_number)
              ON DELETE CASCADE,
  phone       TEXT NOT NULL,
  delta       NUMERIC(10, 2) NOT NULL,
  reason      TEXT NOT NULL DEFAULT '',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_credit_ledger_lookup
  ON referral_credit_ledger (cook_phone, phone);

-- ── freemium first-order offers (cook-configurable) ─────────────────
CREATE TABLE IF NOT EXISTS marketing_offers (
  id          BIGSERIAL PRIMARY KEY,
  cook_phone  TEXT NOT NULL REFERENCES users (phone_number)
              ON DELETE CASCADE,
  offer_type  TEXT NOT NULL CHECK (offer_type IN
              ('first_order_percent_off', 'first_order_free_item',
               'first_order_free_delivery')),
  value_text  TEXT NOT NULL DEFAULT '',
  active      BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (cook_phone, offer_type)
);

-- ── broadcast campaigns + opt-ins ──────────────────────────────────
CREATE TABLE IF NOT EXISTS campaigns (
  id         BIGSERIAL PRIMARY KEY,
  cook_phone TEXT NOT NULL REFERENCES users (phone_number)
             ON DELETE CASCADE,
  title      TEXT NOT NULL CHECK (char_length(title) BETWEEN 1 AND 120),
  body       TEXT NOT NULL CHECK (char_length(body) BETWEEN 1 AND 1000),
  sent_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketing_optins (
  cook_phone      TEXT NOT NULL REFERENCES users (phone_number)
                  ON DELETE CASCADE,
  customer_phone  TEXT NOT NULL REFERENCES users (phone_number)
                  ON DELETE CASCADE,
  opted_in        BOOLEAN NOT NULL DEFAULT TRUE,
  last_winback_at TIMESTAMPTZ,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (cook_phone, customer_phone)
);
