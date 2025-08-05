# Secure Configuration Integration Guide

This guide explains how to integrate the secure configuration system into your OPRYXX_LOGS2 project.

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Configuration](#advanced-configuration)
5. [Best Practices](#best-practices)
6. [Migration Guide](#migration-guide)
7. [Troubleshooting](#troubleshooting)

## Overview

The secure configuration system provides:
- Secure storage of sensitive data (API keys, credentials, etc.)
- Environment variable management
- Credential rotation
- Type-safe configuration access
- Automatic environment detection

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements-security.txt
```

2. Initialize the secure configuration system:

```bash
python scripts/init_secure_config.py --config-dir=config
```

3. Update your `.gitignore` to exclude sensitive files:

```
# Config files
config/secrets.enc
config/.encryption_key
config/.env
*.log
```

## Basic Usage

### Accessing Configuration

```python
from core.security import get_config_manager, get_env_loader

# Get config manager and env loader
config_manager = get_config_manager()
env_loader = get_env_loader()

# Access configuration sections
db_config = config_manager.get_config('database')
print(f"Database: {db_config.host}:{db_config.port}")

# Access environment variables
api_key = env_loader.get('API_KEY', required=True)
```

### Managing Secrets

```python
# Get a secret
secret = env_loader.get('SECRET_KEY')

# Set a secret (only in development)
env_loader.set('NEW_SECRET', 'value')

# Get a secret with type conversion
timeout = env_loader.get_int('TIMEOUT', default=30)
debug = env_loader.get_bool('DEBUG', default=False)
hosts = env_loader.get_list('ALLOWED_HOSTS')
```

### Using the Credential Manager

```bash
# List all credentials
python scripts/credential_manager.py list

# Get a specific credential
python scripts/credential_manager.py get API_KEY

# Rotate all credentials
python scripts/credential_manager.py rotate
```

## Advanced Configuration

### Environment-Specific Configuration

The system automatically loads environment-specific `.env` files:
- `.env` - Base configuration
- `.env.development` - Development overrides
- `.env.test` - Test overrides
- `.env.production` - Production overrides

Set the `OPRYXX_ENV` environment variable to specify the environment.

### Custom Configuration Sections

1. Define a configuration class:

```python
from dataclasses import dataclass
from core.security.config_manager import BaseConfig

@dataclass
class APIConfig(BaseConfig):
    base_url: str = "https://api.example.com"
    timeout: int = 30
    retry_attempts: int = 3
```

2. Register the configuration:

```python
config_manager = get_config_manager()
config_manager.update_config('api', APIConfig())
```

## Best Practices

1. **Never commit sensitive data** to version control
2. **Use environment variables** for all configuration
3. **Rotate credentials** regularly using the credential manager
4. **Validate configuration** on application startup
5. **Use type hints** for better IDE support

## Migration Guide

### From Hardcoded Values

**Before:**
```python
# config.py
API_KEY = "hardcoded-key"
DB_URL = "postgres://user:pass@localhost/db"
```

**After:**
```python
# config.py
from core.security import get_env_loader

env = get_env_loader()
API_KEY = env.get('API_KEY', required=True)
DB_URL = env.get('DB_URL', required=True)
```

### From Python Config Files

**Before:**
```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**After:**
```python
# config/settings.py
from core.security import get_config_manager

config = get_config_manager()
db_config = config.get_config('database')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_config.name,
        'USER': db_config.user,
        'PASSWORD': db_config.password,
        'HOST': db_config.host,
        'PORT': str(db_config.port),
    }
}
```

## Troubleshooting

### Missing Environment Variables

If you get errors about missing environment variables:

1. Check that the `.env` file exists in the config directory
2. Verify the variable is defined in the `.env` file
3. Ensure the environment is set correctly (development/test/production)

### Permission Errors

On Unix-like systems, ensure the config directory has the correct permissions:

```bash
chmod 700 config
chmod 600 config/*
```

### Encryption Errors

If you encounter encryption errors:

1. Verify the `.encryption_key` file exists in the config directory
2. Check file permissions
3. If needed, delete the key file and let the system generate a new one

## Next Steps

1. Run the security audit script to identify hardcoded credentials
2. Update your deployment process to handle secure configuration
3. Set up automated credential rotation in production
