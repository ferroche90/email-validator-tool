# Email Validator Tool  
**Internal – © <Webatix>**

> A production-ready, cloud-agnostic service that validates e-mail lists fast, accurately and at scale. The mono-repo ships a FastAPI backend, a React + Vite SPA, and a pure-Python core library that can also be consumed stand-alone or via CLI.

---

## Table of Contents
1. [Overview](#1-overview)  
2. [Repository Layout](#2-repository-layout)  
3. [Feature Matrix](#3-feature-matrix)  
4. [Technology Stack](#4-technology-stack)  
5. [Quick Start](#5-quick-start)  
   5.1 [Docker Compose (all-in)](#51-docker-compose-all-in)  
   5.2 [Local Developer Setup](#52-local-developer-setup)  
6. [Environment Configuration](#6-environment-configuration)  
7. [Command-Line Interface (CLI)](#7-command-line-interface-cli)  
8. [REST API](#8-rest-api)  
9. [Frontend SPA](#9-frontend-spa)  
10. [Testing & Quality Gates](#10-testing--quality-gates)  
11. [Observability & Metrics](#11-observability--metrics)  
12. [Database Migrations](#12-database-migrations)  
13. [Load Testing](#13-load-testing)  
14. [Deployment](#14-deployment)  
15. [Git & CI/CD Workflow](#15-git--cicd-workflow)  
16. [Code Style Guide](#16-code-style-guide)  
17. [Security & Compliance](#17-security--compliance)  
18. [Troubleshooting FAQ](#18-troubleshooting-faq)  
19. [License](#19-license)  
20. [Contributors](#20-contributors)

---

## 1. Overview
The service performs **three progressive validation phases**:
1. **Syntax & domain checks** – RFC 5322 syntax, disposable/typo domains, role accounts, provider type detection.
2. **DNS / MX look-ups** – asynchronous MX resolution with optional per-domain caching and catch-all detection.
3. **SMTP handshake** *(optional)* – verifies mailboxes and catch-all servers without sending emails.

Results are available via:
* **REST API** – `POST /validate` returns per-address verdicts (+verdict codes).  
* **CLI** – `email-validator validate emails.csv results.csv`.  
* **React SPA** – modern interface with CSV upload, status badges & Material-UI components.

---

## 2. Repository Layout
```text
repo/
├─ backend/                # FastAPI app, Alembic migrations, services
│  ├─ app/                 # FastAPI application layer
│  │  ├─ api/             # REST API routes
│  │  ├─ auth/            # JWT authentication
│  │  ├─ database/        # SQLModel models and session
│  │  ├─ services/        # Business logic adapters
│  │  └─ main.py          # FastAPI app entry point
│  ├─ email_validator_tool/   # Pure-Python core lib, CLI entry-points
│  │  ├─ core/            # Validation pipeline and models
│  │  ├─ validators/      # Individual validation modules
│  │  ├─ utils/           # Shared utilities
│  │  └─ cli.py           # CLI entry point
│  ├─ alembic/            # Database migrations
│  ├─ tests/              # Backend tests
│  └─ Dockerfile          # Multi-stage Docker build
├─ frontend/               # Vite + React 19 SPA (TypeScript, Material-UI)
│  ├─ src/
│  │  ├─ components/      # React components
│  │  ├─ lib/             # API hooks and utilities
│  │  ├─ types/           # TypeScript definitions
│  │  └─ i18n/            # Internationalization
│  └─ test/               # Vitest + React-Testing-Library
├─ infra/
│  └─ env/                # *.example.env templates for each tier
├─ loadtest/               # Locust load-testing scenarios
├─ docker-compose.yml      # Spins up API + Caddy + Prometheus + Grafana
├─ pyproject.toml          # Python package configuration
├─ Makefile                # One-liners for common dev tasks
├─ STARTUP_GUIDE.md        # Detailed setup instructions
├─ RAILWAY_DEPLOYMENT.md   # Railway deployment guide
└─ MONITORING_SETUP.md     # Observability setup guide
```

---

## 3. Feature Matrix
| Layer | Check | Core Lib | API | CLI | Notes |
|-------|-------|---------|-----|-----|-------|
| Syntax | RFC 5322 parser | ✓ | ✓ | ✓ | leveraging `email-validator` lib |
| Typo Suggestions | `gmail.com` vs `gmai.com` | ✓ | ✓ | ✓ | Damerau-Levenshtein |
| Disposable Domains | blocklists refreshed daily | ✓ | ✓ | ✓ | 120 k+ domains |
| Role Accounts | `info@`, `sales@` | ✓ | ✓ | ✓ | Configurable list |
| Provider Type | B2B / Freemail heuristic | ✓ | ✓ | ✓ | MX patterns |
| DNS / MX | async aiodns cache | ✓ | ✓ | ✓ | CLI flag `--enable-catch-all` |
| Catch-All Detection | RCPT-TO probing | ✓ | ✓ | ✓ | CLI flag |
| SMTP Validation | 3-way handshake | ✓ | ✓ | ✓ | CLI flag `--enable-smtp` |
| Abuse / Bounce Lists | internal SQLite store | ✓ | ✓ | ✓ | Admin only |
| Rate Limiting | sliding-window per JWT | – | ✓ | – | via `slowapi` |
| Multi-tenancy | Organizations & Users | – | ✓ | – | SQLModel + JWT |
| User Authentication | Email/Password + JWT | – | ✓ | – | bcrypt + PyJWT |
| API Key Management | Encrypted storage | ✓ | ✓ | ✓ | CLI management |

---

## 4. Technology Stack
* **Python 3.8+** – core library & FastAPI backend  
* **FastAPI 0.104+** – async REST endpoints  
* **React 19 + Vite 6** – frontend SPA  
* **Material-UI 5** – React component library
* **SQLite / Postgres** – persistence (configurable via `DATABASE_URL`)  
* **SQLModel** – SQLAlchemy + Pydantic integration  
* **Docker & Caddy** – containerisation & TLS termination  
* **Prometheus & Grafana** – metrics & dashboards  
* **GitHub Actions** – CI (lint, test, build, deploy)  

---

## 5. Quick Start
### 5.1 Docker Compose (all-in)
```bash
# 0) prerequisites: Docker ≥ 24 & Make
make dev        # → docker compose up --build
```
Services:
* `api` – FastAPI (`localhost:8000`)  
* `caddy` – reverse-proxy with auto-reload (`localhost`)
* `prometheus` – metrics collection (`localhost:9090`)
* `grafana` – dashboards (`localhost:3000`)

### 5.2 Local Developer Setup
```bash
# Backend + CLI
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[backend,dev]
cp infra/env/dev.example.env .env
alembic -c backend/alembic.ini upgrade head
uvicorn backend.app.main:app --reload

# Frontend
cd frontend && pnpm install && cp ../infra/env/frontend.example.env .env && pnpm dev
```

---

## 6. Environment Configuration
Environment variables are centralised in [`infra/env/`](infra/env) templates.  
Copy the relevant file to project root (`.env`) or `frontend/.env` and adjust:

| Variable | Default (dev) | Description |
|----------|---------------|-------------|
| `ENVIRONMENT` | `dev` | Runtime identifier (`prod` disables debug, etc.) |
| `JWT_SECRET_KEY` | *change me* | 32-byte secret for signing JWTs |
| `DATABASE_URL` | `sqlite:///./data/email_validator.db` | SQLAlchemy DSN |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` | Per-key sliding window |
| `ENABLE_DNS_CACHE` | `true` | Toggle MX cache |
| `ENABLE_SMTP` | `false` | Enable SMTP validation |
| `ENABLE_CATCH_ALL` | `false` | Enable catch-all detection |
| `VITE_API_URL` | `http://localhost:8000` | Frontend → API base URL |
| `VITE_API_KEY` | `test_admin_api_key` | Frontend auto-authentication |
| `METRICS_ALLOWLIST` | `127.0.0.1,::1` | IPs allowed to access metrics |

> **Tip** – any variable prefixed with `VITE_` is exposed to the SPA at build-time.

---

## 7. Command-Line Interface (CLI)
Install the package with backend extras (`pip install -e .[backend]`) then:
```bash
email-validator validate emails.csv results.csv \
  --enable-catch-all  --enable-smtp

email-validator manage-keys create admin   # create API key
email-validator cache-stats                # DNS cache insight
email-validator clear-cache                # clear DNS cache
email-validator bounce-stats               # bounce list statistics
```
Run `email-validator --help` for the full tree.

---

## 8. REST API
Base URL defaults to `/` when served behind Caddy, or `/api` when served directly.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/signup` | – | Create user account with organization |
| `POST` | `/api/login` | – | User login (email/password) |
| `POST` | `/api/token` | API-Key | Exchange API-Key → JWT |
| `POST` | `/api/public-token` | – | Get anonymous access token |
| `POST` | `/api/validate` | Bearer | Validate one or many addresses |
| `GET` | `/health` | – | Liveness probe |
| `GET` | `/metrics` | allow-list | Prometheus metrics |
| `GET` | `/api/cache-stats` | Admin JWT | MX cache info |
| `POST` | `/api/cache-clear` | Admin JWT | Clear DNS cache |
| `GET` | `/api/bounce-stats` | Admin JWT | Bounce list info |

Swagger is available at `/docs` in non-prod environments.

---

## 9. Frontend SPA
```bash
cd frontend
pnpm install
pnpm dev            # http://localhost:5173
```
The app auto-authenticates using `VITE_API_KEY`, displays per-address verdicts and exports CSV. Internationalisation (i18n) currently supports **EN** and **ES**.

To build production assets:
```bash
pnpm build          # output → frontend/dist
```

---

## 10. Testing & Quality Gates
| Target | Framework | Command |
|--------|-----------|---------|
| Core + Backend | PyTest (+ asyncio) | `make test` |
| Frontend | Vitest + React-Testing-Library | `pnpm test` |
| Load | Locust | `locust -f loadtest/locustfile.py` |

Coverage ≥ 95 % is enforced by CI. `make lint` runs Black, Ruff and ESLint.

---

## 11. Observability & Metrics
* **Prometheus** endpoint at `/metrics` (disabled in prod unless `ENABLE_METRICS=true`).  
* Grafana dashboard JSON under `infra/observability/grafana-dashboard.json`.  
* Request latency, verdict counts, DNS cache hit/miss, and rate-limit rejects are tracked.
* Docker Compose includes Prometheus and Grafana services for local monitoring.

---

## 12. Database Migrations
```bash
# Create new migration
alembic -c backend/alembic.ini revision --autogenerate -m "description"

# Apply migrations
alembic -c backend/alembic.ini upgrade head

# Rollback
alembic -c backend/alembic.ini downgrade -1
```

---

## 13. Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f loadtest/locustfile.py --host=http://localhost:8000
```

---

## 14. Deployment

### 14.1 Railway Deployment
See [`RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md) for detailed instructions.

**Required Environment Variables for Railway:**
- `ENVIRONMENT=prod`
- `DEBUG=false`
- `JWT_SECRET_KEY=your-secure-jwt-secret`
- `DATABASE_URL=postgresql://...` (Railway will provide this if you add a PostgreSQL service)
- `VITE_API_URL=https://your-app-name.railway.app` (set this after deployment)

**Optional Environment Variables:**
- `RATE_LIMIT_REQUESTS_PER_MINUTE=100`
- `ENABLE_DNS_CACHE=true`
- `ENABLE_SMTP=false`
- `ENABLE_CATCH_ALL=false`
- `ENABLE_METRICS=true`

### 14.2 Docker Deployment
```bash
# Build and run with Docker Compose
docker compose up --build -d

# Or build individual containers
docker build -f backend/Dockerfile -t email-validator-api .
docker run -p 8000:8000 email-validator-api
```

### 14.3 Manual Deployment
```bash
# Backend
pip install -e .[backend]
cp infra/env/prod.example.env .env
# Edit .env with production values
alembic -c backend/alembic.ini upgrade head
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
cp ../infra/env/frontend.prod.example.env .env
# Edit .env with production values
pnpm build
# Serve dist/ directory with your web server
```

---

## 15. Git & CI/CD Workflow
1. **Feature branches** → `feature/description`
2. **Pull requests** → `main` branch
3. **CI checks**: lint, test, build
4. **Deploy**: auto-deploy on merge to `main`

---

## 16. Code Style Guide
* **Python**: Black (120 chars), isort, flake8
* **TypeScript**: ESLint, Prettier
* **Commits**: Conventional commits format
* **Documentation**: Inline docstrings + README updates

---

## 17. Security & Compliance
* **JWT tokens** with configurable expiration
* **Rate limiting** per IP/API key
* **CORS** configuration for production
* **Environment variables** for sensitive data
* **API key management** with encrypted storage
* **Password hashing** with bcrypt
* **Multi-tenancy** with organization isolation

---

## 18. Troubleshooting FAQ

### Q: "Module not found" errors
A: Ensure you've installed with extras: `pip install -e .[backend,dev]`

### Q: Frontend can't connect to API
A: Check `VITE_API_URL` in `frontend/.env` and CORS settings

### Q: Database migration errors
A: Run `alembic -c backend/alembic.ini upgrade head`

### Q: API key authentication fails
A: Create new API key with `email-validator manage-keys create admin`

### Q: Monitoring services not accessible
A: Check `METRICS_ALLOWLIST` environment variable and ensure your IP is included

---

## 19. License
Internal use only – © Webatix

---

## 20. Contributors
* Fernando @ Webatix 