"""
Logging Utilities for AI Workbench

This module provides logging configuration and utilities for the AI Workbench.
It sets up a consistent logging format and provides helper functions for logging.
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class ColorFormatter(logging.Formatter):
    """Custom log formatter that adds colors to log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[1;31m',# Bold Red
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format the specified record as text with colors"""
        # Get the original message
        message = super().format(record)
        
        # Add color if the level has a color defined
        if record.levelname in self.COLORS:
            message = f"{self.COLORS[record.levelname]}{message}{self.COLORS['RESET']}"
            
        return message


def setup_logger(
    name: str = 'ai_workbench',
    log_level: str = 'INFO',
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, no file logging)
        console: Whether to log to console
        max_bytes: Maximum log file size in bytes before rotation
        backup_count: Number of backup log files to keep
        log_format: Custom log format string
        date_format: Custom date format string
        
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # Create formatters
    log_format = log_format or DEFAULT_LOG_FORMAT
    date_format = date_format or DEFAULT_DATE_FORMAT
    
    # Create console formatter (with colors)
    console_formatter = ColorFormatter(log_format, datefmt=date_format)
    
    # Create file formatter (no colors)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name, or the root logger if no name is given.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name or 'ai_workbench')


def log_system_info(logger: Optional[logging.Logger] = None) -> None:
    """
    Log system information at startup
    
    Args:
        logger: Logger instance (if None, uses the root logger)
    """
    if logger is None:
        logger = get_logger()
    
    import platform
    import psutil
    
    try:
        # Basic system info
        logger.info("=" * 80)
        logger.info(f"AI Workbench - System Information")
        logger.info("=" * 80)
        
        # Python and platform info
        logger.info(f"Python: {sys.version.split()[0]} on {platform.platform()}")
        logger.info(f"Executable: {sys.executable}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # CPU info
        logger.info(f"CPU: {platform.processor() or 'Unknown'}")
        logger.info(f"CPU Cores: {psutil.cpu_count(logical=True)} logical, {psutil.cpu_count(logical=False)} physical")
        
        # Memory info
        mem = psutil.virtual_memory()
        logger.info(f"Total Memory: {mem.total / (1024**3):.2f} GB")
        logger.info(f"Available Memory: {mem.available / (1024**3):.2f} GB")
        logger.info(f"Memory Used: {mem.percent}%")
        
        # Disk info
        disk = psutil.disk_usage('/')
        logger.info(f"Disk Usage: {disk.percent}%")
        logger.info(f"Total Disk Space: {disk.total / (1024**3):.2f} GB")
        logger.info(f"Used Disk Space: {disk.used / (1024**3):.2f} GB")
        logger.info(f"Free Disk Space: {disk.free / (1024**3):.2f} GB")
        
        # Network info
        net_io = psutil.net_io_counters()
        logger.info(f"Network - Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB")
        logger.info(f"Network - Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error logging system info: {e}", exc_info=True)


def log_exception(
    logger: logging.Logger,
    message: str,
    exc_info: Optional[BaseException] = None,
    extra: Optional[Dict[str, Any]] = None,
    level: str = 'error'
) -> None:
    """
    Log an exception with a custom message and optional extra data
    
    Args:
        logger: Logger instance
        message: Error message
        exc_info: Exception object (if any)
        extra: Additional data to include in the log record
        level: Log level ('error', 'warning', 'info', 'debug')
    """
    log_method = getattr(logger, level.lower(), logger.error)
    
    # Include exception info if provided
    exc_info = exc_info or (sys.exc_info() if sys.exc_info() != (None, None, None) else None)
    
    # Log the message
    log_method(message, exc_info=exc_info, extra=extra or {})


class LoggingContext:
    """Context manager for logging with a specific context"""
    
    def __init__(
        self,
        logger: logging.Logger,
        level: Optional[int] = None,
        handler: Optional[logging.Handler] = None,
        close: bool = True
    ):
        """
        Initialize the context manager
        
        Args:
            logger: Logger instance
            level: Optional log level to set temporarily
            handler: Optional handler to add temporarily
            close: Whether to close the handler when done
        """
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close
        self.old_level = None
        
    def __enter__(self):
        """Enter the context"""
        # Save old level and set new level if provided
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
            
        # Add handler if provided
        if self.handler is not None:
            self.logger.addHandler(self.handler)
            
        return self.logger
        
    def __exit__(self, et, ev, tb):
        """Exit the context"""
        # Restore old level
        if self.level is not None and self.old_level is not None:
            self.logger.setLevel(self.old_level)
            
        # Remove and optionally close handler
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            if self.close:
                self.handler.close()
                
        # Don't suppress exceptions
        return False
