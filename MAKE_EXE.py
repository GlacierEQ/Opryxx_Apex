#!/usr/bin/env python3
"""
OPRYXX EXE MAKER - Create Standalone Executable
Creates a single executable file that contains everything
"""

import os
import sys
import subprocess
from pathlib import Path

def create_exe():
    """Create standalone executable using PyInstaller"""
    
    print("🚀 OPRYXX EXE MAKER")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed")
    
    # Get current directory
    base_dir = Path(__file__).parent
    
    # Create spec file for PyInstaller
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['UNIFIED_FULL_STACK_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'psutil', 'wmi', 'win32api', 'win32con', 'win32file', 'win32process', 'win32service', 'win32serviceutil', 'pythoncom'],
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
    icon=None,
)
"""
    
    spec_file = base_dir / "opryxx_unified.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")
    
    # Build the executable
    print("🔨 Building executable... (this may take a few minutes)")
    
    try:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed", 
            "--name=OPRYXX_UNIFIED_SYSTEM",
            "--add-data=*.py;.",
            "--hidden-import=tkinter",
            "--hidden-import=psutil", 
            "--hidden-import=wmi",
            "--hidden-import=win32api",
            "--hidden-import=win32con",
            "--hidden-import=win32file",
            "--hidden-import=win32process",
            "--hidden-import=win32service",
            "--hidden-import=win32serviceutil",
            "--hidden-import=pythoncom",
            "UNIFIED_FULL_STACK_GUI.py"
        ]
        
        result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable created successfully!")
            
            # Find the executable
            exe_path = base_dir / "dist" / "OPRYXX_UNIFIED_SYSTEM.exe"
            if exe_path.exists():
                print(f"📁 Executable location: {exe_path}")
                
                # Create a simple launcher
                launcher_content = f"""@echo off
title OPRYXX UNIFIED SYSTEM
echo.
echo ========================================
echo    OPRYXX UNIFIED SYSTEM
echo ========================================
echo.
echo Starting OPRYXX Unified System...
echo.

"{exe_path}"

if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit.
    pause >nul
)
"""
                
                launcher_path = base_dir / "START_OPRYXX.bat"
                with open(launcher_path, "w") as f:
                    f.write(launcher_content)
                
                print(f"✅ Created launcher: {launcher_path}")
                
                print("\n" + "=" * 50)
                print("🎉 EXECUTABLE PACKAGE READY!")
                print("=" * 50)
                print("TO RUN OPRYXX:")
                print(f"1. Double-click: {exe_path}")
                print(f"2. Or double-click: START_OPRYXX.bat")
                print("\nThe executable is completely standalone!")
                print("No Python installation required on target machines.")
                print("=" * 50)
                
                return exe_path
            else:
                print("❌ Executable not found in expected location")
                return None
        else:
            print(f"❌ Build failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error building executable: {e}")
        return None

def create_simple_exe():
    """Create simple executable without PyInstaller"""
    
    print("🚀 CREATING SIMPLE EXECUTABLE")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Create a simple Python executable wrapper
    wrapper_content = """#!/usr/bin/env python3
import sys
import os
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import and run the unified GUI
    from UNIFIED_FULL_STACK_GUI import main
    main()
except ImportError:
    # Fallback to master start
    try:
        from master_start import main
        main()
    except ImportError:
        # Last resort - run as subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script = os.path.join(script_dir, 'UNIFIED_FULL_STACK_GUI.py')
        master_script = os.path.join(script_dir, 'master_start.py')
        
        if os.path.exists(gui_script):
            subprocess.run([sys.executable, gui_script])
        elif os.path.exists(master_script):
            subprocess.run([sys.executable, master_script])
        else:
            print("ERROR: No OPRYXX scripts found!")
            input("Press Enter to exit...")
"""
    
    exe_wrapper = base_dir / "OPRYXX_LAUNCHER.py"
    with open(exe_wrapper, "w") as f:
        f.write(wrapper_content)
    
    # Create batch file that acts like an exe
    batch_exe_content = """@echo off
title OPRYXX UNIFIED SYSTEM
cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install requirements
if exist requirements.txt (
    pip install -r requirements.txt --quiet --user
)

REM Run the launcher
python OPRYXX_LAUNCHER.py

if errorlevel 1 (
    echo.
    echo Trying alternative method...
    if exist UNIFIED_FULL_STACK_GUI.py (
        python UNIFIED_FULL_STACK_GUI.py
    ) else if exist master_start.py (
        python master_start.py
    ) else (
        echo ERROR: No OPRYXX files found!
    )
)

pause
"""
    
    batch_exe = base_dir / "OPRYXX.bat"
    with open(batch_exe, "w") as f:
        f.write(batch_exe_content)
    
    print("✅ Created: OPRYXX_LAUNCHER.py")
    print("✅ Created: OPRYXX.bat")
    
    # Create requirements
    requirements = """psutil>=5.8.0
pywin32>=227
wmi>=1.5.1
"""
    
    with open(base_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created: requirements.txt")
    
    print("\n" + "=" * 50)
    print("🎉 SIMPLE EXECUTABLE READY!")
    print("=" * 50)
    print("TO RUN OPRYXX:")
    print("1. Double-click: OPRYXX.bat")
    print("2. It will auto-install requirements and launch")
    print("\nThis works on any Windows machine with Python!")
    print("=" * 50)
    
    return batch_exe

if __name__ == "__main__":
    print("Choose installation method:")
    print("1. Create standalone EXE (requires PyInstaller)")
    print("2. Create simple executable (Python required)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        exe_path = create_exe()
        if exe_path:
            response = input(f"\nRun the executable now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                subprocess.run([str(exe_path)])
    else:
        exe_path = create_simple_exe()
        response = input(f"\nRun OPRYXX now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            subprocess.run([str(exe_path)], shell=True)