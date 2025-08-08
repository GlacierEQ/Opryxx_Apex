"""
OPRYXX System Monitor
Implements memory leak detection and performance monitoring according to OPRYXX standards.
Integrated with Cascade for enhanced monitoring and control.
"""
import psutil
import time
import threading
import logging
import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Deque
from collections import deque
from cascade_integration import CascadeIntegration

@dataclass
class MemoryStats:
    """Track memory usage statistics."""
    current_mb: float = 0.0
    peak_mb: float = 0.0
    usage_percent: float = 0.0
    timestamp: float = 0.0
    leak_rate_mb_min: float = 0.0  # Memory leak rate in MB per minute
    trend: str = "stable"  # 'increasing', 'decreasing', or 'stable'

@dataclass
class PerformanceMetrics:
    """Track system performance metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_io: Tuple[float, float] = (0.0, 0.0)  # read, write in MB/s
    network_io: Tuple[float, float] = (0.0, 0.0)  # sent, recv in MB/s
    timestamp: float = 0.0

class SystemMonitor:
    """
    Monitor system resources and detect issues with Cascade integration.
    Implements OPRYXX standards for monitoring and stability.
    """
    
    # OPRYXX Compliance Constants
    MEMORY_LEAK_THRESHOLD_MB = 10  # 10MB increase per minute (OPRYXX standard)
    PERFORMANCE_SCORE_WEIGHTS = {
        'cpu': 0.4,
        'memory': 0.3,
        'disk': 0.2,
        'network': 0.1
    }
    
    # Recovery settings
    MAX_RETRIES = 3
    RECOVERY_DELAY = 5.0  # seconds
    
    # Performance thresholds (0-100 scale)
    CRITICAL_THRESHOLD = 30
    WARNING_THRESHOLD = 60
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.memory_history: Deque[MemoryStats] = deque(maxlen=60)  # Store 5 minutes of history at 5s intervals
        self.performance_history: Deque[PerformanceMetrics] = deque(maxlen=60)
        self.logger = logging.getLogger('OPRYXX.Monitor')
        
        # Initialize metrics
        self.memory_stats = MemoryStats()
        self.performance_metrics = PerformanceMetrics()
        
        # Initialize Cascade integration
        self.cascade = CascadeIntegration()
        self.cascade.register_callback('on_error', self._on_cascade_error)
        self.cascade.register_callback('on_update', self._on_cascade_update)
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = 0.0
        self.recovery_attempts = 0
        
        # Performance tracking
        self.performance_scores = deque(maxlen=60)  # Track performance over time
        self.performance_trend = 'stable'  # 'improving', 'degrading', or 'stable'
        
    def start(self) -> bool:
        """Start the monitoring thread and Cascade connection."""
        if self.running:
            return False
            
        try:
            # Start Cascade connection
            if not self.cascade.connect():
                self.logger.error("Failed to connect to Cascade")
                return False
                
            self.running = True
            self.thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="SystemMonitor"
            )
            self.thread.start()
            self.logger.info("System monitoring started with Cascade integration")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            self.running = False
            return False
    
    def stop(self) -> None:
        """Stop the monitoring thread and clean up resources."""
        self.running = False
        
        # Stop monitoring thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            
        # Disconnect from Cascade
        try:
            self.cascade.disconnect()
        except Exception as e:
            self.logger.error(f"Error disconnecting from Cascade: {e}")
            
        self.logger.info("System monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop with error handling and recovery."""
        consecutive_errors = 0
        
        while self.running and consecutive_errors < self.MAX_RETRIES:
            try:
                # Update system metrics
                self._update_memory_stats()
                self._update_performance_metrics()
                
                # Check for and handle issues
                self._check_for_issues()
                
                # Calculate performance score
                score = self._calculate_performance_score()
                self.performance_scores.append(score)
                self._update_performance_trend()
                
                # Update Cascade with current status
                self._update_cascade_status()
                
                # Reset error counter on successful iteration
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                self.error_count += 1
                self.last_error_time = time.time()
                
                error_msg = f"Error in monitor loop (attempt {consecutive_errors}/{self.MAX_RETRIES}): {e}"
                self.logger.error(error_msg, exc_info=True)
                
                # Attempt recovery if possible
                if consecutive_errors < self.MAX_RETRIES:
                    self._attempt_recovery()
                    time.sleep(self.RECOVERY_DELAY)
                else:
                    self.logger.critical("Max retries reached, stopping monitor")
                    self.running = False
                    self._emergency_shutdown()
                    break
            
            # Normal sleep between iterations
            time.sleep(self.check_interval)
    
    def _update_memory_stats(self) -> None:
        """Update memory usage statistics."""
        process = psutil.Process()
        with process.oneshot():
            mem_info = process.memory_info()
            self.memory_stats = MemoryStats(
                current_mb=mem_info.rss / (1024 * 1024),
                peak_mb=process.memory_info().vms / (1024 * 1024),
                usage_percent=process.memory_percent(),
                timestamp=time.time()
            )
    
    def _update_performance_metrics(self) -> None:
        """Update system performance metrics."""
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
            timestamp=time.time()
        )
        
        # Add to history
        self.memory_history.append(self.memory_stats)
        self.performance_history.append(self.performance_metrics)
    
    def _check_for_issues(self) -> None:
        """Check for potential issues."""
        # Check for memory leaks
        self._check_memory_leak()
    
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
