"""
End-to-end integration tests for OPRYXX_LOGS recovery system.

These tests verify the complete recovery process from driver backup
through system restoration.
"""
import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add recovery directory to path
sys.path.append(str(Path(__file__).parent.parent / 'recovery'))

# Import modules to test
from driver_manager import DriverManager

class TestRecoveryIntegration(unittest.TestCase):
    """Integration tests for the complete recovery process."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = tempfile.mkdtemp(prefix="opryxx_integration_test_")
        cls.backup_dir = os.path.join(cls.test_dir, "driver_backup")
        os.makedirs(cls.backup_dir, exist_ok=True)
        
        # Create a test driver structure
        cls.create_test_drivers()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_drivers(cls):
        """Create a test driver structure."""
        # Create test driver files
        drivers = {
            "network": ["net1.inf", "net2.inf"],
            "display": ["display1.inf", "display2.inf"],
            "storage": ["storage1.inf"]
        }
        
        for category, files in drivers.items():
            cat_dir = os.path.join(cls.test_dir, "drivers", category)
            os.makedirs(cat_dir, exist_ok=True)
            
            for file in files:
                with open(os.path.join(cat_dir, file), 'w') as f:
                    f.write(f"[Version]\nSignature=\"$WINDOWS NT$\"\n")
                    f.write(f"DriverVer=01/01/2023,1.0.0.0\n")
                    f.write(f"[DefaultInstall]\n")
                    f.write(f"CopyFiles=CopyToSystem\n")
                    f.write(f"[CopyToSystem]\n")
                    f.write(f"{file},,,\n")
    
    @patch('subprocess.run')
    def test_complete_recovery_flow(self, mock_run):
        """Test the complete recovery flow from backup to restore."""
        # Setup mock for subprocess.run
        mock_run.return_value.returncode = 0
        
        # Initialize driver manager
        dm = DriverManager(backup_dir=self.backup_dir)
        
        # 1. Test driver backup
        backup_name = "pre_recovery_backup"
        backup_path = dm.backup_drivers(backup_name)
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn(backup_name, os.path.basename(backup_path))
        
        # Verify metadata was updated
        self.assertIn(backup_name, dm.metadata['backups'])
        
        # 2. Test backup listing
        backups = dm.list_backups()
        self.assertGreaterEqual(len(backups), 1)
        backup_found = any(b['name'] == backup_name for b in backups)
        self.assertTrue(backup_found, f"Backup {backup_name} not found in {backups}")
        
        # 3. Simulate system restore
        # Create a test system state file
        system_state = {
            'backup_name': backup_name,
            'timestamp': '2023-01-01T00:00:00',
            'system_info': dm._get_system_info()
        }
        
        state_file = os.path.join(self.test_dir, 'system_state.json')
        with open(state_file, 'w') as f:
            json.dump(system_state, f)
        
        # 4. Test driver restoration
        # Mock the pnputil calls
        def mock_pnputil(args, **kwargs):
            if args[0] == 'pnputil' and args[1] == '/add-driver':
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)
        
        mock_run.side_effect = mock_pnputil
        
        # Perform restore
        restore_result = dm.restore_drivers(backup_name)
        self.assertTrue(restore_result, "Driver restoration failed")
        
        # 5. Verify cleanup of old backups
        # Create additional test backups
        for i in range(5):
            backup_dir = os.path.join(self.backup_dir, f"old_backup_{i}")
            os.makedirs(backup_dir, exist_ok=True)
            dm.metadata['backups'][f"old_backup_{i}"] = {
                'path': backup_dir,
                'timestamp': f'2023-01-{i+1:02d}T00:00:00'
            }
        
        # Clean up old backups, keep only 2
        dm.cleanup_old_backups(keep_last=2)
        
        # Verify only 2 backups remain (1 from this test + 2 kept)
        self.assertEqual(len(dm.metadata['backups']), 3)  # 1 from this test + 2 kept
    
    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test error handling during recovery operations."""
        # Test backup failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "DISM error: Access denied"
        
        with self.assertRaises(subprocess.CalledProcessError):
            dm = DriverManager(backup_dir=self.backup_dir)
            dm.backup_drivers("failing_backup")
        
        # Test restore with invalid backup
        dm = DriverManager(backup_dir=self.backup_dir)
        with self.assertRaises(KeyError):
            dm.restore_drivers("nonexistent_backup")


if __name__ == '__main__':
    unittest.main()
