"""
Comprehensive tests for OPRYXX Unified System
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.base import BaseModule, ModuleRegistry, ModuleResult, ModuleStatus
from core.config import Config
from modules.recovery.samsung_recovery import SamsungRecoveryModule
from modules.recovery.dell_recovery import DellRecoveryModule
from modules.ai.optimization_engine import AIOptimizationModule
from unified_system import UnifiedOPRYXXSystem

class TestBaseModule(unittest.TestCase):
    """Test base module functionality"""
    
    def setUp(self):
        class TestModule(BaseModule):
            def initialize(self):
                return ModuleResult(True, "Test initialized")
            
            def execute(self, **kwargs):
                return ModuleResult(True, "Test executed", data=kwargs)
            
            def cleanup(self):
                return ModuleResult(True, "Test cleaned up")
        
        self.test_module = TestModule("test_module")
    
    def test_module_initialization(self):
        """Test module initialization"""
        self.assertEqual(self.test_module.name, "test_module")
        self.assertEqual(self.test_module.status, ModuleStatus.INACTIVE)
        self.assertFalse(self.test_module.is_ready())
    
    def test_module_status_management(self):
        """Test module status management"""
        self.test_module.set_status(ModuleStatus.ACTIVE)
        self.assertEqual(self.test_module.get_status(), ModuleStatus.ACTIVE)
        self.assertTrue(self.test_module.is_ready())
    
    def test_module_execution(self):
        """Test module execution"""
        result = self.test_module.execute(test_param="test_value")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test executed")
        self.assertEqual(result.data["test_param"], "test_value")

class TestModuleRegistry(unittest.TestCase):
    """Test module registry functionality"""
    
    def setUp(self):
        self.registry = ModuleRegistry()
        
        class MockModule(BaseModule):
            def initialize(self):
                return ModuleResult(True, "Mock initialized")
            
            def execute(self, **kwargs):
                return ModuleResult(True, "Mock executed")
            
            def cleanup(self):
                return ModuleResult(True, "Mock cleaned up")
        
        self.mock_module = MockModule("mock_module")
    
    def test_module_registration(self):
        """Test module registration"""
        self.assertTrue(self.registry.register(self.mock_module))
        self.assertFalse(self.registry.register(self.mock_module))  # Duplicate
        
        retrieved = self.registry.get_module("mock_module")
        self.assertEqual(retrieved, self.mock_module)
    
    def test_module_unregistration(self):
        """Test module unregistration"""
        self.registry.register(self.mock_module)
        self.assertTrue(self.registry.unregister("mock_module"))
        self.assertFalse(self.registry.unregister("nonexistent"))
        
        self.assertIsNone(self.registry.get_module("mock_module"))
    
    def test_initialize_all_modules(self):
        """Test initializing all modules"""
        self.registry.register(self.mock_module)
        results = self.registry.initialize_all()
        
        self.assertIn("mock_module", results)
        self.assertTrue(results["mock_module"].success)
        self.assertEqual(self.mock_module.get_status(), ModuleStatus.ACTIVE)

class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.config = Config("test_config.json")
    
    def test_default_configuration(self):
        """Test default configuration values"""
        self.assertFalse(self.config.system.debug)
        self.assertEqual(self.config.system.log_level, "INFO")
        self.assertTrue(self.config.recovery.auto_backup)
    
    def test_configuration_get_set(self):
        """Test configuration get/set operations"""
        self.config.set("system", "debug", True)
        self.assertTrue(self.config.get("system", "debug"))
        
        # Test default value
        self.assertEqual(self.config.get("nonexistent", "key", "default"), "default")
    
    def tearDown(self):
        # Clean up test config file
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

class TestSamsungRecoveryModule(unittest.TestCase):
    """Test Samsung recovery module"""
    
    def setUp(self):
        self.module = SamsungRecoveryModule()
    
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_admin_check(self, mock_admin):
        """Test administrator privilege check"""
        mock_admin.return_value = 1
        self.assertTrue(self.module._check_admin())
        
        mock_admin.return_value = 0
        self.assertFalse(self.module._check_admin())
    
    @patch('subprocess.run')
    def test_command_execution(self, mock_run):
        """Test command execution"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "success"
        mock_run.return_value.stderr = ""
        
        success, output = self.module._run_command(['test', 'command'])
        self.assertTrue(success)
        self.assertEqual(output, "success")
    
    @patch('subprocess.run')
    def test_samsung_drive_detection(self, mock_run):
        """Test Samsung drive detection"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '''[{
            "Number": 1,
            "FriendlyName": "Samsung SSD 980 PRO 4TB",
            "Size": 4000000000000
        }]'''
        mock_run.return_value.stderr = ""
        
        drives = self.module._detect_samsung_drives()
        self.assertEqual(len(drives), 1)
        self.assertEqual(drives[0]['number'], 1)
        self.assertAlmostEqual(drives[0]['size_gb'], 3725.29, places=1)

class TestDellRecoveryModule(unittest.TestCase):
    """Test Dell recovery module"""
    
    def setUp(self):
        self.module = DellRecoveryModule()
    
    @patch('subprocess.run')
    def test_dell_system_detection(self, mock_run):
        """Test Dell system detection"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '''{
            "Manufacturer": "Dell Inc.",
            "Model": "Inspiron 7040"
        }'''
        mock_run.return_value.stderr = ""
        
        system_info = self.module._detect_dell_system()
        self.assertTrue(system_info['is_dell'])
        self.assertIn('inspiron', system_info['model'])
    
    @patch('subprocess.run')
    def test_boot_issue_detection(self, mock_run):
        """Test boot issue detection"""
        # Mock BCD corruption
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "error"
        
        issues = self.module._check_boot_issues()
        self.assertIn('bcd_corruption', issues)

class TestAIOptimizationModule(unittest.TestCase):
    """Test AI optimization module"""
    
    def setUp(self):
        self.module = AIOptimizationModule()
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_metrics_collection(self, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value.percent = 60.0
        mock_disk.return_value.used = 500000000000
        mock_disk.return_value.total = 1000000000000
        
        metrics = self.module._collect_metrics()
        self.assertEqual(metrics.cpu_usage, 50.0)
        self.assertEqual(metrics.memory_usage, 60.0)
        self.assertEqual(metrics.disk_usage, 50.0)
    
    def test_performance_prediction(self):
        """Test performance prediction"""
        from modules.ai.optimization_engine import SystemMetrics
        
        # Good performance metrics
        good_metrics = SystemMetrics(30.0, 40.0, 20.0, 10.0)
        score = self.module._predict_performance(good_metrics)
        self.assertGreater(score, 70)
        
        # Poor performance metrics
        poor_metrics = SystemMetrics(90.0, 95.0, 95.0, 0.0)
        score = self.module._predict_performance(poor_metrics)
        self.assertLess(score, 30)
    
    def test_optimization_generation(self):
        """Test optimization action generation"""
        from modules.ai.optimization_engine import SystemMetrics
        
        high_usage_metrics = SystemMetrics(85.0, 80.0, 90.0, 0.0)
        actions = self.module._generate_optimizations(high_usage_metrics)
        
        self.assertGreater(len(actions), 0)
        action_types = [action.action_type for action in actions]
        self.assertIn("cpu_optimization", action_types)
        self.assertIn("memory_cleanup", action_types)
        self.assertIn("disk_cleanup", action_types)

class TestUnifiedSystem(unittest.TestCase):
    """Test unified OPRYXX system"""
    
    def setUp(self):
        self.system = UnifiedOPRYXXSystem()
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertIsNotNone(self.system.registry)
        self.assertIsNotNone(self.system.config)
        self.assertIsNotNone(self.system.logger)
    
    def test_module_registration(self):
        """Test module registration during setup"""
        modules = self.system.registry.get_all_modules()
        self.assertIn("samsung_recovery", modules)
        self.assertIn("dell_recovery", modules)
        self.assertIn("ai_optimization", modules)
    
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_system_status(self, mock_admin):
        """Test system status reporting"""
        mock_admin.return_value = 1
        
        # Initialize system
        self.system.initialize()
        
        status = self.system.get_system_status()
        self.assertIn('system_ready', status)
        self.assertIn('modules', status)
        self.assertIn('timestamp', status)
        
        # Check module statuses
        for module_name in ['samsung_recovery', 'dell_recovery', 'ai_optimization']:
            self.assertIn(module_name, status['modules'])

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_full_system_workflow(self, mock_admin):
        """Test complete system workflow"""
        mock_admin.return_value = 1
        
        # Initialize system
        system = UnifiedOPRYXXSystem()
        init_results = system.initialize()
        
        # Verify initialization
        self.assertTrue(all(result.success for result in init_results.values()))
        
        # Test system status
        status = system.get_system_status()
        self.assertTrue(status['system_ready'])
        
        # Test AI optimization (mocked)
        with patch('psutil.cpu_percent', return_value=30.0), \
             patch('psutil.virtual_memory') as mock_mem, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_mem.return_value.percent = 40.0
            mock_disk.return_value.used = 200000000000
            mock_disk.return_value.total = 1000000000000
            
            result = system.execute_recovery("ai_optimization")
            self.assertTrue(result.success)
        
        # Cleanup
        system.shutdown()

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestBaseModule,
        TestModuleRegistry,
        TestConfig,
        TestSamsungRecoveryModule,
        TestDellRecoveryModule,
        TestAIOptimizationModule,
        TestUnifiedSystem,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)