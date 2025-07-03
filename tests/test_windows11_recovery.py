"""
Test cases for Windows 11 Recovery module
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from core.modules.windows11_recovery import Windows11Recovery

class TestWindows11Recovery(unittest.TestCase):
    """Test cases for Windows11Recovery class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.recovery = Windows11Recovery()
        
    @patch('subprocess.run')
    def test_check_tpm_success(self, mock_run):
        """Test TPM check with successful response"""
        # Mock the subprocess.run output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"TpmPresent": true, "TpmReady": true, "TpmVersion": "2.0"}'
        mock_run.return_value = mock_result
        
        result = self.recovery.check_tpm()
        self.assertTrue(result['passed'])
        self.assertIn('TPM 2.0', result['message'])
        
    @patch('subprocess.run')
    def test_check_secure_boot_enabled(self, mock_run):
        """Test Secure Boot check when enabled"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'True'
        mock_run.return_value = mock_result
        
        result = self.recovery.check_secure_boot()
        self.assertTrue(result['passed'])
        self.assertIn('enabled', result['message'])
        
    @patch('psutil.virtual_memory')
    def test_check_ram_sufficient(self, mock_virtmem):
        """Test RAM check with sufficient memory"""
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024**3  # 8GB
        mock_virtmem.return_value = mock_mem
        
        result = self.recovery.check_ram()
        self.assertTrue(result['passed'])
        self.assertIn('8.0GB', result['message'])
        
    @patch('psutil.disk_usage')
    def test_check_storage_sufficient(self, mock_disk):
        """Test storage check with sufficient space"""
        mock_disk.return_value.total = 256 * 1024**3  # 256GB
        
        result = self.recovery.check_storage()
        self.assertTrue(result['passed'])
        self.assertIn('256.0GB', result['message'])
        
    @patch('winreg.CreateKey')
    @patch('winreg.SetValueEx')
    def test_bypass_tpm_check_admin(self, mock_set, mock_create):
        """Test TPM bypass with admin privileges"""
        with patch.object(self.recovery, 'is_admin', True):
            result = self.recovery.bypass_tpm_check()
            self.assertTrue(result['success'])
            self.assertIn('bypassed', result['message'])
            
    @patch('builtins.open')
    @patch('os.makedirs')
    def test_create_registry_bypass(self, mock_mkdir, mock_open):
        """Test creation of registry bypass file"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        success, path = self.recovery.create_registry_bypass()
        self.assertTrue(success)
        self.assertIn('win11_bypass.reg', path)
        mock_file.write.assert_called()
        
    def test_check_upgrade_status(self):
        """Test complete upgrade status check"""
        with patch.multiple(
            self.recovery,
            check_tpm=MagicMock(return_value={'passed': True, 'message': 'Mock TPM'}),
            check_secure_boot=MagicMock(return_value={'passed': True, 'message': 'Mock Secure Boot'}),
            check_ram=MagicMock(return_value={'passed': True, 'message': 'Mock RAM'}),
            check_storage=MagicMock(return_value={'passed': True, 'message': 'Mock Storage'}),
            check_cpu=MagicMock(return_value={'passed': True, 'message': 'Mock CPU'})
        ):
            status = self.recovery.check_upgrade_status()
            self.assertEqual(len(status), 7)  # 5 checks + is_admin + system_info
            self.assertTrue(all(check['passed'] for key, check in status.items() 
                             if key not in ['is_admin', 'system_info']))

if __name__ == '__main__':
    unittest.main()
