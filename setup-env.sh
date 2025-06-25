#!/bin/bash

# Email Validator Tool - Environment Setup Script
# This script helps set up the environment for development

set -e

echo "🚀 Setting up Email Validator Tool environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create backend environment file
echo "📝 Creating backend environment file..."
if [ ! -f ".env.dev" ]; then
    cp infra/env/dev.example.env .env.dev
    echo "✅ Created .env.dev from template"
else
    echo "ℹ️  .env.dev already exists, skipping..."
fi

# Create frontend environment file
echo "📝 Creating frontend environment file..."
if [ ! -f "frontend/.env" ]; then
    cp infra/env/frontend.example.env frontend/.env
    echo "✅ Created frontend/.env from template"
else
    echo "ℹ️  frontend/.env already exists, skipping..."
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
touch data/.gitkeep
echo "✅ Created data directory"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review and update API keys in .env.dev"
echo "2. Review and update API key in frontend/.env"
echo "3. Make sure VITE_API_KEY in frontend/.env matches a valid API key in your backend"
echo "4. Run 'make install' to install dependencies"
echo "5. Run 'make dev' to start development servers"
echo ""
echo "🔐 Authentication:"
echo "- The application now uses JWT authentication"
echo "- API keys are used to generate JWT tokens"
echo "- Frontend automatically handles token management"
echo ""
echo "📚 For more information, see README.md" 