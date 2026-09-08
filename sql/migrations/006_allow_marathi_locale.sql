-- ═══════════════════════════════════════════════════════════════════
-- BiteFlow migration 006: allow Marathi ('mr') locale
-- ═══════════════════════════════════════════════════════════════════
-- The original schema.sql CHECK allowed only ('en', 'es', 'hi'), but
-- models.SUPPORTED_LANGUAGES = ("en", "es", "hi", "mr") and the chat
-- language menu offers option 4 = मराठी. A user selecting Marathi hit
-- `db.set_user_language(phone, 'mr')`, which Postgres rejected with:
--   ERROR: new row for relation "users" violates check constraint
--          "users_preferred_language_check"
-- This migration widens the constraint for databases created with the
-- old schema (fresh installs get the fixed schema.sql directly).
-- ═══════════════════════════════════════════════════════════════════

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_preferred_language_check;

ALTER TABLE users ADD CONSTRAINT users_preferred_language_check
  CHECK (preferred_language IN ('en', 'es', 'hi', 'mr'));
