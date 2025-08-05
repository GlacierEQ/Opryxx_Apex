"""
Environment Variable Loader for OPRYXX_LOGS2

This module provides secure loading of environment variables from .env files
with support for different environments (development, testing, production).
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv, find_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvLoaderError(Exception):
    """Base exception for environment loading errors."""
    pass

class EnvLoader:
    """Loads and manages environment variables securely."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, env_file: str = None, env: str = None):
        if not self._initialized:
            self.env = env or os.getenv("OPRYXX_ENV", "development")
            self.env_file = env_file or f".env.{self.env}"
            self._loaded = False
            self._overrides = {}
            self._initialized = True
    
    def load(self, override: bool = False) -> bool:
        """Load environment variables from .env file.
        
        Args:
            override: If True, override existing environment variables.
                     If False, only set variables that don't already exist.
        
        Returns:
            bool: True if loading was successful, False otherwise.
        """
        if self._loaded and not override:
            return True
        
        try:
            # Try to find .env file in current or parent directories
            env_path = find_dotenv(self.env_file, usecwd=True)
            
            if not env_path:
                logger.warning(f"No {self.env_file} file found. Using system environment variables.")
                self._loaded = True
                return False
            
            # Load environment variables
            load_dotenv(env_path, override=override, encoding='utf-8')
            
            # Apply any overrides
            for key, value in self._overrides.items():
                if override or key not in os.environ:
                    os.environ[key] = value
            
            self._loaded = True
            logger.info(f"Loaded environment from {env_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load environment: {e}")
            raise EnvLoaderError(f"Failed to load environment: {e}") from e
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Optional[str]:
        """Get an environment variable.
        
        Args:
            key: The environment variable name.
            default: Default value if the variable is not set.
            required: If True, raise an error if the variable is not set.
            
        Returns:
            The value of the environment variable, or the default if not set.
            
        Raises:
            EnvLoaderError: If the variable is required but not set.
        """
        value = os.getenv(key, self._overrides.get(key, default))
        
        if required and value is None:
            raise EnvLoaderError(f"Required environment variable '{key}' is not set")
            
        return value
    
    def get_int(self, key: str, default: int = 0, required: bool = False) -> int:
        """Get an environment variable as an integer.
        
        Args:
            key: The environment variable name.
            default: Default value if the variable is not set or invalid.
            required: If True, raise an error if the variable is not set.
            
        Returns:
            The value of the environment variable as an integer, or the default.
        """
        value = self.get(key, default=default, required=required)
        
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            if required:
                raise EnvLoaderError(
                    f"Environment variable '{key}' must be an integer"
                ) from None
            return default
    
    def get_bool(self, key: str, default: bool = False, required: bool = False) -> bool:
        """Get an environment variable as a boolean.
        
        Args:
            key: The environment variable name.
            default: Default value if the variable is not set or invalid.
            required: If True, raise an error if the variable is not set.
            
        Returns:
            The value of the environment variable as a boolean, or the default.
        """
        value = self.get(key, default=str(default) if default is not None else None, 
                        required=required)
        
        if isinstance(value, bool):
            return value
            
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', 't', 'yes', 'y', '1'):
                return True
            if value in ('false', 'f', 'no', 'n', '0'):
                return False
        
        if required:
            raise EnvLoaderError(
                f"Environment variable '{key}' must be a boolean (true/false)"
            )
            
        return default
    
    def get_list(self, key: str, default: list = None, 
                delimiter: str = ',', required: bool = False) -> list:
        """Get an environment variable as a list.
        
        Args:
            key: The environment variable name.
            default: Default value if the variable is not set.
            delimiter: The delimiter used to split the string into a list.
            required: If True, raise an error if the variable is not set.
            
        Returns:
            The value of the environment variable as a list, or the default.
        """
        if default is None:
            default = []
            
        value = self.get(key, default=None, required=required)
        
        if value is None:
            return default
            
        if isinstance(value, str):
            return [item.strip() for item in value.split(delimiter) if item.strip()]
            
        if isinstance(value, (list, tuple)):
            return list(value)
            
        return default
    
    def set(self, key: str, value: Any, override: bool = True):
        """Set an environment variable.
        
        Args:
            key: The environment variable name.
            value: The value to set.
            override: If True, override existing value.
        """
        if not isinstance(value, str):
            value = str(value)
            
        if override or key not in os.environ:
            os.environ[key] = value
            self._overrides[key] = value
    
    def unset(self, key: str):
        """Unset an environment variable.
        
        Args:
            key: The environment variable name.
        """
        if key in os.environ:
            del os.environ[key]
        if key in self._overrides:
            del self._overrides[key]
    
    def to_dict(self) -> Dict[str, str]:
        """Get all environment variables as a dictionary.
        
        Returns:
            A dictionary of all environment variables.
        """
        return dict(os.environ)
    
    def from_dict(self, env_dict: Dict[str, str], override: bool = True):
        """Set multiple environment variables from a dictionary.
        
        Args:
            env_dict: Dictionary of environment variables.
            override: If True, override existing values.
        """
        for key, value in env_dict.items():
            self.set(key, value, override=override)

def get_env_loader() -> EnvLoader:
    """Get or create the global EnvLoader instance."""
    if EnvLoader._instance is None:
        EnvLoader()
    return EnvLoader._instance

# Example usage
if __name__ == "__main__":
    # Initialize environment loader
    env_loader = get_env_loader()
    
    # Load environment variables
    env_loader.load()
    
    # Get a required environment variable
    try:
        db_host = env_loader.get("DB_HOST", required=True)
        print(f"Database host: {db_host}")
    except EnvLoaderError as e:
        print(f"Error: {e}")
    
    # Get an optional environment variable with a default
    db_port = env_loader.get_int("DB_PORT", default=5432)
    print(f"Database port: {db_port}")
    
    # Get a boolean environment variable
    debug_mode = env_loader.get_bool("DEBUG", default=False)
    print(f"Debug mode: {debug_mode}")
    
    # Get a list from an environment variable
    allowed_hosts = env_loader.get_list("ALLOWED_HOSTS", default=["localhost"])
    print(f"Allowed hosts: {allowed_hosts}")
    
    # Set an environment variable
    env_loader.set("CUSTOM_VAR", "custom_value")
    print(f"Custom var: {env_loader.get('CUSTOM_VAR')}")
