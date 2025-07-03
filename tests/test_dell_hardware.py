"""
Tests for Dell Hardware Detection
"""

import os
import sys
import platform
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.modules.dell_hardware import DellHardwareDetector, DellSystemInfo

class TestDellHardwareDetection:
    """Test cases for Dell hardware detection"""
    
    @patch('platform.system', return_value='Windows')
    @patch('os.environ', {'SystemDrive': 'C:'})
    def test_windows_detection(self, mock_system):
        """Test Windows-specific detection"""
        with patch('wmi.WMI') as mock_wmi:
            # Mock WMI responses
            mock_computer = MagicMock()
            mock_computer.Win32_ComputerSystem.return_value = [
                MagicMock(
                    Model='Inspiron 7040 2-in-1',
                    Manufacturer='Dell Inc.',
                    PCSystemType=2  # Laptop
                )
            ]
            
            mock_bios = MagicMock()
            mock_bios.Win32_BIOS.return_value = [
                MagicMock(
                    Version='1.2.3',
                    SerialNumber='ABC123',
                    AssetTag='XYZ789'
                )
            ]
            
            mock_wmi.return_value = MagicMock(
                Win32_ComputerSystem=mock_computer.Win32_ComputerSystem,
                Win32_BIOS=mock_bios.Win32_BIOS
            )
            
            detector = DellHardwareDetector()
            
            assert detector.is_dell_system() is True
            assert '7040' in detector.get_model()
            assert detector.get_service_tag() == 'ABC123'
            assert detector.get_asset_tag() == 'XYZ789'
            assert detector.get_bios_version() == '1.2.3'
            assert detector.is_inspiron_7040_2in1() is True
    
    @patch('platform.system', return_value='Linux')
    def test_linux_detection(self, mock_system):
        """Test Linux-specific detection"""
        # Mock file system responses
        mock_files = {
            '/sys/class/dmi/id/sys_vendor': 'Dell Inc.\n',
            '/sys/class/dmi/id/product_name': 'Inspiron 7040 2-in-1\n',
            '/sys/class/dmi/id/product_family': 'Inspiron\n',
            '/sys/class/dmi/id/product_serial': 'ABC123\n',
            '/sys/class/dmi/id/bios_version': '1.2.3\n'
        }
        
        def mock_open_wrapper(path, *args, **kwargs):
            if path in mock_files:
                return mock_open(read_data=mock_files[path])(path, *args, **kwargs)
            return open(path, *args, **kwargs)
        
        with patch('builtins.open', mock_open_wrapper):
            with patch('os.path.exists', lambda x: x in mock_files):
                detector = DellHardwareDetector()
                
                assert detector.is_dell_system() is True
                assert '7040' in detector.get_model()
                assert detector.get_service_tag() == 'ABC123'
                assert detector.get_bios_version() == '1.2.3'
                assert detector.is_inspiron_7040_2in1() is True
    
    @patch('platform.system', return_value='Windows')
    @patch('wmi.WMI')
    def test_windows_fallback_detection(self, mock_wmi, mock_system):
        """Test Windows fallback detection when wmi module is not available"""
        # Simulate ImportError for wmi module
        mock_wmi.side_effect = ImportError("wmi module not found")
        
        # Mock WMIC command output
        mock_output = """
        Model=Inspiron 7040 2-in-1
        Manufacturer=Dell Inc.
        SystemType=Mobile
        """
        
        with patch('subprocess.run') as mock_run:
            # Mock WMIC command for system info
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr=''
            )
            
            # Mock WMIC command for BIOS info
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="""
                SerialNumber=ABC123
                Version=1.2.3
                AssetTag=XYZ789
                """,
                stderr=''
            )
            
            detector = DellHardwareDetector()
            
            assert detector.is_dell_system() is True
            assert '7040' in detector.get_model()
            assert detector.get_service_tag() == 'ABC123'
    
    @patch('platform.system', return_value='Windows')
    @patch('wmi.WMI')
    def test_diagnostics(self, mock_wmi, mock_system):
        """Test running diagnostics"""
        # Mock WMI responses
        mock_computer = MagicMock()
        mock_computer.Win32_ComputerSystem.return_value = [
            MagicMock(
                Model='Inspiron 7040 2-in-1',
                Manufacturer='Dell Inc.',
                PCSystemType=2  # Laptop
            )
        ]
        
        mock_bios = MagicMock()
        mock_bios.Win32_BIOS.return_value = [
            MagicMock(
                Version='1.2.3',
                SerialNumber='ABC123',
                AssetTag='XYZ789'
            )
        ]
        
        mock_wmi.return_value = MagicMock(
            Win32_ComputerSystem=mock_computer.Win32_ComputerSystem,
            Win32_BIOS=mock_bios.Win32_BIOS
        )
        
        # Mock registry access for Dell tools
        with patch('winreg.OpenKey') as mock_reg_open:
            # Mock Dell Command | Update check
            mock_reg_key = MagicMock()
            mock_reg_open.return_value.__enter__.return_value = mock_reg_key
            mock_reg_key.QueryValueEx.return_value = ('3.0.0', 1)
            
            detector = DellHardwareDetector()
            diagnostics = detector.run_diagnostics()
            
            assert diagnostics['is_dell'] is True
            assert '7040' in diagnostics['model']
            assert 'diagnostics' in diagnostics
            
            # Verify Dell tools were checked
            assert 'dell_command_update' in diagnostics['diagnostics']
            assert 'support_assist' in diagnostics['diagnostics']
            assert 'bios_update_available' in diagnostics['diagnostics']
    
    def test_inspiron_7040_specifics(self):
        """Test Inspiron 7040 2-in-1 specific detection"""
        # Create a test instance with known values
        info = DellSystemInfo(
            model='Inspiron 7040 2-in-1',
            is_dell=True,
            is_inspiron=True
        )
        
        detector = DellHardwareDetector()
        detector.system_info = info
        
        assert detector.is_inspiron_7040_2in1() is True
        
        # Test with different model
        info.model = 'XPS 13'
        info.is_inspiron = False
        assert detector.is_inspiron_7040_2in1() is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
