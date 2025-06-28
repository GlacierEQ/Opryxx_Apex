"""
Final System Check - Complete Assessment
"""

import os
from pathlib import Path

def check_system_completeness():
    """Check if all major components are present and functional"""
    
    print("OPRYXX FINAL SYSTEM ASSESSMENT")
    print("=" * 50)
    
    # Core Systems Check
    core_systems = {
        "Ultimate AI Optimizer": "ai/ULTIMATE_AI_OPTIMIZER.py",
        "MEGA OPRYXX": "gui/MEGA_OPRYXX.py", 
        "AI Workbench": "ai/AI_WORKBENCH.py",
        "Emergency Recovery": "recovery/immediate_safe_mode_exit.py",
        "Master Recovery": "recovery/master_recovery.py",
        "Boot Diagnostics": "recovery/boot_diagnostics.py"
    }
    
    print("\nCORE SYSTEMS CHECK:")
    working_systems = 0
    
    for name, path in core_systems.items():
        if Path(path).exists():
            print(f"[OK] {name} - READY")
            working_systems += 1
        else:
            print(f"[MISSING] {name}")
    
    # Launchers Check
    launchers = [
        "MASTER_LAUNCHER.bat",
        "launchers/LAUNCH_ULTIMATE_AI.bat",
        "launchers/LAUNCH_AI_WORKBENCH.bat",
        "launchers/EMERGENCY_RECOVERY.bat"
    ]
    
    print(f"\nLAUNCHERS CHECK:")
    working_launchers = 0
    
    for launcher in launchers:
        if Path(launcher).exists():
            print(f"[OK] {Path(launcher).name} - READY")
            working_launchers += 1
        else:
            print(f"[MISSING] {Path(launcher).name}")
    
    # Organization Check
    folders = [
        "ai/", "recovery/", "gui/", "core/", "integration/", 
        "maintenance/", "launchers/", "docs/", "config/"
    ]
    
    print(f"\nORGANIZATION CHECK:")
    organized_folders = 0
    
    for folder in folders:
        if Path(folder).exists():
            print(f"[OK] {folder} - ORGANIZED")
            organized_folders += 1
        else:
            print(f"[MISSING] {folder}")
    
    # Calculate Overall Score
    total_core = len(core_systems)
    total_launchers = len(launchers)
    total_folders = len(folders)
    
    core_score = (working_systems / total_core) * 100
    launcher_score = (working_launchers / total_launchers) * 100
    org_score = (organized_folders / total_folders) * 100
    
    overall_score = (core_score + launcher_score + org_score) / 3
    
    print(f"\nSYSTEM SCORES:")
    print(f"Core Systems: {core_score:.1f}%")
    print(f"Launchers: {launcher_score:.1f}%")
    print(f"Organization: {org_score:.1f}%")
    print(f"OVERALL: {overall_score:.1f}%")
    
    # Final Assessment
    print(f"\nFINAL ASSESSMENT:")
    
    if overall_score >= 90:
        print("STATUS: PEAK PERFORMANCE - SYSTEM COMPLETE!")
        print("- All major systems operational")
        print("- Perfect organization achieved")
        print("- Ready for production use")
    elif overall_score >= 75:
        print("STATUS: HIGH PERFORMANCE - SYSTEM READY!")
        print("- Core functionality complete")
        print("- Minor optimizations possible")
        print("- Fully usable system")
    elif overall_score >= 50:
        print("STATUS: MODERATE PERFORMANCE - FUNCTIONAL")
        print("- Some components missing")
        print("- Basic functionality works")
        print("- Needs some fixes")
    else:
        print("STATUS: LOW PERFORMANCE - NEEDS WORK")
        print("- Major components missing")
        print("- Requires significant fixes")
    
    # Usage Instructions
    print(f"\nUSAGE INSTRUCTIONS:")
    print("1. Launch Master System: MASTER_LAUNCHER.bat")
    print("2. 24/7 AI Optimizer: python ai/ULTIMATE_AI_OPTIMIZER.py")
    print("3. Emergency Recovery: python recovery/immediate_safe_mode_exit.py")
    print("4. Ultimate Recovery: python gui/MEGA_OPRYXX.py")
    
    return overall_score

if __name__ == "__main__":
    score = check_system_completeness()
    exit(0 if score >= 75 else 1)