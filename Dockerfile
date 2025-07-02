# Optimized Dockerfile for Render and general deployment
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and pnpm for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm

# Copy project files
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY frontend ./frontend

# Install Python dependencies
RUN pip install --no-cache-dir -e .[backend]

# Build frontend
RUN cd frontend && pnpm install && pnpm build

# Create data directory
RUN mkdir -p data

# Copy frontend build to backend directory for static serving
RUN cp -r frontend/dist backend/frontend/dist

# Expose port (Render will set $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command with database migrations
CMD ["sh", "-c", "cd backend && alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"] 