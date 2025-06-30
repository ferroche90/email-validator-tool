#!/bin/bash

echo "🚀 Starting Email Validator with Monitoring Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start all services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ Monitoring stack is ready!"
echo ""
echo "📊 Access your monitoring tools:"
echo "   • Grafana Dashboard: http://localhost:3000"
echo "     Username: admin"
echo "     Password: admin"
echo ""
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "   • Email Validator API: http://localhost:8000"
echo ""
echo "🔧 To stop the stack: docker-compose down"
echo "🔧 To view logs: docker-compose logs -f" 