# Railway Deployment Guide

This guide will help you deploy the Email Validator Tool to Railway.

## Prerequisites

1. A GitHub account with this repository
2. A Railway account (sign up at [railway.app](https://railway.app))

## Step-by-Step Deployment

### 1. Connect Repository to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose the repository
5. Railway will automatically detect the `railway.json` configuration

### 2. Configure Environment Variables

1. In the Railway project dashboard, go to the "Variables" tab
2. Add the following required environment variables:

#### Required Variables:
```
ENVIRONMENT=prod
DEBUG=false
JWT_SECRET_KEY=the-super-secure-jwt-secret-key-here
```

#### Optional Variables (with recommended values):
```
RATE_LIMIT_REQUESTS_PER_MINUTE=100
ENABLE_DNS_CACHE=true
ENABLE_SMTP=false
ENABLE_CATCH_ALL=false
ENABLE_METRICS=true
METRICS_ALLOWLIST=127.0.0.1,::1
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### 3. Add PostgreSQL Database (Optional)

1. In the Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provide the `DATABASE_URL` environment variable
4. If you don't add PostgreSQL, the app will use SQLite by default

### 4. Deploy

1. Railway will automatically build and deploy the application
2. The build process will:
   - Install Python dependencies
   - Build the frontend with the correct API URL
   - Run database migrations
   - Start the FastAPI server

### 5. Configure Frontend API URL

After deployment:

1. Note the Railway app URL (e.g., `https://the-app-name.railway.app`)
2. Add this environment variable to the Railway project:
   ```
   VITE_API_URL=https://the-app-name.railway.app
   ```
3. Redeploy the application to rebuild the frontend with the correct API URL

### 6. Verify Deployment

1. Visit the Railway app URL
2. You should see the Email Validator Tool interface
3. Test the health endpoint: `https://the-app-name.railway.app/health`
4. Check the API documentation: `https://the-app-name.railway.app/docs`

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | Yes | `prod` | Runtime environment |
| `DEBUG` | Yes | `false` | Debug mode (must be false in prod) |
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT tokens |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `VITE_API_URL` | Yes* | - | Frontend API URL (*after deployment) |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | No | `100` | API rate limiting |
| `ENABLE_DNS_CACHE` | No | `true` | Enable DNS caching |
| `ENABLE_SMTP` | No | `false` | Enable SMTP validation |
| `ENABLE_CATCH_ALL` | No | `false` | Enable catch-all detection |
| `ENABLE_METRICS` | No | `true` | Enable Prometheus metrics |
| `METRICS_ALLOWLIST` | No | `127.0.0.1,::1` | IPs allowed to access metrics |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `CORS_ORIGINS` | No | `*` | CORS allowed origins |

## Troubleshooting

### Build Failures
- Check that all required environment variables are set
- Ensure `JWT_SECRET_KEY` is a secure random string
- Verify the repository structure matches the expected layout

### Runtime Errors
- Check Railway logs in the dashboard
- Verify database connectivity if using PostgreSQL
- Ensure `VITE_API_URL` is set correctly after deployment

### Frontend Issues
- Make sure `VITE_API_URL` is set to the Railway app URL
- Redeploy after setting `VITE_API_URL` to rebuild the frontend
- Check browser console for API connection errors

## Monitoring

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics` (if enabled)
- API documentation: `/docs`

## Scaling

Railway automatically scales the application based on traffic. We can also manually adjust resources in the Railway dashboard.

## Cost Optimization

- Use SQLite instead of PostgreSQL for small deployments
- Disable unused features like SMTP validation and catch-all detection
- Monitor usage in the Railway dashboard