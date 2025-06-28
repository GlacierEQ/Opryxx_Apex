"""Unit tests for the retry functionality."""
import pytest
import time
import random
from unittest.mock import patch, MagicMock, call
from ai_workbench.core.retry import (
    RetryConfig,
    RetryStrategy,
    retry,
    retry_async,
    MaxRetriesExceededError,
)
import asyncio

# Test functions for sync retry
@retry(max_retries=3, initial_delay=0.1, max_delay=0.5, strategy=RetryStrategy.EXPONENTIAL)
def flaky_function(succeed_after: int = 0):
    """Test function that fails a specified number of times before succeeding."""
    if not hasattr(flaky_function, 'call_count'):
        flaky_function.call_count = 0
    
    flaky_function.call_count += 1
    if flaky_function.call_count <= succeed_after:
        raise ValueError(f"Intentional failure (attempt {flaky_function.call_count})")
    return "success"

# Test functions for async retry
@retry_async(max_retries=3, initial_delay=0.1, max_delay=0.5, strategy=RetryStrategy.EXPONENTIAL)
async def async_flaky_function(succeed_after: int = 0):
    """Async test function that fails a specified number of times before succeeding."""
    if not hasattr(async_flaky_function, 'call_count'):
        async_flaky_function.call_count = 0
    
    async_flaky_function.call_count += 1
    if async_flaky_function.call_count <= succeed_after:
        raise ValueError(f"Async intentional failure (attempt {async_flaky_function.call_count})")
    return "async_success"

