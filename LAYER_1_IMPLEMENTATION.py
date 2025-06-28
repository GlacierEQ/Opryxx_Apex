"""
LAYER 1: CORE INFRASTRUCTURE IMPLEMENTATION
==========================================
The foundation layer that everything else builds upon.
No shortcuts - build it right the first time!
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from queue import Queue
import configparser
import importlib.util

# Try to import yaml, create fallback if not available
try:
    import yaml
except ImportError:
    class yaml:
        @staticmethod
        def safe_load(f):
            return json.load(f)
        @staticmethod
        def dump(data, f, **kwargs):
            json.dump(data, f, indent=2)

# =============================================================================
# 1. ENHANCED CONFIGURATION SYSTEM
# =============================================================================

class ConfigManager:
    """Enhanced configuration management with validation and hot-reload"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._config = {}
        self._validators = {}
        self._watchers = []
        self._lock = threading.RLock()
        
    def load_config(self, filename: str = "opryxx.yaml") -> Dict:
        """Load configuration from file with validation"""
        config_path = self.config_dir / filename
        
        try:
            if config_path.suffix.lower() == '.yaml':
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                # Try to load as INI
                parser = configparser.ConfigParser()
                parser.read(config_path)
                config = {section: dict(parser[section]) for section in parser.sections()}
                
            # Validate configuration
            self._validate_config(config)
            
            with self._lock:
                self._config.update(config)
                
            self.log_config_load(filename, len(config))
            return config
            
        except Exception as e:
            self._create_default_config(config_path)
            return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        
        # Validate
        self._validate_config(self._config)
        
        # Notify watchers
        self._notify_watchers(key, value)
    
    def watch(self, key_pattern: str, callback: Callable) -> None:
        """Watch for configuration changes"""
        self._watchers.append((key_pattern, callback))
    
    def _validate_config(self, config: Dict) -> None:
        """Validate configuration against registered validators"""
        for key, validator in self._validators.items():
            try:
                value = self.get(key)
                if value is not None and not validator(value):
                    raise ValueError(f"Invalid value for {key}: {value}")
            except Exception as e:
                Logger().warning(f"Config validation failed for {key}: {e}")
    
    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify configuration watchers"""
        for pattern, callback in self._watchers:
            if pattern in key or pattern == "*":
                try:
                    callback(key, value)
                except Exception as e:
                    Logger().error(f"Config watcher failed: {e}")
    
    def _create_default_config(self, config_path: Path) -> None:
        """Create default configuration file"""
        default_config = {
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
        
        self._config = default_config
        
        # Save to file
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        Logger().info(f"Created default config: {config_path}")
    
    def log_config_load(self, filename: str, count: int) -> None:
        """Log configuration loading"""
        Logger().info(f"Loaded config {filename}: {count} settings")

# =============================================================================
# 2. ROBUST LOGGING FRAMEWORK
# =============================================================================

class Logger:
    """Enhanced logging system with structured logging and performance metrics"""
    
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
        if self._initialized:
            return
            
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        
        # Setup loggers
        self._setup_main_logger()
        self._setup_performance_logger()
        self._setup_security_logger()
        
        self._initialized = True
    
    def _setup_main_logger(self):
        """Setup main application logger"""
        self.main_logger = logging.getLogger("OPRYXX")
        self.main_logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        main_handler = logging.FileHandler(
            self.log_dir / "opryxx.log",
            encoding='utf-8'
        )
        main_handler.setFormatter(self.detailed_formatter)
        main_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.simple_formatter)
        console_handler.setLevel(logging.INFO)
        
        self.main_logger.addHandler(main_handler)
        self.main_logger.addHandler(console_handler)
    
    def _setup_performance_logger(self):
        """Setup performance metrics logger"""
        self.perf_logger = logging.getLogger("OPRYXX.Performance")
        self.perf_logger.setLevel(logging.INFO)
        
        perf_handler = logging.FileHandler(
            self.log_dir / "performance.log",
            encoding='utf-8'
        )
        perf_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(message)s'
        ))
        
        self.perf_logger.addHandler(perf_handler)
    
    def _setup_security_logger(self):
        """Setup security events logger"""
        self.security_logger = logging.getLogger("OPRYXX.Security")
        self.security_logger.setLevel(logging.WARNING)
        
        security_handler = logging.FileHandler(
            self.log_dir / "security.log",
            encoding='utf-8'
        )
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s | SECURITY | %(levelname)s | %(message)s'
        ))
        
        self.security_logger.addHandler(security_handler)
    
    def debug(self, message: str, extra: Dict = None):
        """Debug level logging"""
        self.main_logger.debug(self._format_message(message, extra))
    
    def info(self, message: str, extra: Dict = None):
        """Info level logging"""
        self.main_logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Dict = None):
        """Warning level logging"""
        self.main_logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Dict = None):
        """Error level logging"""
        self.main_logger.error(self._format_message(message, extra))
    
    def critical(self, message: str, extra: Dict = None):
        """Critical level logging"""
        self.main_logger.critical(self._format_message(message, extra))
    
    def performance(self, operation: str, duration: float, extra: Dict = None):
        """Log performance metrics"""
        metrics = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        if extra:
            metrics.update(extra)
        
        self.perf_logger.info(json.dumps(metrics))
    
    def security(self, event: str, level: str = "WARNING", extra: Dict = None):
        """Log security events"""
        message = self._format_message(f"SECURITY EVENT: {event}", extra)
        
        if level.upper() == "WARNING":
            self.security_logger.warning(message)
        elif level.upper() == "ERROR":
            self.security_logger.error(message)
        elif level.upper() == "CRITICAL":
            self.security_logger.critical(message)
    
    def _format_message(self, message: str, extra: Dict = None) -> str:
        """Format log message with extra data"""
        if extra:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
            return f"{message} | {extra_str}"
        return message

# =============================================================================
# 3. EVENT SYSTEM (Observer Pattern)
# =============================================================================

@dataclass
class Event:
    """Event data structure"""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: int = 0  # Higher = more important

class EventBus:
    """Central event bus using Observer pattern"""
    
    def __init__(self):
        self._subscribers = {}
        self._event_queue = Queue()
        self._processing = False
        self._lock = threading.RLock()
        self._filters = []
        
    def subscribe(self, event_name: str, callback: Callable, priority: int = 0):
        """Subscribe to events"""
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            self._subscribers[event_name].append({
                'callback': callback,
                'priority': priority
            })
            
            # Sort by priority (higher first)
            self._subscribers[event_name].sort(
                key=lambda x: x['priority'], 
                reverse=True
            )
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Unsubscribe from events"""
        with self._lock:
            if event_name in self._subscribers:
                self._subscribers[event_name] = [
                    sub for sub in self._subscribers[event_name]
                    if sub['callback'] != callback
                ]
    
    def publish(self, event_name: str, data: Dict = None, source: str = "unknown"):
        """Publish event to subscribers"""
        event = Event(
            name=event_name,
            data=data or {},
            timestamp=datetime.now(),
            source=source
        )
        
        # Apply filters
        if not self._should_process_event(event):
            return
        
        # Add to queue for async processing
        self._event_queue.put(event)
        
        # Start processing if not already running
        if not self._processing:
            threading.Thread(target=self._process_events, daemon=True).start()
    
    def _process_events(self):
        """Process events from queue"""
        self._processing = True
        
        try:
            while not self._event_queue.empty():
                event = self._event_queue.get()
                self._handle_event(event)
        finally:
            self._processing = False
    
    def _handle_event(self, event: Event):
        """Handle individual event"""
        with self._lock:
            subscribers = self._subscribers.get(event.name, [])
            
        for subscriber in subscribers:
            try:
                subscriber['callback'](event)
            except Exception as e:
                Logger().error(f"Event handler failed for {event.name}: {e}")
    
    def add_filter(self, filter_func: Callable[[Event], bool]):
        """Add event filter"""
        self._filters.append(filter_func)
    
    def _should_process_event(self, event: Event) -> bool:
        """Check if event should be processed"""
        for filter_func in self._filters:
            try:
                if not filter_func(event):
                    return False
            except Exception as e:
                Logger().warning(f"Event filter failed: {e}")
        return True

