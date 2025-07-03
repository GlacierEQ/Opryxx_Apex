"""
Tests for UEFI Boot Repair functionality
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.modules.uefi_boot_repair import UEFIBootRepair, DiskPartition

class TestUEFIBootRepair:
    """Test cases for UEFI Boot Repair"""
    
    @patch('os.name', 'nt')
    @patch('ctypes.windll.kernel32.GetFirmwareType')
    def test_uefi_detection_windows(self, mock_get_firmware):
        """Test UEFI detection on Windows"""
        # Mock Windows UEFI detection
        from ctypes import c_uint
        mock_get_firmware.return_value = 1  # Success
        
        # Test UEFI mode
        with patch('ctypes.byref', return_value=c_uint(2)):  # FirmwareTypeUefi = 2
            repair = UEFIBootRepair()
            assert repair.uefi is True
        
        # Test Legacy BIOS mode
        with patch('ctypes.byref', return_value=c_uint(1)):  # FirmwareTypeBios = 1
            repair = UEFIBootRepair()
            assert repair.uefi is False
    
    @patch('os.name', 'posix')
    def test_uefi_detection_linux(self):
        """Test UEFI detection on Linux"""
        # Test UEFI mode
        with patch('os.path.exists', return_value=True):
            repair = UEFIBootRepair()
            assert repair.uefi is True
        
        # Test Legacy BIOS mode
        with patch('os.path.exists', return_value=False):
            repair = UEFIBootRepair()
            assert repair.uefi is False
    
    @patch('subprocess.run')
    @patch('os.name', 'nt')
    def test_find_efi_partition_windows(self, mock_run):
        """Test finding EFI partition on Windows"""
        # Mock diskpart output
        mock_output = """
        DISKPART> list disk
        
          Disk ###  Status         Size     Free     Dyn  Gpt
          --------  -------------  -------  -------  ---  ---
          Disk 0    Online          476 GB      0 B        *
        
        DISKPART> select disk 0
        
        Disk 0 is now the selected disk.
        
        DISKPART> list partition
        
          Partition ###  Type              Size     Offset
          -------------  ----------------  -------  -------
          Partition 1    System             100 MB   1024 KB
          Partition 2    Reserved            16 MB    101 MB
          Partition 3    Primary            475 GB    117 MB
        """
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
        
        repair = UEFIBootRepair()
        partition = repair._find_efi_partition()
        assert partition == '1'  # Should find the System partition
    
    @patch('subprocess.run')
    @patch('os.name', 'posix')
    def test_find_efi_partition_linux(self, mock_run):
        """Test finding EFI partition on Linux"""
        # Mock efibootmgr output
        mock_output = """
        BootCurrent: 0000
        Timeout: 1 seconds
        BootOrder: 0000,0001,0002
        Boot0000* ubuntu
        Boot0001* Windows Boot Manager
        Boot0002* UEFI:CD/DVD Drive
        """
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
        
        # Test with /boot/efi mounted
        with patch('os.path.ismount', side_effect=lambda x: x == '/boot/efi'):
            repair = UEFIBootRepair()
            partition = repair._find_efi_partition()
            assert partition == '/boot/efi'
    
    @patch('subprocess.run')
    @patch('os.name', 'nt')
    def test_repair_bootloader_windows(self, mock_run):
        """Test UEFI bootloader repair on Windows"""
        # Mock successful commands
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Mock UEFI and EFI partition detection
        with patch.object(UEFIBootRepair, '_check_uefi', return_value=True), \
             patch.object(UEFIBootRepair, '_find_efi_partition', return_value='1'):
            
            repair = UEFIBootRepair()
            result = repair.repair_bootloader()
            
            # Verify bcdboot and bootsect were called
            assert any('bcdboot' in ' '.join(args[0]) for args, _ in mock_run.call_args_list)
            assert any('bootsect' in ' '.join(args[0]) for args, _ in mock_run.call_args_list)
            assert result is True
    
    @patch('os.name', 'nt')
    @patch('winreg.OpenKey')
    def test_check_secure_boot_windows(self, mock_openkey):
        """Test Secure Boot detection on Windows"""
        # Mock registry access
        mock_key = MagicMock()
        mock_openkey.return_value.__enter__.return_value = mock_key
        
        # Test with Secure Boot enabled
        with patch('winreg.QueryValueEx', return_value=(1, 0)):
            repair = UEFIBootRepair()
            assert repair.check_secure_boot() is True
        
        # Test with Secure Boot disabled
        with patch('winreg.QueryValueEx', return_value=(0, 0)):
            repair = UEFIBootRepair()
            assert repair.check_secure_boot() is False
    
    @patch('os.name', 'posix')
    @patch('builtins.open', new_callable=mock_open, read_data=b'\x00\x00\x00\x00\x01')
    def test_check_secure_boot_linux(self, mock_file):
        """Test Secure Boot detection on Linux"""
        # Test with Secure Boot enabled
        with patch('pathlib.Path.exists', return_value=True):
            repair = UEFIBootRepair()
            assert repair.check_secure_boot() is True
        
        # Test with Secure Boot disabled
        mock_file.return_value = mock_open(read_data=b'\x00\x00\x00\x00\x00').return_value
        with patch('pathlib.Path.exists', return_value=True):
            repair = UEFIBootRepair()
            assert repair.check_secure_boot() is False
    
    @patch('subprocess.run')
    def test_get_boot_entries_windows(self, mock_run):
        """Test getting boot entries on Windows"""
        # Mock bcdedit output
        mock_output = """
        Firmware Boot Manager
        --------------------
        identifier              {fwbootmgr}
        displayorder            {bootmgr}
                                {1a411b89-7fa0-11ec-a8a3-1866da697b79}
        timeout                 30
        
        Windows Boot Manager
        -------------------
        identifier              {bootmgr}
        device                  partition=\\Device\HarddiskVolume1
        path                    \EFI\MICROSOFT\BOOT\BOOTMGFW.EFI
        description             Windows Boot Manager
        locale                  en-US
        inherit                 {globalsettings}
        default                 {current}
        displayorder            {current}
        toolsdisplayorder       {memdiag}
        timeout                 30
        """
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)
        
        repair = UEFIBootRepair()
        entries = repair.get_boot_entries()
        
        assert len(entries) > 0
        assert any(entry.get('identifier') == '{bootmgr}' for entry in entries)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
