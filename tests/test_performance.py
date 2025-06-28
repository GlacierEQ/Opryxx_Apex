"""
Tests for performance monitoring and optimization.
"""
import time
import pytest
import threading
from unittest.mock import patch, MagicMock

from core.performance import PerformanceMonitor, PerformanceStats, monitor_performance

class TestPerformanceStats:
    """Test performance statistics collection."""
    
    def test_initialization(self):
        """Test initialization of PerformanceStats."""
        stats = PerformanceStats()
        assert stats.call_count == 0
        assert stats.total_time == 0.0
        assert stats.min_time == float('inf')
        assert stats.max_time == 0.0
        assert stats.last_call_time is None
        assert len(stats.call_history) == 0
    
    def test_update_stats(self):
        """Test updating statistics."""
        stats = PerformanceStats()
        
        # First update
        stats.update(0.1)
        assert stats.call_count == 1
        assert stats.total_time == 0.1
        assert stats.min_time == 0.1
        assert stats.max_time == 0.1
        assert stats.last_call_time is not None
        assert len(stats.call_history) == 1
        
        # Second update with higher value
        stats.update(0.3)
        assert stats.call_count == 2
        assert stats.total_time == 0.4
        assert stats.min_time == 0.1
        assert stats.max_time == 0.3
        assert len(stats.call_history) == 2
        
        # Third update with lower value
        stats.update(0.05)
        assert stats.call_count == 3
        assert stats.total_time == 0.45
        assert stats.min_time == 0.05
        assert stats.max_time == 0.3
        assert len(stats.call_history) == 3
    
    def test_avg_time(self):
        """Test average time calculation."""
        stats = PerformanceStats()
        assert stats.avg_time == 0.0  # No calls yet
        
        stats.update(0.1)
        stats.update(0.2)
        stats.update(0.3)
        
        assert stats.avg_time == pytest.approx(0.2)
    
    def test_median_time(self):
        """Test median time calculation."""
        stats = PerformanceStats()
        assert stats.median_time == 0.0  # No calls yet
        
        stats.update(0.1)
        stats.update(0.3)
        stats.update(0.2)
        
        assert stats.median_time == 0.2
    
    def test_std_dev(self):
        """Test standard deviation calculation."""
        stats = PerformanceStats()
        assert stats.std_dev == 0.0  # Not enough data
        
        stats.update(1)
        assert stats.std_dev == 0.0  # Only one data point
        
        stats.update(3)
        stats.update(5)
        stats.update(7)
        stats.update(9)
        
        # Standard deviation of [1, 3, 5, 7, 9] is ~2.828
        assert stats.std_dev == pytest.approx(2.828, abs=0.001)


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""
    
    def test_singleton_pattern(self):
        """Test that PerformanceMonitor follows singleton pattern."""
        monitor1 = PerformanceMonitor()
        monitor2 = PerformanceMonitor()
        assert monitor1 is monitor2
    
    def test_monitor_decorator(self):
        """Test the monitor decorator."""
        monitor = PerformanceMonitor()
        
        @monitor.monitor("test_function")
        def test_func():
            time.sleep(0.1)
            return "result"
        
        result = test_func()
        assert result == "result"
        
        stats = monitor.get_stats("test_function")
        assert stats["call_count"] == 1
        assert stats["avg_time"] > 0.0
    
    def test_record_metric(self):
        """Test recording a metric."""
        monitor = PerformanceMonitor()
        monitor.record_metric("test_metric", 0.123)
        
        stats = monitor.get_stats("test_metric")
        assert stats["call_count"] == 1
        assert stats["total_time"] == 0.123
        assert stats["min_time"] == 0.123
        assert stats["max_time"] == 0.123
    
    def test_reset_stats(self):
        """Test resetting statistics."""
        monitor = PerformanceMonitor()
        monitor.record_metric("test_metric", 0.1)
        monitor.record_metric("test_metric", 0.2)
        
        stats = monitor.get_stats("test_metric")
        assert stats["call_count"] == 2
        
        monitor.reset_stats("test_metric")
        stats = monitor.get_stats("test_metric")
        assert stats["call_count"] == 0
        assert stats["total_time"] == 0.0
    
    def test_get_bottlenecks(self):
        """Test identifying bottlenecks."""
        monitor = PerformanceMonitor()
        
        # Add some metrics
        monitor.record_metric("fast_operation", 0.05)  # Below threshold
        monitor.record_metric("slow_operation", 0.15)  # Above threshold
        monitor.record_metric("very_slow_operation", 0.5)  # Well above threshold
        
        # Default threshold is 0.1
        bottlenecks = monitor.get_bottlenecks(threshold=0.1)
        
        # Should find 2 bottlenecks
        assert len(bottlenecks) == 2
        
        # Should be sorted by total_time (descending)
        assert bottlenecks[0]["name"] == "very_slow_operation"
        assert bottlenecks[1]["name"] == "slow_operation"
    
    def test_disable_monitoring(self):
        """Test disabling monitoring."""
        monitor = PerformanceMonitor()
        monitor.disable()
        
        @monitor.monitor("disabled_function")
        def test_func():
            pass
        
        test_func()
        
        # Should not record any metrics when disabled
        stats = monitor.get_stats("disabled_function")
        assert stats == {}


def test_monitor_performance_decorator():
    """Test the module-level monitor_performance decorator."""
    calls = []
    
    @monitor_performance("decorated_function")
    def test_func():
        calls.append(1)
        return "test"
    
    # Call the decorated function
    result = test_func()
    
    # Verify function behavior
    assert result == "test"
    assert len(calls) == 1
    
    # Verify metrics were recorded
    stats = performance_monitor.get_stats("decorated_function")
    assert stats["call_count"] == 1
    assert stats["total_time"] > 0


def test_concurrent_monitoring():
    """Test that monitoring works correctly with concurrent access."""
    monitor = PerformanceMonitor()
    monitor.enable()
    monitor.reset_stats()
    
    def worker():
        for _ in range(100):
            monitor.record_metric("concurrent_test", 0.01)
    
    # Start multiple threads
    threads = [threading.Thread(target=worker) for _ in range(10)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # Verify all calls were recorded
    stats = monitor.get_stats("concurrent_test")
    assert stats["call_count"] == 1000  # 100 calls * 10 threads
    assert stats["total_time"] == pytest.approx(10.0, abs=0.1)  # 1000 * 0.01


@patch('prometheus_client.start_http_server')
def test_enable_prometheus_metrics(mock_start_server):
    """Test enabling Prometheus metrics."""
    monitor = PerformanceMonitor()
    
    # Enable Prometheus metrics
    monitor.enable_prometheus_metrics(9090)
    
    # Verify server was started
    mock_start_server.assert_called_once_with(9090)
    assert monitor._metrics_enabled is True
