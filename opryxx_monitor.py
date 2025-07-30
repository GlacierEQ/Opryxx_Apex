"""
OPRYXX System Monitor
Implements memory leak detection and performance monitoring according to OPRYXX standards.
"""
import psutil
import time
import threading
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import deque

@dataclass
class MemoryStats:
    """Track memory usage statistics."""
    current_mb: float = 0.0
    peak_mb: float = 0.0
    usage_percent: float = 0.0
    timestamp: float = 0.0

@dataclass
class PerformanceMetrics:
    """Track system performance metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_io: Tuple[float, float] = (0.0, 0.0)  # read, write in MB/s
    network_io: Tuple[float, float] = (0.0, 0.0)  # sent, recv in MB/s
    timestamp: float = 0.0

class SystemMonitor:
    """Monitor system resources and detect issues."""
    
    MEMORY_LEAK_THRESHOLD_MB = 10  # 10MB increase per minute
    PERFORMANCE_SCORE_WEIGHTS = {
        'cpu': 0.4,
        'memory': 0.3,
        'disk': 0.2,
        'network': 0.1
    }
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.memory_history = deque(maxlen=60)  # Store 5 minutes of history at 5s intervals
        self.performance_history = deque(maxlen=60)
        self.logger = logging.getLogger('OPRYXX.Monitor')
        
        # Initialize metrics
        self.memory_stats = MemoryStats()
        self.performance_metrics = PerformanceMetrics()
        
    def start(self) -> None:
        """Start the monitoring thread."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("System monitor started")
    
    def stop(self) -> None:
        """Stop the monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.info("System monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        disk_io_last = psutil.disk_io_counters()
        net_io_last = psutil.net_io_counters()
        
        while self.running:
            try:
                # Get current timestamp
                now = time.time()
                
                # Update memory stats
                process = psutil.Process()
                with process.oneshot():
                    mem_info = process.memory_info()
                    self.memory_stats = MemoryStats(
                        current_mb=mem_info.rss / (1024 * 1024),
                        peak_mb=process.memory_info().vms / (1024 * 1024),
                        usage_percent=process.memory_percent(),
                        timestamp=now
                    )
                
                # Check for memory leaks
                self._check_memory_leak()
                
                # Get system-wide performance metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Calculate disk I/O rates
                disk_io = psutil.disk_io_counters()
                disk_read = (disk_io.read_bytes - disk_io_last.read_bytes) / (1024 * 1024)  # MB
                disk_write = (disk_io.write_bytes - disk_io_last.write_bytes) / (1024 * 1024)
                disk_io_last = disk_io
                
                # Calculate network I/O rates
                net_io = psutil.net_io_counters()
                net_sent = (net_io.bytes_sent - net_io_last.bytes_sent) / (1024 * 1024)  # MB
                net_recv = (net_io.bytes_recv - net_io_last.bytes_recv) / (1024 * 1024)
                net_io_last = net_io
                
                # Store performance metrics
                self.performance_metrics = PerformanceMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=psutil.virtual_memory().percent,
                    disk_io=(disk_read, disk_write),
                    network_io=(net_sent, net_recv),
                    timestamp=now
                )
                
                # Add to history
                self.memory_history.append(self.memory_stats)
                self.performance_history.append(self.performance_metrics)
                
                # Calculate performance score
                score = self.calculate_performance_score()
                if score < 60:  # Below threshold
                    self.logger.warning(f"Low performance score: {score:.1f}")
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
            
            # Wait for next interval
            time.sleep(max(0, self.check_interval - (time.time() - now)))
    
    def _check_memory_leak(self) -> None:
        """Check for potential memory leaks."""
        if len(self.memory_history) < 2:
            return
            
        # Check if memory is consistently increasing
        recent_increase = 0
        for i in range(1, min(6, len(self.memory_history))):  # Check last 5 samples
            recent_increase += (self.memory_history[-1].current_mb - 
                              self.memory_history[-i-1].current_mb) / i
        
        if recent_increase > self.MEMORY_LEAK_THRESHOLD_MB:
            self.logger.warning(
                f"Potential memory leak detected: {recent_increase:.2f}MB increase in last minute"
            )
    
    def calculate_performance_score(self) -> float:
        """Calculate overall system performance score (0-100)."""
        if not self.performance_history:
            return 100.0
            
        latest = self.performance_history[-1]
        
        # Calculate individual component scores (lower is better for IO)
        cpu_score = 100 - min(latest.cpu_percent, 100)
        mem_score = 100 - latest.memory_percent
        
        # Disk score based on IO wait (simplified)
        disk_io = sum(latest.disk_io)
        disk_score = 100 - min(disk_io * 10, 100)  # Scale factor for MB/s to percentage
        
        # Network score based on utilization (simplified)
        net_io = sum(latest.network_io)
        net_score = 100 - min(net_io * 50, 100)  # Scale factor for MB/s to percentage
        
        # Weighted average of all scores
        total_score = (
            cpu_score * self.PERFORMANCE_SCORE_WEIGHTS['cpu'] +
            mem_score * self.PERFORMANCE_SCORE_WEIGHTS['memory'] +
            disk_score * self.PERFORMANCE_SCORE_WEIGHTS['disk'] +
            net_score * self.PERFORMANCE_SCORE_WEIGHTS['network']
        )
        
        return max(0, min(100, total_score))
    
    def get_system_status(self) -> Dict:
        """Get current system status summary."""
        if not self.performance_history or not self.memory_history:
            return {"status": "initializing", "score": 0.0}
            
        score = self.calculate_performance_score()
        
        return {
            "status": "ok" if score >= 60 else "warning" if score >= 30 else "critical",
            "score": score,
            "cpu_percent": self.performance_metrics.cpu_percent,
            "memory_mb": self.memory_stats.current_mb,
            "memory_percent": self.memory_stats.usage_percent,
            "disk_io": self.performance_metrics.disk_io,
            "network_io": self.performance_metrics.network_io,
            "timestamp": self.performance_metrics.timestamp
        }
