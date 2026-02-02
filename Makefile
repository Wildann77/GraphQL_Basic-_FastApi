.PHONY: install dev-install up down watch test lint format migrate shell

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt
	pre-commit install

up:
	docker compose up --build -d

watch:
	docker compose up --watch

down:
	docker compose down -v

down-no-v:
	docker compose down

logs:
	docker compose logs -f api

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ --cov=src --cov-report=html

lint:
	ruff check src
	mypy src

format:
	black src tests
	ruff check src --fix

migrate:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

migrate-up:
	docker compose exec api alembic upgrade head

migrate-down:
	docker compose exec api alembic downgrade -1

shell:
	docker compose exec api bash
