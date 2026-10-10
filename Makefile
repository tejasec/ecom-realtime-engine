# ==============================================================================
# AI System Design - Automation & Operational Tasks Makefile
# ==============================================================================

.PHONY: help up down restart ps logs test test-unit test-drift seed stream simulate clean

help:
	@echo "Available commands:"
	@echo "  make up          - Start all containers in background (Docker Compose)"
	@echo "  make down        - Stop and remove all containers and volumes"
	@echo "  make restart     - Restart the service stack"
	@echo "  make ps          - List status of all system containers"
	@echo "  make logs        - Tail logs from all containers"
	@echo "  make test        - Run all tests with pytest"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make test-drift  - Run KS-test drift detector unit test"
	@echo "  make seed        - Populate PostgreSQL warehouse with initial product vectors"
	@echo "  make stream      - Launch Kafka synthetic clickstream producer"
	@echo "  make simulate    - Execute end-to-end system simulation (stream -> drift -> retrain)"
	@echo "  make clean       - Remove cached bytecode and temporary files"

up:
	docker compose up -d --build

down:
	docker compose down -v

restart:
	docker compose restart

ps:
	docker compose ps

logs:
	docker compose logs -f

test:
	pytest tests/

test-unit:
	pytest tests/unit/

test-drift:
	pytest tests/unit/test_drift.py

seed:
	python3 scripts/seed_products.py

stream:
	python3 src/data_engineering/kafka_producer.py

simulate:
	python3 scripts/run_simulation.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
