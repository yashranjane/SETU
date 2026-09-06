#!/bin/bash
set -e

echo "===================================================="
echo " Starting SETU Backend (FastAPI + SQLModel)"
echo " Statutory Framework: GFR 2017 Rule 173"
echo "===================================================="

# Run database seed if needed
python seed.py || true

# Launch uvicorn with dynamic PORT support (default: 8000)
PORT="${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
