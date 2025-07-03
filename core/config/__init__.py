"""
OPRYXX Configuration Package

This package provides a unified configuration management system for the OPRYXX platform.

Features:
- Multiple config formats (YAML, JSON, TOML, ENV)
- Environment variable overrides
- Hot-reloading of config files
- Schema validation
- Type conversion and defaults
"""

from .manager import ConfigManager, ConfigSource, ConfigFormat, config, get_config

__all__ = [
    'ConfigManager',
    'ConfigSource',
    'ConfigFormat',
    'config',
    'get_config',
]
