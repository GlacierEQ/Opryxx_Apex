"""
Install Ollama Binary to User PATH
"""

import os
import urllib.request
import subprocess

def install_ollama_user():
    """Install Ollama to user directory"""
    print("Installing Ollama to user directory...")
    
    # User directory path
    user_dir = os.path.expanduser("~\\AppData\\Local\\Ollama")
    ollama_exe = os.path.join(user_dir, "ollama.exe")
    
    try:
        # Create directory
        os.makedirs(user_dir, exist_ok=True)
        
        # Download binary
        print("Downloading Ollama...")
        url = "https://ollama.com/download/ollama-windows-amd64.exe"
        urllib.request.urlretrieve(url, ollama_exe)
        
        # Add to user PATH
        subprocess.run([
            'setx', 'PATH', f'%PATH%;{user_dir}'
        ], check=True)
        
        print(f"Ollama installed to: {user_dir}")
        print("Added to user PATH")
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def quick_test():
    """Quick test of Ollama"""
    try:
        # Test direct execution
        user_dir = os.path.expanduser("~\\AppData\\Local\\Ollama")
        ollama_exe = os.path.join(user_dir, "ollama.exe")
        
        if os.path.exists(ollama_exe):
            result = subprocess.run([ollama_exe, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Ollama working: {result.stdout.strip()}")
                return True
        
        print("Ollama not working yet")
        return False
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    if install_ollama_user():
        print("\nTesting installation...")
        quick_test()
        print("\nRestart terminal for PATH changes to take effect")
    else:
        print("Installation failed")