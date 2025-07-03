"""
Streamlined Build Script
"""

import subprocess

def build_ultimate():
    """Build ultimate OPRYXX package"""
    print("Building OPRYXX Ultimate...")
    
    # Install PyInstaller
    subprocess.run(['pip', 'install', 'pyinstaller'])
    
    # Build single EXE
    subprocess.run([
        'pyinstaller',
        '--onefile',
        '--name', 'OPRYXX_ULTIMATE',
        '--distpath', 'dist',
        '--clean',
        'OPRYXX_ULTIMATE.py'
    ])
    
    print("Build complete: dist/OPRYXX_ULTIMATE.exe")

if __name__ == "__main__":
    build_ultimate()
