@echo off
echo 🚀 Starting Email Validator with Monitoring Stack...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Build and start all services
echo 📦 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

echo.
echo ✅ Monitoring stack is ready!
echo.
echo 📊 Access your monitoring tools:
echo    • Grafana Dashboard: http://localhost:3000
echo      Username: admin
echo      Password: admin
echo.
echo    • Prometheus: http://localhost:9090
echo.
echo    • Email Validator API: http://localhost:8000
echo.
echo 🔧 To stop the stack: docker-compose down
echo 🔧 To view logs: docker-compose logs -f
pause 