# Email Validator Tool - Local Development Guide

This guide will walk you through setting up and running the Email Validator Tool locally for development.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.12+** - [Download from python.org](https://www.python.org/downloads/)
- **Node.js 18+** - [Download from nodejs.org](https://nodejs.org/)
- **pnpm** - Install with `npm install -g pnpm`

## Backend Setup

### Step 1: Create Python Virtual Environment
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

### Step 2: Install Dependencies
```bash
# Install the package with backend and development dependencies
pip install -e .[backend,dev]
```

### Step 3: Configure Environment
```bash
# Copy the development environment configuration
cp infra/env/dev.example.env .env

# Edit .env file if needed (optional)
# The default settings should work for most cases
```

### Step 4: Set Up Database

```bash
# 1. Change to the backend directory
cd backend

# 2. If this is your first time setting up, initialize Alembic (creates the alembic/ folder)
python -m alembic init alembic

# 3. (Optional) If you already have an alembic/ folder, you can skip the previous step.

# 4. Run database migrations
python -m alembic -c alembic.ini upgrade head

# 5. Return to the project root if needed
cd ..
```

**Notes:**
- If you see an error like `Path doesn't exist: alembic`, it means you need to run the `init` step above.
- Always use `python -m alembic ...` to ensure you're using the correct Python environment.
- If you already have the `alembic/` folder, you only need to run the migration command.

### Step 5: Create API Key for Development
```bash
# Create an admin API key for development
cd backend
python -m email_validator_tool.cli manage-keys create admin

# Save the generated API key - you'll need it for the frontend env configuration
# The output will show:
# ✅ API Key created successfully!
# Role: admin
# API Key: [YOUR_GENERATED_KEY]
# JWT Token: [YOUR_JWT_TOKEN]
```

### Step 6: Start Backend Server
```bash
# Start the FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Frontend Setup

### Step 1: Install Frontend Dependencies
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
pnpm install
```

### Step 2: Configure Frontend Environment
```bash
# Copy frontend environment configuration
cp ../infra/env/frontend.example.env .env

# Edit the .env file and update VITE_API_KEY with the API key from Step 5
# nano .env  # or use your preferred editor
# Update: VITE_API_KEY=YOUR_GENERATED_API_KEY_HERE
```

### Step 3: Start Frontend Development Server
```bash
# Start the Vite development server
pnpm dev
```

The frontend will be available at:
- **Frontend**: http://localhost:5173

## Testing the Application

### Backend API Tests

#### Health Check
```bash
curl http://localhost:8000/health
```
Expected response: `{"status": "healthy"}`

#### API Documentation
Visit http://localhost:8000/docs to see the interactive API documentation.

#### Test Email Validation
```bash
# Test single email validation
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "emails": ["test@example.com", "invalid-email", "user@gmail.com"]
  }'
```

### Frontend Tests

#### Manual Testing
1. Open http://localhost:5173 in your browser
2. The app should auto-authenticate using the API key
3. Try uploading a CSV file with email addresses
4. Check that validation results are displayed correctly

#### Run Frontend Test Suite
```bash
cd frontend
pnpm test
```

### CLI Tool Tests

#### Basic Validation
```bash
# Create a test CSV file
echo "email" > test_emails.csv
echo "test@example.com" >> test_emails.csv
echo "invalid-email" >> test_emails.csv
echo "user@gmail.com" >> test_emails.csv

# Run validation
email-validator validate test_emails.csv results.csv
```

#### Advanced Validation with Catch-All Detection
```bash
email-validator validate test_emails.csv results.csv --enable-catch-all
```

#### Full Validation with SMTP
```bash
email-validator validate test_emails.csv results.csv --enable-catch-all --enable-smtp
```

### Run Backend Test Suite
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

## Development Shortcuts (Make Commands)

The project includes a Makefile with helpful shortcuts:

```bash
# Development
make dev-frontend          # Start frontend only
make dev-backend           # Start backend only

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

### Port Already in Use
If you get "port already in use" errors:
```bash
# Find processes using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill the process or use different ports
uvicorn app.main:app --reload --port 8001
```

### Database Issues
If you encounter database errors:
```bash
# Reset database
rm -f data/email_validator.db
alembic -c backend/alembic.ini upgrade head
```

### Frontend Build Issues
If frontend dependencies fail:
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Python Environment Issues
If you have Python dependency conflicts:
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[backend,dev]
```

## Environment Variables

### Backend Environment (.env)
Key environment variables for backend development:
- `DATABASE_URL`: SQLite database location (default: `sqlite:///./data/email_validator.db`)
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `JWT_ALGORITHM`: JWT algorithm (default: `HS256`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `ENVIRONMENT`: Set to `dev` for development mode
- `DEBUG`: Set to `true` for development

### Frontend Environment (frontend/.env)
Key environment variables for frontend development:
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `VITE_API_KEY`: API key for authentication (use the key generated in Step 5)

## API Key Management

### List All API Keys
```bash
python -m email_validator_tool.cli manage-keys list
```

### Create New API Key
```bash
# Create a user-level API key
python -m email_validator_tool.cli manage-keys create user

# Create an admin-level API key
python -m email_validator_tool.cli manage-keys create admin
```

### Revoke API Key
```bash
python -m email_validator_tool.cli manage-keys revoke YOUR_API_KEY
```

## Next Steps

Once the application is running:

1. **Explore the API**: Visit http://localhost:8000/docs to see all available endpoints
2. **Test with real data**: Upload CSV files with email addresses to test validation
3. **Configure settings**: Modify the `.env` files to adjust validation behavior
4. **Run load tests**: Use the loadtest directory for performance testing
5. **Review documentation**: Check README.md for detailed feature information

## Development Tips

- Use `--reload` flag with uvicorn for hot reloading during backend development
- Frontend has hot module replacement (HMR) enabled by default
- Run `make lint` before committing to ensure code quality
- Check test files for usage examples and expected behaviors
- Use the interactive API documentation for testing endpoints
- Remember to create an API key before starting development (Step 5)

Happy coding! 🚀