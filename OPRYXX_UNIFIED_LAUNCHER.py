#!/usr/bin/env python3
"""
OPRYXX Unified Launcher
Single entry point for all OPRYXX functionality
"""

import sys
import os
import threading
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

class OPRYXXUnifiedLauncher:
    def __init__(self):
        self.systems_status = {
            'performance': False,
            'memory': False,
            'gpu': False,
            'recovery': False,
            'gui': False,
            'web': False
        }
        
    def display_banner(self):
        """Display OPRYXX banner"""
        print("""
 ██████╗ ██████╗ ██████╗ ██╗   ██╗██╗  ██╗██╗  ██╗
██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝╚██╗██╔╝╚██╗██╔╝
██║   ██║██████╔╝██████╔╝ ╚████╔╝  ╚███╔╝  ╚███╔╝ 
██║   ██║██╔═══╝ ██╔══██╗  ╚██╔╝   ██╔██╗  ██╔██╗ 
╚██████╔╝██║     ██║  ██║   ██║   ██╔╝ ██╗██╔╝ ██╗
 ╚═════╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
        
UNIFIED SYSTEM LAUNCHER - ALL SYSTEMS READY
""")
    
    def check_system_status(self):
        """Check status of all systems"""
        print("[STATUS] Checking system components...")
        
        # Check core systems
        try:
            from core.performance_monitor import performance_monitor
            self.systems_status['performance'] = True
            print("[OK] Performance Monitor")
        except:
            print("[ERROR] Performance Monitor")
        
        try:
            from core.memory_optimizer import memory_optimizer
            self.systems_status['memory'] = True
            print("[OK] Memory Optimizer")
        except:
            print("[ERROR] Memory Optimizer")
        
        try:
            from core.gpu_acceleration import is_gpu_available
            self.systems_status['gpu'] = is_gpu_available()
            status = "GPU ACTIVE" if self.systems_status['gpu'] else "CPU FALLBACK"
            print(f"[OK] GPU Acceleration - {status}")
        except:
            print("[ERROR] GPU Acceleration")
        
        try:
            from recovery.hardware_rescue import HardwareRescue
            self.systems_status['recovery'] = True
            print("[OK] Hardware Recovery")
        except:
            print("[ERROR] Hardware Recovery")
        
        try:
            from gui.unified_gui import UnifiedGUI
            self.systems_status['gui'] = True
            print("[OK] Desktop GUI")
        except:
            print("[ERROR] Desktop GUI")
        
        try:
            from gui.web_interface import WebInterface
            self.systems_status['web'] = True
            print("[OK] Web Interface")
        except:
            print("[ERROR] Web Interface")
    
    def launch_desktop_gui(self):
        """Launch desktop GUI"""
        try:
            from gui.unified_gui import UnifiedGUI
            print("\n[LAUNCH] Starting Desktop GUI...")
            app = UnifiedGUI()
            app.run()
        except Exception as e:
            print(f"[ERROR] Desktop GUI failed: {e}")
    
    def launch_web_interface(self):
        """Launch web interface"""
        try:
            from gui.web_interface import web_interface
            print("\n[LAUNCH] Starting Web Interface...")
            print("Access at: http://localhost:5000")
            web_interface.run(host='0.0.0.0', port=5000)
        except Exception as e:
            print(f"[ERROR] Web interface failed: {e}")
    
    def launch_emergency_rescue(self):
        """Launch emergency hardware rescue"""
        try:
            from recovery.hardware_rescue import HardwareRescue
            print("\n[EMERGENCY] Hardware Rescue Mode")
            rescue = HardwareRescue()
            rescue.run_full_rescue()
        except Exception as e:
            print(f"[ERROR] Emergency rescue failed: {e}")
    
    def launch_samsung_recovery(self):
        """Launch Samsung SSD recovery"""
        try:
            from recovery.samsung_4tb_recovery import Samsung4TBRecovery
            print("\n[SAMSUNG] Samsung 4TB SSD Recovery")
            
            recovery_key = input("Enter BitLocker recovery key: ").strip()
            drive_letter = input("Enter drive letter (or press Enter for auto): ").strip()
            
            recovery = Samsung4TBRecovery(
                drive_letter if drive_letter else None,
                recovery_key if recovery_key else None
            )
            
            result = recovery.full_samsung_recovery()
            
            if result['success']:
                print(f"[SUCCESS] {result['message']}")
            else:
                print(f"[FAILED] {result['error']}")
                
        except Exception as e:
            print(f"[ERROR] Samsung recovery failed: {e}")
    
    def launch_windows11_bypass(self):
        """Launch Windows 11 bypass"""
        try:
            from recovery.windows11_bypass import Windows11Recovery
            print("\n[WIN11] Windows 11 TPM Bypass")
            
            recovery = Windows11Recovery()
            
            # Check status
            status = recovery.check_upgrade_status()
            print("\nCompatibility Status:")
            for check, result in status.items():
                print(f"  {check}: {'PASS' if result else 'FAIL'}")
            
            # Apply bypass
            if input("\nApply TPM bypass? (y/n): ").lower() == 'y':
                success, message = recovery.bypass_tmp_check()
                print(f"Bypass result: {message}")
                
        except Exception as e:
            print(f"[ERROR] Windows 11 bypass failed: {e}")
    
    def launch_ultimate_optimizer(self):
        """Launch ultimate optimizer"""
        try:
            from ULTIMATE_OPTIMIZER import UltimateOptimizer
            print("\n[OPTIMIZE] Ultimate System Optimizer")
            
            optimizer = UltimateOptimizer()
            optimizer.start_ultimate_optimization()
            
            print("Press Ctrl+C to stop...")
            while True:
                status = optimizer.get_system_status()
                print(f"\r[STATUS] CPU: {status['system_state']['cpu_usage']:.1f}% | "
                      f"MEM: {status['system_state']['memory_usage']:.1f}% | "
                      f"Level: {status['system_state']['optimization_level']}", end="")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n[STOP] Optimizer stopped")
        except Exception as e:
            print(f"[ERROR] Ultimate optimizer failed: {e}")
    
    def show_main_menu(self):
        """Show main menu"""
        while True:
            print("\n" + "=" * 50)
            print("OPRYXX UNIFIED SYSTEM MENU")
            print("=" * 50)
            print("1. Desktop GUI (Recommended)")
            print("2. Web Interface")
            print("3. Emergency Hardware Rescue")
            print("4. Samsung 4TB SSD Recovery")
            print("5. Windows 11 TPM Bypass")
            print("6. Ultimate System Optimizer")
            print("7. System Status Check")
            print("8. Exit")
            
            try:
                choice = input("\nSelect option (1-8): ").strip()
                
                if choice == '1':
                    self.launch_desktop_gui()
                elif choice == '2':
                    self.launch_web_interface()
                elif choice == '3':
                    self.launch_emergency_rescue()
                elif choice == '4':
                    self.launch_samsung_recovery()
                elif choice == '5':
                    self.launch_windows11_bypass()
                elif choice == '6':
                    self.launch_ultimate_optimizer()
                elif choice == '7':
                    self.check_system_status()
                elif choice == '8':
                    print("\n[EXIT] Goodbye!")
                    break
                else:
                    print("[ERROR] Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n[EXIT] Goodbye!")
                break
            except Exception as e:
                print(f"[ERROR] Menu error: {e}")
    
    def run(self):
        """Run the unified launcher"""
        self.display_banner()
        self.check_system_status()
        
        # Show quick status
        active_systems = sum(self.systems_status.values())
        total_systems = len(self.systems_status)
        
        print(f"\n[READY] {active_systems}/{total_systems} systems operational")
        
        if active_systems == total_systems:
            print("[STATUS] ALL SYSTEMS GO! 🚀")
        elif active_systems >= total_systems * 0.8:
            print("[STATUS] MOSTLY OPERATIONAL ⚡")
        else:
            print("[STATUS] PARTIAL SYSTEMS 🔧")
        
        self.show_main_menu()

def main():
    launcher = OPRYXXUnifiedLauncher()
    launcher.run()

if __name__ == "__main__":
    main()