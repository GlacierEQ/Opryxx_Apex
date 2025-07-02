# OPRYXX Deployment Guide

This document provides comprehensive deployment instructions for the OPRYXX system, including the enhanced logging and monitoring features.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Logging System](#logging-system)
- [Monitoring](#monitoring)
- [Health Checks](#health-checks)
- [Deployment Checklist](#deployment-checklist)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware
- CPU: 4+ cores (8+ recommended for production)
- RAM: 8GB minimum (16GB+ recommended for production)
- Disk: 50GB+ free space (SSD recommended)
  - Logs directory: 100GB+ recommended for production

### Software
- OS: Linux/Unix (Ubuntu 20.04 LTS recommended), Windows Server 2019+
- Python: 3.10+
- Database: PostgreSQL 13+ / SQLite (for development)
- Redis: 6.0+ (for caching and task queue)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/opryxx.git
cd opryxx
```

### 2. Create and Activate Virtual Environment
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Application
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/opryxx

# Redis
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/opryxx
LOG_RETENTION_DAYS=30

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=8001

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Configuration

### Main Configuration File
Edit `config/config.yaml` to configure application settings:

```yaml
core:
  environment: production
  debug: false
  log_level: INFO
  
  # API settings
  api_host: 0.0.0.0
  api_port: 8000
  
  # Security
  cors_origins:
    - "https://your-domain.com"
  
  # Database
  database_url: ${DATABASE_URL}
  
  # Redis
  redis_url: ${REDIS_URL}

# Logging configuration
logging:
  log_dir: ${LOG_DIR:-logs}
  max_size_mb: 100
  backup_count: 5
  retention_days: ${LOG_RETENTION_DAYS:-30}
  compress_logs: true
  
  # Log levels
  console_level: ${LOG_LEVEL:-INFO}
  file_level: DEBUG

# Monitoring configuration
monitoring:
  enabled: true
  metrics_interval: 60  # seconds
  prometheus_port: ${METRICS_PORT:-8001}
  
  # Alert thresholds
  alert_thresholds:
    cpu_percent: 90
    memory_percent: 90
    disk_percent: 90
```

## Logging System

The enhanced logging system provides comprehensive logging with rotation, retention, and compression.

### Key Features
- **Rotation**: Logs rotate when they reach 100MB (configurable)
- **Retention**: Logs are kept for 30 days by default (configurable)
- **Compression**: Rotated logs are automatically compressed with gzip
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Error Logs**: Separate error logs for easier debugging

### Log Files
- `app.log`: Main application log
- `error.log`: Error logs (ERROR level and above)
- `performance.log`: Performance metrics and timing information
- `security.log`: Security-related events

### Log Directory Structure
```
/var/log/opryxx/
├── app.log
├── app.log.1.gz
├── app.log.2.gz
├── error.log
├── error.log.1.gz
├── performance.log
└── security.log
```

### Configuration Options
- `logging.log_dir`: Directory to store log files
- `logging.max_size_mb`: Maximum log file size before rotation (MB)
- `logging.backup_count`: Number of backup files to keep
- `logging.retention_days`: Number of days to keep log files (0 = keep forever)
- `logging.compress_logs`: Whether to compress rotated logs

## Monitoring

The monitoring system collects system and application metrics for observability.

### Available Metrics
- **System Metrics**:
  - CPU usage
  - Memory usage
  - Disk usage
  - Network I/O
  - Process metrics

- **Application Metrics**:
  - Request rates
  - Error rates
  - Response times
  - Queue lengths

### Accessing Metrics

#### Prometheus Metrics
Metrics are available in Prometheus format at:
```
http://<host>:8001/metrics
```

#### Health Endpoints
- `GET /health`: Basic health check
- `GET /health/detailed`: Detailed health information
- `GET /metrics`: Prometheus metrics (if enabled)

### Alerting
Alerts are triggered when thresholds are exceeded:
- CPU usage > 90%
- Memory usage > 90%
- Disk usage > 90%

## Deployment

### Systemd Service
Create a systemd service file at `/etc/systemd/system/opryxx.service`:

```ini
[Unit]
Description=OPRYXX Application
After=network.target postgresql.service redis-server.service

[Service]
User=opryxx
Group=opryxx
WorkingDirectory=/opt/opryxx
EnvironmentFile=/opt/opryxx/.env
ExecStart=/opt/opryxx/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

# Security
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=opryxx

[Install]
WantedBy=multi-user.target
```

### Log Rotation with logrotate
Create a logrotate configuration at `/etc/logrotate.d/opryxx`:

```
/var/log/opryxx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 opryxx opryxx
    sharedscripts
    postrotate
        systemctl kill -s USR1 opryxx.service
    endscript
}
```

## Health Checks

The system exposes the following health check endpoints:

### Liveness Probe
```
GET /health
```

**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2025-07-01T00:00:00Z"
}
```

### Readiness Probe
```
GET /health/detailed
```

**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2025-07-01T00:00:00Z",
    "checks": {
        "database": {
            "status": "healthy",
            "response_time_ms": 5.2
        },
        "cache": {
            "status": "healthy",
            "response_time_ms": 1.1
        },
        "external_service": {
            "status": "healthy",
            "response_time_ms": 12.7
        }
    }
}
```

## Deployment Checklist

### Pre-Deployment
- [ ] Backup existing data and configuration
- [ ] Review and update environment variables
- [ ] Verify database migrations are up to date
- [ ] Check system requirements
- [ ] Schedule maintenance window if needed

### Deployment
- [ ] Deploy new code
- [ ] Run database migrations
- [ ] Restart services
- [ ] Verify service status
- [ ] Run smoke tests

### Post-Deployment
- [ ] Verify logs for errors
- [ ] Check system metrics
- [ ] Test health endpoints
- [ ] Verify monitoring is working
- [ ] Update deployment documentation

## Troubleshooting

### Common Issues

#### Log Rotation Not Working
- Verify log directory permissions
- Check disk space
- Verify logrotate configuration
- Check systemd journal for errors

#### High CPU/Memory Usage
- Check application logs for errors
- Review recent deployments
- Check for memory leaks
- Review monitoring dashboards

#### Database Connection Issues
- Verify database is running
- Check connection string
- Verify network connectivity
- Check database logs

### Getting Help
For additional support, please contact:
- **Support Email**: support@opryxx.ai
- **Documentation**: https://docs.opryxx.ai
- **GitHub Issues**: https://github.com/your-org/opryxx/issues

## License
Copyright © 2025 OPRYXX. All rights reserved.
