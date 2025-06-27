"""
Async utilities for OPRYXX system.
Provides decorators and context managers for async operations and caching.
"""
import asyncio
import functools
import json
import os
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from pathlib import Path
import aiofiles
from cryptography.fernet import Fernet
from hashlib import sha256
import logging

T = TypeVar('T')

# Initialize logger
logger = logging.getLogger(__name__)

# Global cache dictionary
_cache: Dict[str, Any] = {}
_cache_expiry: Dict[str, datetime] = {}

# Encryption key management
def generate_encryption_key() -> bytes:
    """Generate a new encryption key."""
    return Fernet.generate_key()

def load_or_generate_key(key_path: Union[str, Path]) -> bytes:
    """Load encryption key from file or generate a new one if not exists."""
    key_path = Path(key_path)
    if key_path.exists():
        return key_path.read_bytes()
    
    key = generate_encryption_key()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    return key

# Initialize encryption
KEY_PATH = Path("c:/CATHEDRAL/OPRYXX_LOGS/config/encryption.key")
ENCRYPTION_KEY = load_or_generate_key(KEY_PATH)
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> bytes:
    """Encrypt string data."""
    return cipher_suite.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt data to string."""
    return cipher_suite.decrypt(encrypted_data).decode('utf-8')

def async_cache(ttl: int = 300):
    """
    Async cache decorator with TTL (time-to-live) in seconds.
    
    Args:
        ttl: Time in seconds to keep the cache entry
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = sha256(cache_key.encode()).hexdigest()
            
            # Check if cache is valid
            current_time = datetime.now()
            if (cache_key in _cache and 
                cache_key in _cache_expiry and 
                _cache_expiry[cache_key] > current_time):
                return _cache[cache_key]
                
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            _cache[cache_key] = result
            _cache_expiry[cache_key] = current_time + timedelta(seconds=ttl)
            
            return result
        return wrapper
    return decorator

async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """Run synchronous function in executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, functools.partial(func, *args, **kwargs)
    )

class AsyncFileIO:
    """Asynchronous file I/O operations."""
    
    @staticmethod
    async def read_file(file_path: Union[str, Path], binary: bool = False) -> Union[str, bytes]:
        """Read file asynchronously."""
        mode = 'rb' if binary else 'r'
        async with aiofiles.open(file_path, mode=mode) as f:
            return await f.read()
    
    @staticmethod
    async def write_file(file_path: Union[str, Path], 
                        content: Union[str, bytes], 
                        binary: bool = False) -> None:
        """Write file asynchronously."""
        mode = 'wb' if binary or isinstance(content, bytes) else 'w'
        async with aiofiles.open(file_path, mode=mode) as f:
            await f.write(content)
    
    @staticmethod
    async def read_json(file_path: Union[str, Path]) -> Any:
        """Read JSON file asynchronously."""
        content = await AsyncFileIO.read_file(file_path, binary=False)
        return json.loads(content)
    
    @staticmethod
    async def write_json(file_path: Union[str, Path], 
                        data: Any, 
                        indent: int = 4) -> None:
        """Write JSON file asynchronously."""
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        await AsyncFileIO.write_file(file_path, content)

class SecureConfig:
    """Secure configuration manager with encryption."""
    
    def __init__(self, config_path: Union[str, Path]):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
    
    async def load(self) -> None:
        """Load configuration from encrypted file."""
        try:
            if self.config_path.exists():
                encrypted_data = await AsyncFileIO.read_file(self.config_path, binary=True)
                decrypted_data = decrypt_data(encrypted_data)
                self._config = json.loads(decrypted_data)
            else:
                self._config = {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._config = {}
    
    async def save(self) -> None:
        """Save configuration to encrypted file."""
        try:
            config_str = json.dumps(self._config, indent=4)
            encrypted_data = encrypt_data(config_str)
            await AsyncFileIO.write_file(self.config_path, encrypted_data, binary=True)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        self._config[key] = value
    
    def delete(self, key: str) -> None:
        """Delete configuration key."""
        if key in self._config:
            del self._config[key]
