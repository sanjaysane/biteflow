#!/usr/bin/env bash
# Container entrypoint: wait for Postgres, apply schema + migrations
# (all idempotent), then start the webhook server.
set -euo pipefail

python - <<'EOF'
import os, time
import psycopg

url = os.environ.get("DATABASE_URL", "")
if not url:
    raise SystemExit("DATABASE_URL is not set")

for i in range(60):
    try:
        with psycopg.connect(url, connect_timeout=3):
            pass
        break
    except Exception as exc:  # noqa: BLE001 - boot-time retry loop
        print(f"[entrypoint] waiting for postgres ({i + 1}/60): {exc}")
        time.sleep(2)
else:
    raise SystemExit("postgres never became reachable")
print("[entrypoint] postgres reachable")
EOF

python scripts/apply_migrations.py

exec python -m uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"
