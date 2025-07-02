"""
Resilience and Recovery System
Implements circuit breakers, retry logic, and automatic recovery mechanisms
"""

import time
import threading
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = auto()    # Normal operation
    OPEN = auto()      # Circuit breaker tripped
    HALF_OPEN = auto() # Testing if service recovered

@dataclass
class FailureRecord:
    timestamp: float
    error_type: str
    error_message: str
    operation: str

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.failure_history: List[FailureRecord] = []
        self._lock = threading.RLock()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == CircuitState.OPEN:
                    if self._should_attempt_reset():
                        self.state = CircuitState.HALF_OPEN
                    else:
                        raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
                
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except self.expected_exception as e:
                    self._on_failure(func.__name__, e)
                    raise
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self, operation: str, error: Exception):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        failure_record = FailureRecord(
            timestamp=self.last_failure_time,
            error_type=type(error).__name__,
            error_message=str(error),
            operation=operation
        )
        self.failure_history.append(failure_record)
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED for {operation} after {self.failure_count} failures")

class RetryPolicy:
    """Configurable retry policy with exponential backoff"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == self.max_attempts - 1:
                        break
                    
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    
                    if self.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper

class HealthChecker:
    """System health monitoring and recovery"""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, bool] = {}
        self.recovery_actions: Dict[str, Callable] = {}
        self.monitoring = False
        self._thread: Optional[threading.Thread] = None
    
    def register_health_check(self, name: str, check_func: Callable, recovery_func: Optional[Callable] = None):
        """Register a health check with optional recovery action"""
        self.health_checks[name] = check_func
        self.health_status[name] = True
        if recovery_func:
            self.recovery_actions[name] = recovery_func
    
    def start_monitoring(self, interval: float = 30.0):
        """Start health monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self._thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            for name, check_func in self.health_checks.items():
                try:
                    is_healthy = check_func()
                    
                    if not is_healthy and self.health_status.get(name, True):
                        # Health degraded
                        logger.warning(f"Health check failed: {name}")
                        self.health_status[name] = False
                        
                        # Attempt recovery
                        if name in self.recovery_actions:
                            try:
                                self.recovery_actions[name]()
                                logger.info(f"Recovery action executed for {name}")
                            except Exception as e:
                                logger.error(f"Recovery failed for {name}: {e}")
                    
                    elif is_healthy and not self.health_status.get(name, False):
                        # Health recovered
                        logger.info(f"Health check recovered: {name}")
                        self.health_status[name] = True
                        
                except Exception as e:
                    logger.error(f"Health check error for {name}: {e}")
                    self.health_status[name] = False
            
            time.sleep(interval)
    
    def get_health_status(self) -> Dict[str, bool]:
        """Get current health status"""
        return self.health_status.copy()
    
    def is_system_healthy(self) -> bool:
        """Check if all systems are healthy"""
        return all(self.health_status.values())

class ResilienceManager:
    """Central resilience management system"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.health_checker = HealthChecker()
        self.failure_stats: Dict[str, List[FailureRecord]] = {}
    
    def create_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Create and register a circuit breaker"""
        breaker = CircuitBreaker(**kwargs)
        self.circuit_breakers[name] = breaker
        return breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def get_system_resilience_report(self) -> Dict:
        """Generate comprehensive resilience report"""
        report = {
            'timestamp': time.time(),
            'circuit_breakers': {},
            'health_status': self.health_checker.get_health_status(),
            'system_healthy': self.health_checker.is_system_healthy()
        }
        
        for name, breaker in self.circuit_breakers.items():
            report['circuit_breakers'][name] = {
                'state': breaker.state.name,
                'failure_count': breaker.failure_count,
                'last_failure': breaker.last_failure_time,
                'recent_failures': len([f for f in breaker.failure_history 
                                      if time.time() - f.timestamp < 300])  # Last 5 minutes
            }
        
        return report

# Global resilience manager
resilience_manager = ResilienceManager()

# Convenience decorators
def circuit_breaker(name: str = None, **kwargs):
    """Decorator to add circuit breaker protection"""
    def decorator(func):
        breaker_name = name or f"{func.__module__}.{func.__name__}"
        breaker = resilience_manager.create_circuit_breaker(breaker_name, **kwargs)
        return breaker(func)
    return decorator

def retry(max_attempts: int = 3, **kwargs):
    """Decorator to add retry logic"""
    policy = RetryPolicy(max_attempts=max_attempts, **kwargs)
    return policy