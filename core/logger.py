"""
Centralized logging system for OPRYXX
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import threading
from logging.handlers import RotatingFileHandler

class Logger:
    """Centralized logger for OPRYXX"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                RotatingFileHandler(
                    log_dir / "opryxx.log",
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
            ]
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger for specific module"""
        if name not in self.loggers:
            logger = logging.getLogger(f"opryxx.{name}")
            
            # Create module-specific log file
            log_dir = Path("logs")
            handler = RotatingFileHandler(
                log_dir / f"{name}.log",
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(handler)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_operation(self, module: str, operation: str, success: bool, details: str = ""):
        """Log operation result"""
        logger = self.get_logger(module)
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        logger.log(level, f"{operation}: {status} - {details}")
    
    def log_error(self, module: str, error: Exception, context: str = ""):
        """Log error with context"""
        logger = self.get_logger(module)
        logger.error(f"{context}: {type(error).__name__}: {error}", exc_info=True)

# Global logger instance
def get_logger(name: str = "main") -> logging.Logger:
    """Get logger instance"""
    return Logger().get_logger(name)