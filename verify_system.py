"""
OPRYXX System Verification
Verify all components work correctly
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_core_modules():
    """Verify core modules can be imported"""
    print("🔍 Verifying core modules...")
    
    try:
        from core.base import BaseModule, ModuleRegistry, ModuleResult, ModuleStatus
        print("✅ Core base module imported successfully")
        
        from core.logger import get_logger
        logger = get_logger("verification")
        logger.info("Logger test successful")
        print("✅ Core logger module imported successfully")
        
        from core.exceptions import OPRYXXException, RecoveryException
        print("✅ Core exceptions module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Core module import failed: {e}")
        return False

def verify_recovery_modules():
    """Verify recovery modules can be imported"""
    print("🔍 Verifying recovery modules...")
    
    try:
        from modules.recovery.samsung_recovery import SamsungRecoveryModule
        samsung = SamsungRecoveryModule()
        print("✅ Samsung recovery module imported successfully")
        
        from modules.recovery.dell_recovery import DellRecoveryModule
        dell = DellRecoveryModule()
        print("✅ Dell recovery module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Recovery module import failed: {e}")
        return False

def verify_ai_module():
    """Verify AI module can be imported"""
    print("🔍 Verifying AI module...")
    
    try:
        from modules.ai.optimization_engine import AIOptimizationModule
        ai = AIOptimizationModule()
        print("✅ AI optimization module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ AI module import failed: {e}")
        return False

def verify_unified_system():
    """Verify unified system works"""
    print("🔍 Verifying unified system...")
    
    try:
        from unified_system import UnifiedOPRYXXSystem
        system = UnifiedOPRYXXSystem()
        print("✅ Unified system created successfully")
        
        # Test system status
        status = system.get_system_status()
        print(f"✅ System status retrieved: {len(status['modules'])} modules")
        
        return True
    except Exception as e:
        print(f"❌ Unified system verification failed: {e}")
        return False

def verify_module_functionality():
    """Verify basic module functionality"""
    print("🔍 Verifying module functionality...")
    
    try:
        from core.base import ModuleRegistry
        from modules.ai.optimization_engine import AIOptimizationModule
        
        # Test module registry
        registry = ModuleRegistry()
        ai_module = AIOptimizationModule()
        
        # Register module
        if registry.register(ai_module):
            print("✅ Module registration successful")
        else:
            print("❌ Module registration failed")
            return False
        
        # Test module retrieval
        retrieved = registry.get_module("ai_optimization")
        if retrieved == ai_module:
            print("✅ Module retrieval successful")
        else:
            print("❌ Module retrieval failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Module functionality verification failed: {e}")
        return False

def verify_dependencies():
    """Verify required dependencies are available"""
    print("🔍 Verifying dependencies...")
    
    dependencies = [
        ('psutil', 'System monitoring'),
        ('json', 'JSON processing'),
        ('threading', 'Multi-threading'),
        ('subprocess', 'Process execution'),
        ('pathlib', 'Path handling'),
        ('tkinter', 'GUI framework')
    ]
    
    missing = []
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {desc}")
        except ImportError:
            print(f"❌ {dep} - {desc} (MISSING)")
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    
    return True

def verify_file_structure():
    """Verify file structure is correct"""
    print("🔍 Verifying file structure...")
    
    required_files = [
        'core/__init__.py',
        'core/base.py',
        'core/logger.py',
        'core/exceptions.py',
        'modules/recovery/samsung_recovery.py',
        'modules/recovery/dell_recovery.py',
        'modules/ai/optimization_engine.py',
        'unified_system.py',
        'OPRYXX_FINAL.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    return True

def run_basic_tests():
    """Run basic functionality tests"""
    print("🔍 Running basic functionality tests...")
    
    try:
        # Test AI module metrics collection
        from modules.ai.optimization_engine import AIOptimizationModule
        ai = AIOptimizationModule()
        
        metrics = ai._collect_metrics()
        if metrics.cpu_usage >= 0 and metrics.memory_usage >= 0:
            print("✅ AI metrics collection working")
        else:
            print("❌ AI metrics collection failed")
            return False
        
        # Test performance prediction
        score = ai._predict_performance(metrics)
        if 0 <= score <= 100:
            print(f"✅ Performance prediction working (score: {score:.1f})")
        else:
            print("❌ Performance prediction failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def main():
    """Main verification function"""
    print("OPRYXX SYSTEM VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("File Structure", verify_file_structure),
        ("Dependencies", verify_dependencies),
        ("Core Modules", verify_core_modules),
        ("Recovery Modules", verify_recovery_modules),
        ("AI Module", verify_ai_module),
        ("Unified System", verify_unified_system),
        ("Module Functionality", verify_module_functionality),
        ("Basic Tests", run_basic_tests)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"VERIFICATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - OPRYXX SYSTEM VERIFIED!")
        print("\nSystem is ready for use. Run START_OPRYXX_FINAL.bat to launch.")
    else:
        print("⚠️ SOME TESTS FAILED - Check errors above")
    
    print("=" * 50)
    return passed == total

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)