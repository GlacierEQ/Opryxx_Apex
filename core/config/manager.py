"""
Unified Configuration Management System
Handles configuration loading, validation, and hot-reloading
"""

import os
import yaml
import json
import toml
from typing import Any, Dict, Optional, Type, TypeVar, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import threading
from typing import List, Callable
from pydantic import BaseModel, ValidationError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    YAML = 'yaml'
    JSON = 'json'
    TOML = 'toml'
    ENV = 'env'

@dataclass
class ConfigSource:
    """Represents a configuration source (file, env vars, etc.)"""
    path: str
    format: ConfigFormat
    required: bool = True
    watch: bool = False
    env_prefix: Optional[str] = None

class ConfigUpdateEvent:
    """Event fired when configuration is updated"""
    def __init__(self, source: str, data: dict):
        self.source = source
        self.data = data
        self.timestamp = time.time()

class ConfigUpdateHandler(FileSystemEventHandler):
    """Handles file system events for config files"""
    def __init__(self, callback: Callable[[ConfigUpdateEvent], None], source: str):
        self.callback = callback
        self.source = source
        self.last_update = 0
        
    def on_modified(self, event):
        if not event.is_directory and time.time() - self.last_update > 1.0:  # Debounce
            self.last_update = time.time()
            logger.info(f"Config file modified: {event.src_path}")
            self.callback(ConfigUpdateEvent(self.source, {event.src_path: "modified"}))

class ConfigManager:
    """
    Centralized configuration management with hot-reloading support.
    
    Features:
    - Multiple config formats (YAML, JSON, TOML, ENV)
    - Environment variable overrides
    - Hot-reloading of config files
    - Schema validation
    - Type conversion and defaults
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config = {}
            self._sources: List[ConfigSource] = []
            self._observers = []
            self._watch_dog = None
            self._lock = threading.RLock()
            self._subscribers = []
            self._initialized = True
            
            # Start file watcher in a daemon thread
            self._start_watcher()
    
    def _start_watcher(self):
        """Start the file system watcher"""
        if self._watch_dog is None:
            self._watch_dog = Observer()
            self._watch_dog.daemon = True
            self._watch_dog.start()
    
    def add_source(self, source: Union[str, ConfigSource], **kwargs) -> bool:
        """
        Add a configuration source
        
        Args:
            source: Path to config file or ConfigSource instance
            **kwargs: Additional arguments for ConfigSource
            
        Returns:
            bool: True if source was added successfully
        """
        if not isinstance(source, ConfigSource):
            source = ConfigSource(path=source, **kwargs)
        
        try:
            # Load the config first to validate
            config_data = self._load_config(source)
            if config_data is not None:
                with self._lock:
                    self._sources.append(source)
                    self._config.update(config_data)
                    
                    # Set up file watcher if requested
                    if source.watch and os.path.isfile(source.path):
                        handler = ConfigUpdateHandler(self._on_config_updated, source.path)
                        self._watch_dog.schedule(handler, os.path.dirname(source.path), recursive=False)
                        self._observers.append(handler)
                
                logger.info(f"Added config source: {source.path}")
                return True
                
        except Exception as e:
            if source.required:
                raise RuntimeError(f"Failed to load required config: {source.path}") from e
            logger.warning(f"Skipping optional config: {source.path} - {str(e)}")
            
        return False
    
    def _load_config(self, source: ConfigSource) -> Optional[dict]:
        """Load configuration from a source"""
        if not os.path.exists(source.path):
            if source.required:
                raise FileNotFoundError(f"Config file not found: {source.path}")
            return None
            
        try:
            with open(source.path, 'r', encoding='utf-8') as f:
                if source.format == ConfigFormat.YAML:
                    config = yaml.safe_load(f) or {}
                elif source.format == ConfigFormat.JSON:
                    config = json.load(f)
                elif source.format == ConfigFormat.TOML:
                    config = toml.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {source.format}")
                
                # Apply environment variable overrides if prefix is set
                if source.env_prefix:
                    config = self._apply_env_overrides(config, source.env_prefix)
                    
                return config
                
        except Exception as e:
            logger.error(f"Error loading config {source.path}: {str(e)}")
            if source.required:
                raise
            return None
    
    def _apply_env_overrides(self, config: dict, prefix: str) -> dict:
        """Apply environment variable overrides to config"""
        prefix = prefix.upper()
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert ENV_VAR to config.key.path
                path = key[len(prefix):].lower().split('__')
                current = config
                
                # Navigate to the correct nested dict
                for part in path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value with type conversion
                if path[-1] in current:
                    target_type = type(current[path[-1]])
                    try:
                        if target_type == bool:
                            current[path[-1]] = value.lower() in ('true', '1', 'yes')
                        elif target_type == int:
                            current[path[-1]] = int(value)
                        elif target_type == float:
                            current[path[-1]] = float(value)
                        else:
                            current[path[-1]] = value
                    except (ValueError, TypeError):
                        current[path[-1]] = value
                        
        return config
    
    def _on_config_updated(self, event: ConfigUpdateEvent):
        """Handle configuration file updates"""
        logger.info(f"Configuration updated: {event.source}")
        try:
            # Find the source that was updated
            for source in self._sources:
                if source.path == event.source or source.path in event.source:
                    # Reload the config
                    config_data = self._load_config(source)
                    if config_data is not None:
                        with self._lock:
                            # Update only the changed parts
                            self._config.update(config_data)
                            
                        # Notify subscribers
                        for callback in self._subscribers:
                            try:
                                callback(ConfigUpdateEvent(source.path, config_data))
                            except Exception as e:
                                logger.error(f"Error in config update callback: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling config update: {str(e)}")
    
    def subscribe(self, callback: Callable[[ConfigUpdateEvent], None]):
        """Subscribe to configuration updates"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[ConfigUpdateEvent], None]):
        """Unsubscribe from configuration updates"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot notation"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def __getitem__(self, key: str) -> Any:
        """Get a configuration value by dot notation"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError) as e:
            raise KeyError(f"Config key not found: {key}") from e
    
    def get_section(self, section: str) -> dict:
        """Get a configuration section as a dictionary"""
        try:
            return self[section]
        except KeyError:
            return {}
    
    def to_dict(self) -> dict:
        """Return the entire configuration as a dictionary"""
        with self._lock:
            return self._config.copy()
    
    def validate(self, schema: Type[BaseModel]) -> bool:
        """Validate the current configuration against a Pydantic schema"""
        try:
            schema(**self._config)
            return True
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    def reload(self) -> bool:
        """Reload all configuration sources"""
        success = True
        with self._lock:
            for source in self._sources:
                try:
                    config_data = self._load_config(source)
                    if config_data is not None:
                        self._config.update(config_data)
                except Exception as e:
                    logger.error(f"Failed to reload config {source.path}: {str(e)}")
                    success = False
        return success
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, '_watch_dog') and self._watch_dog is not None:
            self._watch_dog.stop()
            self._watch_dog.join()

# Global instance for easy access
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config
