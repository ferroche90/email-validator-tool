# Email-Validator-Tool – Internal Developer README

> Confidential – for core contributors only

---

## 1. Vision & Repository Map

**Vision** – Provide a production-grade, cloud-agnostic service that validates e-mail lists fast, accurately and at scale.  The mono-repo ships:

*  💻 **Backend** (`backend/`) – FastAPI micro-service exposed via `/api/*` with multi-tenant support.
*  🌐 **Frontend** (`frontend/`) – Vite + React 19 + Tailwind CSS single-page app.
*  🧠 **Core lib** (`backend/email_validator_tool/`) – Validator pipeline & pluggable rule engine, 100 % Python only.  Also published to PyPI.
*  🐳 **Infra** (`docker-compose.yml`, `infra/`) – Dev/prod compose files, Caddy reverse-proxy, SQLite/PostgreSQL, etc.
*  🧪 **Tests** (`tests/`, `backend/tests/`, `frontend/test/`) – Unified PyTest + Vitest suites.

```
repo/
├─ backend/                    # FastAPI app + services
│  ├─ app/                    # FastAPI application layer
│  ├─ email_validator_tool/   # Pure-Py core library
│  ├─ alembic/                # Database migrations
│  └─ tests/                  # Backend tests
├─ frontend/                  # React SPA (Vite)
├─ infra/                     # Env templates & IaC snippets
├─ docs/                      # Architecture docs & ADRs
├─ docker-compose.yml         # Orchestrates full stack
├─ pyproject.toml             # Python package config
└─ Makefile                   # One-liners for dev & CI
```

---

## 2. Quick Start

```bash
# 0) prerequisites: Docker ≥24 & Make

# 1) clone + spin up everything
make dev            # → docker compose up --build

# 2) front-end only hot-reload (outside Docker)
cd frontend && pnpm install && pnpm dev

# 3) backend only (outside Docker)
pip install -e .[backend,dev]
uvicorn backend.app.main:app --reload

# 4) run unit tests
make test           # backend + core + frontend (Vitest)
```

Shortcuts (`Makefile`):

* `make dev` – full stack in watch mode.
* `make dev-backend` – backend only.
* `make dev-frontend` – frontend only.
* `make lint` – black + flake8 + ESLint.
* `make test` – run all tests.
* `make clean` – stop & prune containers/volumes.

---

## 3. Git Workflow

1. Create a **feature branch** from `main` (e.g. `feature/csv-upload`).
2. Keep commits atomic & **Conventional Commits** compliant (`feat:`, `fix:`, `chore:`…).
3. Open PR → squash-merge via GitHub UI (merges as one commit; PR title becomes commit msg).
4. CI must be green & code-owners review (2 👍 minimum).

Release branches follow `release/x.y.z`; tags are semver.

---

## 4. Testing & Coverage

| Target          | Framework  | Command                  | Threshold |
|-----------------|------------|--------------------------|-----------|
| Core + Backend  | **PyTest** + `pytest-cov` | `make test` | ≥ 95 % |
| Frontend        | **Vitest** + jsdom | `cd frontend && pnpm test` | ≥ 95 % |

Coverage reports are uploaded to Codecov; PRs with regression < threshold are blocked.

---

## 5. CI / CD Pipeline

GitHub Actions workflows live in `.github/workflows/`.

* **lint.yml** – black, flake8, isort, ESLint, prettier.
* **test.yml** – matrix (py3.12) + vitest.  Uploads coverage.
* **build.yml** – build & push multi-arch Docker images on tag; triggers Render.com deploy.

Branch protection rules require lint + test.

---

## 6. Environment Variables

| Variable | Default (dev) | Purpose |
|----------|---------------|---------|
| `ENVIRONMENT` | `dev` | Runtime env identifier |
| `DEBUG` | `true` | Verbose logging |
| `JWT_SECRET_KEY` | `dev-secret-key…` | Sign JWTs |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token TTL |
| `DATABASE_URL` | `sqlite:///./data/email_validator.db` | SQLAlchemy DSN |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` | Abuse control |
| `ENABLE_DNS_CACHE` | `true` | MX lookup cache |
| `ENABLE_SMTP` | `false` | SMTP validation |
| `ENABLE_CATCH_ALL` | `false` | Catch-all detection |
| `VITE_API_URL` | `http://localhost:8000` | SPA → API base |
| `VITE_API_KEY` | `test_admin_api_key` | Frontend auto-auth |

Full lists: `infra/env/*.example.env`.

---

## 7. Architecture Diagram

```mermaid
graph TD
  subgraph Browser
    FE[React SPA (frontend)]
    FE -->|REST JSON| Caddy
  end

  Caddy[[Caddy Reverse-Proxy]] -->|80/443| API

  subgraph Backend
    API[FastAPI app] --> Core
    API --> DB[(SQLite/PostgreSQL)]
    Core[Python core library\n(email_validator_tool)] -->|async validation| Validators
    Validators --> DNS[(DNS/MX)]
    Validators --> SMTP[(SMTP servers)]
  end

  Core -.->|PyPI| Devs
```

---

## 8. Key Components

### Backend Architecture
- **FastAPI**: Modern async web framework
- **SQLModel**: SQLAlchemy + Pydantic integration
- **JWT Authentication**: Token-based auth with API key fallback
- **Multi-tenancy**: Organizations and users with role-based access
- **Rate Limiting**: Per-IP/API key rate limiting with slowapi

### Core Library
- **Validation Pipeline**: Async pipeline with pluggable validators
- **DNS Caching**: Optional MX record caching
- **SMTP Validation**: Optional mailbox verification
- **CLI Interface**: Command-line tool for batch processing

### Frontend
- **React 19**: Latest React features
- **TypeScript**: Full type safety
- **JWT Management**: Automatic token refresh
- **Internationalization**: EN/ES support
- **CSV Processing**: Bulk email validation

---

Happy hacking!  Ping `@maintainers` on Slack #email-validator when in doubt. 