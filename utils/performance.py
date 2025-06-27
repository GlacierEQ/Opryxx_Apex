"""
Performance monitoring and optimization utilities for OPRYXX.
Tracks system metrics, performance bottlenecks, and provides optimization suggestions.
"""
import time
import psutil
import platform
import os
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import statistics
import functools
import threading
import tracemalloc
from pathlib import Path
import json

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Container for system metrics."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_io_read: float  # MB/s
    disk_io_write: float  # MB/s
    network_sent: float  # MB/s
    network_recv: float  # MB/s
    process_cpu: float  # Process CPU %
    process_memory: float  # Process memory in MB
    process_threads: int
    process_handles: int

@dataclass
class PerformanceStats:
    """Performance statistics over a time window."""
    avg_cpu: float = 0.0
    max_cpu: float = 0.0
    avg_memory: float = 0.0
    max_memory: float = 0.0
    avg_disk_read: float = 0.0
    avg_disk_write: float = 0.0
    max_disk_read: float = 0.0
    max_disk_write: float = 0.0
    avg_network_sent: float = 0.0
    avg_network_recv: float = 0.0
    max_network_sent: float = 0.0
    max_network_recv: float = 0.0
    process_avg_cpu: float = 0.0
    process_max_cpu: float = 0.0
    process_avg_memory: float = 0.0  # in MB
    process_max_memory: float = 0.0  # in MB
    process_threads: int = 0
    process_handles: int = 0

