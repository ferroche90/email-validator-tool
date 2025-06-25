@echo off

REM Email Validator Tool - Environment Setup Script (Windows)
REM This script helps you set up your development environment quickly

echo 🚀 Setting up Email Validator Tool environment...

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Create backend environment file
if not exist ".env.dev" (
    echo 📝 Creating .env.dev for backend...
    copy "infra\env\dev.example.env" ".env.dev" >nul
    echo ✅ Backend environment file created: .env.dev
) else (
    echo ℹ️  Backend environment file already exists: .env.dev
)

REM Create frontend environment file
if not exist "frontend\.env" (
    echo 📝 Creating frontend\.env...
    copy "infra\env\frontend.example.env" "frontend\.env" >nul
    echo ✅ Frontend environment file created: frontend\.env
) else (
    echo ℹ️  Frontend environment file already exists: frontend\.env
)

echo.
echo 🎉 Environment setup complete!
echo.
echo 📋 Next steps:
echo 1. Review and edit .env.dev if needed
echo 2. Review and edit frontend\.env if needed
echo 3. Make sure VITE_API_TOKEN in frontend\.env matches API_TOKEN in .env.dev
echo 4. Run 'make dev' to start the development servers
echo.
echo 🌐 Access points:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs

pause 