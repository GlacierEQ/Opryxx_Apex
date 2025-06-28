"""
Test suite for the AdvancedSystemMonitor class.

This module contains unit tests for the system monitoring functionality,
including metric collection, anomaly detection, and database operations.
"""

import unittest
import time
import json
import logging
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY

# Add parent directory to path to allow importing the module
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from monitors.system_monitor import AdvancedSystemMonitor, SystemMetrics, SystemMonitorError

class TestSystemMonitor(unittest.TestCase):
    """Test cases for the AdvancedSystemMonitor class."""

    def setUp(self):
        """Set up test environment before each test method."""
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.monitor = AdvancedSystemMonitor(db_path=self.db_path)
        
        # Patch psutil functions for consistent testing
        self.psutil_patcher = patch('monitors.system_monitor.psutil')
        self.mock_psutil = self.psutil_patcher.start()
        
        # Set up mock return values for psutil functions
        self.setup_psutil_mocks()
        
        # Disable logging during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        self.psutil_patcher.stop()
        
        # Close and remove temporary database
        self.monitor.cleanup()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
        # Re-enable logging
        logging.disable(logging.NOTSET)
    
    def setup_psutil_mocks(self):
        """Set up mock return values for psutil functions."""
        # Mock CPU metrics
        cpu_times = MagicMock()
        cpu_times._asdict.return_value = {'user': 10.5, 'system': 5.2, 'idle': 84.3}
        self.mock_psutil.cpu_times_percent.return_value = cpu_times
        
        cpu_freq = MagicMock()
        cpu_freq._asdict.return_value = {'current': 2400.0, 'min': 800.0, 'max': 3200.0}
        self.mock_psutil.cpu_freq.return_value = cpu_freq
        
        cpu_stats = MagicMock()
        cpu_stats.ctx_switches = 1000
        cpu_stats.interrupts = 500
        self.mock_psutil.cpu_stats.return_value = cpu_stats
        
        self.mock_psutil.cpu_percent.side_effect = [25.5, [25.5, 30.1, 20.8, 26.2]]
        self.mock_psutil.cpu_count.return_value = 4
        self.mock_psutil.getloadavg.return_value = (1.5, 1.2, 1.0)
        
        # Mock memory metrics
        vmem = MagicMock()
        vmem._asdict.return_value = {
            'total': 16 * 1024**3,  # 16 GB
            'available': 8 * 1024**3,  # 8 GB
            'percent': 50.0,
            'used': 8 * 1024**3,
            'free': 8 * 1024**3,
            'active': 6 * 1024**3,
            'inactive': 2 * 1024**3,
            'buffers': 1 * 1024**3,
            'cached': 3 * 1024**3,
            'shared': 1 * 1024**3,
            'slab': 1 * 1024**3
        }
        self.mock_psutil.virtual_memory.return_value = vmem
        
        swap = MagicMock()
        swap._asdict.return_value = {
            'total': 8 * 1024**3,  # 8 GB
            'used': 2 * 1024**3,   # 2 GB
            'free': 6 * 1024**3,   # 6 GB
            'percent': 25.0,
            'sin': 0,
            'sout': 0
        }
        self.mock_psutil.swap_memory.return_value = swap
        
        # Mock disk metrics
        partition = MagicMock()
        partition.device = '/dev/sda1'
        partition.mountpoint = '/'
        partition.fstype = 'ext4'
        partition.opts = 'rw,relatime'
        self.mock_psutil.disk_partitions.return_value = [partition]
        
        usage = MagicMock()
        usage._asdict.return_value = {
            'total': 500 * 1024**3,  # 500 GB
            'used': 250 * 1024**3,   # 250 GB
            'free': 250 * 1024**3,   # 250 GB
            'percent': 50.0
        }
        self.mock_psutil.disk_usage.return_value = usage
        
        disk_io = MagicMock()
        disk_io._asdict.return_value = {
            'read_count': 1000,
            'write_count': 500,
            'read_bytes': 1024**3,  # 1 GB
            'write_bytes': 512 * 1024**2,  # 512 MB
            'read_time': 1000,
            'write_time': 500
        }
        self.mock_psutil.disk_io_counters.return_value = disk_io
        
        # Mock network metrics
        net_io = MagicMock()
        net_io._asdict.return_value = {
            'bytes_sent': 1024**3,  # 1 GB
            'bytes_recv': 2 * 1024**3,  # 2 GB
            'packets_sent': 1000000,
            'packets_recv': 2000000,
            'errin': 0,
            'errout': 0,
            'dropin': 0,
            'dropout': 0
        }
        self.mock_psutil.net_io_counters.return_value = net_io
        
        # Mock process metrics
        process = MagicMock()
        process.info = {
            'pid': 1234,
            'name': 'python',
            'username': 'testuser',
            'cpu_percent': 10.5,
            'memory_percent': 5.2,
            'status': 'running',
            'create_time': time.time() - 3600,  # 1 hour ago
            'cmdline': ['python', 'test.py']
        }
        process.pid = 1234
        process.name.return_value = 'python'
        process.username.return_value = 'testuser'
        process.cpu_percent.return_value = 10.5
        process.memory_percent.return_value = 5.2
        process.status.return_value = 'running'
        process.create_time.return_value = time.time() - 3600
        process.cmdline.return_value = ['python', 'test.py']
        
        self.mock_psutil.process_iter.return_value = [process]
        
        # Mock network connections
        conn = MagicMock()
        conn.type = 1  # SOCK_STREAM (TCP)
        conn.status = 'ESTABLISHED'
        self.mock_psutil.net_connections.return_value = [conn]
        
        # Mock network interfaces
        self.mock_psutil.net_if_addrs.return_value = {
            'lo': [MagicMock(address='127.0.0.1', netmask='255.0.0.0')],
            'eth0': [MagicMock(address='192.168.1.100', netmask='255.255.255.0')]
        }

    def test_initialization(self):
        """Test that the monitor initializes correctly."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(len(self.monitor.metrics_history['cpu']), 0)
        self.assertEqual(self.monitor.anomaly_thresholds['cpu_usage'], 80.0)

    def test_collect_cpu_metrics(self):
        """Test collection of CPU metrics."""
        metrics = self.monitor._get_cpu_metrics()
        self.assertIn('usage_percent', metrics)
        self.assertIn('per_cpu', metrics)
        self.assertIn('freq', metrics)
        self.assertIn('load_avg', metrics)
        self.assertIn('stats', metrics)
        
        # Verify the mock was called
        self.mock_psutil.cpu_percent.assert_called()
        self.mock_psutil.cpu_times_percent.assert_called()
        self.mock_psutil.cpu_freq.assert_called()
        self.mock_psutil.cpu_stats.assert_called()
        self.mock_psutil.getloadavg.assert_called()

    def test_collect_memory_metrics(self):
        """Test collection of memory metrics."""
        metrics = self.monitor._get_memory_metrics()
        self.assertIn('virtual', metrics)
        self.assertIn('swap', metrics)
        self.assertIn('usage_trend', metrics)
        
        # Verify the mock was called
        self.mock_psutil.virtual_memory.assert_called()
        self.mock_psutil.swap_memory.assert_called()

    def test_collect_disk_metrics(self):
        """Test collection of disk metrics."""
        metrics = self.monitor._get_disk_metrics()
        self.assertIn('/dev/sda1', metrics)
        self.assertEqual(metrics['/dev/sda1']['mountpoint'], '/')
        
        # Verify the mock was called
        self.mock_psutil.disk_partitions.assert_called_with(all=False)
        self.mock_psutil.disk_usage.assert_called_with('/')
        self.mock_psutil.disk_io_counters.assert_called()

    def test_collect_network_metrics(self):
        """Test collection of network metrics."""
        metrics = self.monitor._get_network_metrics()
        self.assertIn('io', metrics)
        self.assertIn('connections', metrics)
        self.assertIn('interfaces', metrics)
        self.assertIn('addresses', metrics)
        
        # Verify the mock was called
        self.mock_psutil.net_io_counters.assert_called()
        self.mock_psutil.net_connections.assert_called_with(kind='inet')
        self.mock_psutil.net_if_addrs.assert_called()

    def test_collect_process_metrics(self):
        """Test collection of process metrics."""
        processes = self.monitor._get_process_metrics()
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]['name'], 'python')
        
        # Verify the mock was called
        self.mock_psutil.process_iter.assert_called()

    def test_comprehensive_metrics(self):
        """Test collection of all metrics together."""
        metrics = self.monitor.collect_comprehensive_metrics()
        
        # Verify all main sections are present
        self.assertIn('cpu', metrics)
        self.assertIn('memory', metrics)
        self.assertIn('disk', metrics)
        self.assertIn('network', metrics)
        self.assertIn('processes', metrics)
        
        # Verify timestamp is included
        self.assertIn('timestamp', metrics)
        
        # Verify process metrics
        self.assertEqual(metrics['processes']['total'], 1)
        self.assertEqual(len(metrics['processes']['top_cpu']), 1)
        self.assertEqual(metrics['processes']['top_cpu'][0]['name'], 'python')

    def test_anomaly_detection(self):
        """Test anomaly detection logic."""
        # Test with normal metrics (no anomalies expected)
        metrics = self.monitor.collect_comprehensive_metrics()
        anomalies = self.monitor.detect_anomalies(metrics)
        self.assertEqual(len(anomalies), 0)
        
        # Test with high CPU usage
        self.monitor.anomaly_thresholds['cpu_usage'] = 20.0  # Lower threshold to trigger anomaly
        metrics['cpu']['usage_percent'] = 25.0  # Above threshold
        anomalies = self.monitor.detect_anomalies(metrics)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]['anomaly_type'], 'high_cpu_usage')
        
        # Test with high memory usage
        self.monitor.anomaly_thresholds['memory_usage'] = 40.0  # Lower threshold
        metrics['memory']['virtual']['percent'] = 85.0  # Above threshold
        anomalies = self.monitor.detect_anomalies(metrics)
        self.assertTrue(any(a['anomaly_type'] == 'high_memory_usage' for a in anomalies))

    def test_metrics_storage(self):
        """Test that metrics are properly stored in the database."""
        # Collect and store metrics
        metrics = self.monitor.collect_comprehensive_metrics()
        self.monitor.store_metrics_db(metrics)
        
        # Verify data was stored in the database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM metrics")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)  # Should have at least one metric
            
            # Verify anomaly table is empty (no anomalies expected with default metrics)
            cursor.execute("SELECT COUNT(*) FROM anomalies")
            anomaly_count = cursor.fetchone()[0]
            self.assertEqual(anomaly_count, 0)

    def test_metrics_summary(self):
        """Test the get_metrics_summary method."""
        summary = self.monitor.get_metrics_summary()
        
        # Verify summary structure
        self.assertIn('timestamp', summary)
        self.assertIn('cpu', summary)
        self.assertIn('memory', summary)
        self.assertIn('disk', summary)
        self.assertIn('processes', summary)
        
        # Verify CPU data
        self.assertIn('usage_percent', summary['cpu'])
        self.assertIn('load_avg', summary['cpu'])
        
        # Verify memory data
        self.assertIn('percent', summary['memory'])
        self.assertIn('available_gb', summary['memory'])
        
        # Verify disk data
        self.assertIn('total_devices', summary['disk'])
        self.assertIsInstance(summary['disk']['devices'], list)
        
        # Verify process data
        self.assertIn('total', summary['processes'])
        self.assertIn('top_cpu', summary['processes'])

    def test_error_handling(self):
        """Test that errors are properly handled and logged."""
        # Test with invalid metric type in calculate_trend
        trend = self.monitor.calculate_trend('invalid_metric')
        self.assertEqual(trend, 'insufficient_data')
        
        # Test with empty metrics in store_metrics_db
        self.monitor.store_metrics_db({})
        
        # Test with None metrics in detect_anomalies
        anomalies = self.monitor.detect_anomalies(None)
        self.assertEqual(anomalies, [])

    def test_cleanup(self):
        """Test that resources are properly cleaned up."""
        self.monitor.cleanup()
        # No exception should be raised
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
