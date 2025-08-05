"""
Secure Configuration Manager for OPRYXX_LOGS2

This module provides secure handling of configuration and secrets,
including environment variables, secret rotation, and encryption.
"""
import os
import json
import hashlib
import base64
import logging
from typing import Dict, Any, Optional, TypeVar, Type
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import keyring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseConfig')

class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass

class SecretRotationError(ConfigError):
    """Raised when secret rotation fails."""
    pass

class EncryptionError(ConfigError):
    """Raised when encryption/decryption fails."""
    pass

@dataclass
class BaseConfig:
    """Base configuration class that provides serialization and validation."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create config from dictionary."""
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            bool: True if config is valid, False otherwise
        """
        return True

@dataclass
class SecurityConfig(BaseConfig):
    """Security-related configuration."""
    encryption_key: str = field(default_factory=lambda: Fernet.generate_key().decode())
    key_rotation_days: int = 30
    max_failed_attempts: int = 5
    lockout_minutes: int = 15

@dataclass
class DatabaseConfig(BaseConfig):
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "opryxx_logs"
    user: str = "postgres"
    password: str = ""  # Will be stored encrypted
    ssl_mode: str = "prefer"

@dataclass
class APIConfig(BaseConfig):
    """API configuration."""
    base_url: str = "https://api.opryxx.ai/v1"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5

class ConfigManager:
    """Manages application configuration and secrets."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_dir: str = None):
        if not self._initialized:
            self.config_dir = Path(config_dir or os.getenv("OPRYXX_CONFIG_DIR", "./config"))
            self.secrets_file = self.config_dir / "secrets.enc"
            self.config_file = self.config_dir / "config.json"
            self.key_file = self.config_dir / ".encryption_key"
            self._fernet = None
            self._config = {}
            self._secrets = {}
            
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize or load configuration
            self._initialize()
            self._initialized = True
    
    def _initialize(self):
        """Initialize or load configuration."""
        # Initialize or load encryption key
        self._load_or_generate_key()
        
        # Load or create config
        if self.config_file.exists():
            self._load_config()
        else:
            self._create_default_config()
        
        # Load secrets if they exist
        if self.secrets_file.exists():
            self._load_secrets()
    
    def _load_or_generate_key(self):
        """Load encryption key or generate a new one."""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                self._fernet = Fernet(key)
            except Exception as e:
                logger.error(f"Failed to load encryption key: {e}")
                raise EncryptionError("Failed to load encryption key") from e
        else:
            # Generate new key
            key = Fernet.generate_key()
            try:
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions (Unix-like systems)
                if os.name != 'nt':
                    os.chmod(self.key_file, 0o600)
                self._fernet = Fernet(key)
            except Exception as e:
                logger.error(f"Failed to save encryption key: {e}")
                raise EncryptionError("Failed to save encryption key") from e
    
    def _create_default_config(self):
        """Create default configuration."""
        self._config = {
            "security": SecurityConfig(),
            "database": DatabaseConfig(),
            "api": APIConfig()
        }
        self._save_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self._config = {
                "security": SecurityConfig(**data.get("security", {})),
                "database": DatabaseConfig(**data.get("database", {})),
                "api": APIConfig(**data.get("api", {}))
            }
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise ConfigError("Failed to load configuration") from e
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            # Convert config objects to dictionaries
            config_data = {
                section: self._config[section].to_dict()
                for section in self._config
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Set restrictive permissions (Unix-like systems)
            if os.name != 'nt':
                os.chmod(self.config_file, 0o600)
                
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigError("Failed to save configuration") from e
    
    def _load_secrets(self):
        """Load secrets from encrypted file."""
        if not self._fernet:
            raise EncryptionError("Encryption key not initialized")
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._fernet.decrypt(encrypted_data)
            self._secrets = json.loads(decrypted_data.decode())
            
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            raise ConfigError("Failed to load secrets") from e
    
    def _save_secrets(self):
        """Save secrets to encrypted file."""
        if not self._fernet:
            raise EncryptionError("Encryption key not initialized")
        
        try:
            encrypted_data = self._fernet.encrypt(
                json.dumps(self._secrets).encode()
            )
            
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions (Unix-like systems)
            if os.name != 'nt':
                os.chmod(self.secrets_file, 0o600)
                
        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")
            raise ConfigError("Failed to save secrets") from e
    
    def get_config(self, section: str) -> BaseConfig:
        """Get configuration section."""
        if section not in self._config:
            raise ConfigError(f"Configuration section '{section}' not found")
        return self._config[section]
    
    def update_config(self, section: str, config: BaseConfig):
        """Update configuration section."""
        if section not in self._config:
            raise ConfigError(f"Configuration section '{section}' not found")
        
        if not isinstance(config, BaseConfig):
            raise ValueError("Config must be an instance of BaseConfig")
        
        if not config.validate():
            raise ValueError("Invalid configuration")
        
        self._config[section] = config
        self._save_config()
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get a secret value."""
        return self._secrets.get(key, default)
    
    def set_secret(self, key: str, value: Any):
        """Set a secret value."""
        self._secrets[key] = value
        self._save_secrets()
    
    def delete_secret(self, key: str):
        """Delete a secret."""
        if key in self._secrets:
            del self._secrets[key]
            self._save_secrets()
    
    def rotate_secrets(self):
        """Rotate all secrets and update configuration."""
        try:
            # Backup current secrets
            backup = self._secrets.copy()
            
            # Generate new encryption key
            new_key = Fernet.generate_key()
            new_fernet = Fernet(new_key)
            
            # Re-encrypt all secrets with new key
            encrypted_data = new_fernet.encrypt(
                json.dumps(self._secrets).encode()
            )
            
            # Write new encrypted data
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Update encryption key
            with open(self.key_file, 'wb') as f:
                f.write(new_key)
            
            # Update in-memory fernet instance
            self._fernet = new_fernet
            
            logger.info("Successfully rotated secrets and encryption key")
            
        except Exception as e:
            logger.error(f"Failed to rotate secrets: {e}")
            # Restore backup if possible
            if 'backup' in locals():
                self._secrets = backup
                self._save_secrets()
            raise SecretRotationError("Failed to rotate secrets") from e

def get_config_manager() -> ConfigManager:
    """Get or create the global ConfigManager instance."""
    if ConfigManager._instance is None:
        ConfigManager()
    return ConfigManager._instance

# Example usage
if __name__ == "__main__":
    # Initialize config manager
    config_manager = get_config_manager()
    
    # Get database config
    db_config = config_manager.get_config("database")
    print(f"Database host: {db_config.host}")
    
    # Set a secret
    config_manager.set_secret("api_key", "your-secret-api-key")
    
    # Get a secret
    api_key = config_manager.get_secret("api_key")
    print(f"API Key: {'*' * len(api_key) if api_key else 'Not set'}")
    
    # Rotate secrets (in a real app, you'd call this periodically)
    # config_manager.rotate_secrets()
