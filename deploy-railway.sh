#!/bin/bash

echo "🚀 Deploying Email Validator to Railway with Full Monitoring..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    
    # Install Railway CLI
    echo "📥 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Deploy the project
echo "📦 Deploying to Railway..."
railway up

# Show deployment status
echo "📊 Deployment Status:"
railway status

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your services will be available at:"
echo "   • Main App: https://your-app.railway.app"
echo "   • Grafana: https://your-app.railway.app:3000"
echo "   • Prometheus: https://your-app.railway.app:9090"
echo ""
echo "🔧 To view logs: railway logs"
echo "🔧 To restart: railway service restart"
echo "🔧 To check status: railway status" 