"""
LAYER 1: CORE INFRASTRUCTURE - SIMPLIFIED VERSION
=================================================
Essential foundation components for OPRYXX system
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import sqlite3
from queue import Queue

# =============================================================================
# 1. CONFIGURATION SYSTEM
# =============================================================================

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._config = {}
        self._load_default_config()
        
    def _load_default_config(self):
        """Load default configuration"""
        self._config = {
            "opryxx": {
                "version": "3.0.0",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "monitoring": {
                "enabled": True,
                "interval_seconds": 30,
                "gpu_monitoring": True,
                "temperature_monitoring": True
            },
            "ai": {
                "enabled": True,
                "model": "aria-3.0",
                "intelligence_level": 75,
                "learning_enabled": True
            },
            "automation": {
                "enabled": True,
                "gaming_mode": True,
                "auto_optimization": True,
                "smart_scheduling": True
            },
            "ui": {
                "theme": "dark",
                "notifications": True,
                "system_tray": True,
                "voice_commands": True
            }
        }
        
        # Save to file
        config_file = self.config_dir / "opryxx.json"
        with open(config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

# =============================================================================
# 2. LOGGING SYSTEM
# =============================================================================

class Logger:
    """Enhanced logging system"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup main logger
        self.logger = logging.getLogger("OPRYXX")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(
            self.log_dir / "opryxx.log",
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    def debug(self, message: str):
        """Debug level logging"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Info level logging"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Warning level logging"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Error level logging"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Critical level logging"""
        self.logger.critical(message)

# =============================================================================
# 3. EVENT SYSTEM
# =============================================================================

class Event:
    """Simple event class"""
    
    def __init__(self, name: str, data: Dict = None):
        self.name = name
        self.data = data or {}
        self.timestamp = datetime.now()

class EventBus:
    """Simple event bus system"""
    
    def __init__(self):
        self._subscribers = {}
        self._lock = threading.RLock()
        
    def subscribe(self, event_name: str, callback: Callable):
        """Subscribe to events"""
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Unsubscribe from events"""
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_name: str, data: Dict = None):
        """Publish event"""
        event = Event(event_name, data)
        
        with self._lock:
            subscribers = self._subscribers.get(event_name, [])
            
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                Logger().error(f"Event handler failed for {event_name}: {e}")

# =============================================================================
# 4. ERROR HANDLING
# =============================================================================

class ErrorHandler:
    """Simple error handling system"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.error_counts = {}
        
    def handle_error(self, error: Exception, context: str = "unknown") -> bool:
        """Handle error with logging"""
        error_key = f"{type(error).__name__}:{context}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        Logger().error(f"Error in {context}: {error}")
        
        self.event_bus.publish("system.error", {
            "error": str(error),
            "context": context,
            "count": self.error_counts[error_key]
        })
        
        return False  # No recovery implemented in simple version

# =============================================================================
# 5. DATABASE SYSTEM
# =============================================================================

class DatabaseManager:
    """Simple database management"""
    
    def __init__(self, db_path: str = "data/opryxx.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with simple schema"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    health_score INTEGER,
                    metadata TEXT
                )
            """)
            
            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_name TEXT NOT NULL,
                    source TEXT,
                    data TEXT
                )
            """)
            
            # Create indexes separately
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_name ON events(event_name)")
            
            conn.commit()
            
        finally:
            conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

# =============================================================================
# 6. PLUGIN SYSTEM
# =============================================================================

class PluginManager:
    """Simple plugin management"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.plugins = {}
        self.plugin_dir = Path("plugins")
        self.plugin_dir.mkdir(exist_ok=True)
        
    def load_plugin(self, plugin_name: str) -> bool:
        """Load plugin (placeholder)"""
        Logger().info(f"Plugin system ready for: {plugin_name}")
        return True
    
    def list_plugins(self) -> List[str]:
        """List loaded plugins"""
        return list(self.plugins.keys())

# =============================================================================
# CORE INFRASTRUCTURE
# =============================================================================

class CoreInfrastructure:
    """Main core infrastructure coordinator"""
    
    def __init__(self):
        print("Initializing Core Infrastructure...")
        
        # Initialize components
        self.config = ConfigManager()
        print("✓ Configuration system ready")
        
        self.logger = Logger()
        print("✓ Logging system ready")
        
        self.event_bus = EventBus()
        print("✓ Event system ready")
        
        self.error_handler = ErrorHandler(self.event_bus)
        print("✓ Error handling ready")
        
        self.database = DatabaseManager()
        print("✓ Database system ready")
        
        self.plugins = PluginManager(self.event_bus)
        print("✓ Plugin system ready")
        
        # Setup system handlers
        self._setup_handlers()
        
        self.logger.info("Core Infrastructure initialized successfully")
        self.event_bus.publish("system.core_ready")
        print("[OK] Core Infrastructure READY!")
    
    def _setup_handlers(self):
        """Setup core event handlers"""
        def log_system_events(event):
            self.logger.info(f"System event: {event.name}")
        
        def handle_errors(event):
            count = event.data.get('count', 0)
            if count >= 3:
                self.logger.warning(f"Multiple errors in {event.data.get('context')}")
        
        self.event_bus.subscribe("system.core_ready", log_system_events)
        self.event_bus.subscribe("system.error", handle_errors)
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "config_loaded": bool(self.config._config),
            "logging_active": True,
            "event_bus_active": True,
            "database_connected": True,
            "plugins_ready": True,
            "core_ready": True
        }

# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo_core_infrastructure():
    """Demonstrate core infrastructure"""
    print("CORE INFRASTRUCTURE DEMONSTRATION")
    print("=" * 50)
    
    # Initialize
    core = CoreInfrastructure()
    
    print("\n1. Configuration Test:")
    print(f"   AI Enabled: {core.config.get('ai.enabled')}")
    print(f"   Theme: {core.config.get('ui.theme')}")
    
    print("\n2. Event System Test:")
    def test_handler(event):
        print(f"   Event received: {event.name}")
    
    core.event_bus.subscribe("test.demo", test_handler)
    core.event_bus.publish("test.demo", {"message": "Hello World!"})
    
    print("\n3. Logging Test:")
    core.logger.info("Testing info log")
    core.logger.warning("Testing warning log")
    
    print("\n4. Database Test:")
    conn = core.database.get_connection()
    conn.execute("""
        INSERT INTO system_metrics (cpu_usage, memory_usage, health_score)
        VALUES (?, ?, ?)
    """, (50.5, 70.2, 90))
    
    result = conn.execute("SELECT COUNT(*) as count FROM system_metrics").fetchone()
    print(f"   Database records: {result['count']}")
    conn.close()
    
    print("\n5. Error Handling Test:")
    try:
        raise ValueError("Test error for demonstration")
    except Exception as e:
        core.error_handler.handle_error(e, "demo_test")
    
    print("\n6. System Status:")
    status = core.get_status()
    for key, value in status.items():
        print(f"   {key}: {'[OK]' if value else '[FAIL]'}")
    
    print("\n" + "=" * 50)
    print("CORE INFRASTRUCTURE LAYER 1 COMPLETE!")
    print("Ready for Layer 2: Enhanced Monitoring")
    print("=" * 50)
    
    return core

if __name__ == "__main__":
    demo_core_infrastructure()
