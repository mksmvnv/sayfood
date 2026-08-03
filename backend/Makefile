.PHONY: fix check run all migrate upgrade downgrade setup test test-cov

SRC ?= src

all: fix check run

setup:
	@test -f .config/settings.yaml || cp .config/settings.example.yaml .config/settings.yaml
	@echo "Created .config/settings.yaml — edit LLM API key before running."

run:
	uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic revision --autogenerate -m "$(m)"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

fix:
	uv run ruff format $(SRC)
	uv run ruff check --fix $(SRC)

check:
	uv run ruff check $(SRC)
	uv run mypy $(SRC)

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=term-missing
