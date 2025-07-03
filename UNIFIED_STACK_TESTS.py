"""
UNIFIED STACK COMPREHENSIVE TESTS
Complete testing suite for the unified recovery system
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ULTIMATE_UNIFIED_STACK import (
    SystemType, RecoveryStatus, SystemInfo, RecoveryResult,
    UnifiedLogger, HardwareDetector, RecoveryEngine
)

class TestUnifiedLogger(unittest.TestCase):
    """Test unified logging system"""
    
    def setUp(self):
        self.logger = UnifiedLogger("TEST")
    
    def test_logger_creation(self):
        """Test logger creation"""
        self.assertIsNotNone(self.logger.logger)
        self.assertEqual(self.logger.logger.name, "TEST")
    
    def test_logging_methods(self):
        """Test logging methods"""
        # These should not raise exceptions
        self.logger.info("Test info message")
        self.logger.warning("Test warning message")
        self.logger.error("Test error message")

class TestSystemInfo(unittest.TestCase):
    """Test SystemInfo dataclass"""
    
    def test_system_info_creation(self):
        """Test SystemInfo creation"""
        system_info = SystemInfo(
            manufacturer="Dell",
            model="Inspiron 2-in-1 7040",
            system_type=SystemType.DELL_INSPIRON_7040,
            drives=[],
            bitlocker_drives=[],
            raw_drives=[]
        )
        
        self.assertEqual(system_info.manufacturer, "Dell")
        self.assertEqual(system_info.model, "Inspiron 2-in-1 7040")
        self.assertEqual(system_info.system_type, SystemType.DELL_INSPIRON_7040)

class TestRecoveryResult(unittest.TestCase):
    """Test RecoveryResult dataclass"""
    
    def test_recovery_result_creation(self):
        """Test RecoveryResult creation"""
        result = RecoveryResult(
            status=RecoveryStatus.SUCCESS,
            message="Test successful",
            details={"test": True},
            timestamp=datetime.now().isoformat()
        )
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertEqual(result.message, "Test successful")
        self.assertTrue(result.details["test"])

class TestHardwareDetector(unittest.TestCase):
    """Test hardware detection"""
    
    def setUp(self):
        self.logger = UnifiedLogger("TEST")
        self.detector = HardwareDetector(self.logger)
    
    @patch('subprocess.run')
    def test_detect_system_dell(self, mock_run):
        """Test Dell system detection"""
        # Mock wmic output for Dell system
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Manufacturer  Model\nDell Inc.     Inspiron 2-in-1 7040"
        )
        
        with patch.object(self.detector, '_detect_drives', return_value=[]):
            with patch.object(self.detector, '_detect_bitlocker_drives', return_value=[]):
                with patch.object(self.detector, '_detect_raw_drives', return_value=[]):
                    system_info = self.detector.detect_system()
        
        self.assertEqual(system_info.manufacturer, "Dell")
        self.assertEqual(system_info.system_type, SystemType.DELL_INSPIRON_7040)
    
    @patch('subprocess.run')
    def test_detect_system_msi(self, mock_run):
        """Test MSI system detection"""
        # Mock wmic output for MSI system
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Manufacturer  Model\nMSI           Summit 16 2024"
        )
        
        with patch.object(self.detector, '_detect_drives', return_value=[]):
            with patch.object(self.detector, '_detect_bitlocker_drives', return_value=[]):
                with patch.object(self.detector, '_detect_raw_drives', return_value=[]):
                    system_info = self.detector.detect_system()
        
        self.assertEqual(system_info.manufacturer, "MSI")
        self.assertEqual(system_info.system_type, SystemType.MSI_SUMMIT_16_2024)
    
    @patch('subprocess.run')
    def test_detect_drives(self, mock_run):
        """Test drive detection"""
        # Mock wmic output for drives
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Model                    Size         InterfaceType\nSamsung SSD 4TB         4000000000000 SATA\nWD Notebook Drive       1000000000000 SATA"
        )
        
        drives = self.detector._detect_drives()
        
        self.assertEqual(len(drives), 2)
        self.assertIn("Samsung", drives[0]['model'])
        self.assertIn("WD", drives[1]['model'])
    
    @patch('subprocess.run')
    def test_detect_bitlocker_drives(self, mock_run):
        """Test BitLocker drive detection"""
        # Mock manage-bde output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="""Volume C:
