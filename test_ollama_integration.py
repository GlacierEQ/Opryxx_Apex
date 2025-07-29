"""
Test Ollama Integration with Windsurf IDE
"""

from windsurf_ollama_hook import windsurf_ollama
from pipelines import TaskAnalyzer

def test_ollama_integration():
    print("🤖 Testing Ollama Integration...")
    
    # Test basic connection
    if windsurf_ollama.active:
        print("✅ Ollama connected successfully")
    else:
        print("❌ Ollama connection failed")
        return
    
    # Test code chat
    test_code = "def hello(): print('Hello World')"
    response = windsurf_ollama.chat_with_code(test_code, "Explain this code")
    print(f"💬 Code explanation: {response[:100]}...")
    
    # Test optimization
    optimization = windsurf_ollama.optimize_code(test_code)
    print(f"⚡ Optimization: {optimization[:100]}...")
    
    # Test pipeline integration
    analyzer = TaskAnalyzer()
    chat_response = analyzer.chat_with_ollama("How do I optimize Python code?")
    print(f"🔧 Pipeline chat: {chat_response[:100]}...")

if __name__ == "__main__":
    test_ollama_integration()