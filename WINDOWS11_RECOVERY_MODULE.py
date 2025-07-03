"""
Windows 11 Recovery Module
TPM/Secure Boot bypass and compatibility checking
"""

import os
import sys
import subprocess
import winreg
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

class Windows11Recovery:
    """Windows 11 recovery and bypass functionality"""
    
    def __init__(self, logger=None):
        self.logger = logger or self._setup_logging()
        self.is_admin = self._check_admin_privileges()
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_upgrade_status(self) -> Dict[str, bool]:
        """Check Windows 11 upgrade compatibility"""
        self.logger.info("Checking Windows 11 compatibility...")
        
        status = {
            'tpm_available': self._check_tpm(),
            'secure_boot_capable': self._check_secure_boot(),
            'sufficient_ram': self._check_ram(),
            'sufficient_storage': self._check_storage(),
            'cpu_compatible': self._check_cpu()
        }
        
        return status
    
    def _check_tpm(self) -> bool:
        """Check TPM availability"""
        try:
            result = subprocess.run(['powershell', 'Get-Tpm'], 
                                  capture_output=True, text=True, timeout=30)
            return 'TpmPresent' in result.stdout and 'True' in result.stdout
        except:
            return False
    
    def _check_secure_boot(self) -> bool:
        """Check Secure Boot capability"""
        try:
            result = subprocess.run(['powershell', 'Confirm-SecureBootUEFI'], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except:
            return False
    
    def _check_ram(self) -> bool:
        """Check RAM requirement (4GB minimum)"""
        try:
            import psutil
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            return total_ram_gb >= 4
        except:
            return False
    
    def _check_storage(self) -> bool:
        """Check storage requirement (64GB minimum)"""
        try:
            import psutil
            disk = psutil.disk_usage('C:')
            total_storage_gb = disk.total / (1024**3)
            return total_storage_gb >= 64
        except:
            return False
    
    def _check_cpu(self) -> bool:
        """Check CPU compatibility (basic check)"""
        try:
            result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                  capture_output=True, text=True, timeout=30)
            # Basic check - most modern CPUs are compatible
            return 'Intel' in result.stdout or 'AMD' in result.stdout
        except:
            return False
    
    def bypass_tpm_check(self) -> Tuple[bool, str]:
        """Bypass TPM and hardware checks via registry"""
        self.logger.info("Attempting TPM bypass...")
        
        if not self.is_admin:
            return False, "Administrator privileges required for registry modification"
        
        try:
            # Registry keys to bypass Windows 11 requirements
            bypass_keys = [
                {
                    'hkey': winreg.HKEY_LOCAL_MACHINE,
                    'subkey': r'SYSTEM\Setup\MoSetup',
                    'values': {
                        'AllowUpgradesWithUnsupportedTPMOrCPU': 1
                    }
                },
                {
                    'hkey': winreg.HKEY_LOCAL_MACHINE,
                    'subkey': r'SYSTEM\Setup\LabConfig',
                    'values': {
                        'BypassTPMCheck': 1,
                        'BypassSecureBootCheck': 1,
                        'BypassRAMCheck': 1,
                        'BypassStorageCheck': 1,
                        'BypassCPUCheck': 1
                    }
                }
            ]
            
            success_count = 0
            for key_info in bypass_keys:
                try:
                    # Create/open registry key
                    key = winreg.CreateKey(key_info['hkey'], key_info['subkey'])
                    
                    # Set values
                    for value_name, value_data in key_info['values'].items():
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                        self.logger.info(f"Set registry value: {key_info['subkey']}\\{value_name} = {value_data}")
                    
                    winreg.CloseKey(key)
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to set registry key {key_info['subkey']}: {e}")
            
            if success_count == len(bypass_keys):
                return True, "TPM bypass registry keys set successfully"
            else:
                return False, f"Partial success: {success_count}/{len(bypass_keys)} registry keys set"
                
        except Exception as e:
            self.logger.error(f"Registry bypass failed: {e}")
            return False, f"Registry bypass failed: {str(e)}"
    
    def create_registry_bypass(self) -> Tuple[bool, str]:
        """Create registry bypass file"""
        self.logger.info("Creating registry bypass file...")
        
        try:
            reg_content = """Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\\SYSTEM\\Setup\\MoSetup]
"AllowUpgradesWithUnsupportedTPMOrCPU"=dword:00000001

[HKEY_LOCAL_MACHINE\\SYSTEM\\Setup\\LabConfig]
"BypassTPMCheck"=dword:00000001
"BypassSecureBootCheck"=dword:00000001
"BypassRAMCheck"=dword:00000001
"BypassStorageCheck"=dword:00000001
"BypassCPUCheck"=dword:00000001
"""
            
            filename = f"windows11_bypass_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(reg_content)
            
            self.logger.info(f"Registry bypass file created: {filename}")
            return True, filename
            
        except Exception as e:
            self.logger.error(f"Failed to create registry file: {e}")
            return False, f"Failed to create registry file: {str(e)}"
    
    def apply_registry_bypass(self, reg_file: str) -> Tuple[bool, str]:
        """Apply registry bypass file"""
        if not os.path.exists(reg_file):
            return False, f"Registry file not found: {reg_file}"
        
        if not self.is_admin:
            return False, "Administrator privileges required to apply registry changes"
        
        try:
            result = subprocess.run(['reg', 'import', reg_file], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info(f"Registry bypass applied successfully: {reg_file}")
                return True, "Registry bypass applied successfully"
            else:
                self.logger.error(f"Failed to apply registry bypass: {result.stderr}")
                return False, f"Failed to apply registry bypass: {result.stderr}"
                
        except Exception as e:
            self.logger.error(f"Error applying registry bypass: {e}")
            return False, f"Error applying registry bypass: {str(e)}"
    
    def check_bypass_status(self) -> Dict[str, bool]:
        """Check if bypass registry keys are set"""
        self.logger.info("Checking bypass status...")
        
        status = {}
        
        try:
            # Check MoSetup key
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\Setup\MoSetup')
            try:
                value, _ = winreg.QueryValueEx(key, 'AllowUpgradesWithUnsupportedTPMOrCPU')
                status['allow_unsupported_upgrade'] = value == 1
            except FileNotFoundError:
                status['allow_unsupported_upgrade'] = False
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            status['allow_unsupported_upgrade'] = False
        
        try:
            # Check LabConfig key
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\Setup\LabConfig')
            
            bypass_checks = ['BypassTPMCheck', 'BypassSecureBootCheck', 'BypassRAMCheck', 
                           'BypassStorageCheck', 'BypassCPUCheck']
            
            for check in bypass_checks:
                try:
                    value, _ = winreg.QueryValueEx(key, check)
                    status[check.lower()] = value == 1
                except FileNotFoundError:
                    status[check.lower()] = False
            
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            for check in ['bypasstpmcheck', 'bypasssecurebootcheck', 'bypassramcheck', 
                         'bypassstoragecheck', 'bypasscpucheck']:
                status[check] = False
        
        return status
    
    def remove_bypass(self) -> Tuple[bool, str]:
        """Remove bypass registry keys"""
        if not self.is_admin:
            return False, "Administrator privileges required for registry modification"
        
        try:
            # Remove MoSetup value
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\Setup\MoSetup', 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, 'AllowUpgradesWithUnsupportedTPMOrCPU')
                winreg.CloseKey(key)
                self.logger.info("Removed MoSetup bypass value")
            except FileNotFoundError:
                pass
            
            # Remove LabConfig values
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\Setup\LabConfig', 0, winreg.KEY_SET_VALUE)
                
                bypass_values = ['BypassTPMCheck', 'BypassSecureBootCheck', 'BypassRAMCheck', 
                               'BypassStorageCheck', 'BypassCPUCheck']
                
                for value in bypass_values:
                    try:
                        winreg.DeleteValue(key, value)
                        self.logger.info(f"Removed {value}")
                    except FileNotFoundError:
                        pass
                
                winreg.CloseKey(key)
                
            except FileNotFoundError:
                pass
            
            return True, "Bypass registry keys removed successfully"
            
        except Exception as e:
            self.logger.error(f"Failed to remove bypass keys: {e}")
            return False, f"Failed to remove bypass keys: {str(e)}"