"""
Basic Function Test - Core Functions Only
"""

def test_core_functions():
    """Test core functions without heavy dependencies"""
    print("BASIC FUNCTION TEST")
    print("=" * 20)
    
    passed = 0
    failed = 0
    
    # Test Operator Hook
    try:
        from OPERATOR_HOOK import OperatorHook, global_operator
        hook = OperatorHook()
        result = hook.execute("test_command", {"param": "value"})
        print("OK: OperatorHook.execute")
        passed += 1
        
        status = hook.monitor()
        print("OK: OperatorHook.monitor")
        passed += 1
    except Exception as e:
        print(f"FAIL: OperatorHook: {str(e)}")
        failed += 2
    
    # Test Ollama Bridge (basic)
    try:
        from ollama_windsurf_bridge import OllamaWindsurfBridge
        bridge = OllamaWindsurfBridge()
        print("OK: OllamaWindsurfBridge created")
        passed += 1
    except Exception as e:
        print(f"FAIL: OllamaWindsurfBridge: {str(e)}")
        failed += 1
    
    # Test Windsurf Hook (basic)
    try:
        from windsurf_ollama_hook import WindsurfOllamaHook
        hook = WindsurfOllamaHook()
        print("OK: WindsurfOllamaHook created")
        passed += 1
    except Exception as e:
        print(f"FAIL: WindsurfOllamaHook: {str(e)}")
        failed += 1
    
    # Test file operations
    try:
        import os
        test_file = "test_file.txt"
        with open(test_file, "w") as f:
            f.write("test")
        
        if os.path.exists(test_file):
            print("OK: File operations")
            passed += 1
            os.remove(test_file)
        else:
            print("FAIL: File operations")
            failed += 1
    except Exception as e:
        print(f"FAIL: File operations: {str(e)}")
        failed += 1
    
    # Test basic imports
    modules_to_test = [
        "json", "os", "sys", "time", "datetime", 
        "subprocess", "threading", "requests"
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"OK: {module} import")
            passed += 1
        except Exception as e:
            print(f"FAIL: {module} import: {str(e)}")
            failed += 1
    
    print(f"\nRESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("ALL CORE FUNCTIONS WORKING")
    else:
        print(f"ISSUES FOUND: {failed} functions failed")
    
    return passed, failed

if __name__ == "__main__":
    test_core_functions()