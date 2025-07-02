"""
Full Stack Integration Verification
Tests all components working together
"""

import unittest
import threading
import time
import requests
from unittest.mock import patch, MagicMock

# Test imports to verify all modules are accessible
try:
    from core.performance_monitor import performance_monitor
    from core.memory_optimizer import memory_optimizer
    from core.enhanced_gpu_ops import enhanced_gpu_ops
    from core.resilience_system import resilience_manager
    from gui.unified_gui import UnifiedGUI
    from gui.web_interface import WebInterface
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

class TestFullStackIntegration(unittest.TestCase):
    
    def test_imports(self):
        """Verify all modules import correctly"""
        self.assertTrue(IMPORTS_OK, f"Import failed: {IMPORT_ERROR if not IMPORTS_OK else 'OK'}")
    
    def test_core_systems_integration(self):
        """Test core systems work together"""
        # Start performance monitoring
        performance_monitor.start()
        time.sleep(0.1)
        
        # Get metrics
        metrics = performance_monitor.get_metrics()
        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.cpu_usage, 0)
        
        # Test memory optimizer
        mem_metrics = memory_optimizer.get_memory_metrics()
        self.assertGreater(mem_metrics.total_mb, 0)
        
        # Test GPU operations
        device = enhanced_gpu_ops.accelerator.active_device
        self.assertIsNotNone(device)
        
        # Stop monitoring
        performance_monitor.stop()
    
    def test_gui_initialization(self):
        """Test GUI can be initialized"""
        with patch('tkinter.Tk'):
            gui = UnifiedGUI()
            self.assertIsNotNone(gui)
    
    def test_web_interface_setup(self):
        """Test web interface setup"""
        web = WebInterface()
        self.assertIsNotNone(web)
    
    def test_data_flow(self):
        """Test data flows between components"""
        # Start systems
        performance_monitor.start()
        memory_optimizer.start_monitoring(interval=0.1)
        
        time.sleep(0.2)
        
        # Verify data is flowing
        perf_metrics = performance_monitor.get_metrics()
        mem_metrics = memory_optimizer.get_memory_metrics()
        
        self.assertIsNotNone(perf_metrics.timestamp)
        self.assertIsNotNone(mem_metrics.total_mb)
        
        # Stop systems
        performance_monitor.stop()
        memory_optimizer.stop_monitoring()
    
    def test_resilience_integration(self):
        """Test resilience system integration"""
        report = resilience_manager.get_system_resilience_report()
        self.assertIn('timestamp', report)
        self.assertIn('circuit_breakers', report)
        self.assertIn('system_healthy', report)

if __name__ == '__main__':
    unittest.main(verbosity=2)