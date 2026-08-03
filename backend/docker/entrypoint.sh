#!/bin/sh
set -e

SETTINGS_HOST="/app/.config/settings.host.yaml"
SETTINGS_RUNTIME="/app/.config/settings.yaml"

if [ -f "$SETTINGS_HOST" ]; then
    cp "$SETTINGS_HOST" "$SETTINGS_RUNTIME"
    sed -i \
        -e 's/@localhost:/@db:/g' \
        -e 's/host: localhost/host: db/g' \
        -e 's/host: "localhost"/host: "db"/g' \
        "$SETTINGS_RUNTIME"
fi

echo "Waiting for PostgreSQL..."
until uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.infrastructure.config.settings import settings

async def check() -> None:
    engine = create_async_engine(settings.db.url.get_secret_value())
    async with engine.connect() as conn:
        await conn.execute(__import__('sqlalchemy').text('SELECT 1'))
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; do
  sleep 1
done

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting API server..."
exec uv run uvicorn src.app:app --host 0.0.0.0 --port 8000
