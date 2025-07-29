"""Enhanced logging configuration for OPRYXX system with execution tracking"""
import logging
import time
import functools
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from enum import Enum
import os
import threading

# Type variable for generic function typing
F = TypeVar('F', bound=Callable[..., Any])

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ExecutionStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ExecutionTracker:
    """Tracks execution context across function calls"""
    _thread_local = threading.local()
    
    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        if not hasattr(cls._thread_local, 'context'):
            cls._thread_local.context = {'execution_id': str(id(threading.current_thread()))}
        return cls._thread_local.context

def setup_logging(log_level: LogLevel = LogLevel.INFO, log_file: Optional[str] = None) -> None:
    """Initialize logging configuration"""
    log_format = '%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(level=log_level.value, format=log_format, handlers=handlers, force=True)
    logging.getLogger().setLevel(log_level.value)

def log_execution(log_level: LogLevel = LogLevel.INFO, log_result: bool = True) -> Callable[[F], F]:
    """Decorator to log function execution"""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = logging.getLogger(func.__module__)
            
            # Log function start
            logger.log(log_level.value, f"{func.__name__}() started")
            
            # Execute function and track timing
            start_time = time.time()
            status = ExecutionStatus.COMPLETED
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = ExecutionStatus.FAILED
                error = e
                raise
            finally:
                # Calculate duration
                duration = time.time() - start_time
                
                # Log function completion
                log_msg = f"{func.__name__}() {status.value.lower()} in {duration:.4f}s"
                if error:
                    log_msg += f" with error: {str(error)}"
                
                logger.log(log_level.value, log_msg)
        
        return cast(F, wrapper)
    return decorator