class PerformanceMonitor:
    """Monitors system and application performance metrics."""
    
    def __init__(self, window_size: int = 60, interval: float = 1.0):
        """
        Initialize the performance monitor.
        
        Args:
            window_size: Number of samples to keep in memory
            interval: Sampling interval in seconds
        """
        self.window_size = window_size
        self.interval = interval
        self.metrics_history = deque(maxlen=window_size)
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._last_io = psutil.disk_io_counters()
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()
        self.process = psutil.Process()
        self._callbacks = []
        self._lock = threading.Lock()
        self._started = False
        
        # Track function execution times
        self.function_timings = {}
        
        # Track system info
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "system": {
                "os": f"{platform.system()} {platform.release()} {platform.version()}",
                "hostname": platform.node(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
            "cpu": {
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_freq": psutil.cpu_freq().max if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq() else None,
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "used_percent": psutil.virtual_memory().percent,
            },
            "disks": [
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(psutil.disk_usage(part.mountpoint).total / (1024**3), 2),
                    "used_gb": round(psutil.disk_usage(part.mountpoint).used / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage(part.mountpoint).free / (1024**3), 2),
                    "percent_used": psutil.disk_usage(part.mountpoint).percent,
                }
                for part in psutil.disk_partitions(all=False)
            ],
            "network": {
                "hostname": platform.node(),
                "ip_addresses": [
                    addr.address 
                    for iface, addrs in psutil.net_if_addrs().items() 
                    for addr in addrs 
                    if addr.family == 2  # AF_INET
                ],
                "interfaces": list(psutil.net_if_addrs().keys()),
            },
        }
    
    def start(self) -> None:
        """Start the performance monitoring thread."""
        if self._started:
            logger.warning("Performance monitor is already running")
            return
            
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="PerformanceMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        self._started = True
        logger.info("Performance monitoring started")
    
    def stop(self) -> None:
        """Stop the performance monitoring thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self._started = False
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        logger.error(f"Error in performance callback: {e}")
                
                # Sleep for the interval, but check for stop event frequently
                for _ in range(int(self.interval * 10)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(1.0)  # Prevent tight loop on error
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect system and process metrics."""
        now = time.time()
        time_diff = now - self._last_time
        
        # Get CPU and memory
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Get disk I/O
        io = psutil.disk_io_counters()
        disk_read = (io.read_bytes - self._last_io.read_bytes) / (1024 * 1024) / time_diff  # MB/s
        disk_write = (io.write_bytes - self._last_io.write_bytes) / (1024 * 1024) / time_diff  # MB/s
        
        # Get network I/O
        net = psutil.net_io_counters()
        net_sent = (net.bytes_sent - self._last_net.bytes_sent) / (1024 * 1024) / time_diff  # MB/s
        net_recv = (net.bytes_recv - self._last_net.bytes_recv) / (1024 * 1024) / time_diff  # MB/s
        
        # Get process info
        process = self.process
        with process.oneshot():
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss / (1024 * 1024)  # MB
            process_threads = process.num_threads()
            process_handles = process.num_handles()
        
        # Update last values
        self._last_io = io
        self._last_net = net
        self._last_time = now
        
        return SystemMetrics(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_sent=net_sent,
            network_recv=net_recv,
            process_cpu=process_cpu,
            process_memory=process_memory,
            process_threads=process_threads,
            process_handles=process_handles
        )
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]
    
    def get_stats(self, window_seconds: int = 60) -> PerformanceStats:
        """Get performance statistics over a time window."""
        with self._lock:
            if not self.metrics_history:
                return PerformanceStats()
                
            now = time.time()
            recent_metrics = [
                m for m in self.metrics_history
                if now - m.timestamp <= window_seconds
            ]
            
            if not recent_metrics:
                return PerformanceStats()
            
            stats = PerformanceStats()
            
            # Calculate averages and maximums
            stats.avg_cpu = statistics.mean(m.cpu_percent for m in recent_metrics)
            stats.max_cpu = max(m.cpu_percent for m in recent_metrics)
            
            stats.avg_memory = statistics.mean(m.memory_percent for m in recent_metrics)
            stats.max_memory = max(m.memory_percent for m in recent_metrics)
            
            stats.avg_disk_read = statistics.mean(m.disk_io_read for m in recent_metrics)
            stats.avg_disk_write = statistics.mean(m.disk_io_write for m in recent_metrics)
            stats.max_disk_read = max(m.disk_io_read for m in recent_metrics)
            stats.max_disk_write = max(m.disk_io_write for m in recent_metrics)
            
            stats.avg_network_sent = statistics.mean(m.network_sent for m in recent_metrics)
            stats.avg_network_recv = statistics.mean(m.network_recv for m in recent_metrics)
            stats.max_network_sent = max(m.network_sent for m in recent_metrics)
            stats.max_network_recv = max(m.network_recv for m in recent_metrics)
            
            stats.process_avg_cpu = statistics.mean(m.process_cpu for m in recent_metrics)
            stats.process_max_cpu = max(m.process_cpu for m in recent_metrics)
            
            stats.process_avg_memory = statistics.mean(m.process_memory for m in recent_metrics)
            stats.process_max_memory = max(m.process_memory for m in recent_metrics)
            
            stats.process_threads = recent_metrics[-1].process_threads
            stats.process_handles = recent_metrics[-1].process_handles
            
            return stats
    
    def add_callback(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Add a callback to be called with new metrics."""
        with self._lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Remove a callback."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                # Record timing
                func_name = f"{func.__module__}.{func.__qualname__}"
                if func_name not in self.function_timings:
                    self.function_timings[func_name] = {
                        'count': 0,
                        'total_time': 0.0,
                        'min_time': float('inf'),
                        'max_time': 0.0,
                        'last_time': 0.0,
                    }
                
                stats = self.function_timings[func_name]
                stats['count'] += 1
                stats['total_time'] += duration
                stats['min_time'] = min(stats['min_time'], duration)
                stats['max_time'] = max(stats['max_time'], duration)
                stats['last_time'] = duration
                
                # Log slow functions
                if duration > 1.0:  # Log if function takes more than 1 second
                    logger.warning(
                        f"Slow function call: {func_name} took {duration:.3f}s "
                        f"(min: {stats['min_time']:.3f}s, max: {stats['max_time']:.3f}s, "
                        f"avg: {stats['total_time']/stats['count']:.3f}s)"
                    )
        return wrapper

# Global instance for easy access
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance."""
    return performance_monitor.time_function(func)
