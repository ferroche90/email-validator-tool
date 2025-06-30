@echo off
echo 🚀 Deploying Email Validator to Railway with Full Monitoring...

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Railway CLI not found. Installing...
    
    REM Install Railway CLI for Windows
    echo 📥 Installing Railway CLI for Windows...
    powershell -Command "iwr https://railway.app/install.ps1 -useb | iex"
)

REM Login to Railway
echo 🔐 Logging into Railway...
railway login

REM Deploy the project
echo 📦 Deploying to Railway...
railway up

REM Show deployment status
echo 📊 Deployment Status:
railway status

echo.
echo ✅ Deployment complete!
echo.
echo 🌐 Your services will be available at:
echo    • Main App: https://your-app.railway.app
echo    • Grafana: https://your-app.railway.app:3000
echo    • Prometheus: https://your-app.railway.app:9090
echo.
echo 🔧 To view logs: railway logs
echo 🔧 To restart: railway service restart
echo 🔧 To check status: railway status
pause 