.PHONY: fix check

SRC ?= src

# Application

all: fix check

# Code quality

fix:
	uv run ruff format $(SRC)
	uv run ruff check --fix $(SRC)

check:
	uv run ruff check $(SRC)
	uv run mypy $(SRC)