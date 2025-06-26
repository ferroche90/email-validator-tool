# Makefile for email-validator-tool

.PHONY: help lint format test install setup-dev v vca vsmtp vfull cache-stats clear-cache cleanup-cache reload-bounce bounce-stats dev dev-frontend dev-backend build test lint-windows format-windows

help:
	@echo Email Validator Tool - Makefile Shortcuts
	@echo.
	@echo Development Commands:
	@echo   make dev                              - Start frontend + backend concurrently (Linux/Mac)
	@echo   make dev-frontend                     - Start frontend only
	@echo   make dev-backend                      - Start backend only
	@echo   make build                            - Build Docker containers
	@echo   make test                             - Run backend tests
	@echo.
	@echo Linting Commands:
	@echo   make lint                             - Run all linting checks (Linux/Mac)
	@echo   make lint-windows                     - Run all linting checks (Windows)
	@echo   make format                           - Format code (Linux/Mac)
	@echo   make format-windows                   - Format code (Windows)
	@echo.
	@echo Validation Commands:
	@echo   make v ARGS='input.csv output.csv'          - Basic validation
	@echo   make vca ARGS='input.csv output.csv'        - With catch-all detection
	@echo   make vsmtp ARGS='input.csv output.csv'      - With SMTP verification
	@echo   make vfull ARGS='input.csv output.csv'      - With both catch-all and SMTP
	@echo.
	@echo Cache Management:
	@echo   make cache-stats                            - View DNS cache statistics
	@echo   make clear-cache                            - Clear all DNS cache
	@echo   make cleanup-cache                          - Clean up expired cache entries
	@echo.
	@echo Bounce List Management:
	@echo   make reload-bounce                          - Reload bounce list from database
	@echo   make bounce-stats                           - View bounce list statistics
	@echo.
	@echo Development:
	@echo   make setup-dev                              - Install development dependencies
	@echo   make install                                - Install dependencies
	@echo.
	@echo Examples:
	@echo   make dev-frontend
	@echo   make dev-backend
	@echo   make lint-windows
	@echo   make format-windows
	@echo   make v ARGS='emails.csv results.csv'
	@echo   make vca ARGS='emails.csv results.csv'
	@echo   make cache-stats

# Development setup
setup-dev:
	@echo Installing development dependencies...
	@echo Note: If you encounter errors, try running manually:
	@echo   python -m pip install flake8 black isort pytest
	python -m pip install flake8 black isort pytest || echo "Installation failed. Try running the command manually."

# Linting commands for Linux/Mac
lint:
	@echo Running linting checks...
	@echo Running black...
	@python -m black --check tests backend
	@echo Running isort...
	@python -m isort --check-only tests backend
	@echo Running flake8...
	@python -m flake8 tests backend --max-line-length=120
	@echo All linting checks passed!

# Linting commands for Windows
lint-windows:
	@echo Running linting checks (Windows)...
	@echo Running black...
	@python -m black --check email_validator_tool tests backend
	@echo Running isort...
	@python -m isort --check-only email_validator_tool tests backend
	@echo Running flake8...
	@python -m flake8 email_validator_tool tests backend --max-line-length=120
	@echo All linting checks passed!

# Formatting commands for Linux/Mac
format:
	@echo Formatting code...
	@python -m isort email_validator_tool tests backend
	@python -m black email_validator_tool tests backend
	@echo Code formatting completed!

# Formatting commands for Windows
format-windows:
	@echo Formatting code (Windows)...
	@python -m isort email_validator_tool tests backend
	@python -m black email_validator_tool tests backend
	@echo Code formatting completed!

# Test commands
test:
	@echo Running tests...
	@python -c "import pytest" 2>/dev/null && pytest || echo "pytest not available. Run 'make setup-dev' first."

install:
	python -m venv venv
	. venv/bin/activate && pip install -e .[backend,dev]

# Development and deployment
dev:
	@echo Starting development servers...
	@echo Frontend: http://localhost:5173
	@echo Backend:  http://localhost:8000
	@echo.
	@echo Press Ctrl+C to stop both servers
	@pnpm --filter frontend dev & cd backend && uvicorn app.main:app --reload

# Separate frontend and backend commands for Windows compatibility
dev-frontend:
	@echo Starting frontend development server...
	@echo Frontend: http://localhost:5173
	@echo.
	@echo Press Ctrl+C to stop the server
	cd frontend && pnpm dev

dev-backend:
	@echo Starting backend development server...
	@echo Backend:  http://localhost:8000
	@echo API Docs: http://localhost:8000/docs
	@echo.
	@echo Press Ctrl+C to stop the server
	cd backend && python -c "import sys; sys.path.insert(0, '..'); import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)"

build:
	@echo Building Docker containers...
	docker compose build

# Main validation commands (shortcuts)
v:
	python -m email_validator_tool.cli validate $(ARGS)

vca:
	python -m email_validator_tool.cli validate $(ARGS) --enable-catch-all

vsmtp:
	python -m email_validator_tool.cli validate $(ARGS) --enable-smtp

vfull:
	python -m email_validator_tool.cli validate $(ARGS) --enable-catch-all --enable-smtp

# DNS Cache management shortcuts
cache-stats:
	python -m email_validator_tool.cli cache-stats

clear-cache:
	python -m email_validator_tool.cli clear-cache

cleanup-cache:
	python -m email_validator_tool.cli cleanup-cache

# Bounce list management shortcuts
reload-bounce:
	python -m email_validator_tool.cli reload-bounce-list

bounce-stats:
	python -m email_validator_tool.cli bounce-stats