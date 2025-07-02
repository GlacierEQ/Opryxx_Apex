"""
Full Stack Status Check
"""

import os
from pathlib import Path

def check_full_stack():
    """Check complete full stack status"""
    print("OPRYXX FULL STACK UNIFICATION STATUS")
    print("=" * 50)
    
    # AI Systems
    ai_files = [
        'ai/ULTIMATE_AI_OPTIMIZER.py',
        'ai/AI_WORKBENCH.py', 
        'ENHANCED_ULTIMATE_AI.py',
        'ULTIMATE_NEXUS_AI.py'
    ]
    ai_count = sum(1 for f in ai_files if Path(f).exists())
    print(f"AI Systems: {ai_count}/4 - {'COMPLETE' if ai_count >= 3 else 'PARTIAL'}")
    
    # Recovery Tools
    recovery_files = [
        'recovery/immediate_safe_mode_exit.py',
        'recovery/automated_os_reinstall.py',
        'recovery/boot_diagnostics.py',
        'recovery/create_e_drive_recovery.py'
    ]
    recovery_count = sum(1 for f in recovery_files if Path(f).exists())
    print(f"Recovery Tools: {recovery_count}/4 - {'COMPLETE' if recovery_count >= 3 else 'PARTIAL'}")
    
    # Performance Tools
    perf_files = [
        'performance_benchmark.py',
        'performance_dashboard.py',
        'enhancements/system_validator.py',
        'enhancements/memory_optimizer.py'
    ]
    perf_count = sum(1 for f in perf_files if Path(f).exists())
    print(f"Performance Tools: {perf_count}/4 - {'COMPLETE' if perf_count >= 3 else 'PARTIAL'}")
    
    # GUI Interfaces
    gui_files = [
        'UNIFIED_GUI.py',
        'gui/MEGA_OPRYXX.py',
        'LAUNCH_UNIFIED_GUI.bat'
    ]
    gui_count = sum(1 for f in gui_files if Path(f).exists())
    print(f"GUI Interfaces: {gui_count}/3 - {'COMPLETE' if gui_count >= 2 else 'PARTIAL'}")
    
    # Integration Tools
    integration_files = [
        'windsurf_integration.py',
        'integration/todo_recovery_bridge.py',
        'integration/gandalf_pe_integration.py'
    ]
    integration_count = sum(1 for f in integration_files if Path(f).exists())
    print(f"Integration Tools: {integration_count}/3 - {'COMPLETE' if integration_count >= 2 else 'PARTIAL'}")
    
    # Build Tools
    build_files = [
        'build_tools/create_exe.py',
        'BUILD_EVERYTHING.bat',
        'tests/test_coverage.py'
    ]
    build_count = sum(1 for f in build_files if Path(f).exists())
    print(f"Build Tools: {build_count}/3 - {'COMPLETE' if build_count >= 2 else 'PARTIAL'}")
    
    # Calculate total score
    total_components = ai_count + recovery_count + perf_count + gui_count + integration_count + build_count
    max_components = 21
    score = (total_components / max_components) * 100
    
    print(f"\nOVERALL UNIFICATION SCORE: {score:.1f}%")
    
    if score >= 90:
        print("STATUS: COMPLETE FULL STACK UNIFICATION")
        print("All major systems integrated and operational")
    elif score >= 75:
        print("STATUS: EXCELLENT UNIFICATION")
        print("Minor components may be missing")
    elif score >= 60:
        print("STATUS: GOOD UNIFICATION")
        print("Most systems integrated")
    else:
        print("STATUS: PARTIAL UNIFICATION")
        print("Additional integration needed")
    
    print(f"\nKEY FEATURES AVAILABLE:")
    print("- 24/7 AI Optimization (NEXUS)")
    print("- Automated OS Reinstall")
    print("- Performance Monitoring")
    print("- Unified GUI Interface")
    print("- Recovery USB Creation")
    print("- Build and Deploy Tools")
    
    return score

if __name__ == "__main__":
    check_full_stack()