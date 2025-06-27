"""
Configuration Module for AI Workbench

This module handles configuration management for the AI Workbench,
including loading settings from files, environment variables, and defaults.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict

# Set up logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "app": {
        "name": "AI Workbench",
        "version": "1.0.0",
        "description": "Advanced system monitoring and optimization tool",
        "debug": False,
        "log_level": "INFO",
        "log_file": "ai_workbench.log",
    },
    "database": {
        "url": "sqlite:///ai_workbench.db",
        "echo": False,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    },
    "monitoring": {
        "enabled": True,
        "interval": 300,  # seconds
        "cpu_warning": 80.0,  # percentage
        "memory_warning": 80.0,  # percentage
        "disk_warning": 85.0,  # percentage
        "temp_warning": 2048,  # MB
    },
    "optimization": {
        "auto_optimize": True,
        "clean_temp_files": True,
        "clean_logs": True,
        "optimize_startup": True,
        "defrag_drives": False,
        "max_temp_file_age": 7,  # days
    },
    "security": {
        "check_updates": True,
        "check_vulnerabilities": True,
        "require_authentication": False,
        "api_key": "",
    },
    "notifications": {
        "enabled": True,
        "email_alerts": False,
        "email_recipients": [],
        "desktop_alerts": True,
        "log_alerts": True,
    },
    "predictive_analysis": {
        "enabled": True,
        "model_path": "models/predictive_model.pkl",
        "confidence_threshold": 0.7,
        "training_interval": 86400,  # seconds (1 day)
        "max_training_samples": 10000,
    },
    "api": {
        "enabled": False,
        "host": "0.0.0.0",
        "port": 8000,
        "cors_origins": ["*"],
        "api_key_required": True,
    },
}


@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "AI Workbench"
    version: str = "1.0.0"
    description: str = "Advanced system monitoring and optimization tool"
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = "ai_workbench.log"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///ai_workbench.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    interval: int = 300  # seconds
    cpu_warning: float = 80.0  # percentage
    memory_warning: float = 80.0  # percentage
    disk_warning: float = 85.0  # percentage
    temp_warning: int = 2048  # MB


@dataclass
class OptimizationConfig:
    """Optimization configuration"""
    auto_optimize: bool = True
    clean_temp_files: bool = True
    clean_logs: bool = True
    optimize_startup: bool = True
    defrag_drives: bool = False
    max_temp_file_age: int = 7  # days


@dataclass
class SecurityConfig:
    """Security configuration"""
    check_updates: bool = True
    check_vulnerabilities: bool = True
    require_authentication: bool = False
    api_key: str = ""


@dataclass
class NotificationConfig:
    """Notification configuration"""
    enabled: bool = True
    email_alerts: bool = False
    email_recipients: list = field(default_factory=list)
    desktop_alerts: bool = True
    log_alerts: bool = True


@dataclass
class PredictiveAnalysisConfig:
    """Predictive analysis configuration"""
    enabled: bool = True
    model_path: str = "models/predictive_model.pkl"
    confidence_threshold: float = 0.7
    training_interval: int = 86400  # seconds (1 day)
    max_training_samples: int = 10000


@dataclass
class APIConfig:
    """API configuration"""
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = field(default_factory=lambda: ["*"])
    api_key_required: bool = True


class Config:
    """Main configuration class for AI Workbench"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration with optional dictionary
        
        Args:
            config_dict: Optional dictionary with configuration values
        """
        # Set defaults
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.monitoring = MonitoringConfig()
        self.optimization = OptimizationConfig()
        self.security = SecurityConfig()
        self.notifications = NotificationConfig()
        self.predictive_analysis = PredictiveAnalysisConfig()
        self.api = APIConfig()
        
        # Update with provided config
        if config_dict:
            self.update(config_dict)
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary
        
        Args:
            config_dict: Dictionary with configuration values
        """
        for section, values in config_dict.items():
            section_obj = getattr(self, section, None)
            if section_obj and isinstance(values, dict):
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary
        
        Returns:
            Dictionary with all configuration values
        """
        config_dict = {}
        for section in [
            'app', 'database', 'monitoring', 'optimization',
            'security', 'notifications', 'predictive_analysis', 'api'
        ]:
            section_obj = getattr(self, section, None)
            if section_obj:
                config_dict[section] = asdict(section_obj)
        return config_dict
    
    def save(self, file_path: Union[str, Path]) -> bool:
        """
        Save configuration to a JSON file
        
        Args:
            file_path: Path to save the configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            return False
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> 'Config':
        """
        Load configuration from a JSON file
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Config: Loaded configuration instance
        """
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls(config_dict)
        except FileNotFoundError:
            logger.warning(f"Configuration file {file_path} not found, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file {file_path}: {e}")
            return cls()
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            return cls()


def get_default_config_path() -> Path:
    """
    Get the default configuration file path
    
    Returns:
        Path: Path to the default configuration file
    """
    # Try to use XDG config directory if available
    if os.name == 'posix' and 'XDG_CONFIG_HOME' in os.environ:
        config_dir = Path(os.environ['XDG_CONFIG_HOME']) / 'ai_workbench'
    elif os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / 'AI Workbench'
    else:  # Fallback for other OS
        config_dir = Path.home() / '.config' / 'ai_workbench'
    
    # Ensure directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir / 'config.json'


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """
    Load configuration from file or use defaults
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config: Loaded configuration
    """
    # Use default path if none provided
    if config_path is None:
        config_path = get_default_config_path()
    
    # Load or create config
    config = Config.load(config_path)
    
    # Save default config if file didn't exist
    if not os.path.exists(config_path):
        config.save(config_path)
        logger.info(f"Created default configuration at {config_path}")
    
    return config


# Global configuration instance
config = load_config()

# Update environment variables if needed
if 'LOG_LEVEL' in os.environ:
    config.app.log_level = os.environ['LOG_LEVEL']

if 'DATABASE_URL' in os.environ:
    config.database.url = os.environ['DATABASE_URL']

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.app.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.app.log_file) if config.app.log_file else logging.NullHandler()
    ]
)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Log configuration loaded
logger.info(f"{config.app.name} v{config.app.version} - Configuration loaded")
