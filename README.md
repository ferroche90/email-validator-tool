# Email Validator Tool

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=flat-square&logo=github)](https://github.com/ferroche90/email-validator-tool.git)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-19.1+-blue?style=flat-square&logo=react)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)

A comprehensive, production-ready email validation tool with multiple verification layers, featuring both a command-line interface and a modern web application. This tool provides robust email validation through syntax checking, DNS/MX verification, disposable domain detection, role account identification, bounce list checking, and optional SMTP verification and catch-all detection.

## 🌟 Features

### Core Validation Layers
- **📧 Syntax Validation**: RFC-compliant email format verification
- **🌐 DNS/MX Verification**: Domain existence and mail server validation
- **🗑️ Disposable Domain Detection**: Identifies temporary email services
- **👤 Role Account Detection**: Flags generic accounts (admin, info, etc.)
- **📋 Bounce List Checking**: Validates against local bounce database
- **🎯 Catch-all Detection**: Identifies domains that accept any email (optional)
- **📬 SMTP Verification**: Direct mailbox existence verification (optional)

### Application Modes
- **🖥️ Command Line Interface**: Batch processing with CSV input/output
- **🌐 Web Application**: Modern React frontend with FastAPI backend
- **🔌 REST API**: Programmatic access with rate limiting and authentication
- **🐳 Docker Support**: Containerized deployment with Caddy reverse proxy

### Performance Features
- **⚡ Asynchronous Processing**: High-performance concurrent validation
- **💾 DNS Caching**: Intelligent caching to reduce network requests
- **📊 Incremental Processing**: Real-time CSV writing for large datasets
- **🔄 Rate Limiting**: Configurable limits to prevent server blocking

## 🏗️ Architecture

### Project Structure
```
email-validator-tool/
├── 📁 email_validator_tool/     # Core CLI package
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Configuration management
│   ├── core/                    # Core validation logic
│   ├── validators/              # Individual validators
│   └── logger.py                # Logging configuration
├── 📁 backend/                  # FastAPI web service
│   ├── app/                     # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container
├── 📁 frontend/                 # React web application
│   ├── src/                     # React source code
│   ├── package.json             # Node.js dependencies
│   └── vite.config.ts           # Build configuration
├── 📁 tests/                    # Test suite
├── docker-compose.yml           # Multi-container setup
├── render.yaml                  # Render deployment config
└── Makefile                     # Development shortcuts
```

### Technology Stack

#### Backend (Python)
- **FastAPI**: Modern, fast web framework for APIs
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management
- **SQLite**: Local database for bounce list storage
- **aiosmtplib**: Asynchronous SMTP operations
- **dnspython**: DNS resolution and MX record checking
- **email-validator**: RFC-compliant email validation
- **disposable-email-domains**: Disposable domain detection

#### Frontend (React/TypeScript)
- **React 19**: Modern UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Server state management
- **Axios**: HTTP client for API communication
- **Heroicons**: Beautiful icon library

#### Infrastructure
- **Docker**: Containerization
- **Caddy**: Reverse proxy with automatic HTTPS
- **Render**: Cloud deployment platform
- **SQLite**: Lightweight database

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 18+** (for frontend development)
- **Docker** (for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ferroche90/email-validator-tool.git
   cd email-validator
   ```

2. **Set up environment files (choose one option):**
   
   **Option A: Use the setup script (recommended)**
   ```bash
   # Linux/Mac
   chmod +x setup-env.sh && ./setup-env.sh
   
   # Windows
   setup-env.bat
   ```
   
   **Option B: Manual setup**
   ```bash
   # Backend environment
   cp infra/env/dev.example.env .env.dev
   
   # Frontend environment
   cp infra/env/frontend.example.env frontend/.env
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   # All dependencies are now consolidated in a single file
   # (no need to install backend/requirements.txt separately)
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   pnpm install
   cd ..
   ```

5. **Start development servers**
   ```bash
   # Start both frontend and backend
   make dev
   
   # Or start them separately
   make dev-frontend  # Frontend on http://localhost:5173
   make dev-backend   # Backend on http://localhost:8000
   ```

### Using the Command Line Tool

#### Basic Validation
```bash
# Validate emails from CSV file
python -m email_validator_tool.cli validate input.csv output.csv
```

#### Advanced Validation
```bash
# With catch-all detection
python -m email_validator_tool.cli validate input.csv output.csv --enable-catch-all

# With SMTP verification
python -m email_validator_tool.cli validate input.csv output.csv --enable-smtp

# With both advanced features
python -m email_validator_tool.cli validate input.csv output.csv --enable-catch-all --enable-smtp
```

#### Using Makefile Shortcuts
```bash
# Basic validation
make v ARGS='input.csv output.csv'

# With catch-all detection
make vca ARGS='input.csv output.csv'

# With SMTP verification
make vsmtp ARGS='input.csv output.csv'

# Full validation (both catch-all and SMTP)
make vfull ARGS='input.csv output.csv'
```

## 🌐 Web Application

### Features
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **⚡ Real-time Validation**: Instant feedback on email validation
- **📊 Results Export**: Download validation results as CSV
- **🔧 Advanced Options**: Toggle SMTP and catch-all detection
- **🎨 Modern UI**: Clean, intuitive interface with Tailwind CSS

### Access Points
- **Frontend**: `http://localhost:5173` (development)
- **Backend API**: `http://localhost:8000` (development)
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Health Check**: `http://localhost:8000/health`

## 🔧 Configuration

### Environment Configuration

The application supports separate development and production environments with automatic configuration loading.

#### Quick Setup

1. **Backend/CLI Environment:**
   ```bash
   # For Development
   cp infra/env/dev.example.env .env.dev
   
   # For Production
   cp infra/env/prod.example.env .env.prod
   # Edit .env.prod with your secure production values
   ```

2. **Frontend Environment:**
   ```bash
   # For Development
   cp infra/env/frontend.example.env frontend/.env
   
   # For Production
   cp infra/env/frontend.prod.example.env frontend/.env
   # Edit frontend/.env with your secure production values
   ```

3. **Switch Environment:**
   ```bash
   # Development (default)
   ENVIRONMENT=dev make dev
   
   # Production
   ENVIRONMENT=prod make dev
   ```

#### Environment Files Structure

**Backend/CLI (Root Directory):**
- **`infra/env/dev.example.env`** - Development template with dummy values
- **`infra/env/prod.example.env`** - Production template with placeholders
- **`.env.dev`** - Your local development configuration (not committed to git)
- **`.env.prod`** - Your production configuration (not committed to git)

**Frontend (frontend/ Directory):**
- **`infra/env/frontend.example.env`** - Development template with dummy values
- **`infra/env/frontend.prod.example.env`** - Production template with placeholders
- **`frontend/.env`** - Your frontend configuration (not committed to git)

#### Configuration Priority

**Backend/CLI:**
1. **OS Environment Variables** (highest priority)
2. **`.env.{ENVIRONMENT}`** file (e.g., `.env.dev` or `.env.prod`)
3. **`.env`** file (fallback)
4. **Default values** (lowest priority)

**Frontend:**
1. **OS Environment Variables** (highest priority)
2. **`frontend/.env`** file
3. **Default values** (lowest priority)

#### Production Safety

- **DEBUG mode is automatically disabled** in production
- **Running with `ENVIRONMENT=prod DEBUG=true` will abort** with a clear error
- **All sensitive values must be changed** from placeholder values
- **Frontend and backend tokens must match** for authentication to work

#### Available Settings

**Backend/CLI Settings:**
```env
# Environment
ENVIRONMENT=dev|prod
DEBUG=true|false

# API Configuration
API_TOKEN=your_secure_api_token_here
ADMIN_TOKEN=your_secure_admin_token_here

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# CORS
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# DNS Cache
ENABLE_DNS_CACHE=True|False
DNS_CACHE_TTL_SECONDS=3600

# SMTP Configuration
SMTP_TIMEOUT=10
SMTP_PORT=25
MAX_CONCURRENT_CONNECTIONS=10
PER_DOMAIN_DELAY_SECONDS=5.0

# Validation Options
ENABLE_CATCH_ALL=False
ENABLE_SMTP=False

# General parameters
CSV_INPUT_PATH=emails.csv
CSV_OUTPUT_PATH=results.csv
```

**Frontend Settings:**
```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_api_token_here
```

#### Important Notes

- **Token Matching**: The `VITE_API_TOKEN` in `frontend/.env` must match the `API_TOKEN` in your backend `.env.dev` or `.env.prod` file
- **VITE_ Prefix**: Only environment variables prefixed with `VITE_` are available to the frontend
- **File Locations**: Backend env files go in the root, frontend env files go in the `frontend/` directory

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Build and start all services**
   ```bash
   docker compose up -d --build
   ```

2. **Access the application**
   - **Frontend**: `http://localhost`
   - **Backend API**: `http://localhost/api`
   - **API Docs**: `http://localhost/docs`

### Docker Services

- **API Service**: FastAPI backend with email validation logic
- **Caddy Service**: Reverse proxy with automatic HTTPS
- **Volumes**: Persistent storage for SSL certificates and configuration

## ☁️ Cloud Deployment

### Render (Recommended)

This project is optimized for deployment on Render's free tier:

1. **Fork the repository** to your GitHub account
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration and deploy both the backend and frontend services.

3. **Access your deployment**
   - **Web Application**: `https://your-app.onrender.com`
   - **API Endpoints**: `https://your-app.onrender.com/api`
   - **Health Check**: `https://your-app.onrender.com/health`

## 🤝 Contributing

We welcome contributions! Feel free to open issues or submit pull requests. Please make sure to run the tests and linters before pushing your changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.