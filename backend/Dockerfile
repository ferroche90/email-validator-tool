# Multi-stage Dockerfile for Email Validator Tool
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY ../frontend/package*.json ./
COPY ../frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install
COPY ../frontend/ ./
RUN pnpm build

# Stage 2: Python backend with static files
FROM python:3.12-slim AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt ./requirements.txt
COPY backend/requirements.txt ./backend-requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend-requirements.txt

# Copy backend application code so that it is importable as top-level "app"
COPY backend/app ./app

# Copy shared library used by backend (main package)
COPY email_validator_tool ./email_validator_tool

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/dist ./static

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 