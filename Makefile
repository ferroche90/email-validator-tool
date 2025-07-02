# Makefile for email-validator-tool

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON = python
    ACTIVATE = .venv\Scripts\activate
    SEP = &&
else
    PYTHON = python3
    ACTIVATE = . .venv/bin/activate
    SEP = ;
endif

.PHONY: help dev dev-frontend dev-backend setup setup-env setup-db create-key build test lint format install

help:
	@echo Email Validator Tool - Essential Commands
	@echo.
	@echo Setup:
	@echo   make setup-env                        - Set up environment files
	@echo   make setup-db                         - Initialize and run database migrations
	@echo   make create-key                       - Create admin API key for development
	@echo   make install                          - Install dependencies
	@echo.
	@echo Development:
	@echo   make dev-frontend                     - Start frontend development server
	@echo   make dev-backend                      - Start backend development server
	@echo   make build                            - Build Docker containers
	@echo.
	@echo Testing & Quality:
	@echo   make test                             - Run tests
	@echo   make lint                             - Run linting checks
	@echo   make format                           - Format code

# Setup commands
setup-env:
	@echo Setting up environment files...
	@if not exist ".env" copy "infra\env\dev.example.env" ".env"
	@if not exist "frontend\.env" copy "infra\env\frontend.example.env" "frontend\.env"
	@if not exist "data" mkdir data
	@echo ✅ Environment setup complete!

setup-db:
	@echo Setting up database...
	cd backend && $(PYTHON) -m alembic init alembic
	cd backend && $(PYTHON) -m alembic -c alembic.ini upgrade head
	@echo ✅ Database setup complete!

create-key:
	@echo Creating admin API key...
	cd backend && $(PYTHON) -m email_validator_tool.cli manage-keys create admin
	@echo ✅ API key created! Update frontend/.env with the generated key.

# Development setup
install:
	$(PYTHON) -m venv .venv
ifeq ($(OS),Windows_NT)
	.venv\Scripts\pip install -e .[backend,dev]
else
	$(ACTIVATE) && pip install -e .[backend,dev]
endif

# Development servers (matching STARTUP_GUIDE.md exactly)
dev-frontend:
	@echo Starting frontend development server...
	@echo Frontend: http://localhost:5173
	cd frontend && pnpm dev

dev-backend:
	@echo Starting backend development server...
	@echo Backend:  http://localhost:8000
	@echo API Docs: http://localhost:8000/docs
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build and test
build:
	@echo Building Docker containers...
	docker compose build

test:
	@echo Running backend tests...
	$(PYTHON) -m pytest -v backend/tests
	@echo Running frontend tests...
	cd frontend && pnpm test

# Code quality
lint:
	@echo Running linting checks...
	@echo "Backend linting..."
	@$(PYTHON) -m black --check backend
	@$(PYTHON) -m isort --check-only backend
	@$(PYTHON) -m flake8 backend --max-line-length=120
	@echo "Frontend linting..."
	@cd frontend && pnpm lint
	@echo All linting checks passed!

format:
	@echo Formatting code...
	@echo "Backend formatting..."
	@$(PYTHON) -m black backend
	@$(PYTHON) -m isort backend
	@echo "Frontend formatting..."
	@cd frontend && pnpm format
	@echo Code formatting complete!