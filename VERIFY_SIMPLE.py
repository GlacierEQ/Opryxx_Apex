"""
Simple Unified Stack Verification
"""

import os
import sys

def verify_unified_stack():
    print("UNIFIED FULL STACK VERIFICATION")
    print("=" * 50)
    
    # Check core files
    core_files = [
        'UNIFIED_FULL_STACK_GUI.py',
        'gui/MEGA_OPRYXX.py',
        'ULTIMATE_NEXUS_AI.py'
    ]
    
    passed = 0
    failed = 0
    
    print("\nCore Files Check:")
    for file in core_files:
        if os.path.exists(file):
            print(f"[PASS] {file}")
            passed += 1
        else:
            print(f"[FAIL] {file}")
            failed += 1
    
    # Check Python modules
    print("\nPython Modules Check:")
    modules = ['tkinter', 'psutil', 'threading', 'subprocess', 'json', 'time']
    
    for module in modules:
        try:
            __import__(module)
            print(f"[PASS] {module}")
            passed += 1
        except ImportError:
            print(f"[FAIL] {module}")
            failed += 1
    
    # Test system integration
    print("\nSystem Integration Check:")
    try:
        import psutil
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        print(f"[PASS] System monitoring (CPU: {cpu}%, Memory: {memory.percent}%)")
        passed += 1
    except:
        print("[FAIL] System monitoring")
        failed += 1
    
    # Summary
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("Status: FULLY OPERATIONAL")
    elif success_rate >= 75:
        print("Status: MOSTLY OPERATIONAL")
    else:
        print("Status: NEEDS ATTENTION")
    
    print("=" * 50)
    
    return success_rate >= 75

if __name__ == "__main__":
    success = verify_unified_stack()
    sys.exit(0 if success else 1)