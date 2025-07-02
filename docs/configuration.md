# OPRYXX Configuration Guide

This document provides detailed information about the configuration options available in the OPRYXX system.

## Table of Contents
- [Core Configuration](#core-configuration)
- [Logging Configuration](#logging-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [AI Model Configuration](#ai-model-configuration)
- [Environment Variables](#environment-variables)

## Core Configuration

The main configuration file is located at `config/config.yaml`. This file contains all the core settings for the OPRYXX system.

### Example Configuration

```yaml
core:
  environment: development  # or 'production'
  debug: true  # Enable debug mode
  log_level: INFO  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  max_workers: 4  # Maximum number of worker threads
  
  # Data retention settings
  retention_days: 30  # Number of days to retain logs and metrics
  
  # Performance settings
  metrics_interval: 60  # Seconds between metrics collection
  max_metrics_history: 1000  # Maximum number of metrics to keep in memory

  # API settings
  api_host: 0.0.0.0
  api_port: 8000
  api_workers: 2
  api_timeout: 120  # seconds
  
  # Security settings
  cors_origins:  # List of allowed CORS origins
    - "http://localhost:3000"
    - "https://example.com"
  
  # Authentication
  auth_enabled: true
  jwt_secret: ${JWT_SECRET}  # Should be set via environment variable
  password_salt_rounds: 10
  
  # External services
  database_url: ${DATABASE_URL}  # Database connection string
  cache_url: redis://localhost:6379/0  # Cache connection string
  
  # Feature flags
  enable_experimental_features: false
  maintenance_mode: false
```

## Logging Configuration

```yaml
logging:
  # Log file settings
  log_dir: logs  # Directory to store log files
  max_size_mb: 100  # Maximum log file size in MB
  backup_count: 5  # Number of backup log files to keep
  
  # Log levels
  console_level: INFO  # Console log level
  file_level: DEBUG  # File log level
  
  # Log formatting
  console_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
  
  # Performance logging
  enable_performance_logs: true
  performance_log_file: performance.log
  
  # Security logging
  enable_security_logs: true
  security_log_file: security.log
```

## Monitoring Configuration

```yaml
monitoring:
  # System metrics collection
  collect_system_metrics: true
  metrics_interval: 60  # seconds
  
  # Prometheus metrics
  enable_prometheus: true
  prometheus_port: 8001
  
  # Health checks
  health_check_interval: 300  # seconds
  
  # Alerting
  enable_alerts: true
  alert_thresholds:
    cpu_percent: 90
    memory_percent: 90
    disk_percent: 90
  
  # Anomaly detection
  enable_anomaly_detection: true
  anomaly_sensitivity: 3.0  # Standard deviations from mean to trigger alert
```

## AI Model Configuration

```yaml
ai_models:
  # Default model settings
  default_model: gpt-4
  temperature: 0.7
  max_tokens: 2000
  
  # Model-specific configurations
  models:
    gpt-4:
      provider: openai
      api_key: ${OPENAI_API_KEY}
      max_tokens: 8000
      
    deepseek:
      provider: deepseek
      api_key: ${DEEPSEEK_API_KEY}
      max_tokens: 4000
      
    llama-2:
      provider: meta
      model_path: /path/to/llama2
      device: cuda  # or 'cpu'
```

## Environment Variables

The following environment variables can be used to configure the system:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Runtime environment (development, staging, production) | No | `development` |
| `DEBUG` | Enable debug mode | No | `false` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | No | `INFO` |
| `DATABASE_URL` | Database connection URL | Yes | - |
| `REDIS_URL` | Redis connection URL | No | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI | - |
| `DEEPSEEK_API_KEY` | DeepSeek API key | If using DeepSeek | - |
| `JWT_SECRET` | Secret key for JWT token signing | Yes | - |
| `SECRET_KEY` | Secret key for session encryption | Yes | - |

## Health Check Endpoints

The system provides the following health check endpoints:

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check with system metrics
- `GET /metrics` - Prometheus metrics endpoint (if enabled)

## Log Rotation

Log rotation is handled automatically by the logging system with the following settings:
- Maximum log file size: 100MB (configurable)
- Number of backup files: 5 (configurable)
- Logs are rotated when they reach the maximum size
- Old log files are compressed with gzip

## Configuration Best Practices

1. **Use Environment Variables for Secrets**
   Never commit sensitive information like API keys or database credentials to version control. Use environment variables instead.

2. **Different Configurations per Environment**
   Maintain separate configuration files for different environments (development, staging, production).

3. **Validate Configuration on Startup**
   The system validates the configuration on startup and will fail fast if there are any issues.

4. **Monitor Configuration Changes**
   The system can be configured to reload configuration on changes. In production, consider using a configuration management system.

5. **Secure Sensitive Data**
   Use appropriate file permissions for configuration files and ensure they are not world-readable.
