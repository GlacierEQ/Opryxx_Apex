"""
Memory Optimization Module
Implements intelligent memory management and optimization strategies
"""

import gc
import psutil
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class MemoryMetrics:
    """Memory usage metrics"""
    total_mb: float
    available_mb: float
    used_mb: float
    cached_mb: float
    buffers_mb: float
    usage_percent: float
    swap_used_mb: float
    swap_percent: float

class OptimizationLevel(Enum):
    CONSERVATIVE = auto()
    MODERATE = auto()
    AGGRESSIVE = auto()

class MemoryOptimizer:
    """Intelligent memory optimization system"""
    
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.MODERATE):
        self.optimization_level = optimization_level
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self.optimization_history: List[Dict] = []
        
    def start_monitoring(self, interval: float = 30.0):
        """Start automatic memory optimization"""
        if self.running:
            return
            
        self.running = True
        self._thread = threading.Thread(
            target=self._optimization_loop, 
            args=(interval,), 
            daemon=True
        )
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop automatic memory optimization"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _optimization_loop(self, interval: float):
        """Main optimization loop"""
        while self.running:
            try:
                metrics = self.get_memory_metrics()
                if self._should_optimize(metrics):
                    self.optimize_memory()
            except Exception as e:
                print(f"Memory optimization error: {e}")
            time.sleep(interval)
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Get current memory metrics"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return MemoryMetrics(
            total_mb=mem.total / (1024**2),
            available_mb=mem.available / (1024**2),
            used_mb=mem.used / (1024**2),
            cached_mb=getattr(mem, 'cached', 0) / (1024**2),
            buffers_mb=getattr(mem, 'buffers', 0) / (1024**2),
            usage_percent=mem.percent,
            swap_used_mb=swap.used / (1024**2),
            swap_percent=swap.percent
        )
    
    def _should_optimize(self, metrics: MemoryMetrics) -> bool:
        """Determine if optimization is needed"""
        thresholds = {
            OptimizationLevel.CONSERVATIVE: 85.0,
            OptimizationLevel.MODERATE: 75.0,
            OptimizationLevel.AGGRESSIVE: 65.0
        }
        return metrics.usage_percent > thresholds[self.optimization_level]
    
    def optimize_memory(self) -> Dict:
        """Perform memory optimization"""
        before_metrics = self.get_memory_metrics()
        optimizations_applied = []
        
        # Force garbage collection
        collected = gc.collect()
        if collected > 0:
            optimizations_applied.append(f"Garbage collected {collected} objects")
        
        # Clear Python caches
        if hasattr(gc, 'get_stats'):
            gc.set_threshold(700, 10, 10)  # More aggressive GC
            optimizations_applied.append("Adjusted GC thresholds")
        
        # Execute registered callbacks
        for callback in self._callbacks:
            try:
                result = callback()
                if result:
                    optimizations_applied.append(f"Callback optimization: {result}")
            except Exception as e:
                print(f"Callback error: {e}")
        
        after_metrics = self.get_memory_metrics()
        freed_mb = before_metrics.used_mb - after_metrics.used_mb
        
        optimization_result = {
            'timestamp': time.time(),
            'before_usage_percent': before_metrics.usage_percent,
            'after_usage_percent': after_metrics.usage_percent,
            'freed_mb': freed_mb,
            'optimizations': optimizations_applied
        }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback function"""
        self._callbacks.append(callback)
    
    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {'total_optimizations': 0, 'total_freed_mb': 0}
        
        return {
            'total_optimizations': len(self.optimization_history),
            'total_freed_mb': sum(opt['freed_mb'] for opt in self.optimization_history),
            'avg_freed_mb': sum(opt['freed_mb'] for opt in self.optimization_history) / len(self.optimization_history),
            'last_optimization': self.optimization_history[-1]['timestamp']
        }

# Global instance
memory_optimizer = MemoryOptimizer()