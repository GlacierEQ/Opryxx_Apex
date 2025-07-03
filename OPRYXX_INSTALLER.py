#!/usr/bin/env python3
"""
OPRYXX One-Click Installer and Launcher
Creates executable and installs everything
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install all required dependencies"""
    deps = [
        'psutil', 'numpy', 'torch', 'torchvision', 'torchaudio',
        'flask', 'flask-socketio', 'matplotlib', 'tkinter',
        'pyinstaller', 'wmi', 'pyopencl'
    ]
    
    for dep in deps:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"[OK] {dep}")
        except:
            print(f"[SKIP] {dep}")

def create_launcher():
    """Create main launcher script"""
    launcher_code = '''
import sys
import os
import subprocess
import threading
import time
from pathlib import Path

class OPRYXXLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        sys.path.insert(0, str(self.base_path))
        
    def launch_gui(self):
        """Launch desktop GUI"""
        try:
            from gui.unified_gui import UnifiedGUI
            app = UnifiedGUI()
            app.run()
        except Exception as e:
            print(f"GUI Error: {e}")
            input("Press Enter to exit...")
    
    def launch_web(self):
        """Launch web interface"""
        try:
            from gui.web_interface import web_interface
            print("Web interface starting at http://localhost:5000")
            web_interface.run(host='0.0.0.0', port=5000)
        except Exception as e:
            print(f"Web Error: {e}")
            input("Press Enter to exit...")
    
    def launch_performance(self):
        """Start performance monitoring"""
        try:
            from core.performance_monitor import start_performance_monitoring
            from core.memory_optimizer import memory_optimizer
            
            start_performance_monitoring()
            memory_optimizer.start_monitoring()
            
            print("Performance monitoring started!")
            print("Press Ctrl+C to stop...")
            
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        except Exception as e:
            print(f"Performance Error: {e}")
            input("Press Enter to exit...")

def main():
    print("OPRYXX SYSTEM LAUNCHER")
    print("=" * 30)
    print("1. Desktop GUI")
    print("2. Web Interface") 
    print("3. Performance Monitor Only")
    print("4. Exit")
    
    launcher = OPRYXXLauncher()
    
    while True:
        try:
            choice = input("\\nSelect option (1-4): ").strip()
            
            if choice == '1':
                launcher.launch_gui()
            elif choice == '2':
                launcher.launch_web()
            elif choice == '3':
                launcher.launch_performance()
            elif choice == '4':
                break
            else:
                print("Invalid choice")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
'''
    
    with open('OPRYXX_LAUNCHER.py', 'w') as f:
        f.write(launcher_code)

def create_exe():
    """Create executable"""
    print("Creating executable...")
    
    try:
        # Create spec file for PyInstaller
        spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['OPRYXX_LAUNCHER.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('gui', 'gui'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'tkinter', 'matplotlib', 'numpy', 'torch', 'flask', 'flask_socketio',
        'psutil', 'wmi', 'pyopencl'
    ],
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
    name='OPRYXX_SYSTEM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='opryxx.ico' if os.path.exists('opryxx.ico') else None,
)
'''
        
        with open('OPRYXX_SYSTEM.spec', 'w') as f:
            f.write(spec_content)
        
        # Build executable
        subprocess.run([sys.executable, '-m', 'PyInstaller', 'OPRYXX_SYSTEM.spec', '--onefile'], 
                      check=True)
        
        print("[SUCCESS] Executable created: dist/OPRYXX_SYSTEM.exe")
        
    except Exception as e:
        print(f"[ERROR] Failed to create executable: {e}")

def create_installer():
    """Create Windows installer"""
    installer_bat = '''@echo off
echo OPRYXX System Installer
echo ======================

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    winget install Python.Python.3.11
    if errorlevel 1 (
        echo Please install Python manually from python.org
        pause
        exit /b 1
    )
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install psutil numpy torch torchvision torchaudio flask flask-socketio matplotlib wmi pyopencl

REM Create desktop shortcut
echo Creating desktop shortcut...
set "desktop=%USERPROFILE%\\Desktop"
echo @echo off > "%desktop%\\OPRYXX System.bat"
echo cd /d "%~dp0" >> "%desktop%\\OPRYXX System.bat"
echo python OPRYXX_LAUNCHER.py >> "%desktop%\\OPRYXX System.bat"

echo.
echo Installation complete!
echo Double-click "OPRYXX System.bat" on your desktop to start
pause
'''
    
    with open('INSTALL_OPRYXX.bat', 'w') as f:
        f.write(installer_bat)

def main():
    print("OPRYXX INSTALLER AND PACKAGER")
    print("=" * 40)
    
    print("1. Installing dependencies...")
    install_dependencies()
    
    print("2. Creating launcher...")
    create_launcher()
    
    print("3. Creating installer...")
    create_installer()
    
    print("4. Creating executable...")
    create_exe()
    
    print("\n" + "=" * 40)
    print("INSTALLATION COMPLETE!")
    print("=" * 40)
    print("OPTIONS TO START OPRYXX:")
    print("1. Run: python OPRYXX_LAUNCHER.py")
    print("2. Run: INSTALL_OPRYXX.bat (creates desktop shortcut)")
    print("3. Run: dist/OPRYXX_SYSTEM.exe (if build succeeded)")
    print("4. Double-click desktop shortcut after running installer")

if __name__ == "__main__":
    main()