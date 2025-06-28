"""
Create EXE files from Python scripts using PyInstaller
"""

import subprocess
import os

def create_exe_files():
    """Create EXE files for all main systems"""
    
    print("Creating EXE files for NEXUS AI System...")
    
    # Install PyInstaller
    subprocess.run(['pip', 'install', 'pyinstaller'])
    
    # EXE configurations
    exe_configs = [
        ('ENHANCED_ULTIMATE_AI.py', 'NEXUS_AI_Ultimate'),
        ('gui/MEGA_OPRYXX.py', 'MEGA_OPRYXX'),
        ('ai/AI_WORKBENCH.py', 'AI_Workbench')
    ]
    
    for script, name in exe_configs:
        print(f"Creating {name}.exe...")
        
        cmd = [
            'pyinstaller',
            '--onefile',
            '--name', name,
            '--distpath', 'dist',
            '--clean',
            script
        ]
        
        subprocess.run(cmd)
        print(f"Created {name}.exe!")
    
    print("EXE files created in 'dist' folder!")

if __name__ == "__main__":
    create_exe_files()