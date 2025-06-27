"""
Tests for the AI Workbench

This module contains unit tests for the AI Workbench components.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_workbench import AIWorkbench, config
from ai_workbench.config import Config, AppConfig, DatabaseConfig


class TestConfig(unittest.TestCase):
    """Tests for the configuration system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            'app': {
                'name': 'Test Workbench',
                'version': '0.1.0',
                'debug': True,
                'log_level': 'DEBUG',
                'log_file': 'test.log',
            },
            'database': {
                'url': 'sqlite:///:memory:',
                'echo': True,
            },
        }
        
        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / 'config.json'
        with open(self.config_path, 'w') as f:
            import json
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    def test_config_loading(self):
        """Test loading configuration from a file"""
        cfg = Config.load(self.config_path)
        
        # Check app config
        self.assertEqual(cfg.app.name, 'Test Workbench')
        self.assertEqual(cfg.app.version, '0.1.0')
        self.assertTrue(cfg.app.debug)
        self.assertEqual(cfg.app.log_level, 'DEBUG')
        self.assertEqual(cfg.app.log_file, 'test.log')
        
        # Check database config
        self.assertEqual(cfg.database.url, 'sqlite:///:memory:')
        self.assertTrue(cfg.database.echo)
    
    def test_config_saving(self):
        """Test saving configuration to a file"""
        # Create a new config
        cfg = Config()
        
        # Modify some values
        cfg.app.name = 'Modified Workbench'
        cfg.app.debug = True
        cfg.database.url = 'sqlite:///test.db'
        
        # Save to a temporary file
        temp_path = Path(self.temp_dir.name) / 'saved_config.json'
        cfg.save(temp_path)
        
        # Load it back and verify
        loaded = Config.load(temp_path)
        self.assertEqual(loaded.app.name, 'Modified Workbench')
        self.assertTrue(loaded.app.debug)
        self.assertEqual(loaded.database.url, 'sqlite:///test.db')
    
    def test_config_defaults(self):
        """Test default configuration values"""
        cfg = Config()
        
        # Check some default values
        self.assertEqual(cfg.app.name, 'AI Workbench')
        self.assertFalse(cfg.app.debug)
        self.assertEqual(cfg.monitoring.interval, 300)
        self.assertTrue(cfg.optimization.auto_optimize)


class TestAIWorkbench(unittest.TestCase):
    """Tests for the main AIWorkbench class"""
    
    @patch('ai_workbench.AIWorkbenchService')
    @patch('ai_workbench.logging')
    def test_initialization(self, mock_logging, mock_service_class):
        """Test AIWorkbench initialization"""
        # Create a mock service instance
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Initialize the workbench
        workbench = AIWorkbench()
        
        # Verify service was created
        mock_service_class.assert_called_once()
        
        # Verify logging was set up
        mock_logging.basicConfig.assert_called_once()
    
    @patch('ai_workbench.AIWorkbenchService')
    @patch('ai_workbench.signal')
    def test_signal_handlers(self, mock_signal, mock_service_class):
        """Test signal handler setup"""
        # Initialize the workbench
        workbench = AIWorkbench()
        
        # Verify signal handlers were set up
        mock_signal.signal.assert_any_call(mock_signal.SIGINT, workbench._handle_shutdown)
        mock_signal.signal.assert_any_call(mock_signal.SIGTERM, workbench._handle_shutdown)
    
    @patch('ai_workbench.AIWorkbenchService')
    def test_start_stop(self, mock_service_class):
        """Test starting and stopping the workbench"""
        # Create a mock service instance
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Initialize and start the workbench
        workbench = AIWorkbench()
        workbench.start()
        
        # Verify the service was started
        mock_service.start_monitoring.assert_called_once()
        
        # Stop the workbench
        workbench.stop()
        
        # Verify the service was stopped
        mock_service.stop_monitoring.assert_called_once()


class TestSystemUtils(unittest.TestCase):
    """Tests for system utilities"""
    
    @patch('ai_workbench.utils.system_utils.psutil')
    def test_get_system_info(self, mock_psutil):
        """Test getting system information"""
        from ai_workbench.utils import system_utils
        
        # Set up mock return values
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.cpu_freq.return_value = MagicMock(
            current=3000.0,
            min=800.0,
            max=4000.0
        )
        mock_psutil.cpu_stats.return_value = MagicMock(
            ctx_switches=1000,
            interrupts=500,
            soft_interrupts=300,
            syscalls=2000
        )
        
        # Call the function
        info = system_utils.get_system_info()
        
        # Verify the results
        self.assertEqual(info['cpu']['logical_cores'], 8)
        self.assertEqual(info['cpu']['current_frequency'], 3000.0)
        
        # Verify the mock was called
        mock_psutil.cpu_count.assert_called()
        mock_psutil.cpu_freq.assert_called()
        mock_psutil.cpu_stats.assert_called()


if __name__ == '__main__':
    unittest.main()
