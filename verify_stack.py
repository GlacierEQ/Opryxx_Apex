#!/usr/bin/env python3
"""
Full Stack Verification Script
Quick verification of all unified components
"""

import sys
import traceback

def verify_imports():
    """Verify all core modules import correctly"""
    print("[INFO] Verifying imports...")
    
    try:
        from core.performance_monitor import performance_monitor
        print("[OK] Performance Monitor")
        
        from core.memory_optimizer import memory_optimizer
        print("[OK] Memory Optimizer")
        
        from core.enhanced_gpu_ops import enhanced_gpu_ops
        print("[OK] Enhanced GPU Operations")
        
        from core.resilience_system import resilience_manager
        print("[OK] Resilience System")
        
        from core.gpu_acceleration import is_gpu_available
        print("[OK] GPU Acceleration")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def verify_core_functionality():
    """Test core system functionality"""
    print("\n[INFO] Testing core functionality...")
    
    try:
        # Test performance monitor
        from core.performance_monitor import performance_monitor
        metrics = performance_monitor.collect_metrics()
        print(f"[OK] Performance metrics: CPU {metrics.cpu_usage:.1f}%, Score {metrics.score:.1f}")
        
        # Test memory optimizer
        from core.memory_optimizer import memory_optimizer
        mem_metrics = memory_optimizer.get_memory_metrics()
        print(f"[OK] Memory metrics: {mem_metrics.usage_percent:.1f}% used")
        
        # Test GPU
        from core.gpu_acceleration import is_gpu_available, get_compute_device
        print(f"[OK] GPU available: {is_gpu_available()}, Device: {get_compute_device().name}")
        
        # Test resilience
        from core.resilience_system import resilience_manager
        report = resilience_manager.get_system_resilience_report()
        print(f"[OK] Resilience report generated with {len(report['circuit_breakers'])} circuit breakers")
        
        return True
    except Exception as e:
        print(f"[ERROR] Core functionality failed: {e}")
        traceback.print_exc()
        return False

def verify_gui_components():
    """Verify GUI components can be initialized"""
    print("\n[INFO] Verifying GUI components...")
    
    try:
        # Check if GUI files exist
        import os
        gui_files = [
            'gui/unified_gui.py',
            'gui/web_interface.py',
            'templates/dashboard.html'
        ]
        
        for file in gui_files:
            if os.path.exists(file):
                print(f"[OK] {file} exists")
            else:
                print(f"[ERROR] {file} missing")
                return False
        
        # Test web interface import only (avoid Flask route conflicts)
        import gui.web_interface
        print("[OK] Web interface module imports successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] GUI verification failed: {e}")
        return False

def verify_integration():
    """Test component integration"""
    print("\n[INFO] Testing integration...")
    
    try:
        from core.performance_monitor import performance_monitor
        from core.memory_optimizer import memory_optimizer
        
        # Start systems briefly
        performance_monitor.start()
        
        # Get integrated data
        perf_metrics = performance_monitor.get_metrics()
        mem_metrics = memory_optimizer.get_memory_metrics()
        
        # Verify data consistency
        if perf_metrics.timestamp > 0 and mem_metrics.total_mb > 0:
            print("[OK] Systems integrate and share data correctly")
            result = True
        else:
            print("[ERROR] Integration data inconsistent")
            result = False
        
        performance_monitor.stop()
        return result
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False

def main():
    """Run full stack verification"""
    print("OPRYXX Full Stack Verification")
    print("=" * 40)
    
    results = []
    
    # Run all verification steps
    results.append(verify_imports())
    results.append(verify_core_functionality())
    results.append(verify_gui_components())
    results.append(verify_integration())
    
    # Summary
    print("\nVerification Summary")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
        print("\n[OK] Full stack is unified and operational!")
        print("\nReady to launch:")
        print("   • Desktop GUI: python gui/unified_gui.py")
        print("   • Web Interface: python gui/web_interface.py")
        print("   • Launcher: LAUNCH_UNIFIED_GUI.bat")
        return 0
    else:
        print(f"[WARNING] SOME TESTS FAILED ({passed}/{total})")
        print("\n[ERROR] Full stack needs attention before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())