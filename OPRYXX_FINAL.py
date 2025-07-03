"""
OPRYXX FINAL - Complete Optimized System
Best practices, architecture, and functionality unified
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

from unified_system import UnifiedOPRYXXSystem
from core.logger import get_logger

class OPRYXXFinalGUI:
    """Final optimized OPRYXX GUI with all functionality"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX FINAL - Complete System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        self.system = UnifiedOPRYXXSystem()
        self.logger = get_logger("gui")
        self.monitoring_active = False
        
        self.setup_ui()
        self.initialize_system()
    
    def setup_ui(self):
        """Setup optimized user interface"""
        # Header
        header = tk.Frame(self.root, bg='#0a0a0a', height=80)
        header.pack(fill='x', padx=10, pady=5)
        header.pack_propagate(False)
        
        tk.Label(header, text="🚀 OPRYXX FINAL", 
                font=('Arial', 24, 'bold'), fg='#00ff41', bg='#0a0a0a').pack(pady=10)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg='#1a1a2e', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        self.create_control_panel(left_panel)
        
        # Right panel - Results
        right_panel = tk.Frame(main_container, bg='#0a0a0a')
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.create_results_panel(right_panel)
        
        # Status bar
        self.status_var = tk.StringVar(value="🟢 OPRYXX FINAL READY")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bg='#1a1a2e', fg='#00ff41', font=('Arial', 10))
        status_bar.pack(fill='x', pady=(5, 0))
    
    def create_control_panel(self, parent):
        """Create optimized control panel"""
        tk.Label(parent, text="⚡ SYSTEM CONTROLS", 
                font=('Arial', 14, 'bold'), fg='#00ff41', bg='#1a1a2e').pack(pady=10)
        
        # Recovery section
        recovery_frame = tk.LabelFrame(parent, text="Recovery Operations", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        recovery_frame.pack(fill='x', padx=10, pady=5)
        
        # Samsung recovery
        samsung_frame = tk.Frame(recovery_frame, bg='#1a1a2e')
        samsung_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(samsung_frame, text="BitLocker Key:", 
                bg='#1a1a2e', fg='#ffffff', font=('Arial', 9)).pack(anchor='w')
        
        self.bitlocker_entry = tk.Entry(samsung_frame, font=('Arial', 9), show='*', width=35)
        self.bitlocker_entry.pack(fill='x', pady=2)
        
        tk.Button(samsung_frame, text="🔓 Samsung SSD Recovery", 
                 command=self.samsung_recovery, bg='#4caf50', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', pady=2)
        
        # Dell recovery
        tk.Button(recovery_frame, text="💻 Dell Boot Recovery", 
                 command=self.dell_recovery, bg='#2196f3', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', padx=5, pady=2)
        
        # AI optimization section
        ai_frame = tk.LabelFrame(parent, text="AI Optimization", 
                               bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        ai_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(ai_frame, text="🤖 AI Optimize", 
                 command=self.ai_optimization, bg='#ff9800', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', padx=5, pady=2)
        
        tk.Button(ai_frame, text="📊 Start Monitoring", 
                 command=self.toggle_monitoring, bg='#9c27b0', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', padx=5, pady=2)
        
        # System section
        system_frame = tk.LabelFrame(parent, text="System Operations", 
                                   bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        system_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(system_frame, text="🔍 System Status", 
                 command=self.show_system_status, bg='#607d8b', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', padx=5, pady=2)
        
        tk.Button(system_frame, text="🧪 Run Tests", 
                 command=self.run_tests, bg='#795548', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill='x', padx=5, pady=2)
    
    def create_results_panel(self, parent):
        """Create results display panel"""
        # Notebook for different result types
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Recovery results tab
        recovery_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(recovery_frame, text="Recovery Results")
        
        self.recovery_text = scrolledtext.ScrolledText(recovery_frame, bg='#0f0f23', fg='#ffffff',
                                                      font=('Consolas', 9), wrap='word')
        self.recovery_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # AI results tab
        ai_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(ai_frame, text="AI Optimization")
        
        self.ai_text = scrolledtext.ScrolledText(ai_frame, bg='#0f0f23', fg='#00ff41',
                                                font=('Consolas', 9), wrap='word')
        self.ai_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # System status tab
        status_frame = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(status_frame, text="System Status")
        
        self.status_text = scrolledtext.ScrolledText(status_frame, bg='#0f0f23', fg='#ffffff',
                                                    font=('Consolas', 9), wrap='word')
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def initialize_system(self):
        """Initialize the OPRYXX system"""
        def init_worker():
            try:
                self.update_status("🔄 Initializing OPRYXX system...")
                results = self.system.initialize()
                
                success_count = sum(1 for r in results.values() if r.success)
                total_count = len(results)
                
                if success_count == total_count:
                    self.update_status("🟢 OPRYXX SYSTEM READY")
                    self.log_to_tab("recovery", f"✅ System initialized successfully ({success_count}/{total_count} modules)")
                else:
                    self.update_status("🟡 OPRYXX PARTIAL READY")
                    self.log_to_tab("recovery", f"⚠️ Partial initialization ({success_count}/{total_count} modules)")
                
                # Log module results
                for name, result in results.items():
                    status = "✅" if result.success else "❌"
                    self.log_to_tab("recovery", f"{status} {name}: {result.message}")
                    
            except Exception as e:
                self.update_status("❌ INITIALIZATION FAILED")
                self.log_to_tab("recovery", f"❌ Initialization error: {e}")
        
        threading.Thread(target=init_worker, daemon=True).start()
    
    def log_to_tab(self, tab_name: str, message: str):
        """Log message to specific tab"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\\n"
        
        if tab_name == "recovery":
            widget = self.recovery_text
        elif tab_name == "ai":
            widget = self.ai_text
        elif tab_name == "status":
            widget = self.status_text
        else:
            return
        
        def update_widget():
            widget.insert(tk.END, log_message)
            widget.see(tk.END)
            # Keep only last 1000 lines
            lines = widget.get(1.0, tk.END).split('\\n')
            if len(lines) > 1000:
                widget.delete(1.0, tk.END)
                widget.insert(1.0, '\\n'.join(lines[-1000:]))
        
        self.root.after(0, update_widget)
    
    def update_status(self, message: str):
        """Update status bar"""
        self.root.after(0, lambda: self.status_var.set(message))
    
    def samsung_recovery(self):
        """Execute Samsung SSD recovery"""
        def recovery_worker():
            try:
                recovery_key = self.bitlocker_entry.get().strip()
                if not recovery_key:
                    self.log_to_tab("recovery", "⚠️ No BitLocker key provided")
                
                self.update_status("🔓 Samsung SSD Recovery...")
                self.log_to_tab("recovery", "🚀 Starting Samsung SSD recovery...")
                
                result = self.system.execute_recovery("samsung_recovery", recovery_key=recovery_key)
                
                if result.success:
                    self.log_to_tab("recovery", f"✅ Samsung Recovery: {result.message}")
                    if result.data:
                        for item in result.data.get('results', []):
                            if item.get('success'):
                                self.log_to_tab("recovery", f"  ✅ Drive recovered: {item.get('drive_letter', 'Unknown')}")
                            else:
                                self.log_to_tab("recovery", f"  ❌ Drive failed: {item.get('error', 'Unknown error')}")
                else:
                    self.log_to_tab("recovery", f"❌ Samsung Recovery failed: {result.message}")
                
                self.update_status("🟢 Samsung recovery completed")
                
            except Exception as e:
                self.log_to_tab("recovery", f"❌ Samsung recovery error: {e}")
                self.update_status("❌ Samsung recovery failed")
        
        threading.Thread(target=recovery_worker, daemon=True).start()
    
    def dell_recovery(self):
        """Execute Dell boot recovery"""
        def recovery_worker():
            try:
                self.update_status("💻 Dell Boot Recovery...")
                self.log_to_tab("recovery", "🚀 Starting Dell boot recovery...")
                
                result = self.system.execute_recovery("dell_recovery")
                
                if result.success:
                    self.log_to_tab("recovery", f"✅ Dell Recovery: {result.message}")
                    if result.data:
                        fixed = result.data.get('fixed', [])
                        for issue in fixed:
                            self.log_to_tab("recovery", f"  ✅ Fixed: {issue.description}")
                else:
                    self.log_to_tab("recovery", f"❌ Dell Recovery failed: {result.message}")
                
                self.update_status("🟢 Dell recovery completed")
                
            except Exception as e:
                self.log_to_tab("recovery", f"❌ Dell recovery error: {e}")
                self.update_status("❌ Dell recovery failed")
        
        threading.Thread(target=recovery_worker, daemon=True).start()
    
    def ai_optimization(self):
        """Execute AI optimization"""
        def ai_worker():
            try:
                self.update_status("🤖 AI Optimization...")
                self.log_to_tab("ai", "🚀 Starting AI optimization...")
                
                result = self.system.execute_recovery("ai_optimization")
                
                if result.success:
                    self.log_to_tab("ai", f"✅ AI Optimization: {result.message}")
                    if result.data:
                        score = result.data.get('performance_score', 0)
                        self.log_to_tab("ai", f"  📊 Performance Score: {score:.1f}%")
                        
                        executed = result.data.get('executed', [])
                        for action in executed:
                            self.log_to_tab("ai", f"  ⚡ Executed: {action}")
                        
                        metrics = result.data.get('metrics', {})
                        self.log_to_tab("ai", f"  💻 CPU: {metrics.get('cpu_usage', 0):.1f}%")
                        self.log_to_tab("ai", f"  🧠 Memory: {metrics.get('memory_usage', 0):.1f}%")
                        self.log_to_tab("ai", f"  💾 Disk: {metrics.get('disk_usage', 0):.1f}%")
                else:
                    self.log_to_tab("ai", f"❌ AI Optimization failed: {result.message}")
                
                self.update_status("🟢 AI optimization completed")
                
            except Exception as e:
                self.log_to_tab("ai", f"❌ AI optimization error: {e}")
                self.update_status("❌ AI optimization failed")
        
        threading.Thread(target=ai_worker, daemon=True).start()
    
    def toggle_monitoring(self):
        """Toggle system monitoring"""
        if not self.monitoring_active:
            self.system.start_monitoring()
            self.monitoring_active = True
            self.log_to_tab("ai", "📊 System monitoring started")
            self.update_status("🟢 Monitoring active")
        else:
            self.system.stop_monitoring()
            self.monitoring_active = False
            self.log_to_tab("ai", "📊 System monitoring stopped")
            self.update_status("🟢 Monitoring stopped")
    
    def show_system_status(self):
        """Show comprehensive system status"""
        def status_worker():
            try:
                self.log_to_tab("status", "🔍 Gathering system status...")
                status = self.system.get_system_status()
                
                self.log_to_tab("status", f"🟢 System Ready: {status['system_ready']}")
                self.log_to_tab("status", "")
                self.log_to_tab("status", "📋 MODULE STATUS:")
                
                for name, module_status in status['modules'].items():
                    status_icon = "🟢" if module_status['ready'] else "🔴"
                    self.log_to_tab("status", f"  {status_icon} {name}: {module_status['status']}")
                
                # Add system metrics
                try:
                    import psutil
                    self.log_to_tab("status", "")
                    self.log_to_tab("status", "💻 SYSTEM METRICS:")
                    self.log_to_tab("status", f"  CPU: {psutil.cpu_percent():.1f}%")
                    
                    memory = psutil.virtual_memory()
                    self.log_to_tab("status", f"  Memory: {memory.percent:.1f}% ({memory.available/1024/1024/1024:.1f}GB free)")
                    
                    disk = psutil.disk_usage('C:')
                    self.log_to_tab("status", f"  Disk: {(disk.used/disk.total)*100:.1f}% ({disk.free/1024/1024/1024:.1f}GB free)")
                    
                except Exception as e:
                    self.log_to_tab("status", f"⚠️ Could not get system metrics: {e}")
                
            except Exception as e:
                self.log_to_tab("status", f"❌ Status check error: {e}")
        
        threading.Thread(target=status_worker, daemon=True).start()
    
    def run_tests(self):
        """Run system tests"""
        def test_worker():
            try:
                self.log_to_tab("status", "🧪 Running system tests...")
                
                # Import and run tests
                from tests.test_unified_system import run_tests
                success = run_tests()
                
                if success:
                    self.log_to_tab("status", "✅ All tests passed!")
                else:
                    self.log_to_tab("status", "❌ Some tests failed - check console for details")
                
            except Exception as e:
                self.log_to_tab("status", f"❌ Test execution error: {e}")
        
        threading.Thread(target=test_worker, daemon=True).start()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit OPRYXX?"):
            self.system.shutdown()
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point"""
    print("OPRYXX FINAL - Complete Optimized System")
    print("=" * 50)
    print("Starting unified system with GUI...")
    
    try:
        app = OPRYXXFinalGUI()
        app.run()
    except Exception as e:
        print(f"Error starting OPRYXX: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()