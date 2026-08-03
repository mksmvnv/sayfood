.PHONY: help up down build rebuild logs ps restart clean dev-backend dev-frontend dev migrate shell-backend shell-db prod-up prod-down prod-logs deploy

COMPOSE ?= docker compose
COMPOSE_PROD ?= $(COMPOSE) -f docker-compose.prod.yml

help:
	@echo "SayFood — available commands:"
	@echo ""
	@echo "  make up              Start all services (db, backend, frontend)"
	@echo "  make down            Stop and remove containers"
	@echo "  make build           Build Docker images"
	@echo "  make rebuild         Rebuild images without cache and start"
	@echo "  make restart         Restart all services"
	@echo "  make logs            Follow logs from all services"
	@echo "  make ps              Show running containers"
	@echo "  make clean           Stop containers and remove volumes"
	@echo ""
	@echo "  make dev             Run backend + frontend locally (no Docker)"
	@echo "  make dev-backend     Run backend locally with hot reload"
	@echo "  make dev-frontend    Run frontend locally on :3000"
	@echo "  make migrate         Run database migrations locally"
	@echo ""
	@echo "  make shell-backend   Open shell in backend container"
	@echo "  make shell-db        Open psql in database container"
	@echo ""
	@echo "  make prod-up         Start production stack (VPS)"
	@echo "  make prod-down       Stop production stack"
	@echo "  make prod-logs       Follow production logs"
	@echo "  make deploy          Deploy to DEPLOY_HOST (see deploy/DEPLOY.md)"

up:
	@test -f backend/.config/settings.yaml || (echo "Missing backend/.config/settings.yaml — run: cd backend && make setup" && exit 1)
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean:
	$(COMPOSE) down -v --remove-orphans

dev-backend:
	$(MAKE) -C backend run

dev-frontend:
	$(MAKE) -C frontend run

dev:
	@echo "Starting backend on :8000 and frontend on :3000..."
	$(MAKE) -C backend run & $(MAKE) -C frontend run

migrate:
	$(MAKE) -C backend upgrade

test:
	$(MAKE) -C backend test-cov

shell-backend:
	$(COMPOSE) exec backend sh

shell-db:
	$(COMPOSE) exec db psql -U postgres -d sayfood

prod-up:
	@test -f backend/.config/settings.yaml || (echo "Missing backend/.config/settings.yaml" && exit 1)
	$(COMPOSE_PROD) up -d --build

prod-down:
	$(COMPOSE_PROD) down

prod-logs:
	$(COMPOSE_PROD) logs -f

deploy:
	@test -n "$(DEPLOY_HOST)" || (echo "Usage: DEPLOY_HOST=user@server make deploy" && exit 1)
	./deploy/deploy.sh
