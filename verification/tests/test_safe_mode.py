"""
Unit tests for Safe Mode module
"""

import unittest
from unittest.mock import patch, MagicMock
from modules.safe_mode import SafeModeModule
from architecture.core import RecoveryStatus

class TestSafeModeModule(unittest.TestCase):
    
    def setUp(self):
        self.module = SafeModeModule()
    
    @patch('subprocess.run')
    def test_validate_prerequisites_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.module.validate_prerequisites())
    
    @patch('subprocess.run')
    def test_validate_prerequisites_failure(self, mock_run):
        mock_run.side_effect = Exception("Command not found")
        self.assertFalse(self.module.validate_prerequisites())
    
    @patch.dict('os.environ', {'SAFEBOOT_OPTION': 'MINIMAL'})
    def test_is_safe_mode_active_env_var(self):
        self.assertTrue(self.module._is_safe_mode_active())
    
    @patch('subprocess.run')
    def test_clear_safe_mode_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = self.module._clear_safe_mode()
        self.assertEqual(result.status, RecoveryStatus.SUCCESS)
        self.assertTrue(result.details.get('reboot_required'))

if __name__ == '__main__':
    unittest.main()