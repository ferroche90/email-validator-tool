@echo off
REM Setup script for Render deployment
echo Setting up Email Validator Tool for Render deployment...

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "data" mkdir data
if not exist "backend\frontend" mkdir backend\frontend

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo Error: render.yaml not found. Please ensure it exists in the project root.
    exit /b 1
)

REM Check if Dockerfile exists
if not exist "Dockerfile" (
    echo Error: Dockerfile not found. Please ensure it exists in the project root.
    exit /b 1
)

REM Test the build locally (optional)
echo Testing local build...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker found. Testing build...
    docker build -t email-validator-test .
    if %errorlevel% equ 0 (
        echo ✅ Local build test successful!
    ) else (
        echo ⚠️  Local build test failed. This might still work on Render.
    )
) else (
    echo Docker not found. Skipping local build test.
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Push your code to GitHub
echo 2. Go to render.com and create a new Web Service
echo 3. Connect your GitHub repository
echo 4. Set the Dockerfile path to: ./Dockerfile
echo 5. Deploy!
echo.
echo For detailed instructions, see RENDER_DEPLOYMENT.md
pause 