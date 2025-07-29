"""
Start Ollama for Windsurf IDE Integration
"""

import subprocess
import os
import time

def find_ollama():
    """Find Ollama installation"""
    paths = [
        r"C:\Users\casey\AppData\Local\Programs\Ollama\ollama.exe",
        r"C:\Program Files\Ollama\ollama.exe",
        r"C:\Program Files (x86)\Ollama\ollama.exe"
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def start_ollama():
    """Start Ollama server"""
    ollama_path = find_ollama()
    
    if ollama_path:
        print(f"Starting Ollama from: {ollama_path}")
        subprocess.Popen([ollama_path, "serve"])
        time.sleep(3)
        return True
    else:
        print("Ollama not found. Add to PATH or install.")
        return False

if __name__ == "__main__":
    if start_ollama():
        print("Ollama server started")
    else:
        print("Failed to start Ollama")