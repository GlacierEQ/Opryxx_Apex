"""Exponential backoff and retry utilities for handling transient failures."""
import time
import random
import logging
from typing import Callable, TypeVar, Type, Tuple, Optional, Any, List, Dict, Union
from functools import wraps
from enum import Enum, auto

logger = logging.getLogger('retry')

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

class RetryStrategy(Enum):
    """Available retry strategies."""
    EXPONENTIAL = auto()
    LINEAR = auto()
    FIXED = auto()

class MaxRetriesExceededError(Exception):
    """Raised when the maximum number of retries is exceeded."""
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        super().__init__(message)
        self.last_exception = last_exception

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 10.0,
        factor: float = 2.0,
        jitter: Union[float, Tuple[float, float]] = 0.1,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        retry_on: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        on_retry: Optional[Callable[[int, float, Exception], None]] = None,
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay between retries in seconds
            factor: Multiplier for exponential backoff
            jitter: Random jitter to add to delays (can be a float or tuple for range)
            strategy: Retry strategy to use
            retry_on: Exception type(s) to retry on
            on_retry: Callback function called before each retry
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter
        self.strategy = strategy
        self.retry_on = retry_on
        self.on_retry = on_retry
    
    def get_delay(self, attempt: int) -> float:
        """Calculate the delay for the current attempt."""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.initial_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.initial_delay * attempt
        else:  # EXPONENTIAL
            delay = self.initial_delay * (self.factor ** (attempt - 1))
        
        # Apply maximum delay
        delay = min(delay, self.max_delay)
        
        # Apply jitter
        if isinstance(self.jitter, (tuple, list)) and len(self.jitter) == 2:
            jitter_min, jitter_max = self.jitter
        else:
            jitter_min = 1.0 - float(self.jitter)
            jitter_max = 1.0 + float(self.jitter)
        
        jitter = random.uniform(jitter_min, jitter_max)
        return delay * jitter

def retry(config: Optional[RetryConfig] = None, **kwargs):
    """
    Decorator that retries the wrapped function with exponential backoff.
    
    Example:
        @retry(max_retries=3, initial_delay=0.1, max_delay=5.0)
        def might_fail():
            # ...
            pass
    """
    if config is None:
        config = RetryConfig(**kwargs)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_retries + 2):  # +1 for initial attempt
                try:
                    if attempt > 1:  # Not the first attempt
                        delay = config.get_delay(attempt - 1)
                        logger.debug(
                            f"Retry attempt {attempt}/{config.max_retries} "
                            f"after {delay:.2f}s for {func.__name__}"
                        )
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    if attempt > config.max_retries:
                        break
                        
                    if config.on_retry:
                        try:
                            config.on_retry(attempt, config.get_delay(attempt), e)
                        except Exception as retry_error:
                            logger.warning(
                                f"Error in retry callback: {str(retry_error)}", 
                                exc_info=True
                            )
                    
                    logger.warning(
                        f"Attempt {attempt}/{config.max_retries} failed: {str(e)}"
                    )
            
            # If we get here, all retries have been exhausted
            error_msg = (
                f"Failed after {config.max_retries} retries "
                f"calling {func.__name__}"
            )
            logger.error(error_msg, exc_info=last_exception)
            raise MaxRetriesExceededError(error_msg, last_exception) from last_exception
        
        return wrapper
    
    return decorator

async def retry_async(config: Optional[RetryConfig] = None, **kwargs):
    """
    Async version of the retry decorator.
    
    Example:
        @retry_async(max_retries=3, initial_delay=0.1)
        async def might_fail_async():
            # ...
            pass
    """
    if config is None:
        config = RetryConfig(**kwargs)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_retries + 2):  # +1 for initial attempt
                try:
                    if attempt > 1:  # Not the first attempt
                        delay = config.get_delay(attempt - 1)
                        logger.debug(
                            f"Async retry attempt {attempt}/{config.max_retries} "
                            f"after {delay:.2f}s for {func.__name__}"
                        )
                        await asyncio.sleep(delay)
                    
                    return await func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    if attempt > config.max_retries:
                        break
                        
                    if config.on_retry:
                        try:
                            if asyncio.iscoroutinefunction(config.on_retry):
                                await config.on_retry(attempt, config.get_delay(attempt), e)
                            else:
                                config.on_retry(attempt, config.get_delay(attempt), e)
                        except Exception as retry_error:
                            logger.warning(
                                f"Error in async retry callback: {str(retry_error)}",
                                exc_info=True
                            )
                    
                    logger.warning(
                        f"Async attempt {attempt}/{config.max_retries} failed: {str(e)}"
                    )
            
            # If we get here, all retries have been exhausted
            error_msg = (
                f"Failed after {config.max_retries} async retries "
                f"calling {func.__name__}"
            )
            logger.error(error_msg, exc_info=last_exception)
            raise MaxRetriesExceededError(error_msg, last_exception) from last_exception
        
        return wrapper
    
    return decorator
