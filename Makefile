.PHONY: all run lint
.SILENT: all run lint

.DEFAULT_GOAL := all

SOURCE := $(shell pwd)/backend
CONFIG := --config pyproject.toml


all: lint run

run:
	poetry run python3 $(SOURCE)/manage.py runserver

migrations:
	poetry run python3 $(SOURCE)/manage.py makemigrations api
	poetry run python3 $(SOURCE)/manage.py migrate

superuser:
	poetry run python3 $(SOURCE)/manage.py createsuperuser

lint:
	poetry run black $(CONFIG) $(SOURCE)