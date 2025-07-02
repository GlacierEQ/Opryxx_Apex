"""
Create OPRYXX Recovery USB on E: Drive
"""

import os
import subprocess
import shutil

def create_recovery_usb():
    """Create recovery USB on E: drive"""
    print("Creating OPRYXX Recovery USB on E: drive...")
    
    # Backup current drivers
    print("Backing up drivers...")
    os.makedirs("E:\\OPRYXX_DRIVERS", exist_ok=True)
    subprocess.run(['dism', '/online', '/export-driver', '/destination:E:\\OPRYXX_DRIVERS'], 
                   capture_output=True)
    
    # Copy OPRYXX system to USB
    print("Copying OPRYXX system...")
    if os.path.exists("E:\\OPRYXX"):
        shutil.rmtree("E:\\OPRYXX")
    shutil.copytree(".", "E:\\OPRYXX", ignore=shutil.ignore_patterns('*.log', '__pycache__', '.git'))
    
    # Create autorun recovery script
    recovery_script = '''@echo off
title OPRYXX Recovery System
cls

echo.
echo ================================================================
echo              OPRYXX RECOVERY SYSTEM
echo                Boot Failure Recovery
echo ================================================================
echo.
echo Boot failure detected - OPRYXX Recovery active
echo.
echo [1] Automated Windows 11 Reinstall (Recommended)
echo [2] Fix Boot Issues Only
echo [3] Backup Data Only
echo [4] Exit
echo.
set /p choice="Select recovery option (1-4): "

if "%choice%"=="1" goto auto_reinstall
if "%choice%"=="2" goto fix_boot
if "%choice%"=="3" goto backup_data
if "%choice%"=="4" goto exit

:auto_reinstall
echo Starting Automated Windows 11 Reinstall...
cd /d E:\\OPRYXX
python recovery\\automated_os_reinstall.py
goto end

:fix_boot
echo Fixing boot issues...
cd /d E:\\OPRYXX
python recovery\\immediate_safe_mode_exit.py
python recovery\\boot_diagnostics.py
goto end

:backup_data
echo Backing up data...
cd /d E:\\OPRYXX
python recovery\\auto_reinstall_helper.py
goto end

:exit
exit

:end
pause
'''
    
    with open("E:\\OPRYXX_RECOVERY.bat", 'w') as f:
        f.write(recovery_script)
    
    # Create driver restore script
    driver_script = '''@echo off
echo Restoring drivers...
dism /image:C:\\ /add-driver /driver:E:\\OPRYXX_DRIVERS /recurse
echo Drivers restored!
pause
'''
    
    with open("E:\\RESTORE_DRIVERS.bat", 'w') as f:
        f.write(driver_script)
    
    # Create autorun.inf for auto-launch
    autorun_inf = '''[autorun]
open=OPRYXX_RECOVERY.bat
icon=OPRYXX_RECOVERY.bat
label=OPRYXX Recovery USB
'''
    
    with open("E:\\autorun.inf", 'w') as f:
        f.write(autorun_inf)
    
    print("Recovery USB created successfully!")
    print("Boot from E: drive when system fails")

if __name__ == "__main__":
    create_recovery_usb()