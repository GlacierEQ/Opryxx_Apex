"""
Hiren's Boot + OPRYXX Integration
Easy boot-fail recovery with automated OS reinstall
"""

import os
import subprocess
import json
from pathlib import Path

class HirensOPRYXXIntegration:
    def __init__(self):
        self.hirens_path = "C:\\OPRYXX_HIRENS"
        self.drivers_backup = "C:\\OPRYXX_DRIVERS"
        self.recovery_usb = None
        
    def create_recovery_usb(self):
        """Create Hiren's Boot USB with OPRYXX integration"""
        print("🛠️ Creating Hiren's Boot + OPRYXX Recovery USB...")
        
        # Download Hiren's Boot PE
        self._download_hirens()
        
        # Backup all drivers
        self._backup_drivers()
        
        # Create integrated USB
        self._create_integrated_usb()
        
        # Add OPRYXX automation
        self._add_opryxx_automation()
        
        print("✅ Recovery USB created! Boot from USB when system fails.")
    
    def _download_hirens(self):
        """Download Hiren's Boot PE"""
        print("📥 Downloading Hiren's Boot PE...")
        
        ps_script = '''
        $url = "https://www.hirensbootcd.org/files/HBCD_PE_x64.iso"
        $output = "C:\\HirensBootPE.iso"
        Invoke-WebRequest -Uri $url -OutFile $output
        '''
        
        subprocess.run(['powershell', '-Command', ps_script])
        print("✅ Hiren's Boot PE downloaded")
    
    def _backup_drivers(self):
        """Backup all system drivers"""
        print("💾 Backing up all drivers...")
        
        os.makedirs(self.drivers_backup, exist_ok=True)
        
        # Export all drivers
        subprocess.run([
            'dism', '/online', '/export-driver', 
            f'/destination:{self.drivers_backup}'
        ])
        
        # Create driver restore script
        restore_script = f'''
@echo off
echo Restoring drivers...
dism /image:C:\\ /add-driver /driver:{self.drivers_backup} /recurse
echo Drivers restored!
'''
        
        with open(f"{self.drivers_backup}\\restore_drivers.bat", 'w') as f:
            f.write(restore_script)
        
        print("✅ Drivers backed up")
    
    def _create_integrated_usb(self):
        """Create integrated USB with Hiren's + OPRYXX"""
        print("💿 Creating integrated recovery USB...")
        
        # Find USB drive
        drives = subprocess.run(['wmic', 'logicaldisk', 'where', 'drivetype=2', 'get', 'deviceid'], 
                              capture_output=True, text=True)
        
        for line in drives.stdout.split('\n'):
            if ':' in line:
                self.recovery_usb = line.strip()
                break
        
        # Format USB
        subprocess.run(['format', self.recovery_usb, '/FS:FAT32', '/Q', '/Y'])
        
        # Mount and copy Hiren's
        subprocess.run(['powershell', 'Mount-DiskImage -ImagePath "C:\\HirensBootPE.iso"'])
        subprocess.run(['robocopy', 'D:', f"{self.recovery_usb}\\", '/E'])
        
        # Copy OPRYXX system
        subprocess.run(['robocopy', '.', f"{self.recovery_usb}\\OPRYXX", '/E'])
        
        # Copy driver backup
        subprocess.run(['robocopy', self.drivers_backup, f"{self.recovery_usb}\\DRIVERS", '/E'])
        
        print("✅ Integrated USB created")
    
    def _add_opryxx_automation(self):
        """Add OPRYXX automation to Hiren's Boot"""
        print("🤖 Adding OPRYXX automation...")
        
        # Create autorun script for Hiren's
        autorun_script = f'''
@echo off
title OPRYXX Recovery System
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██              OPRYXX RECOVERY SYSTEM                       ██
echo ██                 Boot Failure Recovery                     ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🚨 BOOT FAILURE DETECTED - OPRYXX RECOVERY ACTIVE
echo.
echo [1] 🚀 Automated Windows 11 Reinstall (Recommended)
echo [2] 🔧 Fix Boot Issues Only
echo [3] 💾 Backup Data Only
echo [4] 🛠️ Manual Recovery Tools
echo [5] Exit to Hiren's Boot Menu
echo.
set /p choice="Select recovery option (1-5): "

if "%choice%"=="1" goto auto_reinstall
if "%choice%"=="2" goto fix_boot
if "%choice%"=="3" goto backup_data
if "%choice%"=="4" goto manual_tools
if "%choice%"=="5" goto hirens_menu

:auto_reinstall
echo 🚀 Starting Automated Windows 11 Reinstall...
python OPRYXX\\recovery\\automated_os_reinstall.py
goto end

:fix_boot
echo 🔧 Fixing boot issues...
python OPRYXX\\recovery\\immediate_safe_mode_exit.py
python OPRYXX\\recovery\\boot_diagnostics.py
goto end

:backup_data
echo 💾 Backing up data...
python OPRYXX\\recovery\\auto_reinstall_helper.py
goto end

:manual_tools
echo 🛠️ Loading manual recovery tools...
start "" "Programs\\MiniTool Partition Wizard\\partitionwizard.exe"
start "" "Programs\\CrystalDiskInfo\\DiskInfo64.exe"
goto end

:hirens_menu
echo Returning to Hiren's Boot menu...
exit

:end
pause
'''
        
        with open(f"{self.recovery_usb}\\OPRYXX_RECOVERY.bat", 'w') as f:
            f.write(autorun_script)
        
        # Create boot menu entry
        boot_entry = '''
menuentry "OPRYXX Recovery System" {{
    set root=(hd0,1)
    chainloader /OPRYXX_RECOVERY.bat
}}
'''
        
        with open(f"{self.recovery_usb}\\boot\\grub\\custom.cfg", 'w') as f:
            f.write(boot_entry)
        
        print("✅ OPRYXX automation added")

def main():
    """Create Hiren's + OPRYXX recovery system"""
    integration = HirensOPRYXXIntegration()
    integration.create_recovery_usb()

if __name__ == "__main__":
    main()