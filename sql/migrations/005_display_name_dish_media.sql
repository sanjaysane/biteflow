-- 005 · Phase A: nicknames + dish media
--
-- users.display_name: human nickname shown on every customer-facing
--   surface instead of the raw phone number (phone = fallback only).
-- menus.photo_ref:   "photo:<whatsapp-media-id>" for a real upload, or
--   "sample:<label>" for clearly-labeled sample/fixture data (never a
--   real upload claim).
-- menus.ingredients: free-form ingredient list shown on the menu.

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS display_name TEXT;

ALTER TABLE menus
  ADD COLUMN IF NOT EXISTS photo_ref TEXT;

ALTER TABLE menus
  ADD COLUMN IF NOT EXISTS ingredients TEXT NOT NULL DEFAULT '';