class TestRetry:
    """Test cases for the retry functionality."""

    def setup_method(self):
        """Reset call counts before each test."""
        if hasattr(flaky_function, 'call_count'):
            flaky_function.call_count = 0
        if hasattr(async_flaky_function, 'call_count'):
            async_flaky_function.call_count = 0
    
    def test_success_first_try(self):
        """Test that a function succeeds on the first try."""
        result = flaky_function(succeed_after=0)
        assert result == "success"
        assert flaky_function.call_count == 1
    
    def test_retry_until_success(self):
        """Test that a function retries until it succeeds."""
        result = flaky_function(succeed_after=2)
        assert result == "success"
        assert flaky_function.call_count == 3  # 2 failures + 1 success
    
    def test_max_retries_exceeded(self):
        """Test that MaxRetriesExceeded is raised when max retries are exceeded."""
        with pytest.raises(MaxRetriesExceededError) as exc_info:
            flaky_function(succeed_after=5)  # More than max_retries
        
        assert "Failed after 3 retries" in str(exc_info.value)
        assert flaky_function.call_count == 4  # 3 retries + 1 initial attempt
    
    def test_custom_retry_on(self):
        """Test that only specified exceptions are retried."""
        class CustomError(Exception):
            pass
        
        @retry(retry_on=CustomError, max_retries=2)
        def custom_error_func():
            if not hasattr(custom_error_func, 'call_count'):
                custom_error_func.call_count = 0
            custom_error_func.call_count += 1
            raise ValueError("This should not be retried")
        
        with pytest.raises(ValueError):
            custom_error_func()
        assert custom_error_func.call_count == 1  # Should not retry
    
    def test_retry_with_jitter(self):
        """Test that jitter is applied to retry delays."""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.1,
            jitter=(0.8, 1.2),  # 20% jitter
            strategy=RetryStrategy.FIXED
        )
        
        delays = []
        
        @retry(config=config)
        def failing_func():
            failing_func.call_count = getattr(failing_func, 'call_count', 0) + 1
            raise ValueError("Always fail")
        
        # Mock time.sleep to capture delays
        with patch('time.sleep') as mock_sleep:
            mock_sleep.side_effect = lambda x: delays.append(x)
            with pytest.raises(MaxRetriesExceededError):
                failing_func()
        
        # Should have 3 retry delays
        assert len(delays) == 3
        
        # Each delay should be close to 0.1s but with jitter
        for delay in delays:
            assert 0.08 <= delay <= 0.12  # 0.1s ±20%
    
    def test_retry_callbacks(self):
        """Test that on_retry callbacks are called correctly."""
        mock_callback = MagicMock()
        
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            on_retry=mock_callback
        )
        
        @retry(config=config)
        def failing_func():
            failing_func.call_count = getattr(failing_func, 'call_count', 0) + 1
            raise ValueError("Always fail")
        
        with patch('time.sleep'):
            with pytest.raises(MaxRetriesExceededError):
                failing_func()
        
        # Callback should be called twice (for each retry)
        assert mock_callback.call_count == 2
        
        # Check callback arguments (attempt, delay, exception)
        args, _ = mock_callback.call_args_list[0]
        assert args[0] == 1  # First attempt
        assert args[1] == 0.1  # Initial delay
        assert isinstance(args[2], ValueError)
    
    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Test async retry with eventual success."""
        result = await async_flaky_function(succeed_after=2)
        assert result == "async_success"
        assert async_flaky_function.call_count == 3  # 2 failures + 1 success
    
    @pytest.mark.asyncio
    async def test_async_retry_failure(self):
        """Test async retry with eventual failure."""
        with pytest.raises(MaxRetriesExceededError):
            await async_flaky_function(succeed_after=5)  # More than max_retries
        
        assert async_flaky_function.call_count == 4  # 3 retries + 1 initial attempt
    
    @pytest.mark.asyncio
    async def test_async_retry_with_callback(self):
        """Test async retry with callback."""
        mock_callback = MagicMock()
        
        async def async_callback(attempt, delay, exception):
            mock_callback(attempt, delay, exception)
        
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            on_retry=async_callback
        )
        
        @retry_async(config=config)
        async def async_failing_func():
            async_failing_func.call_count = getattr(async_failing_func, 'call_count', 0) + 1
            raise ValueError("Async failure")
        
        with patch('asyncio.sleep'):
            with pytest.raises(MaxRetriesExceededError):
                await async_failing_func()
        
        # Callback should be called twice (for each retry)
        assert mock_callback.call_count == 2
        
        # Check callback arguments (attempt, delay, exception)
        args, _ = mock_callback.call_args_list[0]
        assert args[0] == 1  # First attempt
        assert args[1] == 0.1  # Initial delay
        assert isinstance(args[2], ValueError)
    
    def test_different_retry_strategies(self):
        """Test different retry strategies (exponential, linear, fixed)."""
        strategies = [
            (RetryStrategy.EXPONENTIAL, [0.1, 0.2, 0.4]),  # 0.1 * 2^(n-1)
            (RetryStrategy.LINEAR, [0.1, 0.2, 0.3]),      # 0.1 * n
            (RetryStrategy.FIXED, [0.1, 0.1, 0.1]),       # Always 0.1
        ]
        
        for strategy, expected_delays in strategies:
            delays = []
            
            @retry(
                max_retries=3,
                initial_delay=0.1,
                strategy=strategy,
                jitter=0  # Disable jitter for predictable tests
            )
            def strategy_test_func():
                strategy_test_func.call_count = getattr(strategy_test_func, 'call_count', 0) + 1
                if strategy_test_func.call_count < 4:  # Always fail first 3 attempts
                    raise ValueError(f"Failure {strategy_test_func.call_count}")
                return "success"
            
            # Reset call count
            if hasattr(strategy_test_func, 'call_count'):
                strategy_test_func.call_count = 0
            
            # Mock time.sleep to capture delays
            with patch('time.sleep') as mock_sleep:
                mock_sleep.side_effect = lambda x: delays.append(round(x, 2))
                with pytest.raises(MaxRetriesExceededError):
                    strategy_test_func()
            
            # Check that the delays match the expected strategy
            assert len(delays) == 3
            assert delays == expected_delays, f"Failed for strategy {strategy}"
