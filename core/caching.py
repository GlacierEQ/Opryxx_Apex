""
Advanced caching system with support for multiple backends and cache invalidation strategies.
"""
import functools
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from typing_extensions import ParamSpec

# Type variables for generic function wrapping
T = TypeVar('T')
P = ParamSpec('P')
R = TypeVar('R')

# Default cache settings
DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_CACHE_SIZE = 1000


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Any:
        """Get a value from the cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set a value in the cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all items from the cache."""
        pass
    
    @abstractmethod
    def has_key(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend using a dictionary."""
    
    def __init__(self, max_size: int = MAX_CACHE_SIZE):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Any:
        with self._lock:
            if key not in self._cache:
                return None
                
            item = self._cache[key]
            
            # Check if the item has expired
            if item['expires'] is not None and item['expires'] < time.time():
                del self._cache[key]
                return None
                
            return item['value']
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        with self._lock:
            # Enforce max size by removing oldest items if needed
            if len(self._cache) >= self._max_size and key not in self._cache:
                # Remove the oldest item
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            expires = None
            if timeout is not None:
                expires = time.time() + timeout
            
            self._cache[key] = {
                'value': value,
                'expires': expires,
                'created': time.time()
            }
    
    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
    
    def has_key(self, key: str) -> bool:
        with self._lock:
            if key not in self._cache:
                return False
                
            # Check if the item has expired
            item = self._cache[key]
            if item['expires'] is not None and item['expires'] < time.time():
                del self._cache[key]
                return False
                
            return True


class RedisCache(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs):
        import redis
        self._client = redis.Redis(host=host, port=port, db=db, **kwargs)
    
    def get(self, key: str) -> Any:
        value = self._client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.decode('utf-8')
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        if not isinstance(value, (str, int, float, bool, type(None))):
            value = json.dumps(value)
        self._client.set(key, value, ex=timeout)
    
    def delete(self, key: str) -> None:
        self._client.delete(key)
    
    def clear(self) -> None:
        self._client.flushdb()
    
    def has_key(self, key: str) -> bool:
        return bool(self._client.exists(key))


class CacheManager:
    """Cache manager that supports multiple backends and namespacing."""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        self._backend = backend or MemoryCache()
        self._logger = logging.getLogger(__name__)
    
    def get_backend(self) -> CacheBackend:
        """Get the current cache backend."""
        return self._backend
    
    def set_backend(self, backend: CacheBackend) -> None:
        """Set the cache backend."""
        self._backend = backend
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the cache."""
        try:
            value = self._backend.get(key)
            if value is None:
                return default
            return value
        except Exception as e:
            self._logger.error(f"Cache get failed for key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = DEFAULT_TIMEOUT) -> None:
        """Set a value in the cache."""
        try:
            self._backend.set(key, value, timeout=timeout)
        except Exception as e:
            self._logger.error(f"Cache set failed for key {key}: {e}")
    
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        try:
            self._backend.delete(key)
        except Exception as e:
            self._logger.error(f"Cache delete failed for key {key}: {e}")
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        try:
            self._backend.clear()
        except Exception as e:
            self._logger.error(f"Cache clear failed: {e}")
    
    def has_key(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        try:
            return self._backend.has_key(key)
        except Exception as e:
            self._logger.error(f"Cache has_key failed for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, default: Any, timeout: Optional[int] = DEFAULT_TIMEOUT) -> Any:
        """
        Get a value from the cache, or set it if it doesn't exist.
        
        Args:
            key: Cache key
            default: Default value to set if key doesn't exist
            timeout: Timeout in seconds (default: 300)
            
        Returns:
            The cached value or the default value if not found
        """
        value = self.get(key)
        if value is None:
            self.set(key, default, timeout=timeout)
            return default
        return value
    
    def cache_result(
        self, 
        key: Optional[str] = None, 
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        unless: Optional[Callable[..., bool]] = None
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Decorator to cache the result of a function.
        
        Args:
            key: Optional cache key (default: function name + args)
            timeout: Cache timeout in seconds
            unless: Optional callable that returns True to bypass caching
        """
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Skip caching if unless condition is met
                if unless is not None and unless(*args, **kwargs):
                    return func(*args, **kwargs)
                
                # Generate cache key if not provided
                cache_key = key or self._generate_cache_key(func, *args, **kwargs)
                
                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Call the function and cache the result
                result = func(*args, **kwargs)
                self.set(cache_key, result, timeout=timeout)
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func: Callable, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key from function and arguments."""
        # Create a hash of the function name and arguments
        key_parts = [
            func.__module__,
            func.__qualname__,
            json.dumps(args, sort_keys=True, default=str),
            json.dumps(kwargs, sort_keys=True, default=str),
        ]
        
        key_str = "".join(str(part) for part in key_parts)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()


# Default cache instance
cache = CacheManager()

# Shortcut functions
def get_cache() -> CacheManager:
    """Get the default cache instance."""
    return cache

def cached(
    key: Optional[str] = None, 
    timeout: Optional[int] = DEFAULT_TIMEOUT,
    unless: Optional[Callable[..., bool]] = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to cache the result of a function using the default cache.
    
    Example:
        @cached(timeout=60)
        def expensive_operation(x, y):
            # ...
            return result
    """
    return cache.cache_result(key=key, timeout=timeout, unless=unless)

def clear_cache() -> None:
    """Clear the default cache."""
    cache.clear()

def delete_key(key: str) -> None:
    """Delete a key from the default cache."""
    cache.delete(key)

def get_cached_or_call(
    key: str, 
    func: Callable[P, R], 
    *args: P.args, 
    timeout: Optional[int] = DEFAULT_TIMEOUT,
    **kwargs: P.kwargs
) -> R:
    """
    Get a value from the cache or call the function if not found.
    
    Args:
        key: Cache key
        func: Function to call if key not in cache
        *args: Positional arguments to pass to the function
        timeout: Cache timeout in seconds
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The cached or computed value
    """
    value = cache.get(key)
    if value is None:
        value = func(*args, **kwargs)
        cache.set(key, value, timeout=timeout)
    return value
