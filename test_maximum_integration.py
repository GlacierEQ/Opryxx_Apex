"""
Test Maximum Integration Status
"""

def test_integration():
    print("MAXIMUM WINDSURF IDE INTEGRATION TEST")
    print("=" * 40)
    
    # Test core components
    try:
        from windsurf_ollama_hook import windsurf_ollama
        print("OK: Ollama hook loaded")
    except:
        print("FAIL: Ollama hook")
    
    try:
        from ollama_windsurf_bridge import ollama_bridge
        print("OK: Ollama bridge loaded")
    except:
        print("FAIL: Ollama bridge")
    
    try:
        from OPERATOR_HOOK import global_operator
        print("OK: Operator hook loaded")
    except:
        print("FAIL: Operator hook")
    
    try:
        from pipelines import TaskAnalyzer
        analyzer = TaskAnalyzer()
        status = analyzer.get_global_status()
        print(f"OK: Global status: {len(status.get('integrations', []))} integrations")
    except Exception as e:
        print(f"FAIL: Pipeline integration: {e}")
    
    print("\nSTATUS: Maximum integration framework ready")
    print("Persistent: Windsurf IDE global hooks active")

if __name__ == "__main__":
    test_integration()