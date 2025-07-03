"""
Windows 11 Recovery Module
Handles Windows 11-specific recovery operations including TPM bypass and requirements checking
"""

import os
import re
import sys
import ctypes
import json
import logging
import platform
import subprocess
import winreg
from typing import Dict, List, Optional, Tuple, Any

class Windows11Recovery:
    """Handles Windows 11-specific recovery operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_admin = self._check_admin_privileges()
        self.system_info = self._get_system_info()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
            
    def _run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Execute a command and return (success, output)"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr or e.stdout or str(e)
            
    def _get_system_info(self) -> Dict[str, Any]:
        """Gather basic system information"""
        return {
            'os_name': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'is_64bit': sys.maxsize > 2**32
        }
        
    def check_tpm(self) -> Dict[str, Any]:
        """Check TPM version and status"""
        try:
            # Check TPM using PowerShell
            cmd = [
                'powershell',
                'Get-Tpm | Select-Object TpmPresent, TpmReady, TpmVersion | ConvertTo-Json'
            ]
            success, output = self._run_command(cmd)
            
            if success and output:
                tpm_info = json.loads(output)
                tpm_version = tpm_info.get('TpmVersion', '1.2')  # Default to 1.2 if not detected
                is_tpm_2_0 = tpm_version.startswith('2.0')
                
                return {
                    'passed': is_tpm_2_0,
                    'message': f'TPM {tpm_version} detected',
                    'details': tpm_info
                }
            
            return {
                'passed': False,
                'message': 'TPM not detected or error occurred',
                'details': output if not success else 'No TPM information found'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking TPM: {e}")
            return {
                'passed': False,
                'message': f'Error checking TPM: {str(e)}',
                'details': str(e)
            }
            
    def check_secure_boot(self) -> Dict[str, Any]:
        """Check if Secure Boot is enabled"""
        try:
            cmd = [
                'powershell',
                'Confirm-SecureBootUEFI'
            ]
            success, output = self._run_command(cmd)
            
            is_secure_boot = 'True' in output
            
            return {
                'passed': is_secure_boot,
                'message': 'Secure Boot enabled' if is_secure_boot else 'Secure Boot not enabled',
                'details': output.strip()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking Secure Boot: {e}")
            return {
                'passed': False,
                'message': f'Error checking Secure Boot: {str(e)}',
                'details': str(e)
            }
            
    def check_ram(self) -> Dict[str, Any]:
        """Check if system has at least 4GB RAM"""
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
            has_enough_ram = ram_gb >= 4
            
            return {
                'passed': has_enough_ram,
                'message': f'{ram_gb:.1f}GB RAM detected',
                'details': f'Minimum required: 4GB, Detected: {ram_gb:.1f}GB'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking RAM: {e}")
            return {
                'passed': False,
                'message': f'Error checking RAM: {str(e)}',
                'details': str(e)
            }
            
    def check_storage(self) -> Dict[str, Any]:
        """Check if system has at least 64GB storage"""
        try:
            import psutil
            total_gb = psutil.disk_usage('C:').total / (1024 ** 3)  # Convert to GB
            has_enough_space = total_gb >= 64
            
            return {
                'passed': has_enough_space,
                'message': f'{total_gb:.1f}GB storage detected',
                'details': f'Minimum required: 64GB, Detected: {total_gb:.1f}GB'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking storage: {e}")
            return {
                'passed': False,
                'message': f'Error checking storage: {str(e)}',
                'details': str(e)
            }
            
    def check_cpu(self) -> Dict[str, Any]:
        """Check if CPU meets Windows 11 requirements"""
        try:
            import cpuinfo
            
            # Get CPU info
            cpu_info = cpuinfo.get_cpu_info()
            brand = cpu_info.get('brand_raw', 'Unknown CPU')
            cores = cpu_info.get('count', 1)
            hz = cpu_info.get('hz_actual_friendly', '0 GHz')
            
            # Basic check for 1GHz+ and 2+ cores
            has_min_specs = ('GHz' in hz and float(hz.split()[0]) >= 1.0) and cores >= 2
            
            return {
                'passed': has_min_specs,
                'message': f'{brand} ({hz}, {cores} cores)',
                'details': cpu_info
            }
            
        except Exception as e:
            self.logger.error(f"Error checking CPU: {e}")
            return {
                'passed': False,
                'message': f'Error checking CPU: {str(e)}',
                'details': str(e)
            }
            
    def bypass_tpm_check(self) -> Dict[str, Any]:
        """Bypass TPM check by setting registry keys.
        
        Returns:
            Dict containing success status and message
        """
        if not self.is_admin:
            return {
                'success': False,
                'message': 'Administrator privileges required to modify registry',
                'requires_admin': True
            }
            
        try:
            # Create or open the LabConfig key
            base_key = winreg.HKEY_LOCAL_MACHINE
            key_path = r"SYSTEM\Setup\LabConfig"
            
            # Create the key if it doesn't exist
            try:
                with winreg.CreateKeyEx(base_key, key_path, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY) as key:
                    # Set the bypass values
                    winreg.SetValueEx(key, 'BypassTPMCheck', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'BypassSecureBootCheck', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'BypassRAMCheck', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'BypassStorageCheck', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'BypassCPUCheck', 0, winreg.REG_DWORD, 1)
            except WindowsError as e:
                self.logger.error(f"Error setting registry key {key_path}: {e}")
                return {
                    'success': False,
                    'message': f'Failed to set registry keys: {str(e)}',
                    'requires_admin': True
                }
                
                        'success': False,
                        'error': f'Failed to set registry key: {str(e)}',
                        'failed_key': f'{key_path}\\{value_name}'
                    }
            
            return {
                'success': True,
                'message': 'Successfully bypassed Windows 11 requirements',
                'details': 'Registry keys have been modified to bypass TPM, Secure Boot, and RAM checks.'
            }
            
        except Exception as e:
            self.logger.error(f"Error bypassing Windows 11 requirements: {e}")
            return {
                'success': False,
                'error': f'Failed to bypass requirements: {str(e)}',
                'details': str(e)
            }
            
    def create_registry_bypass(self) -> Tuple[bool, str]:
        """Create a .reg file to bypass Windows 11 requirements"""
        try:
            reg_content = """Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\Setup\LabConfig]
