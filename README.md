# Email Validator Tool  
**Internal – Confidential – © <Your Company Name>**

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
1. **Syntax & domain checks** – RFC 5322 syntax, disposable/typo domains, role accounts.
2. **DNS / MX look-ups** – asynchronous MX resolution with optional per-domain caching.
3. **SMTP handshake** *(optional)* – verifies mailboxes and catch-all servers without sending emails.

Results are available via:
* **REST API** – `POST /validate` returns per-address verdicts (+verdict codes).  
* **CLI** – `email-validator validate emails.csv results.csv`.  
* **React SPA** – modern interface with CSV upload, status badges & dark mode.

---

## 2. Repository Layout
```text
repo/
├─ backend/                # FastAPI app, Alembic migrations, services
│  ├─ app/
│  └─ tests/
├─ email_validator_tool/   # Pure-Python core lib, CLI entry-points
├─ frontend/               # Vite + React 19 SPA (TypeScript, Tailwind CSS)
│  └─ src/test/            # Vitest + React-Testing-Library
├─ infra/
│  └─ env/                 # *.example.env templates for each tier
├─ loadtest/               # Locust load-testing scenarios
├─ docs/                   # ADRs, architecture diagrams, etc.
├─ docker-compose.yml      # Spins up API + Caddy reverse-proxy
└─ Makefile                # One-liners for common dev tasks
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
| DNS / MX | async aiodns cache | ✓ | ✓ | CLI flag `--enable-catch-all` |
| Catch-All Detection | RCPT-TO probing | ✓ | ✓ | CLI flag |
| SMTP Validation | 3-way handshake | ✓ | ✓ | CLI flag `--enable-smtp` |
| Abuse / Bounce Lists | internal SQLite store | ✓ | ✓ | Admin only |
| Rate Limiting | sliding-window per JWT | – | ✓ | via `slowapi` |

---

## 4. Technology Stack
* **Python 3.11+** – core library & FastAPI backend  
* **FastAPI 0.104+** – async REST endpoints  
* **React 19 + Vite 5** – frontend SPA  
* **SQLite / Postgres** – persistence (configurable via `DATABASE_URL`)  
* **Redis (optional)** – shared DNS cache, rate-limit store  
* **Docker & Caddy** – containerisation & TLS termination  
* **GitHub Actions** – CI (lint, test, build, deploy)  
* **Prometheus / Grafana** – metrics & dashboards (see `infra/observability/`)

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

### 5.2 Local Developer Setup
```bash
# Backend + CLI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -e backend/ -e .
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
| `API_KEY_USER` / `API_KEY_ADMIN` | *change me* | API-key → JWT exchange |
| `DATABASE_URL` | `sqlite:///./data/email_validator.db` | SQLAlchemy DSN |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` | Per-key sliding window |
| `ENABLE_DNS_CACHE` | `true` | Toggle MX cache |
| `VITE_API_URL` | `http://localhost:8000` | Frontend → API base URL |
| `VITE_API_KEY` | `test_admin_api_key` | Frontend auto-authentication |

> **Tip** – any variable prefixed with `VITE_` is exposed to the SPA at build-time.

---

## 7. Command-Line Interface (CLI)
Install core lib in editable mode (`pip install -e .`) then:
```bash
email-validator validate emails.csv results.csv \
  --enable-catch-all  --enable-smtp

email-validator manage-keys create admin   # create API key
email-validator cache-stats                # DNS cache insight
```
Run `email-validator --help` for the full tree.

---

## 8. REST API
Base URL defaults to `/` when served behind Caddy, or `/api` when served directly.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/token` | API-Key | Exchange API-Key → JWT |
| `POST` | `/validate` | Bearer | Validate one or many addresses |
| `GET` | `/health` | – | Liveness probe |
| `GET` | `/metrics` | allow-list | Prometheus metrics |
| `GET` | `/cache-stats` | Admin JWT | MX cache info |
| `POST` | `/admin/reload-spamtraps` | Admin JWT | Refresh spam-trap list |

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

---

## 12. Database Migrations
The backend ships Alembic migrations under `backend/alembic/versions/`.
```bash
alembic -c backend/alembic.ini revision --autogenerate -m "my_change"
alembic -c backend/alembic.ini upgrade head
```

---

## 13. Load Testing
Scripts reside in `loadtest/`. Quick run:
```bash
locust -f loadtest/locustfile.py --host http://localhost:8000
```
The script auto-generates a 10 k email CSV if not present and supports JWT authentication via `/token`.

---

## 14. Deployment
### Docker Image
```bash
# Build multi-arch
DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64,linux/arm64 -t registry.local/email-validator:latest .
```
### Render.com
A [Render Blueprint](render.yaml) is included; pushing to `main` auto-deploys staging.

---

## 15. Git & CI/CD Workflow
* **Branches** – `main` (protected), `release/x.y.z`, `feature/*`, `fix/*`.  
* **Commit messages** – Conventional Commits (`feat:`, `fix:`, `chore:` …).  
* **PRs** – squash-merged after 2 approvals, lint & tests green.  
* **GitHub Actions** – workflows in `.github/workflows/` run lint → test → build.

---

## 16. Code Style Guide
* **Python** – [PEP-8], Black (line-length 100), Ruff for lint, MyPy strict mode.  
* **TypeScript** – ESLint (Airbnb + React), Prettier.  
* **Commits** – run `make pre-commit install` to enable hooks.

---

## 17. Security & Compliance
* The repo is **private**; sharing source is prohibited.  
* Secrets **must not** be committed – use `.env.*` or your secret manager.  
* JWT secret keys must be rotated every 90 days (see SOP-SEC-008).  
* Only the `api` container exposes ports externally; Caddy terminates TLS and enforces HTTPS.

---

## 18. Troubleshooting FAQ
| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| `Import \"locust\" could not be resolved` | Locust not installed in interpreter | `pip install --user locust` |
| `UNIQUE constraint failed: organization.slug` | Org slug collision on test seed | Drop DB `rm data/email_validator.db` |
| 429 Too Many Requests | Rate-limit exceeded | Increase `RATE_LIMIT_REQUESTS_PER_MINUTE` or wait 60 s |

---

## 19. License
Distributed under the **MIT license** (see [LICENSE](LICENSE)). Internal company use only.

---

## 20. Contributors
| Name | Role |
|------|------|
| John Doe | Maintainer |
| Jane Smith | Frontend Lead |
| Dev Team | Contributors |

> _For access requests or questions ping **#email-validator** on Slack._ 