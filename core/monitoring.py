""
System resource monitoring and performance tracking.
"""
import os
import psutil
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from prometheus_client import Gauge, start_http_server

from config.performance import performance_config

# Type aliases
ResourceUsage = Dict[str, float]
ResourceHistory = Dict[str, deque[Tuple[float, float]]]

@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    network_sent: float = 0.0
    network_recv: float = 0.0
    timestamp: float = field(default_factory=time.time)


class ResourceMonitor:
    """Monitors system resources and application performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize the resource monitor."""
        self._max_history = max_history
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._metrics_history: Dict[str, deque[Tuple[float, float]]] = {
            'cpu': deque(maxlen=max_history),
            'memory': deque(maxlen=max_history),
            'disk_read': deque(maxlen=max_history),
            'disk_write': deque(maxlen=max_history),
            'network_sent': deque(maxlen=max_history),
            'network_recv': deque(maxlen=max_history),
        }
        self._process = psutil.Process(os.getpid())
        self._last_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()
        self._start_time = time.time()
        
        # Prometheus metrics
        self._prometheus_metrics: Dict[str, Gauge] = {}
        self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        self._prometheus_metrics = {
            'cpu_percent': Gauge('system_cpu_percent', 'CPU usage percentage'),
            'memory_percent': Gauge('system_memory_percent', 'Memory usage percentage'),
            'disk_read': Gauge('system_disk_read', 'Disk read bytes per second'),
            'disk_write': Gauge('system_disk_write', 'Disk write bytes per second'),
            'network_sent': Gauge('system_network_sent', 'Network sent bytes per second'),
            'network_recv': Gauge('system_network_recv', 'Network received bytes per second'),
            'process_memory': Gauge('process_memory_bytes', 'Process memory usage in bytes'),
            'process_threads': Gauge('process_threads', 'Number of process threads'),
            'process_fds': Gauge('process_fds', 'Number of file descriptors used by process'),
        }
    
    def _update_metrics(self) -> SystemMetrics:
        """Update system metrics."""
        # Get current metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Get disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read = (disk_io.read_bytes - self._last_disk_io.read_bytes) / 1  # Per second
        disk_write = (disk_io.write_bytes - self._last_disk_io.write_bytes) / 1  # Per second
        self._last_disk_io = disk_io
        
        # Get network I/O
        net_io = psutil.net_io_counters()
        net_sent = (net_io.bytes_sent - self._last_io.bytes_sent) / 1  # Per second
        net_recv = (net_io.bytes_recv - self._last_io.bytes_recv) / 1  # Per second
        self._last_io = net_io
        
        # Create metrics object
        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_sent=net_sent,
            network_recv=net_recv
        )
        
        # Update Prometheus metrics
        self._update_prometheus_metrics(metrics)
        
        return metrics
    
    def _update_prometheus_metrics(self, metrics: SystemMetrics) -> None:
        """Update Prometheus metrics."""
        if not hasattr(self, '_prometheus_metrics'):
            return
            
        try:
            # System metrics
            self._prometheus_metrics['cpu_percent'].set(metrics.cpu_percent)
            self._prometheus_metrics['memory_percent'].set(metrics.memory_percent)
            self._prometheus_metrics['disk_read'].set(metrics.disk_io_read)
            self._prometheus_metrics['disk_write'].set(metrics.disk_io_write)
            self._prometheus_metrics['network_sent'].set(metrics.network_sent)
            self._prometheus_metrics['network_recv'].set(metrics.network_recv)
            
            # Process metrics
            self._prometheus_metrics['process_memory'].set(self._process.memory_info().rss)
            self._prometheus_metrics['process_threads'].set(self._process.num_threads())
            
            # File descriptors (Unix-like systems)
            try:
                self._prometheus_metrics['process_fds'].set(self._process.num_fds())
            except (AttributeError, psutil.AccessDenied):
                pass
                
        except Exception as e:
            # Don't let Prometheus errors break the monitoring
            import traceback
            traceback.print_exc()
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                metrics = self._update_metrics()
                timestamp = time.time()
                
                with self._lock:
                    self._metrics_history['cpu'].append((timestamp, metrics.cpu_percent))
                    self._metrics_history['memory'].append((timestamp, metrics.memory_percent))
                    self._metrics_history['disk_read'].append((timestamp, metrics.disk_io_read))
                    self._metrics_history['disk_write'].append((timestamp, metrics.disk_io_write))
                    self._metrics_history['network_sent'].append((timestamp, metrics.network_sent))
                    self._metrics_history['network_recv'].append((timestamp, metrics.network_recv))
                
                # Sleep for the interval (1 second by default)
                time.sleep(1)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Prevent tight loop on error
    
    def start(self) -> None:
        """Start the monitoring thread."""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def get_metrics(self, metric: str, time_window: Optional[float] = None) -> List[Tuple[float, float]]:
        """
        Get metrics history for a specific resource.
        
        Args:
            metric: The metric to retrieve ('cpu', 'memory', 'disk_read', 'disk_write', 'network_sent', 'network_recv')
            time_window: Optional time window in seconds to retrieve data for
            
        Returns:
            List of (timestamp, value) tuples
        """
        if metric not in self._metrics_history:
            raise ValueError(f"Unknown metric: {metric}")
            
        with self._lock:
            history = list(self._metrics_history[metric])
        
        if time_window is not None:
            cutoff = time.time() - time_window
            history = [point for point in history if point[0] >= cutoff]
            
        return history
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get the current system metrics."""
        return self._update_metrics()
    
    def get_usage_summary(self) -> Dict[str, float]:
        """Get a summary of current resource usage."""
        metrics = self.get_current_metrics()
        
        return {
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'disk_read_mb': metrics.disk_io_read / (1024 * 1024),
            'disk_write_mb': metrics.disk_io_write / (1024 * 1024),
            'network_sent_mb': metrics.network_sent / (1024 * 1024),
            'network_recv_mb': metrics.network_recv / (1024 * 1024),
            'uptime_seconds': time.time() - self._start_time,
        }
    
    def check_resource_limits(self) -> Dict[str, str]:
        """Check if any resource limits are being approached."""
        issues = {}
        metrics = self.get_current_metrics()
        
        if metrics.cpu_percent > performance_config.MAX_CPU_USAGE_PERCENT:
            issues['cpu'] = f"High CPU usage: {metrics.cpu_percent:.1f}%"
            
        if metrics.memory_percent > performance_config.MAX_MEMORY_USAGE_PERCENT:
            issues['memory'] = f"High memory usage: {metrics.memory_percent:.1f}%"
        
        # Check disk space
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:  # 90% disk usage threshold
                    issues[f'disk_{partition.mountpoint}'] = (
                        f"High disk usage on {partition.mountpoint}: {usage.percent:.1f}%"
                    )
            except Exception:
                continue
                
        return issues


def start_prometheus_server(port: int = 8000) -> None:
    """Start a Prometheus metrics server."""
    try:
        start_http_server(port)
        print(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        print(f"Failed to start Prometheus metrics server: {e}")


# Global instance
resource_monitor: Optional[ResourceMonitor] = None

def get_resource_monitor() -> ResourceMonitor:
    """Get or create the global resource monitor instance."""
    global resource_monitor
    if resource_monitor is None:
        resource_monitor = ResourceMonitor()
    return resource_monitor


def start_monitoring() -> None:
    """Start system resource monitoring."""
    monitor = get_resource_monitor()
    monitor.start()
    
    # Start Prometheus server if enabled
    if performance_config.LOG_PERFORMANCE_METRICS:
        start_prometheus_server(performance_config.PERFORMANCE_METRICS_PORT)


def stop_monitoring() -> None:
    """Stop system resource monitoring."""
    global resource_monitor
    if resource_monitor is not None:
        resource_monitor.stop()
        resource_monitor = None