Conversion Status: Fully Encrypted
Encryption Method: AES 256"""
        )
        
        bitlocker_drives = self.detector._detect_bitlocker_drives()
        
        self.assertEqual(len(bitlocker_drives), 1)
        self.assertEqual(bitlocker_drives[0]['drive'], 'C:')
    
    @patch('subprocess.run')
    def test_detect_raw_drives(self, mock_run):
        """Test RAW drive detection"""
        # Mock wmic output for RAW drives
        mock_run.return_value = Mock(
            returncode=0,
            stdout="DeviceID  FileSystem  Size\nD:        RAW         1000000000000\nE:                    2000000000000"
        )
        
        raw_drives = self.detector._detect_raw_drives()
        
        self.assertEqual(len(raw_drives), 2)
        self.assertEqual(raw_drives[0]['drive'], 'D:')
        self.assertEqual(raw_drives[0]['filesystem'], 'RAW')

class TestRecoveryEngine(unittest.TestCase):
    """Test recovery engine"""
    
    def setUp(self):
        self.logger = UnifiedLogger("TEST")
        self.engine = RecoveryEngine(self.logger)
        self.system_info = SystemInfo(
            manufacturer="Dell",
            model="Inspiron 2-in-1 7040",
            system_type=SystemType.DELL_INSPIRON_7040,
            drives=[{'model': 'Samsung SSD 4TB', 'size_bytes': 4000000000000, 'interface': 'SATA'}],
            bitlocker_drives=[{'drive': 'C:', 'status': 'Fully Encrypted', 'method': 'AES 256'}],
            raw_drives=[{'drive': 'D:', 'filesystem': 'RAW', 'size_bytes': 1000000000000}]
        )
    
    @patch('subprocess.run')
    def test_execute_dell_recovery_success(self, mock_run):
        """Test successful Dell recovery"""
        # Mock all commands to succeed
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        result = self.engine.execute_dell_recovery(self.system_info)
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertIn("Dell recovery completed successfully", result.message)
        self.assertEqual(result.details['success_rate'], 1.0)
    
    @patch('subprocess.run')
    def test_execute_dell_recovery_partial(self, mock_run):
        """Test partial Dell recovery"""
        # Mock some commands to fail
        mock_run.side_effect = [
            Mock(returncode=0, stderr=""),  # Success
            Mock(returncode=1, stderr="Failed"),  # Failure
            Mock(returncode=0, stderr=""),  # Success
            Mock(returncode=1, stderr="Failed"),  # Failure
            Mock(returncode=0, stderr=""),  # Success
            Mock(returncode=0, stderr=""),  # Success
            Mock(returncode=0, stderr=""),  # Success
            Mock(returncode=0, stderr="")   # Success
        ]
        
        result = self.engine.execute_dell_recovery(self.system_info)
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)  # 6/8 = 75% success
        self.assertIn("Dell recovery completed successfully", result.message)
    
    def test_execute_msi_optimization(self):
        """Test MSI optimization"""
        with patch.object(self.engine, '_set_high_performance', return_value=True):
            with patch.object(self.engine, '_optimize_gaming_mode', return_value=True):
                with patch.object(self.engine, '_optimize_thermal', return_value=True):
                    with patch.object(self.engine, '_optimize_drivers', return_value=True):
                        result = self.engine.execute_msi_optimization(self.system_info)
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertIn("MSI optimization completed successfully", result.message)
        self.assertEqual(result.details['success_rate'], 1.0)
    
    def test_execute_samsung_recovery(self):
        """Test Samsung SSD recovery"""
        with patch.object(self.engine, '_detect_samsung_drives', return_value=True):
            with patch.object(self.engine, '_recover_raw_partitions', return_value=True):
                with patch.object(self.engine, '_analyze_bitlocker', return_value=True):
                    with patch.object(self.engine, '_extract_data', return_value=True):
                        result = self.engine.execute_samsung_recovery(self.system_info)
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertIn("Samsung recovery completed successfully", result.message)
        self.assertEqual(result.details['success_rate'], 1.0)
    
    def test_execute_wd_recovery_no_drives(self):
        """Test WD recovery with no WD drives"""
        system_info_no_wd = SystemInfo(
            manufacturer="Dell",
            model="Test",
            system_type=SystemType.GENERIC,
            drives=[{'model': 'Samsung SSD', 'size_bytes': 1000000000000, 'interface': 'SATA'}],
            bitlocker_drives=[],
            raw_drives=[]
        )
        
        result = self.engine.execute_wd_recovery(system_info_no_wd)
        
        self.assertEqual(result.status, RecoveryStatus.FAILED)
        self.assertEqual(result.message, "No WD drives detected")
    
    def test_execute_wd_recovery_with_drives(self):
        """Test WD recovery with WD drives"""
        system_info_wd = SystemInfo(
            manufacturer="Generic",
            model="Test",
            system_type=SystemType.GENERIC,
            drives=[{'model': 'WD Notebook Drive', 'size_bytes': 1000000000000, 'interface': 'SATA'}],
            bitlocker_drives=[],
            raw_drives=[]
        )
        
        with patch.object(self.engine, '_analyze_wd_partitions', return_value=True):
            with patch.object(self.engine, '_repair_wd_filesystem', return_value=True):
                with patch.object(self.engine, '_recover_wd_data', return_value=True):
                    result = self.engine.execute_wd_recovery(system_info_wd)
        
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertIn("WD recovery completed successfully", result.message)

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.logger = UnifiedLogger("INTEGRATION_TEST")
        self.detector = HardwareDetector(self.logger)
        self.engine = RecoveryEngine(self.logger)
    
    def test_full_workflow_mock(self):
        """Test complete workflow with mocked components"""
        # Mock system detection
        mock_system_info = SystemInfo(
            manufacturer="Dell",
            model="Inspiron 2-in-1 7040",
            system_type=SystemType.DELL_INSPIRON_7040,
            drives=[
                {'model': 'Samsung SSD 4TB', 'size_bytes': 4000000000000, 'interface': 'SATA'},
                {'model': 'WD Notebook Drive', 'size_bytes': 1000000000000, 'interface': 'SATA'}
            ],
            bitlocker_drives=[{'drive': 'C:', 'status': 'Fully Encrypted', 'method': 'AES 256'}],
            raw_drives=[{'drive': 'D:', 'filesystem': 'RAW', 'size_bytes': 1000000000000}]
        )
        
        # Test Dell recovery
        with patch('subprocess.run', return_value=Mock(returncode=0, stderr="")):
            dell_result = self.engine.execute_dell_recovery(mock_system_info)
            self.assertEqual(dell_result.status, RecoveryStatus.SUCCESS)
        
        # Test MSI optimization
        with patch.object(self.engine, '_set_high_performance', return_value=True):
            with patch.object(self.engine, '_optimize_gaming_mode', return_value=True):
                with patch.object(self.engine, '_optimize_thermal', return_value=True):
                    with patch.object(self.engine, '_optimize_drivers', return_value=True):
                        msi_result = self.engine.execute_msi_optimization(mock_system_info)
                        self.assertEqual(msi_result.status, RecoveryStatus.SUCCESS)
        
        # Test Samsung recovery
        with patch.object(self.engine, '_detect_samsung_drives', return_value=True):
            with patch.object(self.engine, '_recover_raw_partitions', return_value=True):
                with patch.object(self.engine, '_analyze_bitlocker', return_value=True):
                    with patch.object(self.engine, '_extract_data', return_value=True):
                        samsung_result = self.engine.execute_samsung_recovery(mock_system_info)
                        self.assertEqual(samsung_result.status, RecoveryStatus.SUCCESS)
        
        # Test WD recovery
        with patch.object(self.engine, '_analyze_wd_partitions', return_value=True):
            with patch.object(self.engine, '_repair_wd_filesystem', return_value=True):
                with patch.object(self.engine, '_recover_wd_data', return_value=True):
                    wd_result = self.engine.execute_wd_recovery(mock_system_info)
                    self.assertEqual(wd_result.status, RecoveryStatus.SUCCESS)

class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        self.logger = UnifiedLogger("PERFORMANCE_TEST")
        self.detector = HardwareDetector(self.logger)
        self.engine = RecoveryEngine(self.logger)
    
    def test_detection_performance(self):
        """Test hardware detection performance"""
        start_time = time.time()
        
        with patch('subprocess.run', return_value=Mock(returncode=0, stdout="Test output")):
            with patch.object(self.detector, '_detect_drives', return_value=[]):
                with patch.object(self.detector, '_detect_bitlocker_drives', return_value=[]):
                    with patch.object(self.detector, '_detect_raw_drives', return_value=[]):
                        system_info = self.detector.detect_system()
        
        end_time = time.time()
        detection_time = end_time - start_time
        
        # Detection should complete within 5 seconds
        self.assertLess(detection_time, 5.0)
    
    def test_recovery_performance(self):
        """Test recovery operation performance"""
        mock_system_info = SystemInfo(
            manufacturer="Dell",
            model="Test",
            system_type=SystemType.DELL_INSPIRON_7040,
            drives=[],
            bitlocker_drives=[],
            raw_drives=[]
        )
        
        start_time = time.time()
        
        with patch('subprocess.run', return_value=Mock(returncode=0, stderr="")):
            result = self.engine.execute_dell_recovery(mock_system_info)
        
        end_time = time.time()
        recovery_time = end_time - start_time
        
        # Recovery should complete within 30 seconds (mocked)
        self.assertLess(recovery_time, 30.0)
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)

class TestErrorHandling(unittest.TestCase):
    """Error handling tests"""
    
    def setUp(self):
        self.logger = UnifiedLogger("ERROR_TEST")
        self.detector = HardwareDetector(self.logger)
        self.engine = RecoveryEngine(self.logger)
    
    def test_detection_error_handling(self):
        """Test error handling in detection"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            system_info = self.detector.detect_system()
            
            # Should return default values on error
            self.assertEqual(system_info.manufacturer, "Unknown")
            self.assertEqual(system_info.model, "Unknown")
            self.assertEqual(system_info.system_type, SystemType.GENERIC)
    
    def test_recovery_error_handling(self):
        """Test error handling in recovery"""
        mock_system_info = SystemInfo(
            manufacturer="Dell",
            model="Test",
            system_type=SystemType.DELL_INSPIRON_7040,
            drives=[],
            bitlocker_drives=[],
            raw_drives=[]
        )
        
        with patch('subprocess.run', side_effect=Exception("Test error")):
            result = self.engine.execute_dell_recovery(mock_system_info)
            
            # Should handle errors gracefully
            self.assertEqual(result.status, RecoveryStatus.FAILED)
            self.assertIn("0/8", result.message)  # No commands succeeded

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("UNIFIED STACK COMPREHENSIVE TESTS")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestUnifiedLogger,
        TestSystemInfo,
        TestRecoveryResult,
        TestHardwareDetector,
        TestRecoveryEngine,
        TestIntegration,
        TestPerformance,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate test report
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
        'status': 'PASS' if result.wasSuccessful() else 'FAIL'
    }
    
    # Save test report
    with open(f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(test_report, f, indent=2)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {test_report['tests_run']}")
    print(f"Failures: {test_report['failures']}")
    print(f"Errors: {test_report['errors']}")
    print(f"Success Rate: {test_report['success_rate']:.1f}%")
    print(f"Overall Status: {test_report['status']}")
    print("=" * 50)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)