#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for OPRYXX Launcher

This script tests the functionality of the OPRYXX launcher without building the full executable.
"""

import sys
import os
import time
import io
import unittest
import importlib
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Set console output encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import the launcher module
import opryxx_launcher
from opryxx_launcher import OPRYXXLauncher

class TestOPRYXXLauncher(unittest.TestCase):
    """Test cases for OPRYXXLauncher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = OPRYXXLauncher()
    
    @patch('opryxx_launcher.sys')
    @patch('builtins.input', return_value='')
    def test_launch_gui(self, mock_input, mock_sys):
        """Test launching the GUI."""
        # Setup mock for the import inside the method
        with patch.dict('sys.modules', {'gui.unified_gui': MagicMock()}) as mock_modules:
            # Create a mock for the UnifiedGUI class
            mock_gui_class = MagicMock()
            mock_gui_instance = MagicMock()
            mock_gui_class.return_value = mock_gui_instance
            
            # Set up the mock for the import
            mock_modules['gui.unified_gui'].UnifiedGUI = mock_gui_class
            
            # Reload the module to apply the mocks
            importlib.reload(opryxx_launcher)
            
            # Create a new instance with the mocked imports
            launcher = opryxx_launcher.OPRYXXLauncher()
            
            # Test
            try:
                launcher.launch_gui()
                mock_gui_instance.run.assert_called_once()
                print("✅ test_launch_gui passed")
                return True
            except Exception as e:
                print(f"❌ test_launch_gui failed: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    @patch('opryxx_launcher.sys')
    @patch('builtins.input', return_value='')
    def test_launch_web(self, mock_input, mock_sys):
        """Test launching the web interface."""
        # Setup mock for the import inside the method
        with patch.dict('sys.modules', {'gui.web_interface': MagicMock()}) as mock_modules:
            # Create a mock for the web_interface module
            mock_web = MagicMock()
            mock_web.run.side_effect = KeyboardInterrupt()  # Simulate keyboard interrupt to exit
            mock_modules['gui.web_interface'] = mock_web
            
            # Reload the module to apply the mocks
            importlib.reload(opryxx_launcher)
            
            # Create a new instance with the mocked imports
            launcher = opryxx_launcher.OPRYXXLauncher()
            
            # Test
            try:
                launcher.launch_web()
                mock_web.run.assert_called_once_with(host='0.0.0.0', port=5000)
                print("✅ test_launch_web passed")
                return True
            except Exception as e:
                print(f"❌ test_launch_web failed: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    @patch('opryxx_launcher.sys')
    @patch('builtins.input', return_value='')
    @patch('opryxx_launcher.time')
    def test_launch_performance(self, mock_time, mock_input, mock_sys):
        """Test launching performance monitoring."""
        # Setup mock for the imports inside the method
        with patch.dict('sys.modules', {
            'core.performance_monitor': MagicMock(),
            'core.memory_optimizer': MagicMock()
        }) as mock_modules:
            # Setup mocks
            mock_perf_monitor = MagicMock()
            mock_mem_optimizer = MagicMock()
            
            # Set up the mocks for the imports
            mock_modules['core.performance_monitor'].start_performance_monitoring = mock_perf_monitor
            mock_modules['core.memory_optimizer'].memory_optimizer = MagicMock()
            mock_modules['core.memory_optimizer'].memory_optimizer.start_monitoring = MagicMock()
            
            # Configure time.sleep to raise KeyboardInterrupt on first call
            mock_time.sleep.side_effect = KeyboardInterrupt()
            
            # Reload the module to apply the mocks
            importlib.reload(opryxx_launcher)
            
            # Create a new instance with the mocked imports
            launcher = opryxx_launcher.OPRYXXLauncher()
            
            # Test
            try:
                launcher.launch_performance()
                mock_perf_monitor.assert_called_once()
                mock_modules['core.memory_optimizer'].memory_optimizer.start_monitoring.assert_called_once()
                print("✅ test_launch_performance passed")
                return True
            except Exception as e:
                print(f"❌ test_launch_performance failed: {e}")
                import traceback
                traceback.print_exc()
                return False

def run_tests():
    """Run all test cases and return overall result."""
    print("🚀 Starting OPRYXX Launcher Tests...\n")
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestOPRYXXLauncher)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    run_tests()
