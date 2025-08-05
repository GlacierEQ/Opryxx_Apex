"""
Fix MCP UVX Error - Install and Configure
"""

import subprocess
import os

def fix_uvx_error():
    print("FIXING MCP UVX ERROR")
    print("=" * 30)
    
    # Install uv first
    try:
        subprocess.run(["pip", "install", "uv"], check=True)
        print("OK: uv installed")
    except:
        print("FAIL: uv install")
        return False
    
    # Add to PATH
    try:
        uv_path = subprocess.run(["where", "uv"], capture_output=True, text=True)
        if uv_path.returncode == 0:
            print("OK: uv found in PATH")
        else:
            print("WARN: uv not in PATH")
    except:
        pass
    
    # Create uvx alias/wrapper
    uvx_content = """@echo off
uv tool run %*"""
    
    try:
        with open("uvx.bat", "w") as f:
            f.write(uvx_content)
        print("OK: uvx.bat created")
    except:
        print("FAIL: uvx.bat creation")
    
    return True

if __name__ == "__main__":
    fix_uvx_error()
    print("\nSOLUTION: Add uvx.bat to PATH or install uv properly")