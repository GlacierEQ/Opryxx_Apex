""
Configuration Utilities
Helper functions for common configuration tasks
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError

from .manager import ConfigManager, ConfigSource, ConfigFormat

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

def load_config_schema(config_path: str, 
                     schema: Type[T],
                     format: ConfigFormat = ConfigFormat.YAML,
                     env_prefix: Optional[str] = None) -> T:
    """
    Load and validate configuration against a Pydantic schema
    
    Args:
        config_path: Path to the configuration file
        schema: Pydantic model class for validation
        format: Configuration file format
        env_prefix: Optional prefix for environment variable overrides
        
    Returns:
        Validated configuration object
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        # Initialize config manager
        config = ConfigManager()
        
        # Add the config source
        if not config.add_source(
            config_path,
            format=format,
            env_prefix=env_prefix,
            required=True
        ):
            raise ValueError(f"Failed to load configuration from {config_path}")
        
        # Validate against schema
        config_dict = config.to_dict()
        return schema(**config_dict)
        
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise ValueError(f"Invalid configuration: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def find_config_file(filename: str, 
                   search_paths: Optional[list] = None,
                   raise_if_not_found: bool = True) -> Optional[str]:
    """
    Search for a configuration file in common locations
    
    Args:
        filename: Name of the config file to find
        search_paths: Additional paths to search (appended to default paths)
        raise_if_not_found: Whether to raise an exception if file not found
        
    Returns:
        Path to the config file if found, None otherwise
        
    Raises:
        FileNotFoundError: If raise_if_not_found is True and file is not found
    """
    # Default search paths
    default_paths = [
        os.curdir,  # Current directory
        os.path.expanduser("~/.config/opryxx"),  # User config dir
        "/etc/opryxx",  # System config dir
        os.path.dirname(os.path.abspath(__file__)),  # Package dir
    ]
    
    # Add custom search paths if provided
    search_paths = (search_paths or []) + default_paths
    
    # Check each path
    for path in search_paths:
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            return os.path.abspath(full_path)
    
    # File not found
    if raise_if_not_found:
        raise FileNotFoundError(
            f"Could not find config file '{filename}' in any of: {', '.join(search_paths)}"
        )
    return None

def get_environment_config(prefix: str = "OPRYXX") -> dict:
    """
    Get all environment variables with the given prefix
    
    Args:
        prefix: Environment variable prefix (case-insensitive)
        
    Returns:
        Dictionary of matching environment variables (without prefix)
    """
    prefix = prefix.upper() + '_'
    prefix_len = len(prefix)
    
    return {
        k[prefix_len:].lower(): v 
        for k, v in os.environ.items() 
        if k.upper().startswith(prefix)
    }

def merge_configs(*configs: dict) -> dict:
    """
    Deep merge multiple configuration dictionaries
    
    Args:
        *configs: Dictionaries to merge (later ones take precedence)
        
    Returns:
        Merged configuration dictionary
    """
    result = {}
    
    for config in configs:
        if not isinstance(config, dict):
            continue
            
        for key, value in config.items():
            if (key in result and isinstance(result[key], dict) 
                    and isinstance(value, dict)):
                # Recursively merge dictionaries
                result[key] = merge_configs(result[key], value)
            else:
                # Overwrite with new value
                result[key] = value
    
    return result

def configure_logging(config: dict = None):
    """
    Configure Python logging from a configuration dictionary
    
    Args:
        config: Logging configuration dictionary
    """
    import logging.config
    
    # Default logging configuration
    default_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    # Merge with user config if provided
    if config:
        logging_config = merge_configs(default_config, config)
    else:
        logging_config = default_config
    
    # Apply the configuration
    logging.config.dictConfig(logging_config)
    logger.info("Logging configured")

def get_typed_config(section: str, 
                   config_type: Type[T],
                   config: Optional[ConfigManager] = None) -> T:
    """
    Get a configuration section as a typed object
    
    Args:
        section: Configuration section name
        config_type: Pydantic model class for the section
        config: Optional ConfigManager instance (uses global if None)
        
    Returns:
        Validated configuration object
        
    Raises:
        ValueError: If configuration is invalid
    """
    cfg = config or ConfigManager()
    section_data = cfg.get_section(section)
    
    try:
        return config_type(**section_data)
    except ValidationError as e:
        logger.error(f"Invalid configuration for section '{section}': {str(e)}")
        raise ValueError(f"Invalid configuration for section '{section}'") from e