# =============================================================================
# 4. ERROR HANDLING & RECOVERY
# =============================================================================

class ErrorHandler:
    """Global error handling and recovery system"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.recovery_strategies = {}
        self.error_counts = {}
        self.max_retries = 3
        
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """Register recovery strategy for error type"""
        self.recovery_strategies[error_type] = strategy
    
    def handle_error(self, error: Exception, context: str = "unknown") -> bool:
        """Handle error with recovery attempts"""
        error_type = type(error)
        error_key = f"{error_type.__name__}:{context}"
        
        # Track error count
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error
        Logger().error(f"Error in {context}: {error}", {
            "error_type": error_type.__name__,
            "count": self.error_counts[error_key]
        })
        
        # Publish error event
        self.event_bus.publish("system.error", {
            "error": str(error),
            "error_type": error_type.__name__,
            "context": context,
            "count": self.error_counts[error_key]
        })
        
        # Try recovery if available and within retry limit
        if (error_type in self.recovery_strategies and 
            self.error_counts[error_key] <= self.max_retries):
            
            try:
                recovery_strategy = self.recovery_strategies[error_type]
                success = recovery_strategy(error, context)
                
                if success:
                    Logger().info(f"Recovered from error in {context}")
                    self.event_bus.publish("system.recovery_success", {
                        "context": context,
                        "error_type": error_type.__name__
                    })
                    return True
                    
            except Exception as recovery_error:
                Logger().error(f"Recovery failed: {recovery_error}")
        
        # Recovery failed or no strategy available
        return False

# =============================================================================
# 5. DATABASE SCHEMA OPTIMIZATION
# =============================================================================

class DatabaseManager:
    """Optimized database management with connection pooling"""
    
    def __init__(self, db_path: str = "data/opryxx.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._connection_pool = Queue(maxsize=5)
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        self._create_indexes()
    
    def _init_database(self):
        """Initialize database with optimized schema"""
        with self.get_connection() as conn:
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    gpu_usage REAL,
                    temperature REAL,
                    health_score INTEGER,
                    metadata TEXT,
                    INDEX(timestamp),
                    INDEX(health_score)
                )
            """)
            
            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_name TEXT NOT NULL,
                    source TEXT,
                    data TEXT,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Configuration history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    config_key TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT
                )
            """)
            
            conn.commit()
    
    def _create_indexes(self):
        """Create performance indexes"""
        with self.get_connection() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_health ON system_metrics(health_score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_events_name_time ON events(event_name, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_config_key_time ON config_history(config_key, timestamp DESC)"
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
            
            conn.commit()
    
    def get_connection(self):
        """Get database connection from pool"""
        try:
            return self._connection_pool.get_nowait()
        except:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        try:
            self._connection_pool.put_nowait(conn)
        except:
            # Pool is full, close connection
            conn.close()

# =============================================================================
# 6. PLUGIN ARCHITECTURE
# =============================================================================

class PluginManager:
    """Dynamic plugin loading and management system"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.plugins = {}
        self.plugin_dir = Path("plugins")
        self.plugin_dir.mkdir(exist_ok=True)
        
    def load_plugin(self, plugin_name: str) -> bool:
        """Load plugin dynamically"""
        try:
            plugin_path = self.plugin_dir / f"{plugin_name}.py"
            
            if not plugin_path.exists():
                Logger().warning(f"Plugin not found: {plugin_name}")
                return False
            
            # Dynamic import
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class
            plugin_class = getattr(module, f"{plugin_name.title()}Plugin")
            plugin_instance = plugin_class(self.event_bus)
            
            # Initialize plugin
            if hasattr(plugin_instance, 'initialize'):
                plugin_instance.initialize()
            
            self.plugins[plugin_name] = plugin_instance
            
            Logger().info(f"Loaded plugin: {plugin_name}")
            self.event_bus.publish("plugin.loaded", {"name": plugin_name})
            
            return True
            
        except Exception as e:
            Logger().error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Cleanup plugin
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
            
            del self.plugins[plugin_name]
            
            Logger().info(f"Unloaded plugin: {plugin_name}")
            self.event_bus.publish("plugin.unloaded", {"name": plugin_name})
            
            return True
            
        except Exception as e:
            Logger().error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str):
        """Get loaded plugin instance"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return list(self.plugins.keys())

# =============================================================================
# CORE INFRASTRUCTURE MAIN CLASS
# =============================================================================

class CoreInfrastructure:
    """Main core infrastructure coordinator"""
    
    def __init__(self):
        # Initialize components in order
        self.config = ConfigManager()
        self.logger = Logger()
        self.event_bus = EventBus()
        self.error_handler = ErrorHandler(self.event_bus)
        self.database = DatabaseManager()
        self.plugins = PluginManager(self.event_bus)
        
        # Setup system event handlers
        self._setup_system_handlers()
        
        self.logger.info("Core Infrastructure initialized successfully")
        self.event_bus.publish("system.core_ready")
    
    def _setup_system_handlers(self):
        """Setup core system event handlers"""
        # Log all system events
        self.event_bus.subscribe("system.*", self._log_system_event)
        
        # Handle configuration changes
        self.event_bus.subscribe("config.changed", self._handle_config_change)
        
        # Handle critical errors
        self.event_bus.subscribe("system.error", self._handle_critical_error)
    
    def _log_system_event(self, event: Event):
        """Log system events"""
        self.logger.info(f"System event: {event.name}", event.data)
    
    def _handle_config_change(self, event: Event):
        """Handle configuration changes"""
        key = event.data.get('key')
        value = event.data.get('value')
        self.logger.info(f"Configuration changed: {key} = {value}")
    
    def _handle_critical_error(self, event: Event):
        """Handle critical system errors"""
        error_count = event.data.get('count', 0)
        
        if error_count >= 3:
            self.logger.critical("Multiple critical errors detected - system may be unstable")
            self.event_bus.publish("system.stability_warning", {
                "reason": "Multiple critical errors",
                "count": error_count
            })
    
    def shutdown(self):
        """Graceful shutdown of core infrastructure"""
        self.logger.info("Shutting down core infrastructure...")
        
        # Cleanup plugins
        for plugin_name in list(self.plugins.list_plugins()):
            self.plugins.unload_plugin(plugin_name)
        
        # Final event
        self.event_bus.publish("system.shutdown")
        
        self.logger.info("Core infrastructure shutdown complete")

# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================

def demo_core_infrastructure():
    """Demonstrate core infrastructure capabilities"""
    print("CORE INFRASTRUCTURE DEMONSTRATION")
    print("=" * 50)
    
    # Initialize core infrastructure
    core = CoreInfrastructure()
    
    print("1. Configuration Management:")
    print(f"   AI Enabled: {core.config.get('ai.enabled')}")
    print(f"   Log Level: {core.config.get('opryxx.log_level')}")
    
    print("\n2. Event System:")
    # Subscribe to test events
    def test_handler(event):
        print(f"   Received event: {event.name} with data: {event.data}")
    
    core.event_bus.subscribe("test.demo", test_handler)
    core.event_bus.publish("test.demo", {"message": "Hello from event system!"})
    
    print("\n3. Logging System:")
    core.logger.info("This is an info message")
    core.logger.warning("This is a warning message")
    core.logger.performance("test_operation", 0.05, {"items_processed": 100})
    
    print("\n4. Error Handling:")
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        core.error_handler.handle_error(e, "demo_context")
    
    print("\n5. Database Operations:")
    with core.database.get_connection() as conn:
        conn.execute("""
            INSERT INTO system_metrics (cpu_usage, memory_usage, health_score)
            VALUES (?, ?, ?)
        """, (45.2, 60.5, 85))
        
        result = conn.execute("""
            SELECT COUNT(*) as count FROM system_metrics
        """).fetchone()
        
        print(f"   Database records: {result['count']}")
    
    print("\nCore Infrastructure is ready!")
    print("All foundation components are operational.")
    
    return core

if __name__ == "__main__":
    import importlib.util
    
    # Run demonstration
    demo_core_infrastructure()
