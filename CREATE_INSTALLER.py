"""
OPRYXX INSTALLER CREATOR
Creates a complete installer package with EXE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_installer():
    print("CREATING OPRYXX INSTALLER...")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create spec file for PyInstaller
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['UNIFIED_FULL_STACK_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui', 'gui'),
        ('core', 'core'),
        ('ai', 'ai'),
        ('*.py', '.'),
        ('*.json', '.'),
        ('*.bat', '.'),
        ('*.md', '.')
    ],
    hiddenimports=['tkinter', 'psutil', 'threading', 'subprocess', 'json', 'time', 'datetime'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OPRYXX_UNIFIED_SYSTEM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='opryxx_icon.ico' if os.path.exists('opryxx_icon.ico') else None,
)
'''
    
    with open('OPRYXX.spec', 'w') as f:
        f.write(spec_content)
    
    # Create simple icon if doesn't exist
    if not os.path.exists('opryxx_icon.ico'):
        print("Creating default icon...")
        # Create a simple text-based icon placeholder
        with open('opryxx_icon.txt', 'w') as f:
            f.write('OPRYXX ICON PLACEHOLDER')
    
    # Build the executable
    print("Building executable...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "OPRYXX.spec"], check=True)
        print("✅ Executable created successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to create executable with windowed mode, trying console mode...")
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--console", "OPRYXX.spec"], check=True)
    
    # Create installer directory
    installer_dir = Path("OPRYXX_INSTALLER")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_path = Path("dist/OPRYXX_UNIFIED_SYSTEM.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, installer_dir / "OPRYXX_UNIFIED_SYSTEM.exe")
        print("✅ Executable copied to installer directory")
    
    # Create installer script
    installer_script = '''@echo off
echo ================================================
echo           OPRYXX UNIFIED SYSTEM INSTALLER
echo ================================================
echo.

set "INSTALL_DIR=%ProgramFiles%\\OPRYXX"
set "DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\OPRYXX Unified System.lnk"

echo Installing OPRYXX Unified System...
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "OPRYXX_UNIFIED_SYSTEM.exe" "%INSTALL_DIR%\\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy executable
    pause
    exit /b 1
)

REM Create desktop shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\OPRYXX_UNIFIED_SYSTEM.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'OPRYXX Unified System'; $Shortcut.Save()"

REM Create start menu shortcut
set "START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\\OPRYXX Unified System.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\OPRYXX_UNIFIED_SYSTEM.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'OPRYXX Unified System'; $Shortcut.Save()"

echo.
echo ================================================
echo           INSTALLATION COMPLETED!
echo ================================================
echo.
echo OPRYXX Unified System has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts created:
echo - Desktop: OPRYXX Unified System
echo - Start Menu: OPRYXX Unified System
echo.
echo You can now run OPRYXX from:
echo 1. Desktop shortcut
echo 2. Start Menu
echo 3. Direct executable: %INSTALL_DIR%\\OPRYXX_UNIFIED_SYSTEM.exe
echo.
pause
'''
    
    with open(installer_dir / "INSTALL.bat", 'w') as f:
        f.write(installer_script)
    
    # Create uninstaller
    uninstaller_script = '''@echo off
echo ================================================
echo         OPRYXX UNIFIED SYSTEM UNINSTALLER
echo ================================================
echo.

set "INSTALL_DIR=%ProgramFiles%\\OPRYXX"
set "DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\OPRYXX Unified System.lnk"
set "START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\OPRYXX Unified System.lnk"

echo Uninstalling OPRYXX Unified System...
echo.

REM Remove shortcuts
if exist "%DESKTOP_SHORTCUT%" del "%DESKTOP_SHORTCUT%"
if exist "%START_MENU%" del "%START_MENU%"

REM Remove installation directory
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo Installation directory removed.
)

echo.
echo ================================================
echo         UNINSTALLATION COMPLETED!
echo ================================================
echo.
echo OPRYXX Unified System has been completely removed.
echo.
pause
'''
    
    with open(installer_dir / "UNINSTALL.bat", 'w') as f:
        f.write(uninstaller_script)
    
    # Create README
    readme_content = '''# OPRYXX UNIFIED SYSTEM INSTALLER

## INSTALLATION INSTRUCTIONS

1. **RIGHT-CLICK** on "INSTALL.bat" and select **"Run as administrator"**
2. Follow the installation prompts
3. Launch OPRYXX from Desktop shortcut or Start Menu

## WHAT GETS INSTALLED

- Main executable: OPRYXX_UNIFIED_SYSTEM.exe
- Desktop shortcut
- Start Menu shortcut
- Installation directory: C:\\Program Files\\OPRYXX

## SYSTEM REQUIREMENTS

- Windows 10/11
- Administrator privileges for installation
- 4GB RAM minimum
- 1GB free disk space

## UNINSTALLATION

Run "UNINSTALL.bat" as administrator to completely remove OPRYXX.

## SUPPORT

If you encounter issues:
1. Ensure you're running as administrator
2. Check Windows Defender/antivirus settings
3. Verify system requirements are met

---
OPRYXX UNIFIED SYSTEM - Complete System Management Solution
'''
    
    with open(installer_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Installer package created in: {installer_dir.absolute()}")
    print("\nTO INSTALL OPRYXX:")
    print("1. Go to OPRYXX_INSTALLER folder")
    print("2. RIGHT-CLICK on INSTALL.bat")
    print("3. Select 'Run as administrator'")
    print("4. Follow installation prompts")
    print("5. Launch from Desktop shortcut")

if __name__ == "__main__":
    create_installer()