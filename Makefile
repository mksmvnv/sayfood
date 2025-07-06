PHONY: all lint run

SRC		?= ./src
HOST	?= localhost
PORT	?= 8000


all: lint run

check:
	ruff check --fix --unsafe-fixes --exit-zero $(SRC)

format:
	ruff format $(SRC)

run:
	uvicorn $(SRC).main:app --host $(HOST) --port $(PORT) --reload