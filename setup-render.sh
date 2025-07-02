#!/bin/bash

# Setup script for Render deployment
echo "Setting up Email Validator Tool for Render deployment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p backend/frontend

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "Error: render.yaml not found. Please ensure it exists in the project root."
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found. Please ensure it exists in the project root."
    exit 1
fi

# Test the build locally (optional)
echo "Testing local build..."
if command -v docker &> /dev/null; then
    echo "Docker found. Testing build..."
    docker build -t email-validator-test .
    if [ $? -eq 0 ]; then
        echo "✅ Local build test successful!"
    else
        echo "⚠️  Local build test failed. This might still work on Render."
    fi
else
    echo "Docker not found. Skipping local build test."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Go to render.com and create a new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Set the Dockerfile path to: ./Dockerfile"
echo "5. Deploy!"
echo ""
echo "For detailed instructions, see RENDER_DEPLOYMENT.md" 