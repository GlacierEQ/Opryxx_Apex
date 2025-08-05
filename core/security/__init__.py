""
OPRYXX Security Package

This package provides secure configuration and credential management for the OPRYXX_LOGS2 system.
It includes modules for secure storage of secrets, environment variable management,
and credential rotation.
"""

# Import key components for easier access
from .config_manager import ConfigManager, get_config_manager, ConfigError, SecretRotationError, EncryptionError
from .env_loader import EnvLoader, get_env_loader, EnvLoaderError

# Define package version
__version__ = '1.0.0'

# Export public API
__all__ = [
    # Core classes
    'ConfigManager',
    'EnvLoader',
    
    # Factory functions
    'get_config_manager',
    'get_env_loader',
    
    # Exceptions
    'ConfigError',
    'SecretRotationError',
    'EncryptionError',
    'EnvLoaderError',
    
    # Version
    '__version__',
]
