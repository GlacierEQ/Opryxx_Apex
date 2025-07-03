
import sys
import os
import subprocess
import threading
import time
from pathlib import Path

class OPRYXXLauncher:
    def __init__(self):
        self.base_path = Path(__file__).parent
        sys.path.insert(0, str(self.base_path))
        
    def launch_gui(self):
        """Launch desktop GUI"""
        try:
            from gui.unified_gui import UnifiedGUI
            app = UnifiedGUI()
            app.run()
        except Exception as e:
            print(f"GUI Error: {e}")
            input("Press Enter to exit...")
    
    def launch_web(self):
        """Launch web interface"""
        try:
            from gui.web_interface import web_interface
            print("Web interface starting at http://localhost:5000")
            web_interface.run(host='0.0.0.0', port=5000)
        except Exception as e:
            print(f"Web Error: {e}")
            input("Press Enter to exit...")
    
    def launch_performance(self):
        """Start performance monitoring"""
        try:
            from core.performance_monitor import start_performance_monitoring
            from core.memory_optimizer import memory_optimizer
            
            start_performance_monitoring()
            memory_optimizer.start_monitoring()
            
            print("Performance monitoring started!")
            print("Press Ctrl+C to stop...")
            
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        except Exception as e:
            print(f"Performance Error: {e}")
            input("Press Enter to exit...")

def main():
    print("OPRYXX SYSTEM LAUNCHER")
    print("=" * 30)
    print("1. Desktop GUI")
    print("2. Web Interface") 
    print("3. Performance Monitor Only")
    print("4. Exit")
    
    launcher = OPRYXXLauncher()
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                launcher.launch_gui()
            elif choice == '2':
                launcher.launch_web()
            elif choice == '3':
                launcher.launch_performance()
            elif choice == '4':
                break
            else:
                print("Invalid choice")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
