"""
Configuration Management
Centralized configuration with validation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union
import json
import os
from pathlib import Path

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MSSQL = "mssql"

@dataclass
class SystemConfig:
    version: str = "2.0"
    log_level: str = "INFO"
    max_log_files: int = 10
    backup_retention_days: int = 30
    
@dataclass
class GANDALFConfig:
    version: str = "Windows 11 PE x64 Redstone 9 Spring 2025"
    pe_path: str = "X:\\"
    tools_path: str = "X:\\Windows\\System32"
    
@dataclass
class DatabaseConfig:
    type: DatabaseType = DatabaseType.SQLITE
    host: str = "localhost"
    port: Optional[int] = None
    name: str = "opryxx"
    user: Optional[str] = None
    password: Optional[str] = None
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    
    @property
    def url(self) -> str:
        """Generate SQLAlchemy connection URL"""
        if self.type == DatabaseType.SQLITE:
            db_path = Path("data") / f"{self.name}.db"
            return f"sqlite:///{db_path}"
        
        if not all([self.host, self.name, self.user, self.password]):
            raise ValueError(f"Missing required database configuration for {self.type}")
            
        return f"{self.type}://{self.user}:{self.password}@{self.host}:{self.port or 5432}/{self.name}"

@dataclass
class RecoveryConfig:
    max_attempts: int = 3
    timeout_seconds: int = 300
    safe_mode_priority: bool = True
    auto_reboot: bool = False

@dataclass
class OPRYXXConfig:
    system: SystemConfig = field(default_factory=SystemConfig)
    gandalf: GANDALFConfig = field(default_factory=GANDALFConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

class ConfigManager:
    def __init__(self, config_path: str = "opryxx_config.json"):
        self.config_path = config_path
        self._config: Optional[OPRYXXConfig] = None
    
    @property
    def config(self) -> OPRYXXConfig:
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> OPRYXXConfig:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                # Create a new config with defaults
                config = OPRYXXConfig()
                # Update only the fields that exist in the config file
                for key, value in data.items():
                    if hasattr(config, key):
                        if isinstance(value, dict):
                            # Handle nested dataclasses
                            attr = getattr(config, key)
                            if hasattr(attr, '__dataclass_fields__'):
                                for sub_key, sub_value in value.items():
                                    if hasattr(attr, sub_key):
                                        setattr(attr, sub_key, sub_value)
                            else:
                                setattr(config, key, value)
                        else:
                            setattr(config, key, value)
                return config
        return OPRYXXConfig()
    
    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)