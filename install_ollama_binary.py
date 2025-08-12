"""
Install Ollama Binary to Global PATH
"""

import os
import urllib.request
import subprocess
import sys

def install_ollama_binary():
    """Download and install Ollama binary"""
    print("Installing Ollama binary...")
    
    # Download Ollama for Windows
    url = "https://ollama.com/download/ollama-windows-amd64.exe"
    ollama_path = "C:\\Program Files\\Ollama"
    ollama_exe = os.path.join(ollama_path, "ollama.exe")
    
    try:
        # Create directory
        os.makedirs(ollama_path, exist_ok=True)
        
        # Download binary
        print("Downloading Ollama...")
        urllib.request.urlretrieve(url, ollama_exe)
        
        # Add to PATH
        current_path = os.environ.get('PATH', '')
        if ollama_path not in current_path:
            subprocess.run([
                'setx', 'PATH', f'{current_path};{ollama_path}'
            ], check=True)
            print(f"Added {ollama_path} to PATH")
        
        print("Ollama binary installed successfully")
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def verify_ollama():
    """Verify Ollama installation"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Ollama version: {result.stdout.strip()}")
            return True
        else:
            print("Ollama not working")
            return False
    except FileNotFoundError:
        print("Ollama not found in PATH")
        return False

if __name__ == "__main__":
    if install_ollama_binary():
        print("\nRestart terminal and run 'ollama --version' to verify")
    else:
        print("Manual install: https://ollama.com/download")