# PostgreSQL Deployment Guide

This guide explains how to deploy the Email Validator Tool with PostgreSQL on Render.

## Overview

The application has been updated to support both SQLite (for local development) and PostgreSQL (for production deployment). PostgreSQL is required for deployment on Render as it doesn't support persistent file storage for SQLite databases.

## Changes Made

### 1. Dependencies
- Added `psycopg2-binary>=2.9.0` to requirements.txt and pyproject.toml
- Added `libpq-dev` to Dockerfile for PostgreSQL client libraries

### 2. Database Configuration
- Updated `backend/app/database/database.py` to handle both SQLite and PostgreSQL
- Added PostgreSQL-specific connection pooling and configuration
- Added automatic URL format conversion for Render's PostgreSQL URLs

### 3. Render Configuration
- Updated `render.yaml` to use PostgreSQL database service
- Configured database connection using Render's `fromDatabase` property
- Added PostgreSQL database service definition

### 4. Alembic Configuration
- Updated Alembic to handle PostgreSQL connections
- Added proper error handling for database connections
- Improved debugging output for deployment issues

## Deployment Steps

### 1. Create PostgreSQL Database on Render
1. Go to your Render dashboard
2. Create a new PostgreSQL database service
3. Note the connection details provided by Render

### 2. Update Environment Variables
The `render.yaml` file is already configured to use the PostgreSQL database. The key configuration is:

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: email-validator-tool-postgresql
      property: connectionString
```

### 3. Deploy the Application
1. Push your changes to your Git repository
2. Render will automatically detect the changes and start a new deployment
3. The deployment will:
   - Install PostgreSQL dependencies
   - Run Alembic migrations to create database tables
   - Start the FastAPI application

## Database Migration

The application uses Alembic for database migrations. The migration process will:

1. Create the `organization` table
2. Create the `user` table with foreign key to organization
3. Set up proper indexes and constraints

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure the PostgreSQL database is running and accessible
2. **Migration Failures**: Check that the database user has proper permissions
3. **Import Errors**: Verify that `psycopg2-binary` is installed correctly

### Debug Information

The application includes debug output for:
- Database URL format conversion
- Connection pool configuration
- Migration status and errors

### Local Development

For local development, you can still use SQLite by setting:
```
DATABASE_URL=sqlite:///./app.db
```

## Database Schema

The application creates the following tables:

- `organization`: Multi-tenant organizations
- `user`: User accounts with organization relationships

## Security Notes

- Database credentials are automatically managed by Render
- Connection strings are encrypted and secure
- Database connections use connection pooling for efficiency

## Performance Considerations

- PostgreSQL connection pooling is configured for production use
- Connections are recycled every 5 minutes
- Pool pre-ping is enabled to verify connections before use 