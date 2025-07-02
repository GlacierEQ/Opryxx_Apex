"""
Performance benchmarks for OPRYXX core components.

These benchmarks measure the performance of critical system components
and help identify potential bottlenecks.
"""
import os
import sys
import time
import pytest
import psutil
from pathlib import Path
from typing import Dict, List, Tuple

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.monitoring import ResourceMonitor, SystemMetrics
    from core.config import ConfigManager
except ImportError as e:
    raise ImportError(
        f"Failed to import core modules. Make sure you're running from the project root and all dependencies are installed.\n"
        f"Error: {e}"
    )

class TestPerformanceBenchmarks:
    """Performance benchmark test suite for core components."""
    
    @pytest.mark.benchmark(group="monitor_initialization")
    def test_monitor_initialization(self, benchmark):
        """Benchmark resource monitor initialization time."""
        def setup():
            return {}
            
        def monitor_init():
            monitor = ResourceMonitor(max_history=1000)
            return monitor
            
        # Run benchmark
        result = benchmark.pedantic(monitor_init, setup=setup, rounds=100, iterations=1)
        assert result is not None
    
    @pytest.mark.benchmark(group="monitor_update")
    def test_monitor_update_performance(self, benchmark):
        """Benchmark resource monitor update performance."""
        monitor = ResourceMonitor(max_history=1000)
        
        def monitor_update():
            with monitor._lock:
                monitor._update_metrics()
                
        # Run benchmark
        benchmark.pedantic(monitor_update, rounds=1000, iterations=1)
    
    @pytest.mark.benchmark(group="config_loading")
    def test_config_loading_performance(self, benchmark, tmp_path):
        """Benchmark configuration loading performance."""
        # Create a test config file
        config_file = tmp_path / "test_config.json"
        config_data = {
            "performance": {
                "update_interval": 0.1,
                "max_history": 1000
            },
            "monitoring": {
                "enabled": True
            }
        }
        
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
            
        def load_config():
            manager = ConfigManager(str(config_file))
            return manager
            
        # Run benchmark
        result = benchmark.pedantic(load_config, rounds=100, iterations=1)
        assert result is not None
    
    @pytest.mark.benchmark(group="metrics_history")
    def test_metrics_history_performance(self, benchmark):
        """Benchmark metrics history management performance."""
        monitor = ResourceMonitor(max_history=1000)
        metrics = SystemMetrics()
        
        def update_history():
            with monitor._lock:
                monitor._update_metrics_history(metrics)
                
        # Run benchmark
        benchmark.pedantic(update_history, rounds=10000, iterations=1)
    
    @pytest.mark.benchmark(group="system_metrics")
    def test_system_metrics_collection(self, benchmark):
        """Benchmark system metrics collection performance."""
        monitor = ResourceMonitor()
        
        def collect_metrics():
            return monitor._collect_metrics()
            
        # Run benchmark
        result = benchmark.pedantic(collect_metrics, rounds=1000, iterations=1)
        assert isinstance(result, SystemMetrics)

    def test_memory_usage(self):
        """Test memory usage of the monitoring system."""
        import tracemalloc
        
        # Start tracing memory allocations
        tracemalloc.start()
        
        # Take initial snapshot
        snapshot1 = tracemalloc.take_snapshot()
        
        # Create and start monitor
        monitor = ResourceMonitor(max_history=1000)
        monitor.start()
        
        try:
            # Let it run for a bit
            import time
            time.sleep(1.0)
            
            # Take another snapshot
            snapshot2 = tracemalloc.take_snapshot()
            
            # Calculate memory usage
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            
            # Check for memory leaks (should be minimal)
            total_memory = sum(stat.size_diff for stat in top_stats)
            assert total_memory < 10 * 1024 * 1024  # Less than 10MB
            
        finally:
            monitor.stop()
            tracemalloc.stop()
    
    def test_cpu_usage(self):
        """Test CPU usage of the monitoring system."""
        import psutil
        
        # Get initial CPU usage
        process = psutil.Process()
        initial_cpu = process.cpu_percent(interval=0.1)
        
        # Start monitor
        monitor = ResourceMonitor(update_interval=0.1)
        monitor.start()
        
        try:
            # Let it run for a bit
            time.sleep(1.0)
            
            # Measure CPU usage
            cpu_usage = process.cpu_percent(interval=1.0)
            
            # Check that CPU usage is reasonable (less than 10% on average)
            assert cpu_usage < 10.0, f"CPU usage too high: {cpu_usage}%"
            
        finally:
            monitor.stop()

# Run benchmarks if executed directly
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--benchmark-only"])
