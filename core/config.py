"""
Configuration Management
Centralized configuration for all OPRYXX components
"""

import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'performance': {
                'update_interval': 5.0,
                'max_history': 1000
            },
            'memory': {
                'optimization_level': 'MODERATE',
                'auto_optimize': True
            },
            'gpu': {
                'enable_acceleration': True,
                'fallback_to_cpu': True
            }
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

config_manager = ConfigManager()