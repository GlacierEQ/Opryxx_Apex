"""
Install and Setup Ollama for Windsurf IDE Integration
"""

import subprocess
import requests
import os
import time

def install_ollama():
    """Install Ollama on Windows"""
    print("Installing Ollama...")
    
    # Download Ollama installer
    try:
        import urllib.request
        url = "https://ollama.ai/download/windows"
        urllib.request.urlretrieve(url, "ollama-installer.exe")
        
        # Run installer
        subprocess.run(["ollama-installer.exe", "/S"], check=True)
        print("Ollama installed successfully")
        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def setup_ollama_service():
    """Setup Ollama as a service"""
    try:
        # Start Ollama service
        subprocess.Popen(["ollama", "serve"], shell=True)
        time.sleep(5)  # Wait for service to start
        
        # Pull essential models
        models = ["llama2", "codellama"]
        for model in models:
            print(f"Pulling {model}...")
            subprocess.run(["ollama", "pull", model], check=True)
        
        return True
    except Exception as e:
        print(f"Service setup failed: {e}")
        return False

def verify_installation():
    """Verify Ollama is working"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama ready with {len(models)} models")
            return True
    except:
        pass
    return False

if __name__ == "__main__":
    print("OLLAMA SETUP FOR WINDSURF IDE")
    print("=" * 30)
    
    if not verify_installation():
        if install_ollama():
            setup_ollama_service()
    
    if verify_installation():
        print("SUCCESS: Ollama ready for Windsurf IDE")
    else:
        print("MANUAL INSTALL: Visit https://ollama.ai")