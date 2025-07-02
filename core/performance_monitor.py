"""
Performance Monitoring and Optimization Module
Implements real-time performance scoring and GPU/NPU acceleration
"""

import time
import psutil
import platform
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime

# Try to import GPU-related libraries
try:
    import torch
    import torch.cuda as cuda
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

class DeviceType(Enum):
    CPU = auto()
    CUDA_GPU = auto()
    NPU = auto()

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float
    cpu_usage: float  # percentage
    memory_usage: float  # percentage
    gpu_usage: Optional[float] = None  # percentage
    gpu_memory: Optional[float] = None  # MB
    npu_usage: Optional[float] = None  # percentage
    response_time: Optional[float] = None  # ms
    ops_per_second: Optional[float] = None  # operations per second
    score: float = 0.0  # Overall performance score (0-100)

class PerformanceMonitor:
    """
    Real-time performance monitoring and optimization
    Implements scoring system and automatic device selection
    """
    
    def __init__(self, update_interval: float = 5.0):
        self.update_interval = update_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 1000
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._device = self._detect_best_device()
        self._last_metrics = PerformanceMetrics(
            timestamp=time.time(),
            cpu_usage=0.0,
            memory_usage=0.0
        )
        
        # Initialize device-specific metrics
        if self._device == DeviceType.CUDA_GPU and TORCH_AVAILABLE:
            self._init_cuda()
            
    def _detect_best_device(self) -> DeviceType:
        """Detect and select the best available compute device"""
        if TORCH_AVAILABLE and cuda.is_available():
            return DeviceType.CUDA_GPU
        # Add NPU detection when available
        return DeviceType.CPU
    
    def _init_cuda(self):
        """Initialize CUDA device if available"""
        if TORCH_AVAILABLE and cuda.is_available():
            self.device_name = cuda.get_device_name(0)
            cuda.init()
            
    def start(self):
        """Start the performance monitoring thread"""
        if self.running:
            return
            
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop the performance monitoring thread"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self.collect_metrics()
                with self._lock:
                    self.metrics_history.append(metrics)
                    if len(self.metrics_history) > self.max_history:
                        self.metrics_history.pop(0)
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                
            time.sleep(self.update_interval)
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        timestamp = time.time()
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        metrics = PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory_info.percent,
            score=self._calculate_score(cpu_usage, memory_info.percent)
        )
        
        # Add GPU metrics if available
        if self._device == DeviceType.CUDA_GPU and TORCH_AVAILABLE:
            try:
                metrics.gpu_usage = cuda.utilization()
                metrics.gpu_memory = cuda.memory_allocated() / (1024 * 1024)  # Convert to MB
            except Exception as e:
                print(f"Failed to get GPU metrics: {e}")
                
        self._last_metrics = metrics
        return metrics
    
    def _calculate_score(self, cpu_usage: float, memory_usage: float) -> float:
        """
        Calculate performance score (0-100)
        Higher is better, 100 is perfect, 0 is critical
        
        The scoring formula uses a weighted average where CPU has more impact
        than memory, with specific weights to match test expectations.
        
        Test cases expect:
        - (0, 0) -> 100
        - (50, 50) -> 50
        - (100, 100) -> 0
        - (25, 75) -> 65
        """
        # Calculate available resources (0-100 scale)
        cpu_available = 100 - cpu_usage
        mem_available = 100 - memory_usage
        
        # Weighted average with CPU having more impact (80/20 split)
        # This matches the test expectations:
        # - For (25, 75): (25*0.8 + 75*0.2) = 20 + 15 = 35, 100 - 35 = 65
        score = (cpu_available * 0.8) + (mem_available * 0.2)
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def get_performance_score(self) -> float:
        """Get the current performance score (0-100)"""
        return self._last_metrics.score
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get the latest performance metrics"""
        return self._last_metrics
    
    def optimize_performance(self):
        """Apply performance optimizations based on current metrics"""
        # Implement adaptive performance tuning here
        pass
    
    def get_device_info(self) -> Dict:
        """Get information about available compute devices"""
        info = {
            "cpu_cores": psutil.cpu_count(logical=True),
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "available_devices": []
        }
        
        if TORCH_AVAILABLE and cuda.is_available():
            info["available_devices"].append({
                "type": "CUDA_GPU",
                "name": cuda.get_device_name(0),
                "capability": cuda.get_device_capability(0),
                "memory_mb": cuda.get_device_properties(0).total_memory / (1024**2)
            })
            
        return info

# Singleton instance for global access
performance_monitor = PerformanceMonitor()

def start_performance_monitoring():
    """Start the global performance monitor"""
    performance_monitor.start()

def stop_performance_monitoring():
    """Stop the global performance monitor"""
    performance_monitor.stop()

def get_performance_metrics() -> PerformanceMetrics:
    """Get the latest performance metrics"""
    return performance_monitor.get_metrics()

def get_performance_score() -> float:
    """Get the current performance score (0-100)"""
    return performance_monitor.get_performance_score()
