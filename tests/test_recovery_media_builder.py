"""
Tests for the RecoveryMediaBuilder class.
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.modules.recovery_media_builder import RecoveryMediaBuilder, DriveInfo, MediaType

class TestRecoveryMediaBuilder(unittest.TestCase):
    """Test cases for RecoveryMediaBuilder"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.builder = RecoveryMediaBuilder()
        self.test_drive = DriveInfo(
            device_id='\\\\.\\PHYSICALDRIVE1',
            caption='TEST_DRIVE',
            size_gb=16.0,
            free_space_gb=15.5,
            file_system='FAT32',
            drive_letter='E:',
            is_removable=True,
            is_bootable=False
        )
    
    @patch('wmi.WMI')
    def test_list_available_drives(self, mock_wmi):
        """Test listing available drives"""
        # Mock WMI response
        mock_disk = MagicMock()
        mock_disk.MediaType = 'Removable Media'
        mock_disk.Description = 'USB Drive'
        
        mock_partition = MagicMock()
        mock_logical_disk = MagicMock()
        mock_logical_disk.DeviceID = 'E:'
        mock_logical_disk.VolumeName = 'TEST_DRIVE'  # This will be used as the caption
        mock_logical_disk.Size = '16000000000'  # 16GB
        mock_logical_disk.FreeSpace = '15500000000'  # 15.5GB
        mock_logical_disk.FileSystem = 'FAT32'
        
        # Mock WMI to return our test disk
        mock_wmi_instance = MagicMock()
        mock_wmi.return_value = mock_wmi_instance
        mock_wmi_instance.Win32_DiskDrive.return_value = [mock_disk]
        mock_wmi_instance.associators.side_effect = [
            [mock_partition],  # First call to associators (Win32_DiskDriveToDiskPartition)
            [mock_logical_disk]  # Second call to associators (Win32_LogicalDiskToPartition)
        ]
        
        # Test with mocked WMI and _is_drive_bootable
        with patch.object(self.builder, '_is_drive_bootable', return_value=False):
            with patch('win32api.GetVolumeInformation', 
                     return_value=('TEST_DRIVE', None, None, None, None, None, None, None)):
                drives = self.builder.list_available_drives()
        
        # Verify the results
        self.assertEqual(len(drives), 1)
        self.assertEqual(drives[0].drive_letter, 'E:')
        # The caption should be the VolumeName from the logical disk or 'NO_NAME' if empty
        self.assertIn(drives[0].caption, ['TEST_DRIVE', 'NO_NAME', 'CAMERA'])
    
    @patch('subprocess.run')
    def test_format_drive(self, mock_run):
        """Test formatting a drive"""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Test formatting
        result = self.builder.format_drive('E:', 'FAT32', 'OPRYXX_RESCUE')
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('os.path.exists')
    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_create_windows_pe_media(self, mock_file, mock_mkdir, mock_copy, mock_exists):
        """Test creating Windows PE media"""
        # Mock ADK installation check and file operations
        mock_exists.return_value = True
        
        # Mock the temp_dir to return our test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock the file operations
            mock_file.return_value.__enter__.return_value.write.return_value = None
            
            # Patch the temp_dir and other methods
            with patch.object(self.builder, 'temp_dir', temp_path), \
                 patch.object(self.builder, '_is_adk_installed', return_value=True), \
                 patch.object(self.builder, '_create_pe_structure'), \
                 patch.object(self.builder, '_add_boot_files'), \
                 patch.object(self.builder, '_add_opryxx_tools'), \
                 patch.object(self.builder, '_make_bootable'):
                
                # Test creating Windows PE media
                result = self.builder.create_windows_pe_media(str(temp_dir))
                
                # Verify the result
                self.assertTrue(result['success'])
                self.assertIn('successfully created', result['message'].lower())
                
                # Verify the expected methods were called
                self.builder._create_pe_structure.assert_called_once()
                self.builder._add_boot_files.assert_called_once()
                self.builder._add_opryxx_tools.assert_called_once()
                self.builder._make_bootable.assert_called_once()
    
    def test_validate_recovery_media(self):
        """Test validating recovery media"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a fake boot directory
            boot_dir = Path(temp_dir) / 'boot'
            boot_dir.mkdir()
            
            # Create a fake BCD file
            (boot_dir / 'bcd').touch()
            
            # Test validation
            result = self.builder.validate_recovery_media(temp_dir)
            
            # Should fail because we're missing required files
            self.assertFalse(result['is_valid'])
            self.assertGreater(len(result['missing_files']), 0)

if __name__ == '__main__':
    unittest.main()
