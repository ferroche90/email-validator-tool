# 🚀 Render Deployment Guide

This guide explains how to deploy your Email Validator Tool to Render with both frontend and backend.

## 📋 **What Will Be Deployed**

1. **Backend API** - FastAPI service with email validation
2. **Frontend** - React SPA with email validation interface
3. **Database** - SQLite (included in backend container)

## 🔧 **Prerequisites**

1. **GitHub Repository** - Your code must be in a public GitHub repo
2. **Render Account** - Sign up at https://render.com
3. **API Keys** - You'll need to create API keys for authentication

## 🚀 **Deployment Steps**

### **Step 1: Prepare Your Repository**

1. **Update the repository URL** in `render.yaml`:
   ```yaml
   repo: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
   ```

2. **Create API Keys** for authentication:
   ```bash
   # You'll need to create these and update the render.yaml
   - key: VITE_API_KEY
     value: your-actual-api-key-here
   ```

### **Step 2: Deploy to Render**

#### **Option A: Using render.yaml (Recommended)**

1. **Connect your GitHub repo** to Render
2. **Create a new Blueprint** in Render
3. **Upload your `render.yaml`** file
4. **Render will automatically** create both services

#### **Option B: Manual Deployment**

1. **Deploy Backend First**:
   - Create new **Web Service**
   - Connect your GitHub repo
   - Set **Environment**: Docker
   - Set **Dockerfile Path**: `./backend/Dockerfile`
   - Add environment variables (see below)

2. **Deploy Frontend**:
   - Create new **Static Site**
   - Connect your GitHub repo
   - Set **Build Command**: `cd frontend && npm install && npm run build`
   - Set **Publish Directory**: `./frontend/dist`
   - Add environment variables (see below)

## 🔑 **Environment Variables**

### **Backend Environment Variables**
```yaml
JWT_SECRET_KEY: [auto-generated]
DATABASE_URL: sqlite:///app.db
LOG_LEVEL: INFO
CORS_ORIGINS: "*"
RATE_LIMIT_REQUESTS_PER_MINUTE: "60"
ENVIRONMENT: "prod"
DEBUG: "false"
ENABLE_DNS_CACHE: "true"
DNS_CACHE_TTL_SECONDS: "3600"
SMTP_TIMEOUT: "10"
SMTP_PORT: "25"
MAX_CONCURRENT_CONNECTIONS: "10"
PER_DOMAIN_DELAY_SECONDS: "1.0"
ENABLE_CATCH_ALL_DETECTION: "false"
ENABLE_SMTP_VALIDATION: "false"
METRICS_ALLOWLIST: "127.0.0.1,::1"
ENABLE_METRICS: "true"
```

### **Frontend Environment Variables**
```yaml
VITE_API_URL: https://your-backend-service.onrender.com
VITE_API_KEY: your-api-key-here
```

## 🌐 **Service URLs**

After deployment, you'll get:

- **Frontend**: `https://email-validator-frontend.onrender.com`
- **Backend API**: `https://email-validator-api.onrender.com`

## 🔧 **Post-Deployment Setup**

### **1. Create API Keys**
Once deployed, you need to create API keys for authentication:

```bash
# Using the backend API
curl -X POST "https://your-backend-service.onrender.com/api/token" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-api-key"}'
```

### **2. Test the Deployment**
```bash
# Test health endpoint
curl https://your-backend-service.onrender.com/health

# Test validation endpoint
curl -X POST "https://your-backend-service.onrender.com/api/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"emails": ["test@example.com"], "enable_smtp": false, "enable_catch_all": false}'
```

## 🚨 **Important Notes**

### **Free Tier Limitations**
- **Backend**: 750 hours/month (may sleep after inactivity)
- **Frontend**: Unlimited static hosting
- **Cold starts**: Backend may take 30-60 seconds to wake up

### **Production Considerations**
1. **Database**: Consider using PostgreSQL instead of SQLite
2. **Caching**: Add Redis for better performance
3. **Monitoring**: Set up alerts for downtime
4. **SSL**: Render provides automatic HTTPS

### **Security**
- Change default API keys
- Set up proper CORS origins
- Enable rate limiting
- Use environment variables for secrets

## 🔍 **Troubleshooting**

### **Backend Won't Start**
1. Check Dockerfile path in render.yaml
2. Verify environment variables
3. Check build logs in Render dashboard

### **Frontend Can't Connect to Backend**
1. Verify `VITE_API_URL` points to correct backend URL
2. Check CORS settings
3. Ensure backend is running

### **API Authentication Issues**
1. Verify API keys are correct
2. Check JWT token generation
3. Ensure proper Authorization headers

## 📊 **Monitoring**

Your deployment will include:
- **Health checks** at `/health`
- **Metrics endpoint** at `/metrics` (if enabled)
- **Render logs** in the dashboard

## 🎯 **Next Steps After Deployment**

1. **Set up custom domain** (optional)
2. **Configure monitoring** and alerts
3. **Set up CI/CD** for automatic deployments
4. **Add database backups** (if using external DB)
5. **Set up SSL certificates** (automatic with Render)

## 📞 **Support**

- **Render Documentation**: https://render.com/docs
- **Render Support**: Available in the dashboard
- **Project Issues**: Check your GitHub repository

---

**Your email validator will be live at**: `https://email-validator-frontend.onrender.com` 🎉 