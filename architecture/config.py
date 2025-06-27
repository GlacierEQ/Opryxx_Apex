"""
Configuration Management
Centralized configuration with validation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os

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
                return OPRYXXConfig(**data)
        return OPRYXXConfig()
    
    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)