# Email Validator Tool - Startup & Testing Guide

This guide will walk you through setting up, starting, and testing the Email Validator Tool application step by step.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.12+** - [Download from python.org](https://www.python.org/downloads/)
- **Node.js 18+** - [Download from nodejs.org](https://nodejs.org/)
- **pnpm** - Install with `npm install -g pnpm`
- **Docker & Docker Compose** (optional, for containerized setup) - [Download from docker.com](https://www.docker.com/)

## Option 1: Docker Compose Setup (Recommended for Quick Start)

This is the fastest way to get the entire application running.

### Step 1: Clone and Navigate
```bash
# Navigate to your project directory
cd email-validator-tool
```

### Step 2: Start with Docker Compose
```bash
# Start all services (API + Frontend + Caddy reverse proxy)
make dev
```

Or manually:
```bash
docker compose up --build
```

### Step 3: Access the Application
- **Frontend**: http://localhost (or http://localhost:5173)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Option 2: Local Development Setup

This setup gives you more control and is better for development.

### Step 1: Backend Setup

#### 1.1 Create Python Virtual Environment
```bash
# Navigate to project root
cd email-validator-tool

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 1.2 Install Dependencies
```bash
# Install the package with backend and development dependencies
pip install -e .[backend,dev]
```

#### 1.3 Configure Environment
```bash
# Copy the development environment configuration
cp infra/env/dev.example.env .env

# Edit .env file if needed (optional)
# The default settings should work for most cases
```

#### 1.4 Set Up Database
```bash
# Run database migrations
alembic -c backend/alembic.ini upgrade head
```

#### 1.5 Start Backend Server
```bash
# Start the FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 2: Frontend Setup

#### 2.1 Install Frontend Dependencies
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
pnpm install
```

#### 2.2 Configure Frontend Environment
```bash
# Copy frontend environment configuration
cp ../infra/env/frontend.example.env .env
```

#### 2.3 Start Frontend Development Server
```bash
# Start the Vite development server
pnpm dev
```

The frontend will be available at:
- **Frontend**: http://localhost:5173

## Testing the Application

### 1. Test Backend API

#### 1.1 Health Check
```bash
curl http://localhost:8000/health
```
Expected response: `{"status": "healthy"}`

#### 1.2 API Documentation
Visit http://localhost:8000/docs to see the interactive API documentation.

#### 1.3 Test Email Validation
```bash
# Test single email validation
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "emails": ["test@example.com", "invalid-email", "user@gmail.com"]
  }'
```

### 2. Test Frontend

#### 2.1 Manual Testing
1. Open http://localhost:5173 in your browser
2. The app should auto-authenticate using the API key
3. Try uploading a CSV file with email addresses
4. Check that validation results are displayed correctly

#### 2.2 Frontend Tests
```bash
cd frontend
pnpm test
```

### 3. Test CLI Tool

#### 3.1 Basic Validation
```bash
# Create a test CSV file
echo "email" > test_emails.csv
echo "test@example.com" >> test_emails.csv
echo "invalid-email" >> test_emails.csv
echo "user@gmail.com" >> test_emails.csv

# Run validation
email-validator validate test_emails.csv results.csv
```

#### 3.2 Advanced Validation with Catch-All Detection
```bash
email-validator validate test_emails.csv results.csv --enable-catch-all
```

#### 3.3 Full Validation with SMTP
```bash
email-validator validate test_emails.csv results.csv --enable-catch-all --enable-smtp
```

### 4. Run Backend Tests
```bash
# From project root
pytest
```

Or run specific test categories:
```bash
# Test API endpoints
pytest backend/tests/test_api_validation.py

# Test validators
pytest tests/test_syntax.py
pytest tests/test_dns_mx.py
```

## Using Make Commands (Shortcuts)

The project includes a Makefile with helpful shortcuts:

```bash
# Development
make dev-frontend          # Start frontend only
make dev-backend           # Start backend only
make dev                   # Start both (Linux/Mac)

# Testing
make test                  # Run all tests
make lint                  # Run linting checks
make format                # Format code

# Validation shortcuts
make v ARGS='input.csv output.csv'          # Basic validation
make vca ARGS='input.csv output.csv'        # With catch-all detection
make vsmtp ARGS='input.csv output.csv'      # With SMTP verification
make vfull ARGS='input.csv output.csv'      # Full validation

# Cache management
make cache-stats           # View DNS cache statistics
make clear-cache           # Clear DNS cache
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
If you get "port already in use" errors:
```bash
# Find processes using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill the process or use different ports
uvicorn app.main:app --reload --port 8001
```

#### 2. Database Issues
If you encounter database errors:
```bash
# Reset database
rm -f data/email_validator.db
alembic -c backend/alembic.ini upgrade head
```

#### 3. Frontend Build Issues
If frontend dependencies fail:
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

#### 4. Python Environment Issues
If you have Python dependency conflicts:
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[backend,dev]
```

### Getting Help

- Check the logs in the terminal where you started the services
- Visit the API documentation at http://localhost:8000/docs
- Review the main README.md for more detailed information
- Check the test files for usage examples

## Next Steps

Once the application is running successfully:

1. **Explore the API**: Visit http://localhost:8000/docs to see all available endpoints
2. **Test with real data**: Upload CSV files with email addresses to test validation
3. **Configure settings**: Modify the `.env` files to adjust validation behavior
4. **Run load tests**: Use the loadtest directory for performance testing
5. **Contribute**: Check CONTRIBUTING.md for development guidelines

## Production Deployment

For production deployment:
1. Use the production environment files in `infra/env/`
2. Set up proper JWT secrets and API keys
3. Configure a production database (PostgreSQL recommended)
4. Set up monitoring and logging
5. Use Docker Compose or container orchestration

The application is now ready for development and testing! 🚀 