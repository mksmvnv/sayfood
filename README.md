# SayFood

AI daily meal planner — FastAPI backend, vanilla JS frontend, PostgreSQL, OpenRouter.

## Quick start (Docker)

```bash
make up
```

Open http://localhost:3000

Docker uses `backend/.config/settings.yaml` and automatically rewrites `db.host` from `localhost` to `db` inside the container.

## Local development

```bash
# Backend
cd backend
make setup          # copies settings.example.yaml → settings.yaml
# Edit .config/settings.yaml (LLM API key, db.host: localhost)
make upgrade        # run migrations (requires local PostgreSQL)
make run            # API on :8000

# Frontend (separate terminal)
cd frontend
make run            # static server on :3000
```

Or from the project root:

```bash
make dev
```

## Configuration

All application settings live in `backend/.config/`:

| File | Purpose |
|------|---------|
| `settings.example.yaml` | Template for new setups (`make setup`) |
| `settings.yaml` | Main config (gitignored) — used locally and in Docker |

## Docker commands

| Command | Description |
|---------|-------------|
| `make up` | Build and start db + backend + frontend |
| `make down` | Stop containers |
| `make logs` | Follow service logs |
| `make rebuild` | Rebuild images from scratch |
| `make clean` | Stop containers and remove volumes |
| `make shell-backend` | Shell into backend container |
| `make shell-db` | Open psql in database container |
| `make test` | Run backend tests with 100% coverage gate |

## Architecture

- **frontend** — nginx serving static files, proxies `/api/*` → backend
- **backend** — FastAPI, runs Alembic migrations on startup
- **db** — PostgreSQL 16

## Testing

```bash
cd backend
make test-cov
```

81 tests cover domain, application, infrastructure, and API layers with a 100% coverage gate on `src/`.

## Production (VPS)

OpenRouter is blocked from some regions (e.g. Russia). Deploy on a EU VPS so the backend can reach the LLM API.

```bash
cp deploy/settings.production.example.yaml backend/.config/settings.yaml
# edit settings (LLM key, CORS with server IP/domain, DB password)

make prod-up
# or on server: docker compose -f docker-compose.prod.yml up -d --build
```

Deploy updates from your machine:

```bash
scp backend/.config/settings.yaml user@server:/opt/sayfood/backend/.config/
DEPLOY_HOST=user@server make deploy
```

Full guide: [deploy/DEPLOY.md](deploy/DEPLOY.md)

See [docs/architecture.md](docs/architecture.md) and [docs/requirements.md](docs/requirements.md).
