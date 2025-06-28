""
Performance monitoring and optimization utilities.
"""
import time
import functools
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, median, stdev
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from prometheus_client import start_http_server, Counter, Gauge, Histogram, Summary

# Type variable for generic function wrapping
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class PerformanceStats:
    """Performance statistics for a single function or operation."""
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_call_time: Optional[float] = None
    call_history: deque[float] = field(default_factory=lambda: deque(maxlen=100))
    
    def update(self, execution_time: float) -> None:
        """Update statistics with a new execution time."""
        self.call_count += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.last_call_time = time.time()
        self.call_history.append(execution_time)
    
    @property
    def avg_time(self) -> float:
        """Calculate average execution time."""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0
    
    @property
    def median_time(self) -> float:
        """Calculate median execution time."""
        return median(self.call_history) if self.call_history else 0.0
    
    @property
    def std_dev(self) -> float:
        """Calculate standard deviation of execution times."""
        return stdev(self.call_history) if len(self.call_history) > 1 else 0.0


class PerformanceMonitor:
    """Performance monitoring and optimization utility."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._stats: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self._lock = Lock()
        self._enabled = True
        self._logger = logging.getLogger(__name__)
        self._metrics_enabled = False
        self._prometheus_port = 9090
        self._initialized = True
    
    def monitor(self, name: Optional[str] = None) -> Callable[[F], F]:
        ""
        Decorator to monitor function execution time.
        
        Args:
            name: Optional name for the monitored function. If not provided, 
                  the function's qualified name will be used.
        """
        def decorator(func: F) -> F:
            nonlocal name
            if name is None:
                name = f"{func.__module__}.{func.__qualname__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)
                    
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.perf_counter() - start_time
                    self.record_metric(name, execution_time)
            
            return cast(F, wrapper)
        return decorator
    
    def record_metric(self, name: str, execution_time: float) -> None:
        """Record a performance metric."""
        if not self._enabled:
            return
            
        with self._lock:
            self._stats[name].update(execution_time)
        
        if self._metrics_enabled:
            self._update_prometheus_metrics(name, execution_time)
    
    def _update_prometheus_metrics(self, name: str, execution_time: float) -> None:
        """Update Prometheus metrics."""
        # This would be implemented with actual Prometheus client calls
        pass
    
    def enable(self) -> None:
        """Enable performance monitoring."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable performance monitoring."""
        self._enabled = False
    
    def get_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            if name:
                stats = self._stats.get(name)
                return vars(stats) if stats else {}
            return {k: vars(v) for k, v in self._stats.items()}
    
    def reset_stats(self, name: Optional[str] = None) -> None:
        """Reset performance statistics."""
        with self._lock:
            if name and name in self._stats:
                self._stats[name] = PerformanceStats()
            elif name is None:
                self._stats.clear()
    
    def enable_prometheus_metrics(self, port: int = 9090) -> None:
        """Enable Prometheus metrics endpoint."""
        if self._metrics_enabled:
            return
            
        try:
            start_http_server(port)
            self._prometheus_port = port
            self._metrics_enabled = True
            self._logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            self._logger.error(f"Failed to start Prometheus metrics server: {e}")
    
    def get_bottlenecks(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks.
        
        Args:
            threshold: Minimum average execution time (in seconds) to consider as a bottleneck.
            
        Returns:
            List of dictionaries containing bottleneck information.
        """
        bottlenecks = []
        
        with self._lock:
            for name, stats in self._stats.items():
                if stats.avg_time >= threshold:
                    bottlenecks.append({
                        'name': name,
                        'avg_time': stats.avg_time,
                        'call_count': stats.call_count,
                        'total_time': stats.total_time,
                        'min_time': stats.min_time,
                        'max_time': stats.max_time,
                        'median_time': stats.median_time,
                        'std_dev': stats.std_dev
                    })
        
        # Sort by total time (most impactful first)
        return sorted(bottlenecks, key=lambda x: x['total_time'], reverse=True)


# Global instance
performance_monitor = PerformanceMonitor()


def monitor_performance(name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to monitor function execution time using the global performance monitor.
    
    Example:
        @monitor_performance("my_expensive_operation")
        def my_function():
            # ...
            pass
    """
    return performance_monitor.monitor(name)


def get_performance_stats(name: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics from the global performance monitor."""
    return performance_monitor.get_stats(name)


def reset_performance_stats(name: Optional[str] = None) -> None:
    """Reset performance statistics in the global performance monitor."""
    performance_monitor.reset_stats(name)


def enable_performance_monitoring() -> None:
    """Enable the global performance monitor."""
    performance_monitor.enable()


def disable_performance_monitoring() -> None:
    """Disable the global performance monitor."""
    performance_monitor.disable()


def start_performance_metrics_server(port: int = 9090) -> None:
    """Start the Prometheus metrics server."""
    performance_monitor.enable_prometheus_metrics(port)
