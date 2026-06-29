.PHONY: fix check run all migrate upgrade downgrade

SRC ?= src

# Application

all: fix check run

run:
	uv run uvicorn src.app:app --reload

# Database

migrate:
	alembic revision --autogenerate -m "$(m)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

# Code quality

fix:
	uv run ruff format $(SRC)
	uv run ruff check --fix $(SRC)

check:
	uv run ruff check $(SRC)
	uv run mypy $(SRC)