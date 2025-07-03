import os
import sys
import shutil
import subprocess

def build():
    print("Starting OPRYXX build process...")
    
    # Clean up old build directories
    for item in ['build', 'dist', 'MEGA_OPRYXX.spec']:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
    
    # Build the executable
    print("Building MEGA_OPRYXX executable...")
    
    # Build the PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=MEGA_OPRYXX',
        '--onefile',
        '--windowed',
        '--add-data=config;config',
        '--add-data=data;data',
        '--add-data=templates;templates',
        '--add-data=assets;assets',
        '--hidden-import=sqlalchemy',
        '--hidden-import=sqlalchemy.orm',
        '--hidden-import=sqlalchemy.ext',
        'gui/MEGA_OPRYXX.py'
    ]
    
    # Add icon if it exists
    if os.path.exists('assets/opryxx.ico'):
        cmd.append('--icon=assets/opryxx.ico')
    
    # Run PyInstaller
    print("Running PyInstaller...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\nBuild complete!")
        print(f"Executable created at: {os.path.abspath('dist/MEGA_OPRYXX.exe')}")
        print("\nTo run the application, double-click on MEGA_OPRYXX.exe in the 'dist' folder.")
    else:
        print("\nError during build:")
        print(result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    build()
