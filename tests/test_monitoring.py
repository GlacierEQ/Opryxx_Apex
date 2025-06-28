"""
Tests for system resource monitoring and performance tracking.
"""
import os
import time
import psutil
import pytest
import threading
from unittest.mock import patch, MagicMock, call

from core.monitoring import (
    SystemMetrics,
    ResourceMonitor,
    get_resource_monitor,
    start_monitoring,
    stop_monitoring
)


class TestSystemMetrics:
    """Test SystemMetrics data class."""
    
    def test_initialization(self):
        """Test initialization with default values."""
        metrics = SystemMetrics()
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.disk_io_read == 0.0
        assert metrics.disk_io_write == 0.0
        assert metrics.network_sent == 0.0
        assert metrics.network_recv == 0.0
        assert metrics.timestamp > 0
    
    def test_initialization_with_values(self):
        """Test initialization with custom values."""
        ts = time.time()
        metrics = SystemMetrics(
            cpu_percent=25.5,
            memory_percent=50.0,
            disk_io_read=1024.0,
            disk_io_write=2048.0,
            network_sent=512.0,
            network_recv=256.0,
            timestamp=ts
        )
        
        assert metrics.cpu_percent == 25.5
        assert metrics.memory_percent == 50.0
        assert metrics.disk_io_read == 1024.0
        assert metrics.disk_io_write == 2048.0
        assert metrics.network_sent == 512.0
        assert metrics.network_recv == 256.0
        assert metrics.timestamp == ts


