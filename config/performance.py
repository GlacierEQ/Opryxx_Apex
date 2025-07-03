""
Performance monitoring and caching configuration.
"""
    """Performance monitoring and caching configuration."""
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