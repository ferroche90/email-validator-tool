# Render.com Deployment Guide

This guide will help you deploy the Email Validator Tool on Render's free tier.

## Prerequisites

1. A GitHub account with this repository
2. A Render.com account (free tier)

## Deployment Steps

### 1. Fork/Clone the Repository

Make sure you have this repository in your GitHub account. You can either:
- Fork this repository to your GitHub account
- Or push your local copy to a new GitHub repository

### 2. Deploy on Render

1. **Sign up/Login to Render.com**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this project

3. **Configure the Service**
   - **Name**: `email-validator-api` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: `Free`

4. **Environment Variables**
   The following environment variables will be automatically set by `render.yaml`:
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `DATABASE_URL=sqlite:///./data/email_validator.db`
   - `JWT_SECRET_KEY` (auto-generated)
   - And many others...

   **Optional**: You can add custom environment variables in the Render dashboard if needed.

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - The first deployment may take 5-10 minutes

## Post-Deployment

### 1. Access Your Application

Once deployed, Render will provide you with a URL like:
```
https://your-app-name.onrender.com
```

### 2. Test the Application

- **Frontend**: Visit the URL directly to access the React SPA
- **API**: Access the API at `/api` endpoints
- **Health Check**: Visit `/health` to verify the service is running
- **Documentation**: Visit `/docs` for API documentation

### 3. Create Admin API Key

After deployment, you'll need to create an admin API key. You can do this by:

1. **Using the CLI locally** (if you have the project set up locally):
   ```bash
   email-validator manage-keys create admin
   ```

2. **Or manually create one** by accessing the deployed application and using the signup endpoint.

## Free Tier Limitations

Render's free tier has the following limitations:
- **Sleep after 15 minutes** of inactivity
- **512 MB RAM** limit
- **Shared CPU** resources
- **No persistent storage** (SQLite database will be reset on redeploy)

### Workarounds for Free Tier Limitations

1. **Database Persistence**: For production use, consider upgrading to a paid plan with PostgreSQL
2. **Keep Alive**: Use external services like UptimeRobot to ping your app every 10 minutes
3. **Memory Optimization**: The current configuration is optimized for the 512MB limit

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are properly specified in `pyproject.toml`

2. **Application Won't Start**
   - Check the logs in Render dashboard
   - Verify environment variables are set correctly
   - Ensure the port is correctly configured (Render sets `$PORT`)

3. **Frontend Not Loading**
   - Verify the frontend build is successful
   - Check that static files are being served correctly

4. **Database Issues**
   - SQLite database is ephemeral on free tier
   - Consider using Render's PostgreSQL service for persistence

### Logs and Monitoring

- **Application Logs**: Available in the Render dashboard
- **Build Logs**: Check the build tab in Render dashboard
- **Health Check**: Monitor `/health` endpoint

## Upgrading to Paid Plan

For production use, consider upgrading to a paid plan for:
- **Persistent storage** (PostgreSQL)
- **No sleep mode**
- **More resources** (RAM, CPU)
- **Custom domains**
- **SSL certificates**

## Support

If you encounter issues:
1. Check the Render documentation
2. Review the application logs
3. Verify your configuration matches this guide
4. Consider the free tier limitations mentioned above 