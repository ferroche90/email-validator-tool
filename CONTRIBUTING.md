# Contributing to Email Validator Tool

Thank you for your interest in contributing! This document outlines the development workflow and standards.

## Prerequisites

### Required Tools
- **Docker** ≥ 24.0 (for full-stack development)
- **Node.js** ≥ 18.0 (for frontend development)
- **Python** ≥ 3.12 (for backend/core development)
- **Make** (for build automation)
- **Git** ≥ 2.30

### Optional Tools
- **pnpm** (recommended for frontend package management)
- **VS Code** with extensions:
  - Python
  - TypeScript and JavaScript
  - Docker
  - ESLint
  - Prettier

## Development Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd email-validator-tool
```

### 2. Environment Configuration
```bash
# Copy environment templates
cp infra/env/dev.example.env .env
cp infra/env/frontend.example.env frontend/.env

# Edit .env and frontend/.env with your local settings
```

### 3. Install Dependencies
```bash
# Backend dependencies
pip install -e .[backend,dev]

# Frontend dependencies
cd frontend && pnpm install
```

### 4. Start Development Environment
```bash
# Full stack (recommended)
make dev

# Or individual services
make dev-backend      # Backend only
make dev-frontend     # Frontend only
```

## Code Quality Standards

### Linting and Formatting

#### Backend (Python)
```bash
# Format code
make format

# Lint code
make lint

# Sort imports
isort backend/ tests/
```

**Standards:**
- **Black** for code formatting (120 chars)
- **flake8** for linting
- **isort** for import organization

#### Frontend (TypeScript/React)
```bash
# Format and lint
cd frontend && pnpm lint

# Fix linting issues
cd frontend && pnpm lint:fix
```

**Standards:**
- **ESLint** with TypeScript rules
- **Prettier** for code formatting
- **TypeScript** strict mode

### Testing

#### Backend Tests
```bash
# Run all backend tests
make test

# Run with coverage
pytest --cov=backend --cov=email_validator_tool

# Run specific test file
pytest tests/test_specific.py -v
```

#### Frontend Tests
```bash
# Run all frontend tests
cd frontend && pnpm test

# Run with coverage
cd frontend && pnpm test:coverage

# Run tests in watch mode
cd frontend && pnpm test:watch
```

**Coverage Requirements:**
- **Backend**: ≥ 95% coverage
- **Frontend**: ≥ 95% coverage
- Coverage reports are generated automatically in CI

### Pre-commit Checks
```bash
# Run all checks before committing
make lint && make test

# This runs:
# - Backend: black, flake8, pytest
# - Frontend: eslint, prettier, vitest
```

## Git Workflow

### Branch Naming
- **Feature branches**: `feature/descriptive-name`
- **Bug fixes**: `fix/issue-description`
- **Hotfixes**: `hotfix/critical-fix`
- **Releases**: `release/x.y.z`

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add CSV upload functionality
fix(api): resolve JWT token expiration issue
docs: update API documentation
test: add unit tests for email validation
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following the standards above
   - Add tests for new functionality
   - Update documentation if needed

3. **Pre-commit Checks**
   ```bash
   make lint && make test
   ```

4. **Push and Create PR**
   ```bash
   git add .
   git commit -m "feat: your descriptive message"
   git push origin feature/your-feature-name
   ```

5. **PR Requirements**
   - ✅ All CI checks pass
   - ✅ Code review from maintainers
   - ✅ Tests pass with ≥95% coverage
   - ✅ Documentation updated if needed

6. **Merge**
   - Use "Squash and merge" option
   - PR title becomes the final commit message

## Code Review Guidelines

### What to Look For
- **Functionality**: Does the code work as intended?
- **Security**: Are there any security vulnerabilities?
- **Performance**: Is the code efficient?
- **Maintainability**: Is the code readable and well-structured?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code properly documented?

### Review Process
1. **Initial Review**: Check for obvious issues
2. **Detailed Review**: Examine logic and implementation
3. **Testing**: Verify tests are comprehensive
4. **Documentation**: Ensure docs are updated
5. **Approval**: Approve or request changes

## Project Structure

### Backend
```
backend/
├── app/                    # FastAPI application
│   ├── api/               # API routes
│   ├── auth/              # Authentication
│   ├── database/          # Database models
│   └── services/          # Business logic
├── email_validator_tool/  # Core validation library
│   ├── core/              # Validation pipeline
│   ├── validators/        # Validation modules
│   └── cli.py             # CLI entry point
└── tests/                 # Test files
```

### Frontend
```
frontend/
├── src/
│   ├── components/        # React components
│   ├── lib/              # Utilities and hooks
│   ├── types/            # TypeScript definitions
│   └── i18n/             # Internationalization
└── test/                 # Test files
```

## Common Issues and Solutions

### Backend Issues
- **Import errors**: Ensure you're using `pip install -e .[backend,dev]`
- **Database errors**: Run `alembic -c backend/alembic.ini upgrade head`
- **JWT errors**: Check `JWT_SECRET_KEY` in `.env`

### Frontend Issues
- **API connection**: Verify `VITE_API_URL` in `frontend/.env`
- **Authentication**: Check `VITE_API_KEY` matches backend
- **Build errors**: Run `pnpm install` to update dependencies

## Getting Help

- **Documentation**: Check README.md and inline docs
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Slack**: Join #email-validator channel for real-time help

Thank you for contributing to Email Validator Tool! 🚀 