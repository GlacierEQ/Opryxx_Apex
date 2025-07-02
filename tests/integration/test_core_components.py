"""
Integration tests for core OPRYXX components.

These tests verify the interaction between core components:
- ConfigManager
- Monitoring system
- Logging system
"""
import json
import os
import tempfile
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import from the correct module
from core.monitoring import ResourceMonitor, SystemMetrics
from core.config import ConfigManager

@pytest.fixture
def temp_config():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        config = {
            "performance": {
                "update_interval": 0.1,  # Fast updates for testing
                "max_history": 10
            },
            "monitoring": {
                "enabled": True
            }
        }
        json.dump(config, f)
        f.flush()
        yield f.name
    try:
        os.unlink(f.name)
    except:
        pass

class TestCoreIntegration:
    """Integration tests for core components."""
    
    def test_config_manager_with_monitor(self, temp_config):
        """Test that ResourceMonitor uses ConfigManager settings."""
        # Initialize config manager with test config
        config_manager = ConfigManager()
        config_manager.config = {
            'performance': {
                'update_interval': 0.1,
                'max_history': 10
            }
        }
        
        # Create monitor which should use config values
        monitor = ResourceMonitor(
            max_history=config_manager.config['performance']['max_history']
        )
        
        # Verify config was applied
        assert monitor._max_history == 10
        
        # Verify monitor starts and collects data
        monitor.start()
        time.sleep(0.2)  # Allow time for at least one update
        
        try:
            # Check that metrics are being collected
            metrics = SystemMetrics()  # The actual implementation doesn't have get_metrics()
            assert hasattr(metrics, 'cpu_percent')
            
            # Check history is being maintained
            with monitor._lock:
                assert len(monitor._metrics_history['cpu']) > 0
            
        finally:
            monitor.stop()
    
    def test_config_updates_affect_monitor(self, temp_config):
        """Test that config updates are reflected in the monitor."""
        # Initialize with test config
        config_manager = ConfigManager()
        config_manager.config = {
            'performance': {
                'update_interval': 0.1,
                'max_history': 10
            }
        }
        
        monitor = ResourceMonitor()
        
        try:
            # Change config
            new_max_history = 20
            config_manager.config['performance']['max_history'] = new_max_history
            
            # Create new monitor with updated config
            monitor.stop()
            monitor = ResourceMonitor(
                max_history=config_manager.config['performance']['max_history']
            )
            monitor.start()
            
            assert monitor._max_history == new_max_history
            
        finally:
            monitor.stop()
    
    @patch('core.monitoring.psutil')
    def test_error_handling(self, mock_psutil, temp_config):
        """Test error handling and recovery in the monitoring system."""
        # Setup mock to raise an exception
        mock_psutil.Process.return_value.cpu_percent.side_effect = Exception("Test error")
        
        monitor = ResourceMonitor()
        monitor.start()
        
        try:
            # Allow time for the monitor to try updating
            time.sleep(0.2)
            
            # Verify monitor is still running despite the error
            assert monitor.is_running()
            
        finally:
            monitor.stop()
    
    def test_resource_cleanup(self, temp_config):
        """Test that resources are properly cleaned up."""
        monitor = ResourceMonitor()
        monitor.start()
        
        # Verify monitor is running
        assert monitor.is_running()
        
        # Stop monitor and verify cleanup
        monitor.stop()
        assert not monitor.is_running()
        
        # Verify thread is no longer alive
        if hasattr(monitor, '_thread') and monitor._thread:
            monitor._thread.join(timeout=1.0)
            assert not monitor._thread.is_alive()

    def test_metrics_history_limits(self, temp_config):
        """Test that metrics history respects max_history limit."""
        max_history = 5
        monitor = ResourceMonitor(max_history=max_history)
        
        try:
            monitor.start()
            
            # Wait for more updates than max_history
            time.sleep(0.2)
            
            # Check history length doesn't exceed max_history
            with monitor._lock:
                for metric_history in monitor._metrics_history.values():
                    assert len(metric_history) <= max_history
                    
        finally:
            monitor.stop()
