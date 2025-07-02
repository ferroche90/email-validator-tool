#!/bin/bash
set -e

echo "Starting Email Validator Tool..."

# Change to backend directory
cd backend

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Warning: DATABASE_URL not set, using SQLite fallback"
else
    echo "Using database: ${DATABASE_URL}"
fi

# Run database migrations with retry logic
echo "Running database migrations..."
max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if alembic -c alembic.ini upgrade head; then
        echo "Database migrations completed successfully"
        break
    else
        retry_count=$((retry_count + 1))
        echo "Migration attempt $retry_count failed, retrying in 5 seconds..."
        sleep 5
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to run database migrations after $max_retries attempts"
    exit 1
fi

# Start the application
echo "Starting FastAPI application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 