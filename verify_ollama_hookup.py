"""
Verify Ollama Hookup to Global Windsurf IDE
"""

import requests
import subprocess
import sys

def verify_ollama_connection():
    """Verify Ollama is connected to Windsurf IDE"""
    print("🔍 Verifying Ollama Integration...")
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama installed")
        else:
            print("❌ Ollama not installed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found in PATH")
        return False
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server running")
            models = response.json().get("models", [])
            print(f"📦 Available models: {len(models)}")
            return True
        else:
            print("❌ Ollama server not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama server")
        return False

def test_basic_chat():
    """Test basic chat functionality"""
    try:
        response = requests.post("http://localhost:11434/api/generate", 
            json={
                "model": "llama2",
                "prompt": "Hello, respond with just 'OK'",
                "stream": False
            }, timeout=30)
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            print(f"✅ Chat test: {result[:50]}")
            return True
        else:
            print("❌ Chat test failed")
            return False
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return False

if __name__ == "__main__":
    print("OLLAMA WINDSURF IDE VERIFICATION")
    print("=" * 40)
    
    if verify_ollama_connection():
        print("\n🧪 Testing chat functionality...")
        test_basic_chat()
        print("\n✅ Ollama hookup verified!")
    else:
        print("\n❌ Ollama hookup failed!")
        print("\n💡 To fix:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Run: ollama serve")
        print("3. Pull a model: ollama pull llama2")