# 📊 Email Validator Monitoring Setup

This guide explains how to use the Prometheus and Grafana monitoring stack for your email validator project.

## 🚀 Quick Start

### Option 1: Using the startup script (Recommended)
```bash
# On Linux/Mac:
chmod +x start-monitoring.sh
./start-monitoring.sh

# On Windows:
start-monitoring.bat
```

### Option 2: Manual startup
```bash
docker-compose up -d --build
```

## 📊 What You Get

### 1. **Grafana Dashboard** - http://localhost:3000
- **Username**: `admin`
- **Password**: `admin`

**Dashboard Panels:**
- 📈 **Email Validation Rate** - Real-time validation throughput
- 📊 **Total Emails by Status** - Breakdown of valid/invalid/abuse/etc.
- ⏱️ **95th Percentile Request Latency** - Performance monitoring
- 🔌 **SMTP Connections Open** - Connection pool monitoring
- 📦 **95th Percentile Batch Size** - Usage patterns
- 🌐 **Request Rate by Endpoint** - API usage analytics

### 2. **Prometheus** - http://localhost:9090
- Raw metrics data
- Query interface
- Alert manager (if configured)

### 3. **Email Validator API** - http://localhost:8000
- Your main application
- Metrics endpoint at `/metrics`

## 🔧 Configuration Files

### Prometheus Configuration
- **File**: `infra/observability/prometheus.yml`
- **Purpose**: Defines what metrics to collect and from where
- **Target**: Scrapes metrics from `api:8000/metrics` every 15 seconds

### Grafana Configuration
- **Dashboard**: `infra/observability/grafana-dashboard.json`
- **Datasource**: `infra/observability/grafana/datasources/prometheus.yml`
- **Provisioning**: `infra/observability/grafana/dashboards/dashboard.yml`

## 📈 Metrics Being Collected

### Custom Metrics (from your API)
- `emails_validated_total` - Count by status and organization
- `smtp_connections_open` - Active SMTP connections by domain
- `request_latency_seconds` - API response times
- `validation_batch_size` - Batch sizes for validation requests

### Standard Metrics (auto-collected)
- HTTP request/response sizes
- HTTP status codes
- Request rates by endpoint
- System metrics (CPU, memory, etc.)

## 🛠️ Management Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f prometheus
docker-compose logs -f grafana

# Restart a specific service
docker-compose restart api

# Check service status
docker-compose ps
```

## 🔍 Troubleshooting

### Services not starting?
```bash
# Check Docker is running
docker info

# Check for port conflicts
netstat -an | grep :3000
netstat -an | grep :9090
netstat -an | grep :8000
```

### No metrics showing in Grafana?
1. Check Prometheus is scraping: http://localhost:9090/targets
2. Check API metrics endpoint: http://localhost:8000/metrics
3. Verify network connectivity between containers

### Can't access Grafana?
1. Check if Grafana container is running: `docker-compose ps`
2. Check Grafana logs: `docker-compose logs grafana`
3. Verify port 3000 is not in use by another application

## 🔐 Security Notes

- **Metrics endpoint** is IP-restricted (only localhost and Docker networks)
- **Grafana** uses default admin/admin credentials - change in production
- **Prometheus** has no authentication by default - secure in production

## 📝 Production Considerations

1. **Change default passwords** in Grafana
2. **Add authentication** to Prometheus
3. **Use persistent volumes** for data retention
4. **Set up alerts** in Grafana
5. **Configure backup** for metrics data
6. **Use HTTPS** for all endpoints

## 🎯 Next Steps

1. **Generate some traffic** to see metrics:
   ```bash
   # Test the API
   curl -X POST "http://localhost:8000/api/validate" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"emails": ["test@example.com"], "enable_smtp": false, "enable_catch_all": false}'
   ```

2. **Explore the dashboard** in Grafana
3. **Set up alerts** for critical metrics
4. **Customize the dashboard** for your needs

## 📚 Useful Links

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/)
- [Grafana Dashboard Tutorial](https://grafana.com/docs/grafana/latest/dashboards/) 