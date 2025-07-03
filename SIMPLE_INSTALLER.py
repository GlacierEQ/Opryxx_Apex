#!/usr/bin/env python3
"""
OPRYXX SIMPLE INSTALLER - One-Click Setup
Creates executable package and installer for the unified system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_installer():
    """Create simple installer and executable"""
    
    print("🚀 OPRYXX SIMPLE INSTALLER")
    print("=" * 50)
    
    # Get current directory
    base_dir = Path(__file__).parent
    
    # Create installer directory
    installer_dir = base_dir / "INSTALLER_PACKAGE"
    installer_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating installer in: {installer_dir}")
    
    # Copy essential files
    essential_files = [
        "master_start.py",
        "UNIFIED_FULL_STACK_GUI.py",
        "requirements.txt"
    ]
    
    for file in essential_files:
        src = base_dir / file
        if src.exists():
            shutil.copy2(src, installer_dir / file)
            print(f"✅ Copied: {file}")
    
    # Create simple launcher batch file
    launcher_content = """@echo off
title OPRYXX UNIFIED SYSTEM
echo.
echo ========================================
echo    OPRYXX UNIFIED SYSTEM LAUNCHER
echo ========================================
echo.
echo Starting unified system...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install requirements if needed
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt --quiet
)

REM Launch the unified system
echo Launching OPRYXX Unified System...
python UNIFIED_FULL_STACK_GUI.py

if errorlevel 1 (
    echo.
    echo Trying alternative launcher...
    python master_start.py
)

pause
"""
    
    with open(installer_dir / "LAUNCH_OPRYXX.bat", "w") as f:
        f.write(launcher_content)
    
    print("✅ Created: LAUNCH_OPRYXX.bat")
    
    # Create requirements.txt if it doesn't exist
    requirements_content = """tkinter
psutil
wmi
pywin32
"""
    
    with open(installer_dir / "requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ Created: requirements.txt")
    
    # Create installer script
    installer_script = """@echo off
title OPRYXX INSTALLER
cls
echo.
echo ========================================
echo         OPRYXX SYSTEM INSTALLER
echo ========================================
echo.
echo This will install OPRYXX Unified System
echo.
pause

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\OPRYXX
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
copy /Y "*.py" "%INSTALL_DIR%\\" >nul
copy /Y "*.txt" "%INSTALL_DIR%\\" >nul
copy /Y "*.bat" "%INSTALL_DIR%\\" >nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\\Desktop
echo @echo off > "%DESKTOP%\\OPRYXX.bat"
echo cd /d "%INSTALL_DIR%" >> "%DESKTOP%\\OPRYXX.bat"
echo call LAUNCH_OPRYXX.bat >> "%DESKTOP%\\OPRYXX.bat"

REM Create start menu entry
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
if not exist "%STARTMENU%\\OPRYXX" mkdir "%STARTMENU%\\OPRYXX"
copy /Y "%DESKTOP%\\OPRYXX.bat" "%STARTMENU%\\OPRYXX\\OPRYXX.bat" >nul

echo.
echo ========================================
echo     INSTALLATION COMPLETED!
echo ========================================
echo.
echo OPRYXX has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: OPRYXX.bat
echo Start menu entry created
echo.
echo To start OPRYXX:
echo 1. Double-click OPRYXX.bat on desktop
echo 2. Or run from Start Menu
echo.
pause
"""
    
    with open(installer_dir / "INSTALL_OPRYXX.bat", "w") as f:
        f.write(installer_script)
    
    print("✅ Created: INSTALL_OPRYXX.bat")
    
    # Create README
    readme_content = """# OPRYXX UNIFIED SYSTEM - INSTALLATION GUIDE

## QUICK START (EASIEST WAY):
1. Double-click: INSTALL_OPRYXX.bat
2. Follow the prompts
3. Double-click the OPRYXX shortcut on your desktop

## MANUAL START:
1. Double-click: LAUNCH_OPRYXX.bat

## WHAT THIS DOES:
- Installs Python dependencies
- Launches the unified system interface
- Provides system optimization and recovery tools

## REQUIREMENTS:
- Windows 10/11
- Python 3.8+ (will prompt to install if missing)
- Administrator privileges (for system optimization)

## FEATURES:
✅ System Optimization
✅ Performance Monitoring  
✅ Emergency Recovery
✅ Predictive Analysis
✅ Automated Maintenance
✅ Real-time Diagnostics

## SUPPORT:
If you encounter issues, run LAUNCH_OPRYXX.bat from command prompt to see error messages.
"""
    
    with open(installer_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    print("✅ Created: README.txt")
    
    print("\n" + "=" * 50)
    print("🎉 INSTALLER PACKAGE CREATED!")
    print("=" * 50)
    print(f"📁 Location: {installer_dir}")
    print("\nTO INSTALL OPRYXX:")
    print("1. Go to the INSTALLER_PACKAGE folder")
    print("2. Double-click: INSTALL_OPRYXX.bat")
    print("3. Follow the installation prompts")
    print("4. Use the desktop shortcut to launch")
    print("\nOR FOR IMMEDIATE USE:")
    print("1. Go to the INSTALLER_PACKAGE folder") 
    print("2. Double-click: LAUNCH_OPRYXX.bat")
    print("=" * 50)
    
    return installer_dir

if __name__ == "__main__":
    try:
        installer_path = create_installer()
        
        # Ask if user wants to run installer now
        response = input("\nDo you want to run the installer now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            installer_bat = installer_path / "INSTALL_OPRYXX.bat"
            subprocess.run([str(installer_bat)], shell=True)
        
    except Exception as e:
        print(f"❌ Error creating installer: {e}")
        input("Press Enter to exit...")