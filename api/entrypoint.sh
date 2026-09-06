#!/bin/bash
set -e

echo "===================================================="
echo " Starting SETU Backend (FastAPI + SQLModel)"
echo " Statutory Framework: GFR 2017 Rule 173"
echo "===================================================="

# Run database seed if needed
python seed.py || true

# Launch uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
