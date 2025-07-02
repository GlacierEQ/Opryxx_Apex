"""
Implement Best Practice Improvements
"""

import os
import subprocess

def implement_error_handling():
    """Implement structured error handling"""
    error_handling_code = '''
"""
Structured Error Handling for OPRYXX
"""

class OPRYXXException(Exception):
    def __init__(self, message: str, error_code: str, context: dict = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)

class RecoveryException(OPRYXXException):
    pass

class OptimizationException(OPRYXXException):
    pass

class ValidationException(OPRYXXException):
    pass

def handle_exception(func):
    """Decorator for consistent error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OPRYXXException:
            raise
        except Exception as e:
            raise OPRYXXException(
                message=f"Unexpected error in {func.__name__}",
                error_code="UNEXPECTED_ERROR",
                context={"original_error": str(e)}
            )
    return wrapper
'''
    
    with open('core/error_handling.py', 'w') as f:
        f.write(error_handling_code)
    
    print("✅ Structured error handling implemented")

def implement_request_tracking():
    """Implement request ID tracking"""
    tracking_code = '''
"""
Request Tracking for OPRYXX
"""

import uuid
from contextvars import ContextVar
from functools import wraps

correlation_id: ContextVar[str] = ContextVar('correlation_id')

def set_correlation_id(request_id: str = None):
    """Set correlation ID for request tracking"""
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
    correlation_id.set(request_id)
    return request_id

def get_correlation_id() -> str:
    """Get current correlation ID"""
    try:
        return correlation_id.get()
    except LookupError:
        return "no-correlation-id"

def track_request(func):
    """Decorator to track requests with correlation ID"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_id = set_correlation_id()
        print(f"[{request_id}] Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            print(f"[{request_id}] Completed {func.__name__}")
            return result
        except Exception as e:
            print(f"[{request_id}] Failed {func.__name__}: {e}")
            raise
    
    return wrapper
'''
    
    with open('core/request_tracking.py', 'w') as f:
        f.write(tracking_code)
    
    print("✅ Request tracking implemented")

def implement_enhanced_logging():
    """Implement enhanced logging"""
    logging_code = '''
"""
Enhanced Logging for OPRYXX
"""

import logging
import json
from datetime import datetime
from core.request_tracking import get_correlation_id

class OPRYXXFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "correlation_id": get_correlation_id()
        }
        
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup enhanced logging configuration"""
    logger = logging.getLogger('opryxx')
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(OPRYXXFormatter())
    
    logger.addHandler(handler)
    return logger

# Global logger instance
opryxx_logger = setup_logging()
'''
    
    with open('core/enhanced_logging.py', 'w') as f:
        f.write(logging_code)
    
    print("✅ Enhanced logging implemented")

def implement_rate_limiting():
    """Implement API rate limiting"""
    rate_limiting_code = '''
"""
Rate Limiting for OPRYXX API
"""

import time
from collections import defaultdict, deque
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False

# Global rate limiter
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_id = "default"  # In real implementation, get from request
            
            if not rate_limiter.is_allowed(client_id):
                raise Exception("Rate limit exceeded")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
'''
    
    with open('api/rate_limiting.py', 'w') as f:
        f.write(rate_limiting_code)
    
    print("✅ Rate limiting implemented")

def create_makefile():
    """Create Makefile for common tasks"""
    makefile_content = '''
# OPRYXX Makefile

.PHONY: test lint format install clean run

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run tests
test:
	python -m pytest tests/ -v --cov=. --cov-report=html

# Run linting
lint:
	flake8 .
	mypy .
	bandit -r .

# Format code
format:
	black .
	isort .

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

# Run application
run:
	python MASTER_LAUNCHER.py

# Run performance tests
benchmark:
	python performance_benchmark.py

# Create recovery USB
recovery-usb:
	python recovery/create_e_drive_recovery.py

# Run security scan
security:
	bandit -r . -f json -o security-report.json
	safety check

# Generate documentation
docs:
	python -c "from api.openapi_spec import OPENAPI_SPEC; print('API docs available')"

# All quality checks
quality: lint test security
	echo "All quality checks passed"
'''
    
    with open('Makefile', 'w') as f:
        f.write(makefile_content)
    
    print("✅ Makefile created")

def main():
    """Implement all improvements"""
    print("🚀 IMPLEMENTING BEST PRACTICE IMPROVEMENTS")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs('core', exist_ok=True)
    os.makedirs('api', exist_ok=True)
    
    # Implement improvements
    implement_error_handling()
    implement_request_tracking()
    implement_enhanced_logging()
    implement_rate_limiting()
    create_makefile()
    
    print("\n✅ ALL IMPROVEMENTS IMPLEMENTED!")
    print("\n📋 NEXT STEPS:")
    print("1. Run: make quality")
    print("2. Run: make test")
    print("3. Run: make benchmark")
    print("4. Review: BEST_PRACTICES_REPORT.md")

if __name__ == "__main__":
    main()