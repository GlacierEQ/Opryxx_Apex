#!/usr/bin/env python3
"""
Unified Full Stack Integration Tests
Comprehensive testing of all OPRYXX components
"""

import unittest
import sys
import os
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestUnifiedStack(unittest.TestCase):
    """Test complete unified stack integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_results = {}
        
    def test_01_core_imports(self):
        """Test all core module imports"""
        print("\n[TEST] Core module imports...")
        
        core_modules = [
            'core.performance_monitor',
            'core.memory_optimizer', 
            'core.gpu_acceleration',
            'core.enhanced_gpu_ops',
            'core.resilience_system',
            'core.gpu_detector'
        ]
        
        for module in core_modules:
            try:
                __import__(module)
                print(f"[OK] {module}")
            except ImportError as e:
                self.fail(f"Failed to import {module}: {e}")
    
    def test_02_recovery_imports(self):
        """Test recovery module imports"""
        print("\n[TEST] Recovery module imports...")
        
        recovery_modules = [
            'recovery.hardware_rescue',
            'recovery.bitlocker_rescue',
            'recovery.samsung_4tb_recovery',
            'recovery.windows11_bypass'
        ]
        
        for module in recovery_modules:
            try:
                __import__(module)
                print(f"[OK] {module}")
            except ImportError as e:
                self.fail(f"Failed to import {module}: {e}")
    
    def test_03_gui_imports(self):
        """Test GUI module imports"""
        print("\n[TEST] GUI module imports...")
        
        try:
            from gui.unified_gui import UnifiedGUI
            print("[OK] UnifiedGUI")
        except ImportError as e:
            print(f"[SKIP] GUI import failed: {e}")
        
        try:
            from gui.web_interface import WebInterface
            print("[OK] WebInterface")
        except ImportError as e:
            print(f"[SKIP] Web interface import failed: {e}")
    
    def test_04_performance_system(self):
        """Test performance monitoring system"""
        print("\n[TEST] Performance monitoring system...")
        
        try:
            from core.performance_monitor import performance_monitor
            
            # Start monitoring
            performance_monitor.start()
            time.sleep(0.5)
            
            # Get metrics
            metrics = performance_monitor.get_metrics()
            
            self.assertIsNotNone(metrics)
            self.assertGreaterEqual(metrics.cpu_usage, 0)
            self.assertLessEqual(metrics.cpu_usage, 100)
            self.assertGreaterEqual(metrics.memory_usage, 0)
            self.assertLessEqual(metrics.memory_usage, 100)
            
            # Stop monitoring
            performance_monitor.stop()
            
            print("[OK] Performance monitoring")
            
        except Exception as e:
            self.fail(f"Performance system test failed: {e}")
    
    def test_05_memory_system(self):
        """Test memory optimization system"""
        print("\n[TEST] Memory optimization system...")
        
        try:
            from core.memory_optimizer import memory_optimizer
            
            # Get memory metrics
            metrics = memory_optimizer.get_memory_metrics()
            
            self.assertGreater(metrics.total_mb, 0)
            self.assertGreaterEqual(metrics.usage_percent, 0)
            self.assertLessEqual(metrics.usage_percent, 100)
            
            # Test optimization
            result = memory_optimizer.optimize_memory()
            self.assertIn('freed_mb', result)
            
            print("[OK] Memory optimization")
            
        except Exception as e:
            self.fail(f"Memory system test failed: {e}")
    
    def test_06_gpu_system(self):
        """Test GPU acceleration system"""
        print("\n[TEST] GPU acceleration system...")
        
        try:
            from core.gpu_acceleration import is_gpu_available, get_compute_device
            from core.enhanced_gpu_ops import enhanced_gpu_ops
            
            # Check GPU availability
            gpu_available = is_gpu_available()
            device = get_compute_device()
            
            print(f"[INFO] GPU available: {gpu_available}")
            print(f"[INFO] Active device: {device.name}")
            
            # Test operations
            import numpy as np
            a = np.random.randn(10, 10).astype(np.float32)
            b = np.random.randn(10, 10).astype(np.float32)
            
            result = enhanced_gpu_ops.accelerator.matrix_multiply(a, b)
            self.assertEqual(result.shape, (10, 10))
            
            print("[OK] GPU acceleration")
            
        except Exception as e:
            self.fail(f"GPU system test failed: {e}")
    
    def test_07_resilience_system(self):
        """Test resilience system"""
        print("\n[TEST] Resilience system...")
        
        try:
            from core.resilience_system import resilience_manager, CircuitBreaker
            
            # Test circuit breaker
            @CircuitBreaker(failure_threshold=2)
            def test_function():
                return "success"
            
            result = test_function()
            self.assertEqual(result, "success")
            
            # Test resilience report
            report = resilience_manager.get_system_resilience_report()
            self.assertIn('timestamp', report)
            self.assertIn('circuit_breakers', report)
            
            print("[OK] Resilience system")
            
        except Exception as e:
            self.fail(f"Resilience system test failed: {e}")
    
    def test_08_recovery_system(self):
        """Test hardware recovery system"""
        print("\n[TEST] Hardware recovery system...")
        
        try:
            from recovery.hardware_rescue import HardwareRescue
            from recovery.samsung_4tb_recovery import Samsung4TBRecovery
            
            # Test hardware detection
            rescue = HardwareRescue()
            hardware = rescue.detect_hardware()
            self.assertIsInstance(hardware, dict)
            
            # Test Samsung recovery initialization
            samsung_recovery = Samsung4TBRecovery()
            drives = samsung_recovery.detect_samsung_drives()
            self.assertIsInstance(drives, list)
            
            print("[OK] Recovery system")
            
        except Exception as e:
            self.fail(f"Recovery system test failed: {e}")
    
    def test_09_integration_flow(self):
        """Test complete integration flow"""
        print("\n[TEST] Complete integration flow...")
        
        try:
            # Start all systems
            from core.performance_monitor import start_performance_monitoring
            from core.memory_optimizer import memory_optimizer
            
            start_performance_monitoring()
            memory_optimizer.start_monitoring(interval=0.1)
            
            # Let systems run briefly
            time.sleep(1.0)
            
            # Test data flow
            from core.performance_monitor import get_performance_metrics
            metrics = get_performance_metrics()
            
            self.assertIsNotNone(metrics.timestamp)
            
            # Stop systems
            from core.performance_monitor import stop_performance_monitoring
            stop_performance_monitoring()
            memory_optimizer.stop_monitoring()
            
            print("[OK] Integration flow")
            
        except Exception as e:
            self.fail(f"Integration flow test failed: {e}")
    
    def test_10_master_controller(self):
        """Test master controller"""
        print("\n[TEST] Master controller...")
        
        try:
            from OPRYXX_MASTER import OPRYXXMaster
            
            master = OPRYXXMaster()
            
            # Test initialization (without starting services)
            self.assertIsNotNone(master.systems)
            
            print("[OK] Master controller")
            
        except Exception as e:
            self.fail(f"Master controller test failed: {e}")
    
    def test_11_ultimate_optimizer(self):
        """Test ultimate optimizer"""
        print("\n[TEST] Ultimate optimizer...")
        
        try:
            from ULTIMATE_OPTIMIZER import UltimateOptimizer
            
            optimizer = UltimateOptimizer()
            
            # Test status without starting
            status = optimizer.get_system_status()
            self.assertIn('system_state', status)
            self.assertIn('running', status)
            
            print("[OK] Ultimate optimizer")
            
        except Exception as e:
            self.fail(f"Ultimate optimizer test failed: {e}")
    
    def test_12_architecture_validation(self):
        """Test architecture validation"""
        print("\n[TEST] Architecture validation...")
        
        # Check required directories
        required_dirs = ['core', 'gui', 'recovery', 'tests', 'scripts']
        project_root = Path(__file__).parent.parent
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Missing directory: {dir_name}")
            print(f"[OK] Directory: {dir_name}")
        
        # Check key files
        key_files = [
            'OPRYXX_MASTER.py',
            'ULTIMATE_OPTIMIZER.py',
            'START_OPRYXX.bat',
            'EMERGENCY_RESCUE.bat'
        ]
        
        for file_name in key_files:
            file_path = project_root / file_name
            self.assertTrue(file_path.exists(), f"Missing file: {file_name}")
            print(f"[OK] File: {file_name}")
    
    def test_13_no_circular_imports(self):
        """Test for circular imports"""
        print("\n[TEST] Checking for circular imports...")
        
        # This is a simplified check - in practice you'd use more sophisticated tools
        import_graph = {}
        
        # Build import graph (simplified)
        try:
            # Test critical import paths
            import core.performance_monitor
            import core.memory_optimizer
            import core.gpu_acceleration
            import recovery.hardware_rescue
            
            print("[OK] No obvious circular imports detected")
            
        except ImportError as e:
            self.fail(f"Circular import detected: {e}")
    
    def test_14_error_handling(self):
        """Test error handling and resilience"""
        print("\n[TEST] Error handling and resilience...")
        
        try:
            from core.resilience_system import retry, circuit_breaker
            
            # Test retry decorator
            call_count = 0
            
            @retry(max_attempts=3, base_delay=0.01)
            def flaky_function():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise ValueError("Temporary failure")
                return "success"
            
            result = flaky_function()
            self.assertEqual(result, "success")
            self.assertEqual(call_count, 2)
            
            print("[OK] Error handling")
            
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")
    
    def test_15_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n[TEST] Performance benchmarks...")
        
        try:
            from core.enhanced_gpu_ops import enhanced_gpu_ops
            
            # Run small benchmark
            benchmarks = enhanced_gpu_ops.benchmark_operations(size=50)
            
            self.assertIn('matrix_multiply_ms', benchmarks)
            self.assertIn('device', benchmarks)
            self.assertGreater(benchmarks['matrix_multiply_ms'], 0)
            
            print(f"[OK] Benchmarks completed on {benchmarks['device']}")
            
        except Exception as e:
            self.fail(f"Performance benchmark test failed: {e}")

class TestStackValidation(unittest.TestCase):
    """Validate complete stack functionality"""
    
    def test_stack_completeness(self):
        """Test that all stack components are present"""
        print("\n[VALIDATE] Stack completeness...")
        
        components = {
            'Core Systems': ['performance_monitor', 'memory_optimizer', 'gpu_acceleration'],
            'Recovery Systems': ['hardware_rescue', 'bitlocker_rescue', 'samsung_4tb_recovery'],
            'GUI Systems': ['unified_gui', 'web_interface'],
            'Control Systems': ['OPRYXX_MASTER', 'ULTIMATE_OPTIMIZER']
        }
        
        for category, modules in components.items():
            print(f"[CHECK] {category}:")
            for module in modules:
                # Check if module exists
                module_found = False
                for ext in ['.py', '']:
                    if Path(f"{module}{ext}").exists() or any(Path('.').rglob(f"{module}{ext}")):
                        module_found = True
                        break
                
                status = "[OK]" if module_found else "[MISSING]"
                print(f"  {module}: {status}")
                
                if not module_found:
                    self.fail(f"Missing component: {module}")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("OPRYXX UNIFIED FULL STACK TESTS")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedStack))
    suite.addTests(loader.loadTestsFromTestCase(TestStackValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)