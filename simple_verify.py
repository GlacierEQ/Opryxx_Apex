"""
Simple OPRYXX System Verification
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Core modules
        from core.base import BaseModule, ModuleRegistry, ModuleResult
        from core.logger import get_logger
        from core.exceptions import OPRYXXException
        print("PASS: Core modules imported")
        
        # Recovery modules
        from modules.recovery.samsung_recovery import SamsungRecoveryModule
        from modules.recovery.dell_recovery import DellRecoveryModule
        print("PASS: Recovery modules imported")
        
        # AI module
        from modules.ai.optimization_engine import AIOptimizationModule
        print("PASS: AI module imported")
        
        # Unified system
        from unified_system import UnifiedOPRYXXSystem
        print("PASS: Unified system imported")
        
        return True
    except Exception as e:
        print(f"FAIL: Import error - {e}")
        return False

def test_system_creation():
    """Test system creation"""
    print("Testing system creation...")
    
    try:
        from unified_system import UnifiedOPRYXXSystem
        system = UnifiedOPRYXXSystem()
        
        # Test registry
        modules = system.registry.get_all_modules()
        if len(modules) >= 3:
            print(f"PASS: System created with {len(modules)} modules")
            return True
        else:
            print(f"FAIL: Expected 3+ modules, got {len(modules)}")
            return False
            
    except Exception as e:
        print(f"FAIL: System creation error - {e}")
        return False

def test_ai_functionality():
    """Test AI module basic functionality"""
    print("Testing AI functionality...")
    
    try:
        from modules.ai.optimization_engine import AIOptimizationModule
        ai = AIOptimizationModule()
        
        # Test metrics collection
        metrics = ai._collect_metrics()
        if metrics.cpu_usage >= 0:
            print("PASS: AI metrics collection working")
            return True
        else:
            print("FAIL: Invalid metrics")
            return False
            
    except Exception as e:
        print(f"FAIL: AI test error - {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    print("Testing file structure...")
    
    required = [
        'core/base.py',
        'core/logger.py',
        'modules/recovery/samsung_recovery.py',
        'modules/recovery/dell_recovery.py',
        'modules/ai/optimization_engine.py',
        'unified_system.py',
        'OPRYXX_FINAL.py'
    ]
    
    missing = []
    for file_path in required:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"FAIL: Missing files - {missing}")
        return False
    else:
        print("PASS: All required files present")
        return True

def main():
    """Run verification"""
    print("OPRYXX SYSTEM VERIFICATION")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("System Creation", test_system_creation),
        ("AI Functionality", test_ai_functionality)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1
    
    print(f"\nRESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("SUCCESS: OPRYXX system verified and ready!")
        print("Run START_OPRYXX_FINAL.bat to launch the system.")
    else:
        print("WARNING: Some tests failed. Check errors above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)