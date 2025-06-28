"""
LAYER 1: CORE INFRASTRUCTURE - UNICODE SAFE VERSION
==================================================
Foundation layer that works with both Python and JavaScript components
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

class CoreInfrastructure:
    """Main core infrastructure - Unicode safe version"""
    
    def __init__(self):
        print("Initializing Core Infrastructure...")
        
        # Initialize components
        self.config = self._init_config()
        print("[OK] Configuration system ready")
        
        self.logger = self._init_logger()
        print("[OK] Logging system ready")
        
        self.event_bus = self._init_events()
        print("[OK] Event system ready")
        
        self.database = self._init_database()
        print("[OK] Database system ready")
        
        self.api = self._init_api_bridge()
        print("[OK] API bridge ready (for JS integration)")
        
        print("[OK] Core Infrastructure READY!")
    
    def _init_config(self):
        """Initialize configuration system"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config = {
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
                "model": "nexus-3.0",
                "intelligence_level": 85,
                "learning_enabled": True
            },
            "javascript": {
                "enabled": True,
                "port": 3000,
                "websocket_port": 3001,
                "api_endpoint": "http://localhost:3000/api"
            }
        }
        
        # Save config
        config_file = config_dir / "opryxx.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _init_logger(self):
        """Initialize logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger("OPRYXX")
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / "opryxx.log",
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
        return logger
    
    def _init_events(self):
        """Initialize event system"""
        class EventBus:
            def __init__(self):
                self._subscribers = {}
                self._lock = threading.RLock()
                
            def subscribe(self, event_name: str, callback: Callable):
                with self._lock:
                    if event_name not in self._subscribers:
                        self._subscribers[event_name] = []
                    self._subscribers[event_name].append(callback)
            
            def publish(self, event_name: str, data: Dict = None):
                with self._lock:
                    subscribers = self._subscribers.get(event_name, [])
                    
                for callback in subscribers:
                    try:
                        callback({"name": event_name, "data": data or {}, "timestamp": datetime.now()})
                    except Exception as e:
                        print(f"Event handler failed: {e}")
        
        return EventBus()
    
    def _init_database(self):
        """Initialize database system"""
        db_dir = Path("data")
        db_dir.mkdir(exist_ok=True)
        
        db_path = db_dir / "opryxx.db"
        conn = sqlite3.connect(db_path)
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                health_score INTEGER,
                data TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_name TEXT,
                data TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        return {"path": str(db_path), "status": "ready"}
    
    def _init_api_bridge(self):
        """Initialize API bridge for JavaScript integration"""
        api_dir = Path("api")
        api_dir.mkdir(exist_ok=True)
        
        # Create API endpoints file for JavaScript to use
        endpoints = {
            "system_status": "/api/system/status",
            "metrics": "/api/metrics",
            "events": "/api/events",
            "config": "/api/config",
            "actions": "/api/actions"
        }
        
        with open(api_dir / "endpoints.json", 'w') as f:
            json.dump(endpoints, f, indent=2)
        
        return {"endpoints": endpoints, "status": "ready"}
    
    def get_status(self):
        """Get system status for JavaScript consumption"""
        return {
            "core_ready": True,
            "config_loaded": True,
            "database_ready": True,
            "api_bridge_ready": True,
            "timestamp": datetime.now().isoformat(),
            "javascript_integration": self.config.get("javascript", {}).get("enabled", False)
        }
    
    def log(self, level: str, message: str):
        """Logging method for JavaScript bridge"""
        if level.upper() == "INFO":
            self.logger.info(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        elif level.upper() == "ERROR":
            self.logger.error(message)

def demo_core():
    """Demo the core system"""
    print("CORE INFRASTRUCTURE DEMO")
    print("=" * 40)
    
    core = CoreInfrastructure()
    
    print("\n1. Configuration Test:")
    print(f"   JavaScript enabled: {core.config.get('javascript', {}).get('enabled')}")
    print(f"   API port: {core.config.get('javascript', {}).get('port')}")
    
    print("\n2. Event Test:")
    def test_handler(event):
        print(f"   Event: {event['name']}")
    
    core.event_bus.subscribe("test.demo", test_handler)
    core.event_bus.publish("test.demo", {"message": "Hello from Python!"})
    
    print("\n3. Logging Test:")
    core.log("INFO", "Testing Python-JS bridge")
    
    print("\n4. Status Check:")
    status = core.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 40)
    print("PYTHON CORE READY FOR JS INTEGRATION!")
    
    return core

if __name__ == "__main__":
    demo_core()
