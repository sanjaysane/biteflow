"""Apply sql/schema.sql plus every sql/migrations/*.sql (in name order) to
the database named by BITEFLOW_TEST_DATABASE_URL (falling back to
DATABASE_URL).

Used by CI (real PostgreSQL service container) and docker/entrypoint.sh
so both prove the same thing: the migrations apply cleanly to a fresh
database. Every file in this repo is written to be idempotent
(IF NOT EXISTS / IF EXISTS / no-op ALTERs), so re-running is safe.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    url = os.environ.get("BITEFLOW_TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        print("BITEFLOW_TEST_DATABASE_URL / DATABASE_URL is not set", file=sys.stderr)
        sys.exit(2)
    import psycopg

    scripts = [ROOT / "sql" / "schema.sql"] + sorted(
        (ROOT / "sql" / "migrations").glob("*.sql")
    )
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            for script in scripts:
                print(f"applying {script.relative_to(ROOT)}")
                cur.execute(script.read_text(encoding="utf-8"))
        conn.commit()
    print("migrations applied OK")


if __name__ == "__main__":
    main()
