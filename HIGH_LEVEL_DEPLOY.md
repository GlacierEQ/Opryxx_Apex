# 🚀 OPRYXX High-Level Deployment Guide

## Quick Deploy Options

### 1. Docker Compose (Recommended)
```bash
# Clone and deploy
git clone https://github.com/yourusername/opryxx_logs.git
cd opryxx_logs
chmod +x deploy.sh
./deploy.sh
```

### 2. Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### 3. GitHub Actions
- Push to `main` branch triggers automatic deployment
- Manual deployment via Actions tab

## Environment Variables
```bash
DB_PASSWORD=your_secure_password
APP_URL=https://your-domain.com
```

## Health Check
```bash
curl http://localhost:8000/health
```

## Monitoring
- Logs: `docker-compose logs -f`
- Metrics: Available at `/metrics` endpoint