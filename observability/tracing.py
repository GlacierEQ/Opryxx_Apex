"""
Observability and Tracing for OPRYXX
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional
from functools import wraps

class CorrelationContext:
    _context = {}
    
    @classmethod
    def set_correlation_id(cls, correlation_id: str):
        cls._context['correlation_id'] = correlation_id
    
    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        return cls._context.get('correlation_id')

class TracingLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, message: str):
        correlation_id = CorrelationContext.get_correlation_id() or 'no-id'
        self.logger.info(message, extra={'correlation_id': correlation_id})

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
    
    def increment_counter(self, name: str, value: int = 1):
        self.metrics[name] = self.metrics.get(name, 0) + value
    
    def record_histogram(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

tracer = TracingLogger('opryxx')
metrics = MetricsCollector()

def trace_function(operation_name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            
            if not CorrelationContext.get_correlation_id():
                CorrelationContext.set_correlation_id(str(uuid.uuid4())[:8])
            
            start_time = time.time()
            tracer.info(f"Starting: {op_name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                tracer.info(f"Completed: {op_name} in {duration:.3f}s")
                metrics.record_histogram('duration', duration)
                return result
            except Exception as e:
                tracer.info(f"Failed: {op_name} - {str(e)}")
                raise
        return wrapper
    return decorator