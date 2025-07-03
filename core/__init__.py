"""
OPRYXX Core Module
Unified system architecture with best practices
"""

__version__ = "1.0.0"
__author__ = "OPRYXX Team"

from .base import BaseModule, ModuleRegistry
from .config import ConfigManager, ConfigSource, ConfigFormat, config, get_config
from .logger import Logger
from .exceptions import OPRYXXException

__all__ = [
    'BaseModule', 
    'ModuleRegistry', 
    'ConfigManager', 
    'ConfigSource', 
    'ConfigFormat', 
    'config', 
    'get_config',
    'Logger', 
    'OPRYXXException'
]