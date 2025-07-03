#!/usr/bin/env python3
"""
Windows 11 TPM/Secure Boot Bypass System
Bypasses Windows 11 hardware requirements for installation
"""

import os
import sys
import subprocess
import winreg
import ctypes
from pathlib import Path
from typing import Dict, Tuple, Optional

class Windows11Recovery:
    def __init__(self):
        self.is_admin = self._check_admin_privileges()
        self.bypass_registry_path = Path("C:\\OPRYXX_RECOVERY\\Windows11_Bypass.reg")
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def check_upgrade_status(self) -> Dict:
        """Check Windows 11 upgrade compatibility"""
        status = {
            'tpm_enabled': False,
            'secure_boot_enabled': False,
            'cpu_compatible': False,
            'ram_sufficient': False,
            'storage_sufficient': False,
            'upgrade_possible': False
        }
        
        try:
            # Check TPM
            result = subprocess.run(['powershell', 'Get-Tpm'], 
                                  capture_output=True, text=True)
            if 'TpmPresent' in result.stdout and 'True' in result.stdout:
                status['tpm_enabled'] = True
            
            # Check Secure Boot
            result = subprocess.run(['powershell', 'Confirm-SecureBootUEFI'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                status['secure_boot_enabled'] = True
            
            # Check RAM (8GB minimum)
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            status['ram_sufficient'] = ram_gb >= 8
            
            # Check storage (64GB minimum)
            disk_usage = psutil.disk_usage('C:')
            storage_gb = disk_usage.total / (1024**3)
            status['storage_sufficient'] = storage_gb >= 64
            
            status['upgrade_possible'] = all([
                status['tpm_enabled'],
                status['secure_boot_enabled'], 
                status['cpu_compatible'],
                status['ram_sufficient'],
                status['storage_sufficient']
            ])
            
        except Exception as e:
            print(f"[ERROR] Status check failed: {e}")
        
        return status
    
    def bypass_tpm_check(self) -> Tuple[bool, str]:
        """Bypass TPM requirement in registry"""
        if not self.is_admin:
            return False, "Administrator privileges required"
        
        try:
            # Registry keys to bypass TPM
            registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, 
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassTPMCheck", 1),
                (winreg.HKEY_LOCAL_MACHINE, 
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassSecureBootCheck", 1),
                (winreg.HKEY_LOCAL_MACHINE, 
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassRAMCheck", 1),
                (winreg.HKEY_LOCAL_MACHINE, 
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassStorageCheck", 1),
                (winreg.HKEY_LOCAL_MACHINE, 
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassCPUCheck", 1)
            ]
            
            for hkey, subkey, value_name, value_data in registry_keys:
                try:
                    key = winreg.CreateKey(hkey, subkey)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    winreg.CloseKey(key)
                except Exception as e:
                    print(f"[WARNING] Failed to set {value_name}: {e}")
            
            return True, "TPM and hardware checks bypassed successfully"
            
        except Exception as e:
            return False, f"Registry bypass failed: {e}"
    
    def create_registry_bypass(self) -> Tuple[bool, str]:
        """Create registry file for manual bypass"""
        try:
            registry_content = '''Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\\SYSTEM\\Setup\\LabConfig]
"BypassTPMCheck"=dword:00000001
"BypassSecureBootCheck"=dword:00000001
"BypassRAMCheck"=dword:00000001
"BypassStorageCheck"=dword:00000001
"BypassCPUCheck"=dword:00000001

[HKEY_LOCAL_MACHINE\\SYSTEM\\Setup\\MoSetup]
"AllowUpgradesWithUnsupportedTPMOrCPU"=dword:00000001
'''
            
            # Create directory if it doesn't exist
            self.bypass_registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.bypass_registry_path, 'w') as f:
                f.write(registry_content)
            
            return True, str(self.bypass_registry_path)
            
        except Exception as e:
            return False, f"Failed to create registry file: {e}"
    
    def modify_installation_media(self, iso_path: str, output_path: str) -> Tuple[bool, str]:
        """Modify Windows 11 ISO to bypass requirements"""
        try:
            # This would require mounting ISO and modifying files
            # Simplified version - create bypass script
            bypass_script = f'''@echo off
echo Bypassing Windows 11 requirements...
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassTPMCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassRAMCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassStorageCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassCPUCheck /t REG_DWORD /d 1 /f
echo Bypass complete!
pause
'''
            
            script_path = Path(output_path) / "Windows11_Bypass.bat"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(script_path, 'w') as f:
                f.write(bypass_script)
            
            return True, f"Bypass script created at {script_path}"
            
        except Exception as e:
            return False, f"Failed to create bypass script: {e}"
    
    def dell_specific_bypass(self) -> Tuple[bool, str]:
        """Dell Inspiron specific Windows 11 bypass"""
        try:
            # Dell-specific registry modifications
            dell_keys = [
                (winreg.HKEY_LOCAL_MACHINE,
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE",
                 "BypassNRO", 1),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"SYSTEM\Setup\LabConfig",
                 "BypassTPMCheck", 1),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"SYSTEM\Setup\LabConfig", 
                 "BypassSecureBootCheck", 1)
            ]
            
            if self.is_admin:
                for hkey, subkey, value_name, value_data in dell_keys:
                    try:
                        key = winreg.CreateKey(hkey, subkey)
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                        winreg.CloseKey(key)
                    except Exception as e:
                        print(f"[WARNING] Dell bypass key failed: {e}")
                
                return True, "Dell-specific Windows 11 bypass applied"
            else:
                return False, "Administrator privileges required for Dell bypass"
                
        except Exception as e:
            return False, f"Dell bypass failed: {e}"

def main():
    recovery = Windows11Recovery()
    
    print("WINDOWS 11 BYPASS SYSTEM")
    print("=" * 30)
    
    # Check current status
    print("\n[STATUS] Checking Windows 11 compatibility...")
    status = recovery.check_upgrade_status()
    
    for check, result in status.items():
        status_text = "[OK]" if result else "[FAIL]"
        print(f"  {check}: {status_text}")
    
    # Create bypass registry file if not admin
    if not recovery.is_admin:
        print("\n[INFO] Administrator privileges required for direct bypass")
        print("Creating registry bypass file...")
        success, message = recovery.create_registry_bypass()
        if success:
            print(f"[OK] Registry file created: {message}")
            print("Run as administrator and double-click the .reg file to apply")
        else:
            print(f"[ERROR] {message}")
    else:
        # Try to bypass checks directly
        print("\n[BYPASS] Applying Windows 11 requirement bypass...")
        success, message = recovery.bypass_tpm_check()
        print(f"[RESULT] {message}")
        
        # Dell-specific bypass
        print("\n[DELL] Applying Dell-specific bypass...")
        success, message = recovery.dell_specific_bypass()
        print(f"[RESULT] {message}")
        
        # Check status after bypass
        if success:
            print("\n[STATUS] Status after bypass:")
            new_status = recovery.check_upgrade_status()
            for check, result in new_status.items():
                status_text = "[OK]" if result else "[FAIL]"
                print(f"  {check}: {status_text}")

if __name__ == "__main__":
    main()