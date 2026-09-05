#!/usr/bin/env bash
# Local development: run the webhook server with env from .env
set -euo pipefail
cd "$(dirname "$0")"
if [ -f .env ]; then set -a; source .env; set +a; fi
exec python -m uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
