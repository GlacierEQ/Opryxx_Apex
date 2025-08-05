"""
Add UVX to Windows PATH
"""

import os
import subprocess

def add_uvx_to_path():
    # Get current directory
    current_dir = os.getcwd()
    
    # Add to PATH using setx
    try:
        subprocess.run([
            "setx", "PATH", f"%PATH%;{current_dir}"
        ], check=True)
        print(f"Added {current_dir} to PATH")
        return True
    except:
        print("Failed to add to PATH")
        return False

if __name__ == "__main__":
    add_uvx_to_path()
    print("Restart terminal for PATH changes to take effect")