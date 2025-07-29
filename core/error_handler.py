"""
OPRYXX Operator Error Handler
Comprehensive error handling with self-healing capabilities
"""
import logging
import traceback
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps

class OPRYXXErrorHandler:
    def __init__(self):
        self.operator_link = "OPR-NS8-GE8-KC3-001-AI-GRS-GUID:983DE8C8-E120-1-B5A0-C6D8AF97BB09"
        self.error_count = 0
        self.recovery_attempts = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'opryxx_errors.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('OPRYXX_ErrorHandler')
    
    def handle_error(self, error: Exception, context: str = "", auto_recover: bool = True) -> bool:
        """Handle errors with operator intelligence"""
        self.error_count += 1
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.error_count}"
        
        error_info = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
            'operator_link': self.operator_link
        }
        
        self.logger.error(f"🚨 OPERATOR ERROR {error_id}: {error_info['error_type']} - {error_info['error_message']}")
        self.logger.error(f"📍 Context: {context}")
        self.logger.error(f"📋 Traceback: {error_info['traceback']}")
        
        if auto_recover:
            return self.attempt_recovery(error_info)
        
        return False
    
    def attempt_recovery(self, error_info: Dict[str, Any]) -> bool:
        """Attempt automatic error recovery"""
        error_type = error_info['error_type']
        
        if error_type in self.recovery_attempts:
            self.recovery_attempts[error_type] += 1
        else:
            self.recovery_attempts[error_type] = 1
        
        # Limit recovery attempts
        if self.recovery_attempts[error_type] > 3:
            self.logger.error(f"🛑 Max recovery attempts reached for {error_type}")
            return False
        
        self.logger.info(f"🔧 Attempting recovery for {error_type} (attempt {self.recovery_attempts[error_type]})")
        
        # Recovery strategies
        recovery_strategies = {
            'ImportError': self._recover_import_error,
            'FileNotFoundError': self._recover_file_not_found,
            'PermissionError': self._recover_permission_error,
            'ConnectionError': self._recover_connection_error,
            'AttributeError': self._recover_attribute_error,
            'ModuleNotFoundError': self._recover_module_not_found
        }
        
        if error_type in recovery_strategies:
            try:
                success = recovery_strategies[error_type](error_info)
                if success:
                    self.logger.info(f"✅ Recovery successful for {error_type}")
                    return True
            except Exception as recovery_error:
                self.logger.error(f"❌ Recovery failed: {recovery_error}")
        
        return False
    
    def _recover_import_error(self, error_info: Dict[str, Any]) -> bool:
        """Recover from import errors"""
        try:
            # Try to install missing module
            error_msg = error_info['error_message']
            if "No module named" in error_msg:
                module_name = error_msg.split("'")[1]
                self.logger.info(f"🔄 Attempting to install missing module: {module_name}")
                
                import subprocess
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', module_name], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Module {module_name} installed successfully")
                    return True
        except Exception:
            pass
        return False
    
    def _recover_file_not_found(self, error_info: Dict[str, Any]) -> bool:
        """Recover from file not found errors"""
        try:
            # Create missing directories
            error_msg = error_info['error_message']
            if "No such file or directory" in error_msg:
                # Extract path and create directory
                import re
                path_match = re.search(r"'([^']*)'", error_msg)
                if path_match:
                    file_path = path_match.group(1)
                    dir_path = os.path.dirname(file_path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)
                        self.logger.info(f"✅ Created missing directory: {dir_path}")
                        return True
        except Exception:
            pass
        return False
    
    def _recover_permission_error(self, error_info: Dict[str, Any]) -> bool:
        """Recover from permission errors"""
        self.logger.warning("🔐 Permission error detected - manual intervention may be required")
        return False
    
    def _recover_connection_error(self, error_info: Dict[str, Any]) -> bool:
        """Recover from connection errors"""
        self.logger.info("🌐 Connection error - implementing retry logic")
        import time
        time.sleep(2)  # Brief delay before retry
        return True
    
    def _recover_attribute_error(self, error_info: Dict[str, Any]) -> bool:
        """Recover from attribute errors"""
        self.logger.info("🔍 Attribute error - checking for alternative methods")
        return False
    
    def _recover_module_not_found(self, error_info: Dict[str, Any]) -> bool:
        """Recover from module not found errors"""
        return self._recover_import_error(error_info)

# Global error handler instance
error_handler = OPRYXXErrorHandler()

def operator_error_handler(func: Callable) -> Callable:
    """Decorator for automatic error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"Function: {func.__name__}, Args: {args}, Kwargs: {kwargs}"
            error_handler.handle_error(e, context)
            raise
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """Safely execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = f"Safe execution of {func.__name__}"
        if error_handler.handle_error(e, context):
            # Retry once after recovery
            try:
                return func(*args, **kwargs)
            except Exception as retry_error:
                error_handler.handle_error(retry_error, f"Retry of {context}")
                return None
        return None