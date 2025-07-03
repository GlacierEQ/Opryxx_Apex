#!/usr/bin/env python3
"""
OPRYXX MASTER CONTROLLER
Single entry point for the entire OPRYXX system
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

class OPRYXXMaster:
    def __init__(self):
        self.systems = {}
        self.running = False
        
    def initialize_all_systems(self):
        """Initialize all OPRYXX systems"""
        print("OPRYXX MASTER CONTROLLER")
        print("=" * 40)
        print("Initializing all systems...")
        
        # Core systems
        self._init_performance_system()
        self._init_memory_system()
        self._init_gpu_system()
        self._init_resilience_system()
        self._init_ultimate_optimizer()
        
        print("[OK] All systems initialized")
    
    def _init_performance_system(self):
        """Initialize performance monitoring"""
        try:
            from core.performance_monitor import start_performance_monitoring
            start_performance_monitoring()
            self.systems['performance'] = True
            print("[OK] Performance monitoring")
        except Exception as e:
            print(f"[ERROR] Performance system: {e}")
            self.systems['performance'] = False
    
    def _init_memory_system(self):
        """Initialize memory optimization"""
        try:
            from core.memory_optimizer import memory_optimizer
            memory_optimizer.start_monitoring()
            self.systems['memory'] = True
            print("[OK] Memory optimization")
        except Exception as e:
            print(f"[ERROR] Memory system: {e}")
            self.systems['memory'] = False
    
    def _init_gpu_system(self):
        """Initialize GPU acceleration"""
        try:
            from core.gpu_acceleration import enable_gpu_acceleration, is_gpu_available
            if is_gpu_available():
                enable_gpu_acceleration(True)
                self.systems['gpu'] = True
                print("[OK] GPU acceleration")
            else:
                self.systems['gpu'] = False
                print("[WARNING] No GPU detected")
        except Exception as e:
            print(f"[ERROR] GPU system: {e}")
            self.systems['gpu'] = False
    
    def _init_resilience_system(self):
        """Initialize resilience system"""
        try:
            from core.resilience_system import resilience_manager
            self.systems['resilience'] = True
            print("[OK] Resilience system")
        except Exception as e:
            print(f"[ERROR] Resilience system: {e}")
            self.systems['resilience'] = False
    
    def _init_ultimate_optimizer(self):
        """Initialize ultimate optimizer"""
        try:
            from ULTIMATE_OPTIMIZER import UltimateOptimizer
            self.optimizer = UltimateOptimizer()
            self.optimizer.start_ultimate_optimization()
            self.systems['optimizer'] = True
            print("[OK] Ultimate optimizer")
        except Exception as e:
            print(f"[ERROR] Ultimate optimizer: {e}")
            self.systems['optimizer'] = False
    
    def launch_gui(self):
        """Launch desktop GUI"""
        try:
            from gui.unified_gui import UnifiedGUI
            print("\n[LAUNCH] Desktop GUI")
            app = UnifiedGUI()
            app.run()
        except Exception as e:
            print(f"[ERROR] GUI launch failed: {e}")
            input("Press Enter to exit...")
    
    def launch_web(self):
        """Launch web interface"""
        try:
            from gui.web_interface import web_interface
            print("\n[LAUNCH] Web Interface")
            print("Access at: http://localhost:5000")
            web_interface.run(host='0.0.0.0', port=5000)
        except Exception as e:
            print(f"[ERROR] Web launch failed: {e}")
            input("Press Enter to exit...")
    
    def launch_console(self):
        """Launch console interface"""
        print("\n[LAUNCH] Console Interface")
        print("=" * 40)
        
        self.running = True
        
        try:
            while self.running:
                self._display_status()
                self._console_menu()
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.shutdown()
    
    def launch_emergency_rescue(self):
        """Launch emergency hardware rescue"""
        try:
            from recovery.hardware_rescue import HardwareRescue
            print("\n[EMERGENCY] Hardware Rescue Mode")
            rescue = HardwareRescue()
            rescue.run_full_rescue()
        except Exception as e:
            print(f"[ERROR] Emergency rescue failed: {e}")
    
    def _display_status(self):
        """Display system status"""
        print(f"\n[STATUS] Systems Active: {sum(self.systems.values())}/{len(self.systems)}")
        
        for system, status in self.systems.items():
            status_text = "[ONLINE]" if status else "[OFFLINE]"
            print(f"  {system.capitalize()}: {status_text}")
        
        # Get live metrics
        try:
            from core.performance_monitor import performance_monitor
            metrics = performance_monitor.get_metrics()
            print(f"\n[METRICS] CPU: {metrics.cpu_usage:.1f}% | Memory: {metrics.memory_usage:.1f}% | Score: {metrics.score:.1f}")
        except:
            pass
    
    def _console_menu(self):
        """Console menu"""
        print("\n[MENU]")
        print("1. Launch Desktop GUI")
        print("2. Launch Web Interface")
        print("3. System Diagnostics")
        print("4. Force Optimization")
        print("5. Emergency Hardware Rescue")
        print("6. BitLocker Recovery")
        print("7. Exit")
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                threading.Thread(target=self.launch_gui, daemon=True).start()
            elif choice == '2':
                threading.Thread(target=self.launch_web, daemon=True).start()
            elif choice == '3':
                self._run_diagnostics()
            elif choice == '4':
                self._force_optimization()
            elif choice == '5':
                self.launch_emergency_rescue()
            elif choice == '6':
                self._launch_bitlocker_rescue()
            elif choice == '7':
                self.running = False
            else:
                print("[ERROR] Invalid choice")
                
        except Exception as e:
            print(f"[ERROR] Menu error: {e}")
    
    def _run_diagnostics(self):
        """Run system diagnostics"""
        print("\n[DIAGNOSTICS] Running system diagnostics...")
        
        # GPU test
        try:
            from scripts.activate_gpu import activate_gpu
            activate_gpu()
        except:
            print("[ERROR] GPU diagnostics failed")
        
        # Memory test
        try:
            from core.memory_optimizer import memory_optimizer
            result = memory_optimizer.optimize_memory()
            print(f"[OK] Memory optimization: {result.get('freed_mb', 0):.1f}MB freed")
        except:
            print("[ERROR] Memory diagnostics failed")
    
    def _force_optimization(self):
        """Force system optimization"""
        print("\n[OPTIMIZATION] Running forced optimization...")
        
        try:
            if hasattr(self, 'optimizer'):
                status = self.optimizer.get_system_status()
                print(f"[OK] Optimization level: {status['system_state']['optimization_level']}")
            else:
                print("[ERROR] Optimizer not available")
        except Exception as e:
            print(f"[ERROR] Optimization failed: {e}")
    
    def shutdown(self):
        """Shutdown all systems"""
        print("\n[SHUTDOWN] Stopping all systems...")
        
        try:
            if hasattr(self, 'optimizer'):
                self.optimizer.stop_ultimate_optimization()
        except:
            pass
        
        try:
            from core.performance_monitor import stop_performance_monitoring
            stop_performance_monitoring()
        except:
            pass
        
        try:
            from core.memory_optimizer import memory_optimizer
            memory_optimizer.stop_monitoring()
        except:
            pass
        
        print("[OK] Shutdown complete")
    
    def _launch_bitlocker_rescue(self):
        """Launch BitLocker rescue"""
        try:
            from recovery.bitlocker_rescue import BitLockerRescue
            print("\n[BITLOCKER] BitLocker Recovery Mode")
            rescue = BitLockerRescue()
            rescue.samsung_ssd_bitlocker_rescue()
        except Exception as e:
            print(f"[ERROR] BitLocker rescue failed: {e}")

def main():
    master = OPRYXXMaster()
    
    try:
        master.initialize_all_systems()
        
        print("\n" + "=" * 40)
        print("OPRYXX SYSTEM READY")
        print("=" * 40)
        print("Choose interface:")
        print("1. Desktop GUI")
        print("2. Web Interface")
        print("3. Console Interface")
        
        choice = input("\nSelect interface (1-3): ").strip()
        
        if choice == '1':
            master.launch_gui()
        elif choice == '2':
            master.launch_web()
        elif choice == '3':
            master.launch_console()
        else:
            print("Invalid choice, launching console interface...")
            master.launch_console()
            
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        master.shutdown()
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        master.shutdown()

if __name__ == "__main__":
    main()