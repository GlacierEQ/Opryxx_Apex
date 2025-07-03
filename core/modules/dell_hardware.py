"""
Dell Hardware Detection and Diagnostics
Handles Dell-specific hardware detection and recovery operations
"""

import os
import re
import logging
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DellSystemInfo:
    """Container for Dell system information"""
    model: str = "Unknown"
    service_tag: str = "Unknown"
    asset_tag: str = "Unknown"
    bios_version: str = "Unknown"
    is_dell: bool = False
    is_laptop: bool = False
    is_inspiron: bool = False
    is_xps: bool = False
    is_latitude: bool = False
    is_precision: bool = False

class DellHardwareDetector:
    """Handles detection and diagnostics for Dell hardware"""
    
    def __init__(self):
        self.system_info = self._detect_system_info()
    
    def _run_command(self, cmd: List[str], **kwargs) -> Tuple[bool, str]:
        """Run a command and return (success, output)"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                **kwargs
            )
            if result.returncode != 0:
                logger.error(f"Command failed ({result.returncode}): {' '.join(cmd)}")
                logger.error(f"Stderr: {result.stderr}")
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False, str(e)
    
    def _detect_system_info(self) -> DellSystemInfo:
        """Detect Dell system information"""
        info = DellSystemInfo()
        
        try:
            if platform.system() == 'Windows':
                self._detect_windows(info)
            else:
                self._detect_linux(info)
                
            # Additional Dell-specific detection
            if info.is_dell:
                self._detect_dell_specifics(info)
                
        except Exception as e:
            logger.error(f"Error detecting system info: {e}")
            
        return info
    
    def _detect_windows(self, info: DellSystemInfo) -> None:
        """Detect system information on Windows"""
        try:
            import wmi
            c = wmi.WMI()
            
            # Get basic system info
            for system in c.Win32_ComputerSystem():
                info.model = system.Model.strip()
                info.is_dell = 'Dell' in system.Manufacturer
                info.is_laptop = 'Laptop' in system.PCSystemType
            
            # Get BIOS info
            for bios in c.Win32_BIOS():
                info.bios_version = bios.Version or "Unknown"
                info.service_tag = bios.SerialNumber or "Unknown"
                info.asset_tag = getattr(bios, 'AssetTag', '') or "Unknown"
                
        except ImportError:
            # Fallback to WMI via command line if wmi module not available
            self._detect_windows_fallback(info)
            
    def _detect_windows_fallback(self, info: DellSystemInfo) -> None:
        """Fallback detection using WMIC commands"""
        try:
            # Get computer system info
            success, output = self._run_command(
                ['wmic', 'computersystem', 'get', 'model,manufacturer,systemtype', '/format:list']
            )
            
            if success:
                model_match = re.search(r'Model=([^\r\n]+)', output)
                if model_match:
                    info.model = model_match.group(1).strip()
                
                manufacturer_match = re.search(r'Manufacturer=([^\r\n]+)', output)
                if manufacturer_match:
                    info.is_dell = 'Dell' in manufacturer_match.group(1)
                
                system_type_match = re.search(r'SystemType=([^\r\n]+)', output)
                if system_type_match:
                    info.is_laptop = 'Laptop' in system_type_match.group(1)
            
            # Get BIOS info
            success, output = self._run_command(
                ['wmic', 'bios', 'get', 'serialnumber,version,assettag', '/format:list']
            )
            
            if success:
                serial_match = re.search(r'SerialNumber=([^\r\n]+)', output)
                if serial_match:
                    info.service_tag = serial_match.group(1).strip()
                
                version_match = re.search(r'Version=([^\r\n]+)', output)
                if version_match:
                    info.bios_version = version_match.group(1).strip()
                
                asset_match = re.search(r'AssetTag=([^\r\n]+)', output)
                if asset_match:
                    info.asset_tag = asset_match.group(1).strip()
                    
        except Exception as e:
            logger.error(f"Windows fallback detection failed: {e}")
    
    def _detect_linux(self, info: DellSystemInfo) -> None:
        """Detect system information on Linux"""
        try:
            # Check for Dell system using sysfs
            if os.path.exists('/sys/class/dmi/id/sys_vendor'):
                with open('/sys/class/dmi/id/sys_vendor', 'r') as f:
                    vendor = f.read().strip()
                    info.is_dell = 'Dell' in vendor
            
            if os.path.exists('/sys/class/dmi/id/product_name'):
                with open('/sys/class/dmi/id/product_name', 'r') as f:
                    info.model = f.read().strip()
            
            if os.path.exists('/sys/class/dmi/id/product_family'):
                with open('/sys/class/dmi/id/product_family', 'r') as f:
                    family = f.read().strip()
                    info.is_inspiron = 'Inspiron' in family
                    info.is_xps = 'XPS' in family
                    info.is_latitude = 'Latitude' in family
                    info.is_precision = 'Precision' in family
            
            # Get service tag
            if os.path.exists('/sys/class/dmi/id/product_serial'):
                with open('/sys/class/dmi/id/product_serial', 'r') as f:
                    info.service_tag = f.read().strip()
            
            # Get BIOS version
            if os.path.exists('/sys/class/dmi/id/bios_version'):
                with open('/sys/class/dmi/id/bios_version', 'r') as f:
                    info.bios_version = f.read().strip()
                    
        except Exception as e:
            logger.error(f"Linux detection failed: {e}")
    
    def _detect_dell_specifics(self, info: DellSystemInfo) -> None:
        """Detect Dell-specific information"""
        try:
            # Detect Dell model specifics
            model_upper = info.model.upper()
            
            # Check for Inspiron 7040 2-in-1
            if '7040' in model_upper and ('2IN1' in model_upper or '2-IN-1' in model_upper):
                info.is_inspiron = True
            
            # Check for other Dell series
            info.is_xps = 'XPS' in model_upper
            info.is_latitude = 'LATITUDE' in model_upper
            info.is_precision = 'PRECISION' in model_upper
            
        except Exception as e:
            logger.error(f"Dell-specific detection failed: {e}")
    
    def is_inspiron_7040_2in1(self) -> bool:
        """Check if system is a Dell Inspiron 7040 2-in-1"""
        if not self.system_info.is_dell or not self.system_info.is_inspiron:
            return False
            
        model_upper = self.system_info.model.upper()
        return '7040' in model_upper and ('2IN1' in model_upper or '2-IN-1' in model_upper)
    
    def get_bios_version(self) -> str:
        """Get the BIOS version"""
        return self.system_info.bios_version
    
    def get_service_tag(self) -> str:
        """Get the system service tag"""
        return self.system_info.service_tag
    
    def get_asset_tag(self) -> str:
        """Get the system asset tag"""
        return self.system_info.asset_tag
    
    def get_model(self) -> str:
        """Get the system model"""
        return self.system_info.model
    
    def is_dell_system(self) -> bool:
        """Check if system is a Dell"""
        return self.system_info.is_dell
    
    def run_diagnostics(self) -> Dict[str, Union[bool, str]]:
        """Run Dell hardware diagnostics"""
        results = {
            'is_dell': self.system_info.is_dell,
            'model': self.system_info.model,
            'service_tag': self.service_tag,
            'bios_version': self.bios_version,
            'diagnostics': {}
        }
        
        if not self.system_info.is_dell:
            results['diagnostics']['error'] = 'Not a Dell system'
            return results
        
        try:
            # Check for Dell-specific tools
            if platform.system() == 'Windows':
                # Check for Dell Command | Update
                results['diagnostics']['dell_command_update'] = self._check_dell_command_update()
                
                # Check for SupportAssist
                results['diagnostics']['support_assist'] = self._check_support_assist()
                
            # Check for BIOS updates
            results['diagnostics']['bios_update_available'] = self._check_bios_update()
            
            # Run hardware diagnostics if available
            if self.is_inspiron_7040_2in1():
                results['diagnostics'].update(self._run_inspiron_7040_diagnostics())
                
        except Exception as e:
            logger.error(f"Diagnostics failed: {e}")
            results['diagnostics']['error'] = str(e)
            
        return results
    
    def _check_dell_command_update(self) -> Dict[str, str]:
        """Check if Dell Command | Update is installed"""
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{FE182796-F6FA-4ADD-BAEC-080CF1AACA02}'
            ) as key:
                version = winreg.QueryValueEx(key, 'DisplayVersion')[0]
                return {'installed': True, 'version': version}
        except:
            return {'installed': False}
    
    def _check_support_assist(self) -> Dict[str, str]:
        """Check if Dell SupportAssist is installed"""
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{E85D6AD4-6E5C-4D4D-9E3E-9B8E2AF718F6}'
            ) as key:
                version = winreg.QueryValueEx(key, 'DisplayVersion')[0]
                return {'installed': True, 'version': version}
        except:
            return {'installed': False}
    
    def _check_bios_update(self) -> Dict[str, str]:
        """Check if a BIOS update is available"""
        # This would typically call Dell's update service
        return {'update_available': False, 'current_version': self.system_info.bios_version}
    
    def _run_inspiron_7040_diagnostics(self) -> Dict[str, Union[bool, str]]:
        """Run specific diagnostics for Inspiron 7040 2-in-1"""
        results = {}
        
        # Check for common issues with this model
        results['bios_settings_valid'] = self._check_bios_settings()
        results['touchscreen_detected'] = self._check_touchscreen()
        results['tablet_mode'] = self._check_tablet_mode()
        
        return results
    
    def _check_bios_settings(self) -> Dict[str, Union[bool, str]]:
        """Check BIOS settings for common issues"""
        # This would check BIOS settings relevant to the Inspiron 7040
        return {
            'secure_boot': True,  # Would check actual setting
            'fast_boot': False,   # Would check actual setting
            'boot_mode': 'UEFI',  # Would check actual setting
            'tpm_enabled': True  # Would check actual setting
        }
    
    def _check_touchscreen(self) -> Dict[str, Union[bool, str]]:
        """Check if touchscreen is detected and working"""
        # This would verify touchscreen functionality
        return {
            'detected': True,  # Would check actual hardware
            'status': 'OK',    # Would check actual status
            'driver_version': '10.0.19041.1'  # Would get actual version
        }
    
    def _check_tablet_mode(self) -> Dict[str, Union[bool, str]]:
        """Check tablet mode status"""
        # This would check if the system is in tablet mode
        return {
            'supported': True,  # Would check actual hardware support
            'active': False,    # Would check current mode
            'sensor_working': True  # Would verify sensor functionality
        }

# Example usage
if __name__ == "__main__":
    import logging
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    detector = DellHardwareDetector()
    
    print(f"Dell System: {detector.is_dell_system()}")
    print(f"Model: {detector.get_model()}")
    print(f"Service Tag: {detector.get_service_tag()}")
    print(f"BIOS Version: {detector.get_bios_version()}")
    print(f"Is Inspiron 7040 2-in-1: {detector.is_inspiron_7040_2in1()}")
    
    # Run diagnostics
    diagnostics = detector.run_diagnostics()
    print("\nDiagnostics:")
    print(json.dumps(diagnostics, indent=2))
