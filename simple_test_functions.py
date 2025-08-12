"""
Simple Test All Functions - No Unicode
"""

def test_function(func, *args, **kwargs):
    """Test a single function"""
    try:
        result = func(*args, **kwargs)
        print(f"OK: {func.__name__}")
        return True
    except Exception as e:
        print(f"FAIL: {func.__name__}: {str(e)[:50]}")
        return False

def simple_test():
    """Simple test without dependencies"""
    print("SIMPLE FUNCTION TEST")
    print("=" * 20)
    
    passed = 0
    failed = 0
    
    # Test basic imports
    try:
        import ai_context
        print("OK: ai_context imported")
        passed += 1
    except Exception as e:
        print(f"FAIL: ai_context: {str(e)[:30]}")
        failed += 1
    
    try:
        import ollama_windsurf_bridge
        print("OK: ollama_bridge imported")
        passed += 1
    except Exception as e:
        print(f"FAIL: ollama_bridge: {str(e)[:30]}")
        failed += 1
    
    try:
        import windsurf_ollama_hook
        print("OK: windsurf_hook imported")
        passed += 1
    except Exception as e:
        print(f"FAIL: windsurf_hook: {str(e)[:30]}")
        failed += 1
    
    try:
        import OPERATOR_HOOK
        print("OK: operator_hook imported")
        passed += 1
    except Exception as e:
        print(f"FAIL: operator_hook: {str(e)[:30]}")
        failed += 1
    
    try:
        import windsurf_global_integration
        print("OK: global_integration imported")
        passed += 1
    except Exception as e:
        print(f"FAIL: global_integration: {str(e)[:30]}")
        failed += 1
    
    # Test basic functions
    try:
        from OPERATOR_HOOK import global_operator
        result = global_operator.execute("test", {})
        print("OK: operator execute")
        passed += 1
    except Exception as e:
        print(f"FAIL: operator execute: {str(e)[:30]}")
        failed += 1
    
    try:
        from ollama_windsurf_bridge import ollama_bridge
        result = ollama_bridge.get_models()
        print("OK: ollama get_models")
        passed += 1
    except Exception as e:
        print(f"FAIL: ollama get_models: {str(e)[:30]}")
        failed += 1
    
    print(f"\nRESULTS: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    simple_test()