"""
Simple Ollama Verification for Windsurf IDE
"""

import requests
import subprocess

def check_ollama():
    print("OLLAMA VERIFICATION")
    print("=" * 30)
    
    # Check installation
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("OK: Ollama installed")
        else:
            print("FAIL: Ollama not installed")
            return False
    except:
        print("FAIL: Ollama not found")
        return False
    
    # Check server
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("OK: Server running")
            return True
        else:
            print("FAIL: Server not responding")
            return False
    except:
        print("FAIL: Cannot connect to server")
        return False

if __name__ == "__main__":
    if check_ollama():
        print("\nSUCCESS: Ollama ready for Windsurf IDE")
    else:
        print("\nFAIL: Ollama not ready")
        print("Install: https://ollama.ai")
        print("Start: ollama serve")