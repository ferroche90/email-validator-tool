# Email-Validator-Tool – Internal Developer README

> Confidential – for core contributors only

---

## 1. Vision & Repository Map

**Vision** – Provide a production-grade, cloud-agnostic service that validates e-mail lists fast, accurately and at scale.  The mono-repo ships:

*  💻 **Backend** (`backend/`) – FastAPI micro-service exposed via `/api/*` plus Celery workers and adapters.
*  🌐 **Frontend** (`frontend/`) – Vite + React 19 + Tailwind CSS single-page app.
*  🧠 **Core lib** (`email_validator_tool/`) – Validator pipeline & pluggable rule engine, 100 % Python only.  Also published to PyPI.
*  🐳 **Infra** (`docker-compose.yml`, `infra/`) – Dev/prod compose files, Caddy reverse-proxy, Postgres/Redis, etc.
*  🧪 **Tests** (`tests/`, `backend/tests/`, `frontend/src/test/`) – Unified PyTest + Vitest suites.

```
repo/
├─ backend/            # FastAPI app + services
├─ email_validator_tool/  # Pure-Py core library
├─ frontend/           # React SPA (Vite)
├─ infra/              # Env templates & IaC snippets
├─ docs/ (empty – put public docs here)
├─ docker-compose.yml  # Orchestrates full stack
└─ Makefile            # One-liners for dev & CI
```

---

## 2. Quick Start

```bash
# 0) prerequisites: Docker ≥24 & Make

# 1) clone + spin up everything
make dev            # → docker compose -f docker-compose.yml up --build

# 2) front-end only hot-reload (outside Docker)
(cd frontend && pnpm install && pnpm dev)

# 3) run unit tests
make test           # backend + core + frontend (Vitest)
```

Shortcuts (`Makefile`):

* `make dev` – full stack in watch mode.
* `make api` – backend only.
* `make lint` – black + ruff + ESLint.
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
| Frontend        | **Vitest** + jsdom | `pnpm test`            | ≥ 95 % |

Coverage reports are uploaded to Codecov; PRs with regression < threshold are blocked.

---

## 5. CI / CD Pipeline

GitHub Actions workflows live in `.github/workflows/`.

* **lint.yml** – ruff, black, isort, ESLint, prettier.
* **test.yml** – matrix (py3.11, py3.12) + vitest.  Uploads coverage.
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
| `API_KEY_*` | *see env* | API-Key → JWT exchange |
| `DATABASE_URL` | `sqlite:///app.db` | SQLAlchemy DSN |
| `RATE_LIMIT_PER_MINUTE` | `100` | Abuse control |
| `ENABLE_DNS_CACHE` | `true` | MX lookup cache |
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
    API --> Redis[(Redis)]
    API --> DB[(PostgreSQL)]
    Core[Python core library\n(email_validator_tool)] -->|async tasks| Celery
    Celery --> SMTP[(SMTP servers)]
    Core --> DNS[(DNS/MX)]
  end

  Core -.->|PyPI| Devs
```

---

Happy hacking!  Ping `@maintainers` on Slack #email-validator when in doubt. 