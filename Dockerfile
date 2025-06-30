# Multi-stage build for Railway deployment
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
COPY frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install
COPY frontend/ ./
RUN pnpm build

# Python backend stage
FROM python:3.12-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
COPY backend/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir -e .[backend]

# Copy backend application code
COPY backend/app ./app
COPY backend/email_validator_tool ./email_validator_tool

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/dist ./static

# Copy docker-compose and other configs
COPY docker-compose.yml ./
COPY infra/observability/ ./

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 