class TestResourceMonitor:
    """Test ResourceMonitor class functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        self.monitor = ResourceMonitor(max_history=10)
        self.monitor._process = MagicMock()
        self.monitor._process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100MB
        self.monitor._process.num_threads.return_value = 5
        
        # Mock psutil functions
        self.psutil_patcher = patch('core.monitoring.psutil')
        self.mock_psutil = self.psutil_patcher.start()
        
        # Setup mock values
        self.mock_psutil.cpu_percent.return_value = 25.5
        self.mock_psutil.virtual_memory.return_value = MagicMock(percent=65.0)
        
        # Mock disk and network I/O
        self.mock_disk_io = MagicMock()
        self.mock_disk_io.read_bytes = 1024 * 1024  # 1MB
        self.mock_disk_io.write_bytes = 512 * 1024  # 0.5MB
        self.mock_psutil.disk_io_counters.return_value = self.mock_disk_io
        
        self.mock_net_io = MagicMock()
        self.mock_net_io.bytes_sent = 1000
        self.mock_net_io.bytes_recv = 2000
        self.mock_psutil.net_io_counters.return_value = self.mock_net_io
        
        # Mock disk partitions
        self.mock_partition = MagicMock()
        self.mock_partition.mountpoint = '/'
        self.mock_psutil.disk_partitions.return_value = [self.mock_partition]
        
        # Mock disk usage
        self.mock_disk_usage = MagicMock()
        self.mock_disk_usage.percent = 75.0
        self.mock_psutil.disk_usage.return_value = self.mock_disk_usage
        
        yield
        
        # Cleanup
        self.psutil_patcher.stop()
        if hasattr(self, 'monitor') and self.monitor._running:
            self.monitor.stop()
    
    def test_initialization(self):
        """Test monitor initialization."""
        assert self.monitor._max_history == 10
        assert not self.monitor._running
        assert len(self.monitor._metrics_history) == 6  # cpu, memory, disk_r/w, net_sent/recv
    
    def test_start_stop(self):
        """Test starting and stopping the monitor."""
        self.monitor.start()
        assert self.monitor._running
        assert self.monitor._thread.is_alive()
        
        self.monitor.stop()
        assert not self.monitor._running
    
    def test_update_metrics(self):
        """Test updating metrics."""
        metrics = self.monitor._update_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_percent == 25.5
        assert metrics.memory_percent == 65.0
        assert metrics.disk_io_read == 1024 * 1024  # 1MB
        assert metrics.disk_io_write == 512 * 1024  # 0.5MB
        assert metrics.network_sent == 1000
        assert metrics.network_recv == 2000
    
    def test_monitor_loop(self):
        """Test the monitoring loop."""
        self.monitor._running = True
        
        # Mock time to control the loop
        with patch('time.time', side_effect=[1, 2, 3, 4]):  # Will run 3 iterations
            with patch.object(self.monitor, '_update_metrics') as mock_update:
                mock_update.return_value = SystemMetrics()
                
                # Run the loop for a short time
                self.monitor._monitor_loop()
                
                # Should update metrics 3 times (once per second)
                assert mock_update.call_count == 3
    
    def test_get_metrics(self):
        """Test getting metrics history."""
        # Add some test data
        now = time.time()
        test_data = [
            (now - 5, 10.0),    # 5 seconds ago
            (now - 3, 20.0),    # 3 seconds ago
            (now - 1, 30.0),    # 1 second ago
        ]
        
        with self.monitor._lock:
            self.monitor._metrics_history['test_metric'] = deque(test_data, maxlen=10)
        
        # Get all metrics
        metrics = self.monitor.get_metrics('test_metric')
        assert len(metrics) == 3
        
        # Get metrics within time window
        metrics = self.monitor.get_metrics('test_metric', time_window=4)  # Last 4 seconds
        assert len(metrics) == 2  # Should get the last 2 data points
        assert metrics[0][1] == 20.0
        assert metrics[1][1] == 30.0
    
    def test_get_usage_summary(self):
        """Test getting usage summary."""
        with patch.object(self.monitor, 'get_current_metrics') as mock_metrics:
            mock_metrics.return_value = SystemMetrics(
                cpu_percent=25.5,
                memory_percent=65.0,
                disk_io_read=1024 * 1024,  # 1MB
                disk_io_write=512 * 1024,   # 0.5MB
                network_sent=1000,          # 1KB
                network_recv=2000           # 2KB
            )
            
            summary = self.monitor.get_usage_summary()
            
            assert summary['cpu_percent'] == 25.5
            assert summary['memory_percent'] == 65.0
            assert summary['disk_read_mb'] == 1.0
            assert summary['disk_write_mb'] == 0.5
            assert summary['network_sent_mb'] == 1000 / (1024 * 1024)
            assert summary['network_recv_mb'] == 2000 / (1024 * 1024)
            assert 'uptime_seconds' in summary
    
    def test_check_resource_limits(self):
        """Test checking resource limits."""
        # Test normal usage (no issues)
        self.mock_psutil.cpu_percent.return_value = 50.0
        self.mock_psutil.virtual_memory.return_value.percent = 70.0
        self.mock_disk_usage.percent = 80.0
        
        issues = self.monitor.check_resource_limits()
        assert not issues
        
        # Test high CPU usage
        self.mock_psutil.cpu_percent.return_value = 95.0
        issues = self.monitor.check_resource_limits()
        assert 'cpu' in issues
        
        # Test high memory usage
        self.mock_psutil.cpu_percent.return_value = 50.0
        self.mock_psutil.virtual_memory.return_value.percent = 95.0
        issues = self.monitor.check_resource_limits()
        assert 'memory' in issues
        
        # Test high disk usage
        self.mock_disk_usage.percent = 95.0
        issues = self.monitor.check_resource_limits()
        assert 'disk_/' in issues


def test_get_resource_monitor():
    """Test getting the resource monitor instance."""
    monitor1 = get_resource_monitor()
    monitor2 = get_resource_monitor()
    
    assert monitor1 is monitor2  # Should be the same instance


@patch('core.monitoring.ResourceMonitor.start')
@patch('core.monitoring.start_prometheus_server')
def test_start_monitoring(mock_start_server, mock_start, monkeypatch):
    """Test starting the monitoring system."""
    # Mock performance config
    mock_config = MagicMock()
    mock_config.LOG_PERFORMANCE_METRICS = True
    mock_config.PERFORMANCE_METRICS_PORT = 9090
    
    monkeypatch.setattr('config.performance.performance_config', mock_config)
    
    # Start monitoring
    start_monitoring()
    
    # Verify monitor was started
    mock_start.assert_called_once()
    mock_start_server.assert_called_once_with(9090)


def test_stop_monitoring():
    """Test stopping the monitoring system."""
    # Create a mock monitor
    mock_monitor = MagicMock()
    
    # Replace the global instance
    import core.monitoring as monitoring_module
    original_monitor = monitoring_module.resource_monitor
    monitoring_module.resource_monitor = mock_monitor
    
    try:
        # Stop monitoring
        stop_monitoring()
        
        # Verify stop was called
        mock_monitor.stop.assert_called_once()
    finally:
        # Restore original monitor
        monitoring_module.resource_monitor = original_monitor
