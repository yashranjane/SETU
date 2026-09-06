#!/bin/bash
set -e

echo "=========================================================="
echo "  SETU: The Innovation Procurement OS (Smart India Hackathon)"
echo "  Statutory Compliance: GFR 2017 Rule 173 (Non-Consultative)"
echo "=========================================================="

echo "[1/4] Stopping existing Docker containers..."
docker-compose down -v --remove-orphans 2>/dev/null || true

echo "[2/4] Building and launching containers (PostgreSQL + FastAPI + Web)..."
docker-compose up -d --build

echo "[3/4] Waiting for services to initialize..."
sleep 5

echo "[4/4] Seeding Pune Municipal Corporation Ward 14 dataset..."
docker-compose exec -T api python seed.py || true

echo ""
echo "=========================================================="
echo "  SETU System Online & Ready for Demonstration!"
echo "=========================================================="
echo "  * Main Operational Feed:  http://localhost:3000"
echo "  * Direct FastAPI UI:      http://localhost:8000"
echo "  * Interactive API Docs:   http://localhost:8000/api/v1/docs"
echo "  * Cryptographic Ledger:   http://localhost:8000/api/v1/audit/verify"
echo "=========================================================="
