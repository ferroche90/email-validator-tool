#!/bin/bash

# Email Validator Tool - Environment Setup Script
# This script helps you set up your development environment quickly

echo "🚀 Setting up Email Validator Tool environment..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create backend environment file
if [ ! -f ".env.dev" ]; then
    echo "📝 Creating .env.dev for backend..."
    cp infra/env/dev.example.env .env.dev
    echo "✅ Backend environment file created: .env.dev"
else
    echo "ℹ️  Backend environment file already exists: .env.dev"
fi

# Create frontend environment file
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend/.env..."
    cp infra/env/frontend.example.env frontend/.env
    echo "✅ Frontend environment file created: frontend/.env"
else
    echo "ℹ️  Frontend environment file already exists: frontend/.env"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review and edit .env.dev if needed"
echo "2. Review and edit frontend/.env if needed"
echo "3. Make sure VITE_API_TOKEN in frontend/.env matches API_TOKEN in .env.dev"
echo "4. Run 'make dev' to start the development servers"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs" 