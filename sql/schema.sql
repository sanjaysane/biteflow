-- ═══════════════════════════════════════════════════════════════════
-- BiteFlow · Supabase / PostgreSQL schema
-- Zero-client WhatsApp micro-commerce for senior citizens.
-- Run once: psql "$DATABASE_URL" -f sql/schema.sql
-- (or paste into the Supabase SQL editor)
-- ═══════════════════════════════════════════════════════════════════

-- ── Enumerated types ─────────────────────────────────────────────
DO $$ BEGIN
  CREATE TYPE system_role AS ENUM ('cook', 'customer');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE payment_type AS ENUM ('COD', 'P2P_TRANSFER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE payment_status AS ENUM ('unpaid', 'pending_approval', 'verified');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE order_status AS ENUM (
    'received', 'accepted', 'cooking',
    'out_for_delivery', 'completed', 'cancelled'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ── users ────────────────────────────────────────────────────────
-- Phone number (E.164) is the natural key: WhatsApp identity == account.
CREATE TABLE IF NOT EXISTS users (
  id                  BIGSERIAL PRIMARY KEY,
  phone_number        TEXT NOT NULL UNIQUE
                      CHECK (phone_number ~ '^\+[1-9][0-9]{6,14}$'),
  system_role         system_role NOT NULL,
  preferred_language  TEXT NOT NULL DEFAULT 'en'
                      CHECK (preferred_language IN ('en', 'es', 'hi', 'mr')),
  display_name        TEXT,  -- human nickname; phone is the fallback
  registration_timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- High-frequency telephone routing: every inbound webhook hits this index.
CREATE INDEX IF NOT EXISTS idx_users_phone ON users (phone_number);

-- ── chat_sessions ────────────────────────────────────────────────
-- Serverless state store. The webhook process is stateless: every inbound
-- message hydrates (phone → session row), dispatches, then persists.
CREATE TABLE IF NOT EXISTS chat_sessions (
  phone_number  TEXT PRIMARY KEY REFERENCES users (phone_number)
                ON DELETE CASCADE,
  system_role   system_role NOT NULL,
  state         TEXT NOT NULL,
  language      TEXT NOT NULL DEFAULT 'en',
  data          JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── menus ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS menus (
  id            BIGSERIAL PRIMARY KEY,
  cook_phone    TEXT NOT NULL REFERENCES users (phone_number)
                ON DELETE CASCADE,
  item_name     TEXT NOT NULL CHECK (char_length(item_name) BETWEEN 1 AND 120),
  description   TEXT NOT NULL DEFAULT '',
  base_price    NUMERIC(10, 2) NOT NULL CHECK (base_price > 0),
  language_iso  TEXT NOT NULL DEFAULT 'en',
  photo_ref     TEXT,  -- "photo:<wa-media-id>" | "sample:<label>"
  ingredients   TEXT NOT NULL DEFAULT '',
  active_status BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_menus_cook ON menus (cook_phone);
-- Partial index: menu browsing only ever reads ACTIVE items.
CREATE INDEX IF NOT EXISTS idx_menus_active
  ON menus (cook_phone, id)
  WHERE active_status = TRUE;

-- ── orders ───────────────────────────────────────────────────────
-- ordered_items: JSONB snapshot [{item, quantity, price}] so later menu
-- edits never rewrite history on a placed order.
CREATE TABLE IF NOT EXISTS orders (
  id                  BIGSERIAL PRIMARY KEY,
  customer_phone      TEXT NOT NULL REFERENCES users (phone_number)
                      ON DELETE RESTRICT,
  cook_phone          TEXT NOT NULL REFERENCES users (phone_number)
                      ON DELETE RESTRICT,
  ordered_items       JSONB NOT NULL DEFAULT '[]'::jsonb,
  total_sum           NUMERIC(10, 2) NOT NULL CHECK (total_sum >= 0),
  payment_type        payment_type NOT NULL,
  payment_status      payment_status NOT NULL DEFAULT 'unpaid',
  payment_proof_ref   TEXT NOT NULL DEFAULT '',
  order_status        order_status NOT NULL DEFAULT 'received',
  delivery_target_time TIMESTAMPTZ,
  creation_time       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_phone);
CREATE INDEX IF NOT EXISTS idx_orders_cook ON orders (cook_phone);
-- Partial index: tracking queues only ever read UNCOMPLETED orders.
CREATE INDEX IF NOT EXISTS idx_orders_open
  ON orders (cook_phone, creation_time DESC)
  WHERE order_status NOT IN ('completed', 'cancelled');
CREATE INDEX IF NOT EXISTS idx_orders_open_customer
  ON orders (customer_phone, creation_time DESC)
  WHERE order_status NOT IN ('completed', 'cancelled');

-- ── Seed: one demo cook + menu (safe to re-run) ──────────────────
INSERT INTO users (phone_number, system_role, preferred_language)
VALUES ('+15550001111', 'cook', 'en')
ON CONFLICT (phone_number) DO NOTHING;

INSERT INTO menus (cook_phone, item_name, description, base_price, language_iso, active_status)
SELECT '+15550001111', item, descr, price, 'en', TRUE
FROM (VALUES
  ('Veg Pulao', 'Fragrant rice with mixed vegetables', 8.50),
  ('Dal Tadka + Roti (2)', 'Yellow dal with two rotis', 7.00),
  ('Masala Chai', 'Spiced milk tea', 2.50)
) AS seed(item, descr, price)
WHERE NOT EXISTS (
  SELECT 1 FROM menus WHERE cook_phone = '+15550001111'
);
