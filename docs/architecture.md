# Architecture

## System components

- **Frontend** — HTML/CSS/JS
- **Backend** — FastAPI
- **Database** — PostgreSQL
- **LLM Provider** — OpenRouter

## Component interaction

```mermaid
flowchart LR
    U[Client Browser]

    subgraph Frontend
        FE[HTML/CSS/JS]
    end

    subgraph Backend
        BE[FastAPI]
    end

    subgraph Database
        PG[(PostgreSQL)]
    end

    subgraph LLM[LLM Provider]
        OR[OpenRouter]
    end

    U -->|HTTPS| FE
    FE -->|REST API| BE
    BE -->|REST API| OR
    BE -->|SQL| PG
```

1. User opens browser
2. Frontend:
    - serves static files (HTTPS)
    - calls Backend (REST API)
3. Backend:
    - Reads/writes PostgreSQL (SQL)
    - Calls OpenRouter for AI generation (REST API)
4. Response returns to Frontend
5. User sees result
