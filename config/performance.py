""
Performance monitoring and caching configuration.
"""
from typing import Dict, Any, Optional, Union
from pathlib import Path
from pydantic import BaseSettings, Field, validator

class PerformanceConfig(BaseSettings):
    """Performance monitoring and caching configuration."""
    
    # Performance monitoring settings
    ENABLE_PERFORMANCE_MONITORING: bool = True
    PERFORMANCE_METRICS_PORT: int = 9090
    BOTTLENECK_THRESHOLD: float = 0.1  # seconds
    
    # Caching settings
    CACHE_ENABLED: bool = True
    CACHE_BACKEND: str = 'memory'  # 'memory' or 'redis'
    CACHE_TIMEOUT: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # Redis settings (if using Redis cache)
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Query optimization
    QUERY_OPTIMIZATION_ENABLED: bool = True
    SLOW_QUERY_THRESHOLD: float = 1.0  # seconds
    
    # Resource usage limits
    MAX_MEMORY_USAGE_PERCENT: int = 90
    MAX_CPU_USAGE_PERCENT: int = 90
    
    # Logging
    LOG_PERFORMANCE_METRICS: bool = True
    METRICS_LOG_FILE: str = 'logs/performance_metrics.log'
    
    class Config:
        env_file = ".env"
        env_prefix = "PERF_"
        case_sensitive = False
    
    @validator('CACHE_BACKEND')
    def validate_cache_backend(cls, v):
        if v not in ('memory', 'redis'):
            raise ValueError("CACHE_BACKEND must be either 'memory' or 'redis'")
        return v
    
    @validator('METRICS_LOG_FILE')
    def validate_metrics_log_file(cls, v):
        # Ensure log directory exists
        log_path = Path(v).parent
        log_path.mkdir(parents=True, exist_ok=True)
        return v


def get_performance_config() -> PerformanceConfig:
    """Get performance configuration."""
    return PerformanceConfig()


# Initialize configuration
performance_config = get_performance_config()
