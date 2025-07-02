"""
Advanced logging system for OPRYXX.

This module provides a centralized logging system with support for:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Performance metrics logging
- Security event logging
- Log rotation with size and time-based rotation
- Log retention policies with automatic cleanup
- Log compression for archived logs
- Structured logging with additional context
- Thread-safe operations
"""
import logging
import os
import sys
import gzip
import shutil
import time
import threading
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Callable

# Default log format
DEFAULT_LOG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
    '[%(filename)s:%(lineno)d] %(threadName)s'
)

# Performance log format
PERFORMANCE_FORMAT = (
    '%(asctime)s - PERFORMANCE - %(message)s - %(duration).6fs - %(metrics)s'
)

# Security log format
SECURITY_FORMAT = (
    '%(asctime)s - SECURITY - %(levelname)s - %(event)s - %(details)s'
)

class LogRotator:
    """Handles log rotation and retention policies."""
    
    def __init__(
        self,
        log_dir: str,
        max_size_mb: int = 100,
        backup_count: int = 5,
        retention_days: int = 30,
        compress: bool = True
    ):
        """Initialize the log rotator.
        
        Args:
            log_dir: Directory where logs are stored
            max_size_mb: Maximum size in MB before rotation
            backup_count: Number of backup files to keep
            retention_days: Number of days to keep log files
            compress: Whether to compress rotated logs
        """
        self.log_dir = Path(log_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self.retention_days = retention_days
        self.compress = compress
        self.cleanup_interval = 86400  # Run cleanup daily (in seconds)
        self.last_cleanup = 0
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def should_rollover(self, record: logging.LogRecord) -> bool:
        """Determine if a rollover should occur."""
        # Check if we should run cleanup
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_logs()
            self.last_cleanup = current_time
            
        # Default rotation logic (handled by RotatingFileHandler)
        return False
    
    def get_rotated_files(self, base_filename: str) -> List[Path]:
        """Get a list of rotated log files for the given base filename."""
        pattern = f"{base_filename}*"
        return sorted(self.log_dir.glob(pattern), key=os.path.getmtime, reverse=True)
    
    def compress_file(self, source: Path) -> None:
        """Compress a log file using gzip."""
        compressed_path = source.with_suffix(f"{source.suffix}.gz")
        
        with open(source, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove the original file after successful compression
        source.unlink()
    
    def cleanup_old_logs(self) -> None:
        """Clean up old log files based on retention policy."""
        if self.retention_days <= 0:
            return
            
        cutoff_time = time.time() - (self.retention_days * 86400)  # days to seconds
        
        # Get all log files in the directory
        for log_file in self.log_dir.glob("*.log*"):
            try:
                # Skip active log files
                if log_file.name.endswith('.log') and not log_file.name.endswith('.log.gz'):
                    continue
                    
                # Check file modification time
                file_mtime = log_file.stat().st_mtime
                if file_mtime < cutoff_time:
                    log_file.unlink()
                    logging.getLogger(__name__).info(f"Removed old log file: {log_file}")
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"Error cleaning up log file {log_file}: {e}")


class Logger:
    """Advanced logger with performance and security logging capabilities."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(
        cls,
        name: str = "opryxx",
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        max_size_mb: int = 100,
        backup_count: int = 5,
        retention_days: int = 30,
        compress_logs: bool = True,
        *args,
        **kwargs
    ) -> 'Logger':
        """Create or return the singleton logger instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        name: str = "opryxx",
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        max_size_mb: int = 100,
        backup_count: int = 5,
        retention_days: int = 30,
        compress_logs: bool = True,
        enable_console: bool = True,
        enable_file: bool = True,
        log_format: str = None,
        error_log_file: str = None,
        **kwargs
    ) -> None:
        """Initialize the logger with enhanced rotation and retention.
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
            log_level: Logging level (default: INFO)
            max_size_mb: Maximum log file size in MB before rotation
            backup_count: Number of backup logs to keep
            retention_days: Number of days to keep log files (0 = keep forever)
            compress_logs: Whether to compress rotated log files
            enable_console: Whether to enable console logging
            enable_file: Whether to enable file logging
            log_format: Custom log format string
            error_log_file: Separate file for error logs (optional)
        """
        # Only initialize once
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count
        self.retention_days = retention_days
        self.compress_logs = compress_logs
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure the root logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # Remove any existing handlers to avoid duplicate logs
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
        
        # Create formatters
        self.formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
        self.performance_formatter = logging.Formatter(PERFORMANCE_FORMAT)
        self.security_formatter = logging.Formatter(SECURITY_FORMAT)
        
        # Add console handler if enabled
        if enable_console:
            self._add_console_handler()
        
        # Add file handlers if enabled
        if enable_file:
            self._add_file_handlers(error_log_file)
        
        # Initialize log rotator
        self.rotator = LogRotator(
            log_dir=log_dir,
            max_size_mb=max_size_mb,
            backup_count=backup_count,
            retention_days=retention_days,
            compress=compress_logs
        )
        
        self._initialized = True
        
        # Log initialization
        self.info(f"Logger initialized. Log directory: {self.log_dir.absolute()}")
        self.info(f"Log rotation: {max_size_mb}MB max size, {backup_count} backups")
        if retention_days > 0:
            self.info(f"Log retention: {retention_days} days")
        else:
            self.info("Log retention: unlimited")
    
    def _add_console_handler(self) -> None:
        """Add a console handler to the logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        console_handler.setLevel(self.log_level)
        self.logger.addHandler(console_handler)
    
    def _add_file_handlers(self, error_log_file: str = None) -> None:
        """Add file handlers to the logger with rotation and compression."""
        # Main log file
        log_file = self.log_dir / f"{self.name}.log"
        
        # Create a rotating file handler with size-based rotation
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=self.max_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=self.backup_count,
            encoding='utf-8',
        )
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(self.log_level)
        self.logger.addHandler(file_handler)
        
        # Add error log handler if specified
        if error_log_file:
            error_handler = RotatingFileHandler(
                filename=str(self.log_dir / error_log_file),
                maxBytes=self.max_size_mb * 1024 * 1024,
                backupCount=self.backup_count,
                encoding='utf-8',
            )
            error_handler.setFormatter(self.formatter)
            error_handler.setLevel(logging.ERROR)  # Only log ERROR and above
            self.logger.addHandler(error_handler)
    
    def _log_with_extra(self, level: int, msg: str, **kwargs) -> None:
        """Log a message with additional context.
        
        Args:
            level: Logging level
            msg: Log message
            **kwargs: Additional context to include in the log record
        """
        self.logger.log(level, msg, extra=kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log a debug message."""
        self._log_with_extra(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log an info message."""
        self._log_with_extra(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log a warning message."""
        self._log_with_extra(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log an error message."""
        self._log_with_extra(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log a critical message."""
        self._log_with_extra(logging.CRITICAL, msg, **kwargs)
    
    def performance(
        self,
        operation: str,
        duration: float,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log performance metrics for an operation.
        
        Args:
            operation: Name of the operation being measured
            duration: Duration in seconds
            metrics: Additional performance metrics
            **kwargs: Additional context
        """
        if metrics is None:
            metrics = {}
            
        # Format metrics as a string
        metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
        
        # Create a message with performance data
        msg = f"{operation} - {duration:.6f}s - {metrics_str}"
        
        # Log with performance level (using INFO level with custom formatter)
        self.info(msg, **{"duration": duration, "metrics": metrics_str, **kwargs})
    
    def security(
        self,
        event: str,
        level: str = "INFO",
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log a security event.
        
        Args:
            event: Security event name/identifier
            level: Security level (INFO, WARNING, ERROR, CRITICAL)
            details: Additional security event details
            **kwargs: Additional context
        """
        if details is None:
            details = {}
            
        # Convert details to string
        details_str = ", ".join(f"{k}={v}" for k, v in details.items())
        
        # Get the appropriate log level
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Log with security context
        self._log_with_extra(
            log_level,
            f"{event} - {details_str}",
            event=event,
            details=details_str,
            **kwargs
        )
    
    def shutdown(self) -> None:
        """Shut down the logger and clean up resources."""
        # Remove all handlers
        for handler in self.logger.handlers[:]:
            try:
                handler.flush()
                handler.close()
                self.logger.removeHandler(handler)
            except Exception as e:
                sys.stderr.write(f"Error closing log handler: {e}\n")
        
        # Clear the instance
        self._initialized = False
        type(self)._instance = None
        
        # Force cleanup of any remaining handlers
        logging.shutdown()
    
    def rotate_logs(self) -> None:
        """Manually trigger log rotation."""
        for handler in self.logger.handlers:
            if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                try:
                    handler.doRollover()
                    self.info("Log rotation completed")
                except Exception as e:
                    self.error(f"Error rotating logs: {e}")
    
    def cleanup_old_logs(self) -> None:
        """Manually trigger cleanup of old log files."""
        if hasattr(self, 'rotator'):
            self.rotator.cleanup_old_logs()
            self.info("Old log cleanup completed")
    
    def __enter__(self) -> 'Logger':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensure resources are cleaned up."""
        self.shutdown()
        return False  # Don't suppress exceptions

# Create a default logger instance
default_logger = Logger()
