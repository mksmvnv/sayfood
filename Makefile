.PHONY: all run lint
.SILENT: all run lint

WORKDIR     = ./backend

BLACKFLAGS  = --config pyproject.toml
FLAKECONFIG = --config ./setup.cfg

all: lint run

run:
	poetry run docker-compose -f ./infra/docker-compose.yml up -d --build

lint:
	poetry run black $(WORKDIR) $(BLACKFLAGS)
	poetry run flake8 $(WORKDIR) $(FLAKECONFIG) || true