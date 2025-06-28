"""Unit tests for the circuit breaker implementation."""
import pytest
import time
import random
from unittest.mock import patch, MagicMock
from ai_workbench.core.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerError,
    circuit_breaker,
    get_circuit_breaker,
)

# Test function that will be decorated
@circuit_breaker("test_breaker", failure_threshold=2, recovery_timeout=0.1)
def test_function(succeed: bool = True):
    """Test function that can be made to fail or succeed."""
    if not succeed:
        raise ValueError("Intentional failure")
    return "success"

class TestCircuitBreaker:
    """Test cases for the CircuitBreaker class."""

    def test_initial_state(self):
        """Test that the circuit breaker starts in the CLOSED state."""
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED

    def test_successful_call(self):
        """Test a successful call through the circuit breaker."""
        cb = CircuitBreaker("test_success")
        
        @cb
        def successful_func():
            return "success"
            
        result = successful_func()
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_failure_threshold(self):
        """Test that the circuit opens after the failure threshold is reached."""
        cb = CircuitBreaker("test_failure", failure_threshold=2)
        
        @cb
        def failing_func():
            raise ValueError("Intentional failure")
        
        # First failure
        with pytest.raises(ValueError):
            failing_func()
        assert cb.state == CircuitState.CLOSED
        
        # Second failure should open the circuit
        with pytest.raises(ValueError):
            failing_func()
        assert cb.state == CircuitState.OPEN
        
        # Next call should fail fast with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            failing_func()

    def test_half_open_state(self):
        """Test the half-open state and recovery."""
        cb = CircuitBreaker("test_recovery", failure_threshold=1, recovery_timeout=0.1)
        
        call_count = 0
        
        @cb
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first two calls
                raise ValueError("Temporary failure")
            return "recovered"
        
        # First call fails and opens the circuit
        with pytest.raises(ValueError):
            flaky_func()
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Next call should be allowed (half-open)
        with pytest.raises(ValueError):
            flaky_func()
        
        # Wait for recovery timeout again
        time.sleep(0.15)
        
        # This call should succeed and close the circuit
        result = flaky_func()
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_decorator(self):
        """Test the circuit_breaker decorator."""
        # First two calls should fail with ValueError
        with pytest.raises(ValueError):
            test_function(succeed=False)
        with pytest.raises(ValueError):
            test_function(succeed=False)
        
        # Third call should fail with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            test_function(succeed=False)
        
        # Get the circuit breaker instance
        cb = get_circuit_breaker("test_breaker")
        assert cb is not None
        assert cb.state == CircuitState.OPEN
        
        # After recovery timeout, should be half-open
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        
        # Successful call should close the circuit
        result = test_function(succeed=True)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_concurrent_access(self):
        """Test thread safety of the circuit breaker."""
        import threading
        
        cb = CircuitBreaker("concurrent_test", failure_threshold=5)
        results = []
        
        @cb
        def failing_func():
            if random.random() > 0.7:  # 30% chance of success
                return "success"
            raise ValueError("Random failure")
        
        def worker():
            try:
                result = failing_func()
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))
        
        # Create and start multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify we got results from all threads
        assert len(results) == 10
        
        # Verify circuit state is consistent
        assert cb.state in [CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN]

    def test_custom_retry_on(self):
        """Test custom exception types for retry logic."""
        class CustomError(Exception):
            pass
            
        cb = CircuitBreaker("custom_error", failure_threshold=1, retry_on=CustomError)
        
        @cb
        def custom_error_func():
            raise CustomError("Custom error")
            
        # Should retry on CustomError
        with pytest.raises(CustomError):
            custom_error_func()
            
        # Should be open now
        assert cb.state == CircuitState.OPEN
        
        # Other exceptions should not be caught
        @cb
        def other_error_func():
            raise ValueError("Other error")
            
        with pytest.raises(ValueError):
            other_error_func()
            
        # State should still be OPEN
        assert cb.state == CircuitState.OPEN
