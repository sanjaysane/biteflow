-- ═══════════════════════════════════════════════════════════════════
-- BiteFlow migration 007: allow grams ('g') as an ingredient unit
-- ═══════════════════════════════════════════════════════════════════
-- The original 002 CHECK allowed only ('kg', 'L', 'pcs'), but
-- seed_default_inventory() (src/owner/economics.py) seeds spice rows in
-- grams, and tests/test_phase_a.py asserts unit == 'g' for them. On a
-- real PostgreSQL the seed crashed with:
--   ERROR: new row for relation "ingredients" violates check constraint
--          "ingredients_unit_check"
-- FakeDatabase never enforced the CHECK, so the suite stayed green.
-- Fresh installs get the fixed 002 migration directly.
-- ═══════════════════════════════════════════════════════════════════

ALTER TABLE ingredients DROP CONSTRAINT IF EXISTS ingredients_unit_check;

ALTER TABLE ingredients ADD CONSTRAINT ingredients_unit_check
  CHECK (unit IN ('kg', 'L', 'g', 'pcs'));
