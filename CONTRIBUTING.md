# Contributing to Email Validator Tool

Thank you for your interest in contributing! This document outlines the development workflow and standards.

## Prerequisites

### Required Tools
- **Docker** ≥ 24.0 (for full-stack development)
- **Node.js** ≥ 18.0 (for frontend development)
- **Python** ≥ 3.11 (for backend/core development)
- **Make** (for build automation)
- **Git** ≥ 2.30

### Optional Tools
- **pnpm** (recommended for frontend package management)
- **Poetry** (for Python dependency management)
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
cp infra/env/dev.example.env .env.dev
cp infra/env/frontend.example.env frontend/.env

# Edit .env.dev and frontend/.env with your local settings
```

### 3. Start Development Environment
```bash
# Full stack (recommended)
make dev

# Or individual services
make api      # Backend only
cd frontend && pnpm dev  # Frontend only
```

## Code Quality Standards

### Linting and Formatting

#### Backend (Python)
```bash
# Format code
make format-backend

# Lint code
make lint-backend

# Type checking
make type-check-backend
```

**Standards:**
- **Black** for code formatting
- **Ruff** for linting and import sorting
- **MyPy** for type checking
- **isort** for import organization

#### Frontend (TypeScript/React)
```bash
# Format and lint
make lint-frontend

# Type checking
make type-check-frontend
```

**Standards:**
- **ESLint** with TypeScript rules
- **Prettier** for code formatting
- **TypeScript** strict mode

### Testing

#### Backend Tests
```bash
# Run all backend tests
make test-backend

# Run with coverage
make test-backend-coverage

# Run specific test file
pytest tests/test_specific.py -v
```

#### Frontend Tests
```bash
# Run all frontend tests
make test-frontend

# Run with coverage
make test-frontend-coverage

# Run tests in watch mode
cd frontend && pnpm test:ui
```

**Coverage Requirements:**
- **Backend**: ≥ 95% coverage
- **Frontend**: ≥ 95% coverage
- Coverage reports are generated automatically in CI

### Pre-commit Checks
```bash
# Run all checks before committing
make pre-commit

# This runs:
# - Backend: black, ruff, mypy, pytest
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
   make pre-commit
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
1. **Automated Checks**: Ensure all CI checks pass
2. **Code Review**: At least 2 maintainers must approve
3. **Testing**: Verify tests pass locally
4. **Documentation**: Check if documentation needs updates

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps
1. Create release branch: `release/x.y.z`
2. Update version numbers in:
   - `pyproject.toml`
   - `frontend/package.json`
   - `CHANGELOG.md`
3. Create PR and get approval
4. Merge to main
5. Create Git tag: `vx.y.z`
6. CI automatically builds and deploys

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Slack**: Join our Slack channel for real-time discussions
- **Documentation**: Check the docs folder for detailed guides

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We are committed to providing a welcoming and inclusive environment for all contributors.

---

Thank you for contributing to Email Validator Tool! 🚀 