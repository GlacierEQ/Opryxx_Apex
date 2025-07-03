"""
OPRYXX Configuration Module

This module provides a unified configuration management system for OPRYXX.

It includes:
- ConfigManager: Centralized configuration management with hot-reloading
- ConfigSource: Represents a configuration source (file, env vars, etc.)
- ConfigFormat: Enum of supported configuration formats (YAML, JSON, TOML, ENV)
"""

from .manager import (
    ConfigManager,
    ConfigSource,
    ConfigFormat,
    config,
    get_config
)

__all__ = [
    'ConfigManager',
    'ConfigSource',
    'ConfigFormat',
    'config',
    'get_config'
]