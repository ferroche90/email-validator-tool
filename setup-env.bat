@echo off

REM Email Validator Tool - Environment Setup Script for Windows
REM This script helps set up the environment for development

echo 🚀 Setting up Email Validator Tool environment...

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)

REM Create backend environment file
echo 📝 Creating backend environment file...
if not exist ".env.dev" (
    copy "infra\env\dev.example.env" ".env.dev"
    echo ✅ Created .env.dev from template
) else (
    echo ℹ️  .env.dev already exists, skipping...
)

REM Create frontend environment file
echo 📝 Creating frontend environment file...
if not exist "frontend\.env" (
    copy "infra\env\frontend.example.env" "frontend\.env"
    echo ✅ Created frontend\.env from template
) else (
    echo ℹ️  frontend\.env already exists, skipping...
)

REM Create data directory
echo 📁 Creating data directory...
if not exist "data" mkdir data
echo. > data\.gitkeep
echo ✅ Created data directory

echo.
echo 🎉 Environment setup complete!
echo.
echo 📋 Next steps:
echo 1. Review and update API keys in .env.dev
echo 2. Review and update API key in frontend\.env
echo 3. Make sure VITE_API_KEY in frontend\.env matches a valid API key in your backend
echo 4. Run 'make install' to install dependencies
echo 5. Run 'make dev' to start development servers
echo.
echo 🔐 Authentication:
echo - The application now uses JWT authentication
echo - API keys are used to generate JWT tokens
echo - Frontend automatically handles token management
echo.
echo 📚 For more information, see README.md

pause 