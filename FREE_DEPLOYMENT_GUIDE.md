# 🆓 Free Deployment Guide with Monitoring

This guide shows you how to deploy your Email Validator Tool **completely free** including Prometheus and Grafana monitoring.

## 🎯 **Best Free Options**

### **🥇 Option 1: Railway (Recommended)**
- **Free tier**: $5 credit monthly (enough for small projects)
- **Supports**: Docker Compose, full monitoring stack
- **Pros**: Easy setup, good performance, includes monitoring
- **Cons**: Limited free credit

### **🥈 Option 2: Fly.io**
- **Free tier**: 3 shared-cpu VMs, 3GB storage
- **Supports**: Docker, monitoring
- **Pros**: Generous free tier, global deployment
- **Cons**: More complex setup

### **🥉 Option 3: Render + External Monitoring**
- **Free tier**: 750 hours/month backend + unlimited frontend
- **Monitoring**: Use external free services
- **Pros**: Simple, reliable
- **Cons**: Monitoring not integrated

---

## 🚀 **Option 1: Railway Deployment (Recommended)**

### **Step 1: Sign Up**
1. Go to https://railway.app
2. Sign up with GitHub
3. Get $5 free credit monthly

### **Step 2: Deploy**
1. **Connect your GitHub repo**
2. **Create new project**
3. **Deploy from GitHub**
4. **Railway will detect** the `railway.toml` and deploy everything

### **Step 3: Configure Environment Variables**
In Railway dashboard, add these variables:
```bash
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
ENVIRONMENT=production
ENABLE_METRICS=true
METRICS_ALLOWLIST=0.0.0.0/0
CORS_ORIGINS=*
```

### **Step 4: Access Your Services**
After deployment, you'll get:
- **Main App**: `https://your-app.railway.app`
- **Grafana**: `https://your-app.railway.app:3000`
- **Prometheus**: `https://your-app.railway.app:9090`

---

## 🚀 **Option 2: Fly.io Deployment**

### **Step 1: Install Fly CLI**
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### **Step 2: Create fly.toml**
```bash
fly launch
```

### **Step 3: Deploy**
```bash
fly deploy
```

### **Step 4: Scale Services**
```bash
# Scale to free tier
fly scale count 1
fly scale memory 256
```

---

## 🚀 **Option 3: Render + External Monitoring**

### **Step 1: Deploy Main App to Render**
Use the existing `render.yaml` configuration.

### **Step 2: Add Free External Monitoring**

#### **Option A: UptimeRobot (Free)**
1. Sign up at https://uptimerobot.com
2. Add your Render URL
3. Get email alerts for downtime

#### **Option B: Better Stack (Free)**
1. Sign up at https://betterstack.com
2. Add your app URL
3. Get logs and monitoring

#### **Option C: Self-hosted Monitoring**
Deploy monitoring separately on Railway:
```yaml
# Separate railway-monitoring.toml
[[services]]
name = "prometheus"
port = 9090

[[services]]
name = "grafana"
port = 3000
```

---

## 🔧 **Configuration Files Created**

### **railway.toml** - Railway deployment config
### **Dockerfile** - Root Dockerfile for Railway
### **Updated docker-compose.yml** - Includes monitoring

---

## 📊 **What You Get with Each Option**

### **Railway (Recommended)**
- ✅ **Complete stack**: Backend + Frontend + Monitoring
- ✅ **Docker Compose**: Full monitoring stack
- ✅ **Easy setup**: One-click deployment
- ✅ **Good performance**: Fast startup times
- ✅ **Integrated**: Everything in one place

### **Fly.io**
- ✅ **Complete stack**: Backend + Frontend + Monitoring
- ✅ **Global deployment**: Multiple regions
- ✅ **Generous limits**: 3 VMs, 3GB storage
- ⚠️ **Complex setup**: More configuration needed

### **Render + External**
- ✅ **Simple deployment**: Easy to set up
- ✅ **Reliable**: Good uptime
- ⚠️ **Separate monitoring**: Not integrated
- ⚠️ **Limited features**: No Prometheus/Grafana

---

## 💰 **Cost Comparison**

| Platform | Free Tier | Monthly Cost | Monitoring |
|----------|-----------|--------------|------------|
| **Railway** | $5 credit | $0-5 | ✅ Included |
| **Fly.io** | 3 VMs | $0 | ✅ Included |
| **Render** | 750h backend | $0 | ❌ External |
| **Heroku** | Discontinued | $7+ | ❌ External |

---

## 🎯 **Recommended Approach**

### **For Beginners**: Railway
- Easiest setup
- Everything included
- Good documentation

### **For Advanced Users**: Fly.io
- More control
- Better performance
- Global deployment

### **For Budget-Conscious**: Render + External
- Completely free
- Simple setup
- Separate monitoring

---

## 🚨 **Important Notes**

### **Free Tier Limitations**
- **Railway**: $5 credit monthly
- **Fly.io**: 3 shared-cpu VMs
- **Render**: 750 hours/month backend

### **Monitoring Considerations**
- **Prometheus**: Stores metrics data
- **Grafana**: Visualizes metrics
- **Data retention**: Limited on free tiers

### **Production Readiness**
- **SSL**: All platforms provide HTTPS
- **Backups**: Consider external database
- **Scaling**: Upgrade when needed

---

## 🔍 **Troubleshooting**

### **Railway Issues**
```bash
# Check logs
railway logs

# Restart services
railway service restart

# Check status
railway status
```

### **Fly.io Issues**
```bash
# Check logs
fly logs

# Restart app
fly apps restart

# Check status
fly status
```

### **Render Issues**
- Check build logs in dashboard
- Verify environment variables
- Check service status

---

## 🎉 **Next Steps**

1. **Choose your platform** (Railway recommended)
2. **Deploy your application**
3. **Set up monitoring**
4. **Test everything works**
5. **Share your live app!**

Your email validator with full monitoring will be live and completely free! 🚀 