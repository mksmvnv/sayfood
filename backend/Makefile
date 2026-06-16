.PHONY: fix check

SRC ?= src

# Application

all: fix check run

run:
	uv run uvicorn src.app:app --reload

# Code quality

fix:
	uv run ruff format $(SRC)
	uv run ruff check --fix $(SRC)

check:
	uv run ruff check $(SRC)
	uv run mypy $(SRC)