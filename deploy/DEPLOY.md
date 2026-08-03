# Деплой на VPS (Нидерланды / EU)

OpenRouter блокируется из РФ на уровне Cloudflare. На сервере в EU всё работает напрямую.

## 1. Подготовка сервера

На VPS (Ubuntu/Debian):

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# перелогиниться
```

## 2. Первый запуск

```bash
git clone <repo-url> /opt/sayfood
cd /opt/sayfood

cp deploy/settings.production.example.yaml backend/.config/settings.yaml
nano backend/.config/settings.yaml
# — OpenRouter API key
# — сильный пароль PostgreSQL (url + password)
# — cors_origins: http://IP_СЕРВЕРА или https://домен

docker compose -f docker-compose.prod.yml up -d --build
```

Откройте `http://IP_СЕРВЕРА` — фронт на порту 80, API проксируется через nginx (`/api/`).

## 3. Обновление с локальной машины

```bash
# settings.yaml на сервер копируется только вручную (не в git)
DEPLOY_HOST=user@1.2.3.4 ./deploy/deploy.sh
```

Первый раз положите `settings.yaml` на сервер:

```bash
scp backend/.config/settings.yaml user@1.2.3.4:/opt/sayfood/backend/.config/settings.yaml
```

## 4. HTTPS с доменом (опционально)

```bash
cp deploy/Caddyfile.example deploy/Caddyfile
nano deploy/Caddyfile   # ваш домен, A-запись → IP сервера

# в settings.yaml: cors_origins + cookie.secure: true
docker compose -f docker-compose.prod.yml --profile tls up -d --build
```

Caddy сам получит Let's Encrypt сертификат.

## 5. Проверка OpenRouter с сервера

```bash
ssh user@server
curl -sS https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY" | head -c 200
```

Должен вернуть JSON со списком моделей, не `403`.

## Порты

| Сервис   | Снаружи | Внутри Docker |
|----------|---------|---------------|
| Frontend | 80      | nginx :80     |
| Backend  | —       | :8000         |
| Postgres | —       | :5432         |

## 6. GitHub Actions (CI/CD)

**CI** (`/.github/workflows/ci.yml`) — на каждый push/PR в `main` и `dev`:
- ruff, mypy, pytest с coverage 100%

**Deploy** (`/.github/workflows/deploy.yml`) — после успешных проверок при push в `main` (или вручную через Actions → Deploy):

| Secret | Описание |
|--------|----------|
| `DEPLOY_HOST` | IP или hostname VPS |
| `DEPLOY_USER` | SSH-пользователь |
| `DEPLOY_SSH_KEY` | Приватный SSH-ключ |

На сервере один раз:
```bash
git clone git@github.com:mksmvnv/sayfood.git /opt/sayfood
cp deploy/settings.production.example.yaml backend/.config/settings.yaml
nano backend/.config/settings.yaml
docker compose -f docker-compose.prod.yml up -d --build
```
