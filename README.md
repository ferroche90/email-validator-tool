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

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   pnpm install
   cd ..
   ```

4. **Start development servers**
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

### Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
API_TOKEN=your_secure_api_token_here
ADMIN_TOKEN=your_secure_admin_token_here

# Database
DATABASE_URL=sqlite:///app.db

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# DNS Cache
ENABLE_DNS_CACHE=True
DNS_CACHE_TTL_SECONDS=3600

# SMTP Configuration
SMTP_TIMEOUT=10
MAX_CONCURRENT_CONNECTIONS=10
PER_DOMAIN_DELAY_SECONDS=5.0

# Validation Options
ENABLE_CATCH_ALL=False
ENABLE_SMTP=False
```

### Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_api_token_here
```

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
   - Render will automatically detect the `render.yaml` configuration

3. **Automatic Configuration**:
   - API tokens are auto-generated
   - HTTPS is automatically configured
   - Database is automatically provisioned
   - Rate limiting is configured for free tier

4. **Access your deployment**:
   - **Web Application**: `https://your-app.onrender.com`
   - **API Endpoints**: `https://your-app.onrender.com/api`
   - **Health Check**: `https://your-app.onrender.com/health`

### Render Free Tier Features
- ✅ **No cost** - Completely free deployment
- ✅ **HTTPS included** - Automatic SSL certificates
- ✅ **Custom domains** - Can add your own domain
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **Logs & monitoring** - Built-in observability

## 📊 API Usage

### Authentication
All API endpoints require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST "https://your-app.onrender.com/api/validate" \
     -d '{"emails": ["test@example.com"], "enable_smtp": false}'
```

### Endpoints

#### Validate Emails
```http
POST /api/validate
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN

{
  "emails": ["test@example.com", "invalid@email"],
  "enable_smtp": false,
  "enable_catch_all": false
}
```

#### Cache Statistics (Admin)
```http
GET /api/cache-stats
Authorization: Bearer YOUR_ADMIN_TOKEN
```

#### Clear Cache (Admin)
```http
POST /api/cache-clear
Authorization: Bearer YOUR_ADMIN_TOKEN
```

#### Bounce Statistics (Admin)
```http
GET /api/bounce-stats
Authorization: Bearer YOUR_ADMIN_TOKEN
```

### Rate Limiting
- **Validation endpoint**: 20 requests per minute per IP
- **Admin endpoints**: 5 requests per minute per IP
- **Health check**: No limits

## 🛠️ Management Commands

### DNS Cache Management

```bash
# View cache statistics
python -m email_validator_tool.cli cache-stats
make cache-stats

# Clear all DNS cache
python -m email_validator_tool.cli clear-cache
make clear-cache

# Clean up expired cache entries
python -m email_validator_tool.cli cleanup-cache
make cleanup-cache
```

### Bounce List Management

```bash
# Reload bounce list from database
python -m email_validator_tool.cli reload-bounce-list
make reload-bounce

# View bounce list statistics
python -m email_validator_tool.cli bounce-stats
make bounce-stats
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_syntax.py

# Run with coverage
pytest --cov=email_validator_tool
```

### Frontend Tests
```bash
cd frontend
pnpm test
pnpm test:ui
```

### Development Tools
```bash
# Code formatting
make format

# Linting
make lint

# Run all tests
make test
```

## 📈 Performance Optimization

### DNS Caching
The tool includes intelligent DNS caching to improve performance:

- **Cache TTL**: Configurable time-to-live (default: 1 hour)
- **Automatic cleanup**: Expired entries are removed automatically
- **Domain-based**: Different emails from the same domain share cache
- **Error caching**: Failed DNS queries are also cached to avoid repeated failures

### Batch Processing
- **Incremental CSV writing**: Results are written as they're processed
- **Memory efficient**: Large lists are processed without loading everything into memory
- **Progress tracking**: Real-time progress updates for long-running validations

### Rate Limiting
- **Per-domain delays**: Configurable delays between requests to the same domain
- **Concurrent connections**: Limited concurrent SMTP connections
- **Timeout configuration**: Configurable timeouts for network operations

## ⚠️ Risk Management

### SMTP and Catch-all Verification
These features are considered high-risk and should be used with caution:

- **IP Blocking**: May result in IP blocking by mail servers
- **Rate Limiting**: Servers may implement rate limiting
- **Legal Considerations**: Ensure compliance with applicable laws

### Recommendations
- Use delays between verifications (`PER_DOMAIN_DELAY_SECONDS`)
- Limit concurrent connections (`MAX_CONCURRENT_CONNECTIONS`)
- Configure appropriate timeouts (`SMTP_TIMEOUT`)
- Consider using a dedicated VPS for high-volume validation
- Implement IP rotation if necessary

## 📋 Validation Results

### Status Types
- **`valid`**: Email passed all validation layers
- **`invalid_syntax`**: Email format is invalid
- **`invalid_domain`**: Domain does not exist
- **`invalid_mx`**: Domain has no valid MX records
- **`disposable`**: Email uses a disposable domain
- **`role_account`**: Email is a generic role account
- **`on_bounce_list`**: Email is in the bounce list
- **`catch_all`**: Domain accepts any email (when enabled)
- **`invalid_smtp`**: SMTP verification failed (when enabled)
- **`unknown_error`**: Unexpected error occurred

### Output Format
Results are provided in CSV format with columns:
- **Email**: The validated email address
- **Status**: Validation result status
- **Details**: Additional information or error details

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Make your changes** and add tests
4. **Run the test suite**: `make test`
5. **Format your code**: `make format`
6. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
7. **Push to the branch**: `git push origin feature/AmazingFeature`
8. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Privacy and Legal Compliance

This tool is designed for legitimate email validation purposes. Users are responsible for:

- Ensuring they have permission to validate email addresses
- Complying with applicable anti-spam laws (CAN-SPAM, GDPR, etc.)
- Respecting rate limits and server policies
- Using the tool responsibly and ethically

For detailed privacy and legal information, see [POLICY.md](POLICY.md).

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/ferroche90/email-validator-tool.git/issues)
- **Documentation**: Check the [API documentation](http://localhost:8000/docs) when running locally
- **Email**: fernando@webatix.com

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- Icons from [Heroicons](https://heroicons.com/)
- Styling with [Tailwind CSS](https://tailwindcss.com/)
- Deployment optimized for [Render](https://render.com/)

---

**⭐ Star this repository if you find it useful!**
