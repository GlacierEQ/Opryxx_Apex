"""
Test All Functions - Minimal Function Testing
"""

import sys
import traceback

def test_function(func, *args, **kwargs):
    """Test a single function"""
    try:
        result = func(*args, **kwargs)
        print(f"✅ {func.__name__}: OK")
        return True
    except Exception as e:
        print(f"❌ {func.__name__}: {str(e)[:50]}")
        return False

def test_all_functions():
    """Test all available functions"""
    print("TESTING ALL FUNCTIONS")
    print("=" * 30)
    
    passed = 0
    failed = 0
    
    # Test AI Context
    try:
        from ai_context import initialize, get_context
        if test_function(initialize):
            passed += 1
        else:
            failed += 1
        if test_function(get_context, "test query"):
            passed += 1
        else:
            failed += 1
    except ImportError:
        print("❌ ai_context: Import failed")
        failed += 2
    
    # Test Pipelines
    try:
        from pipelines import TaskAnalyzer, analyze_task
        analyzer = TaskAnalyzer()
        if test_function(analyze_task, "test"):
            passed += 1
        else:
            failed += 1
        if test_function(analyzer.chat_with_ollama, "hello"):
            passed += 1
        else:
            failed += 1
    except ImportError:
        print("❌ pipelines: Import failed")
        failed += 2
    
    # Test Ollama Integration
    try:
        from ollama_windsurf_bridge import ollama_bridge
        if test_function(ollama_bridge._chat, "test"):
            passed += 1
        else:
            failed += 1
    except ImportError:
        print("❌ ollama_bridge: Import failed")
        failed += 1
    
    # Test Windsurf Hook
    try:
        from windsurf_ollama_hook import windsurf_ollama
        if test_function(windsurf_ollama.setup_ollama):
            passed += 1
        else:
            failed += 1
    except ImportError:
        print("❌ windsurf_hook: Import failed")
        failed += 1
    
    # Test Global Integration
    try:
        from windsurf_global_integration import windsurf_global
        print(f"✅ windsurf_global: {len(windsurf_global.integrations)} integrations")
        passed += 1
    except ImportError:
        print("❌ windsurf_global: Import failed")
        failed += 1
    
    # Test Operator Hook
    try:
        from OPERATOR_HOOK import global_operator
        if test_function(global_operator.execute, "test", {}):
            passed += 1
        else:
            failed += 1
    except ImportError:
        print("❌ operator_hook: Import failed")
        failed += 1
    
    print(f"\nRESULTS: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    test_all_functions()