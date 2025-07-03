"""
Configuration management for OPRYXX
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import threading

@dataclass
class SystemConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_threads: int = 4
    timeout: int = 300
    backup_enabled: bool = True
    
@dataclass
class RecoveryConfig:
    auto_backup: bool = True
    verify_operations: bool = True
    max_retries: int = 3
    
@dataclass
class AIConfig:
    gpu_enabled: bool = True
    npu_enabled: bool = True
    model_path: str = ""
    optimization_level: int = 2

class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self._lock = threading.Lock()
        self.config_file = config_file or "opryxx_config.json"
        self.system = SystemConfig()
        self.recovery = RecoveryConfig()
        self.ai = AIConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update configurations
                if 'system' in data:
                    self.system = SystemConfig(**data['system'])
                if 'recovery' in data:
                    self.recovery = RecoveryConfig(**data['recovery'])
                if 'ai' in data:
                    self.ai = AIConfig(**data['ai'])
                    
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        with self._lock:
            try:
                config_data = {
                    'system': asdict(self.system),
                    'recovery': asdict(self.recovery),
                    'ai': asdict(self.ai)
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                    
            except Exception as e:
                print(f"Error saving config: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        section_obj = getattr(self, section, None)
        if section_obj:
            return getattr(section_obj, key, default)
        return default
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        with self._lock:
            section_obj = getattr(self, section, None)
            if section_obj:
                setattr(section_obj, key, value)
                self.save_config()

# Global config instance
_config_instance = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

# Legacy compatibility
class ConfigManager:
    def __init__(self):
        self.config = get_config()
    
    def get(self, key: str, default=None):
        parts = key.split('.')
        if len(parts) == 2:
            return self.config.get(parts[0], parts[1], default)
        return default

config_manager = ConfigManager()