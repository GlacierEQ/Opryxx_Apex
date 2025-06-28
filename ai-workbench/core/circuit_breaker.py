"""Circuit breaker implementation for external service calls."""
import time
from enum import Enum, auto
from typing import Callable, TypeVar, Optional, Any
from functools import wraps
import logging

logger = logging.getLogger('circuit_breaker')

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitBreakerError(Exception):
    """Raised when the circuit is open and the call is not allowed."""
    pass

class CircuitBreaker:
    """
    Implements the circuit breaker pattern for handling external service calls.
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Calls fail immediately, no calls are made
    - HALF_OPEN: Limited calls are allowed to test if the service has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3,
        name: str = "default"
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds before trying to close the circuit
            half_open_max_calls: Maximum number of calls to allow in half-open state
            name: Name of the circuit breaker for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.name = name
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._half_open_calls = 0
        self._lock = None  # Will be set to a threading.Lock if needed
    
    @property
    def state(self) -> CircuitState:
        """Get the current state of the circuit breaker."""
        if self._state == CircuitState.OPEN and self._should_attempt_recovery():
            self._state = CircuitState.HALF_OPEN
            self._half_open_calls = 0
            logger.info(f"Circuit {self.name} moved to HALF_OPEN state")
        return self._state
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return (time.time() - self._last_failure_time) > self.recovery_timeout
    
    def record_success(self) -> None:
        """Record a successful call and update the circuit state."""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._close_circuit()
        elif self._state == CircuitState.CLOSED and self._failure_count > 0:
            # Reset failure count on success in CLOSED state
            self._failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed call and update the circuit state."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            # If we fail in half-open state, go back to open
            self._open_circuit()
        elif (self._state == CircuitState.CLOSED and 
              self._failure_count >= self.failure_threshold):
            self._open_circuit()
    
    def _open_circuit(self) -> None:
        """Open the circuit and record the failure time."""
        old_state = self._state
        self._state = CircuitState.OPEN
        self._last_failure_time = time.time()
        if old_state != CircuitState.OPEN:
            logger.warning(f"Circuit {self.name} is now OPEN")
    
    def _close_circuit(self) -> None:
        """Close the circuit and reset failure counters."""
        old_state = self._state
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        if old_state != CircuitState.CLOSED:
            logger.info(f"Circuit {self.name} is now CLOSED")
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to wrap a function with circuit breaker logic."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Check circuit state before making the call
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerError(f"Circuit {self.name} is OPEN")
            
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerError(
                        f"Circuit {self.name} is HALF_OPEN and call limit reached"
                    )
            
            # Make the call
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                logger.error(f"Call failed in circuit {self.name}: {str(e)}")
                raise
        
        return wrapper

# Global registry of circuit breakers
_circuit_breakers = {}

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    half_open_max_calls: int = 3
) -> Callable[..., Callable[..., T]]:
    """
    Decorator factory for circuit breakers.
    
    Args:
        name: Unique name for the circuit breaker
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Time in seconds before trying to close the circuit
        half_open_max_calls: Maximum number of calls to allow in half-open state
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                half_open_max_calls=half_open_max_calls,
                name=name
            )
        return _circuit_breakers[name](func)
    return decorator

def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get a circuit breaker by name."""
    return _circuit_breakers.get(name)
