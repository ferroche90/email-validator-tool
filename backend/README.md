# Email Validator Backend

FastAPI backend for the Email Validator Tool with multi-tenant support.

## Features

- **Multi-tenant Architecture**: Organizations and users with role-based access
- **JWT Authentication**: Secure token-based authentication
- **Email Validation API**: Comprehensive email validation endpoints
- **Database Migrations**: Alembic for schema management
- **Rate Limiting**: Built-in rate limiting with slowapi
- **Comprehensive Testing**: Unit tests with SQLite memory database

## Quick Start

### Prerequisites

- Python 3.11+
- pip or poetry

### Installation

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Set up environment**:
   ```bash
   cp ../infra/env/dev.example.env .env
   # Edit .env with your configuration
   ```

3. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /api/signup` - Create new user account with organization
- `POST /api/token` - Get JWT token (legacy API key support)

### Email Validation

- `POST /api/validate` - Validate email addresses
- `GET /api/cache-stats` - Get DNS cache statistics (admin)
- `POST /api/cache-clear` - Clear DNS cache (admin)

### Admin Endpoints

- `GET /api/bounce-stats` - Get bounce list statistics
- `POST /api/admin/reload-spamtraps` - Reload spam trap list
- `POST /api/admin/suppressions` - Add emails to suppression list

## Database Models

### User
- Email, password (hashed with bcrypt)
- First name, last name
- Role (user, admin, super_admin)
- Organization relationship
- Active/verified status

### Organization
- Name and slug (unique identifier)
- Active status
- Timestamps

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./app.db` | Database connection string |
| `JWT_SECRET_KEY` | `dev-secret-key...` | JWT signing secret |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time |
| `DEBUG` | `false` | Enable debug mode |

## Architecture

The backend follows a clean architecture pattern:

```
app/
├── api/           # API routes and endpoints
├── auth/          # Authentication and authorization
├── database/      # Database models and connection
├── services/      # Business logic services
└── main.py        # FastAPI application entry point
```

## Testing

Tests use SQLite in-memory database for fast execution:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints with database
- **Fixtures**: Reusable test data and database sessions

## Deployment

The backend is designed to be deployed with Docker:

```bash
# Build image
docker build -t email-validator-backend .

# Run container
docker run -p 8000:8000 email-validator-backend
```

See the main project README for full deployment instructions. 