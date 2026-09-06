# SETU: Innovation Procurement OS (GFR 2017 Rule 173)

.PHONY: help dev build up down restart test seed logs clean

help:
	@echo "Available commands for Project SETU:"
	@echo "  make up       - Start all Docker containers (db, api, web)"
	@echo "  make down     - Stop all running containers"
	@echo "  make restart  - Restart all containers"
	@echo "  make seed     - Populate database with Maharashtra seed data"
	@echo "  make test     - Run complete 17-test Python test suite"
	@echo "  make logs     - View tail logs of containers"
	@echo "  make local    - Run local FastAPI server with zero-install UI"

up:
	docker-compose up -d --build
	@echo "Waiting for backend..."
	@sleep 3
	docker-compose exec -T api python seed.py || true
	@echo "SETU is live!"
	@echo "Web Dashboard:  http://localhost:3000 (or http://localhost:8000)"
	@echo "API Docs:       http://localhost:8000/api/v1/docs"

down:
	docker-compose down -v

restart: down up

seed:
	docker-compose exec -T api python seed.py

test:
	docker-compose exec -T api pytest tests/ -v

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
