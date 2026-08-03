#!/usr/bin/env bash
set -euo pipefail

# Deploy SayFood to a remote VPS.
#
# Usage:
#   DEPLOY_HOST=user@1.2.3.4 ./deploy/deploy.sh
#
# Optional:
#   REMOTE_DIR=/opt/sayfood
#   COMPOSE_FILE=docker-compose.prod.yml
#   COMPOSE_PROFILES=tls   # enables Caddy HTTPS profile

DEPLOY_HOST="${DEPLOY_HOST:?Set DEPLOY_HOST=user@your-server-ip}"
REMOTE_DIR="${REMOTE_DIR:-/opt/sayfood}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
COMPOSE_PROFILES="${COMPOSE_PROFILES:-}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ Syncing project to ${DEPLOY_HOST}:${REMOTE_DIR}"

rsync -avz --delete \
  --exclude '.git' \
  --exclude 'backend/.config/settings.yaml' \
  --exclude 'backend/.venv' \
  --exclude 'backend/.pytest_cache' \
  --exclude 'backend/htmlcov' \
  --exclude 'backend/pytest-cache-files-*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${ROOT_DIR}/" "${DEPLOY_HOST}:${REMOTE_DIR}/"

PROFILE_ARGS=""
if [ -n "${COMPOSE_PROFILES}" ]; then
  PROFILE_ARGS="--profile ${COMPOSE_PROFILES}"
fi

echo "→ Building and starting containers on server"
ssh "${DEPLOY_HOST}" "cd ${REMOTE_DIR} && docker compose -f ${COMPOSE_FILE} ${PROFILE_ARGS} up -d --build"

echo "Done. Open http://$(ssh "${DEPLOY_HOST}" 'hostname -I | awk "{print \$1}"' 2>/dev/null || echo 'your-server-ip')"
