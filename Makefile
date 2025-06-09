PHONY: all lint run

SRC 	?= src
HOST 	?= localhost
PORT	?= 8000

all: lint run

lint:
	black $(SRC)

run:
	uvicorn $(SRC).main:app --host $(HOST) --port $(PORT) --reload