"BypassTPMCheck"=dword:00000001
"BypassSecureBootCheck"=dword:00000001
"BypassRAMCheck"=dword:00000001

[HKEY_LOCAL_MACHINE\SYSTEM\Setup\MoSetup]
"AllowUpgradesWithUnsupportedTPMOrCPU"=dword:00000001
"""
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'win11_bypass')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Write .reg file
            reg_path = os.path.join(temp_dir, 'win11_bypass.reg')
            with open(reg_path, 'w') as f:
                f.write(reg_content)
                
            return True, reg_path
            
        except Exception as e:
            self.logger.error(f"Error creating registry bypass file: {e}")
            return False, str(e)
            
    def check_upgrade_status(self) -> Dict[str, Any]:
        """Check Windows 11 upgrade status and requirements"""
        return {
            'tpm': self.check_tpm(),
            'secure_boot': self.check_secure_boot(),
            'ram': self.check_ram(),
            'storage': self.check_storage(),
            'cpu': self.check_cpu(),
            'is_admin': self.is_admin,
            'system_info': self.system_info
        }

# Example usage
if __name__ == "__main__":
    import logging
    import json
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create recovery instance
    recovery = Windows11Recovery()
    
    # Check upgrade status
    print("\n=== Windows 11 Upgrade Status ===")
    status = recovery.check_upgrade_status()
    print(json.dumps(status, indent=2))
    
    # Try to bypass requirements if not met
    if not all(check.get('passed', False) for key, check in status.items() 
              if key not in ['is_admin', 'system_info']):
        print("\n=== Attempting to bypass requirements ===")
        
        # Create bypass registry file if not admin
        if not recovery.is_admin:
            print("\n=== Administrator Privileges Required ===")
            print("To bypass Windows 11 requirements, run this script as administrator")
            success, message = recovery.create_registry_bypass()
            if success:
                print(f"Created registry file: {message}")
            else:
                print(f"Error: {message}")
        else:
            # Try to bypass checks directly
            print("\n=== Bypassing Windows 11 Requirements ===")
            result = recovery.bypass_tpm_check()
            print(json.dumps(result, indent=2))
