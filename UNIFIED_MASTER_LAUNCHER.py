#!/usr/bin/env python3
"""
OPRYXX UNIFIED MASTER LAUNCHER
Single entry point for all OPRYXX functionality
"""

import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class UnifiedMasterLauncher:
    """Master launcher for all OPRYXX components"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX UNIFIED MASTER LAUNCHER")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0a')
        
        self.components = {
            'ai_engine': None,
            'full_stack_gui': None,
            'master_start': None
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the launcher interface"""
        # Header
        header = tk.Frame(self.root, bg='#0a0a0a', height=100)
        header.pack(fill='x', padx=20, pady=10)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="OPRYXX UNIFIED SYSTEM", 
                        font=('Arial', 24, 'bold'), fg='#00ff41', bg='#0a0a0a')
        title.pack(pady=20)
        
        subtitle = tk.Label(header, text="Complete System Optimization & AI Engine", 
                           font=('Arial', 12), fg='#ffffff', bg='#0a0a0a')
        subtitle.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Launch options
        self.create_launch_section(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
        
        # Control buttons
        self.create_control_section(main_frame)
    
    def create_launch_section(self, parent):
        """Create launch options section"""
        launch_frame = tk.LabelFrame(parent, text="Launch Options", 
                                   bg='#1a1a2e', fg='#00ff41', font=('Arial', 14, 'bold'))
        launch_frame.pack(fill='x', padx=10, pady=10)
        
        # Launch buttons
        buttons = [
            ("🚀 FULL STACK GUI", self.launch_full_stack, "#00ff41"),
            ("🤖 AI OPTIMIZATION ENGINE", self.launch_ai_engine, "#ff8000"),
            ("⚡ MASTER START", self.launch_master_start, "#ff0040"),
            ("🔧 SYSTEM RECOVERY", self.launch_recovery, "#8000ff"),
            ("📊 PERFORMANCE MONITOR", self.launch_monitor, "#00ffff")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(launch_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 12, 'bold'),
                           relief='flat', padx=20, pady=10, width=30)
            btn.pack(pady=5)
    
    def create_status_section(self, parent):
        """Create status monitoring section"""
        status_frame = tk.LabelFrame(parent, text="System Status", 
                                   bg='#1a1a2e', fg='#00ff41', font=('Arial', 14, 'bold'))
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Status display
        self.status_text = tk.Text(status_frame, bg='#0f0f23', fg='#ffffff',
                                  font=('Consolas', 10), wrap='word', height=10)
        self.status_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Initial status
        self.log_status("OPRYXX Unified System Ready")
        self.log_status("Select a component to launch")
    
    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = tk.Frame(parent, bg='#1a1a2e')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        tk.Button(control_frame, text="🔄 REFRESH STATUS", command=self.refresh_status,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="🛑 STOP ALL", command=self.stop_all,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="❌ EXIT", command=self.exit_launcher,
                 bg='#9e9e9e', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=15, pady=5).pack(side='right', padx=5)
    
    def log_status(self, message):
        """Log status message"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\\n"
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def launch_full_stack(self):
        """Launch Full Stack GUI"""
        self.log_status("🚀 Launching Full Stack GUI...")
        try:
            script_path = Path(__file__).parent / "UNIFIED_FULL_STACK_GUI.py"
            if script_path.exists():
                self.components['full_stack_gui'] = subprocess.Popen([sys.executable, str(script_path)])
                self.log_status("✅ Full Stack GUI launched successfully")
            else:
                self.log_status("❌ Full Stack GUI script not found")
        except Exception as e:
            self.log_status(f"❌ Error launching Full Stack GUI: {e}")
    
    def launch_ai_engine(self):
        """Launch AI Optimization Engine"""
        self.log_status("🤖 Launching AI Optimization Engine...")
        try:
            script_path = Path(__file__).parent / "AI_OPTIMIZATION_ENGINE.py"
            if script_path.exists():
                self.components['ai_engine'] = subprocess.Popen([sys.executable, str(script_path)])
                self.log_status("✅ AI Optimization Engine launched successfully")
            else:
                self.log_status("❌ AI Engine script not found")
        except Exception as e:
            self.log_status(f"❌ Error launching AI Engine: {e}")
    
    def launch_master_start(self):
        """Launch Master Start"""
        self.log_status("⚡ Launching Master Start...")
        try:
            script_path = Path(__file__).parent / "master_start.py"
            if script_path.exists():
                self.components['master_start'] = subprocess.Popen([sys.executable, str(script_path)])
                self.log_status("✅ Master Start launched successfully")
            else:
                self.log_status("❌ Master Start script not found")
        except Exception as e:
            self.log_status(f"❌ Error launching Master Start: {e}")
    
    def launch_recovery(self):
        """Launch System Recovery"""
        self.log_status("🔧 Launching System Recovery...")
        try:
            # Look for recovery scripts
            recovery_scripts = [
                "recovery/master_recovery.py",
                "EMERGENCY_RECOVERY.bat",
                "recovery/safe_mode_recovery.py"
            ]
            
            for script in recovery_scripts:
                script_path = Path(__file__).parent / script
                if script_path.exists():
                    if script.endswith('.py'):
                        subprocess.Popen([sys.executable, str(script_path)])
                    else:
                        subprocess.Popen([str(script_path)], shell=True)
                    self.log_status(f"✅ Recovery launched: {script}")
                    return
            
            self.log_status("❌ No recovery scripts found")
        except Exception as e:
            self.log_status(f"❌ Error launching recovery: {e}")
    
    def launch_monitor(self):
        """Launch Performance Monitor"""
        self.log_status("📊 Launching Performance Monitor...")
        try:
            # Create simple performance monitor
            self.create_performance_monitor()
            self.log_status("✅ Performance Monitor launched")
        except Exception as e:
            self.log_status(f"❌ Error launching monitor: {e}")
    
    def create_performance_monitor(self):
        """Create simple performance monitoring window"""
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("OPRYXX Performance Monitor")
        monitor_window.geometry("600x400")
        monitor_window.configure(bg='#0a0a0a')
        
        # Performance display
        perf_text = tk.Text(monitor_window, bg='#0f0f23', fg='#00ff41',
                           font=('Consolas', 10), wrap='word')
        perf_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        def update_performance():
            """Update performance metrics"""
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('C:')
                
                perf_text.delete(1.0, tk.END)
                perf_text.insert(tk.END, f"OPRYXX PERFORMANCE MONITOR\\n")
                perf_text.insert(tk.END, f"{'='*40}\\n\\n")
                perf_text.insert(tk.END, f"CPU Usage: {cpu:.1f}%\\n")
                perf_text.insert(tk.END, f"Memory Usage: {memory.percent:.1f}%\\n")
                perf_text.insert(tk.END, f"Disk Usage: {(disk.used/disk.total)*100:.1f}%\\n")
                perf_text.insert(tk.END, f"Available Memory: {memory.available/1024/1024/1024:.1f} GB\\n")
                perf_text.insert(tk.END, f"Free Disk Space: {disk.free/1024/1024/1024:.1f} GB\\n\\n")
                perf_text.insert(tk.END, f"Last Updated: {time.strftime('%H:%M:%S')}\\n")
                
                # Schedule next update
                monitor_window.after(5000, update_performance)
                
            except Exception as e:
                perf_text.insert(tk.END, f"Error updating performance: {e}\\n")
        
        # Start performance updates
        update_performance()
    
    def refresh_status(self):
        """Refresh system status"""
        self.log_status("🔄 Refreshing system status...")
        
        # Check component status
        for name, process in self.components.items():
            if process and process.poll() is None:
                self.log_status(f"✅ {name.replace('_', ' ').title()}: Running")
            else:
                self.log_status(f"⭕ {name.replace('_', ' ').title()}: Stopped")
        
        # System info
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            self.log_status(f"💻 System: CPU {cpu:.1f}%, Memory {memory.percent:.1f}%")
        except:
            self.log_status("💻 System: Status unavailable")
    
    def stop_all(self):
        """Stop all running components"""
        self.log_status("🛑 Stopping all components...")
        
        for name, process in self.components.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    self.log_status(f"🛑 Stopped {name.replace('_', ' ').title()}")
                except:
                    self.log_status(f"❌ Failed to stop {name.replace('_', ' ').title()}")
        
        self.log_status("🛑 All components stopped")
    
    def exit_launcher(self):
        """Exit the launcher"""
        if messagebox.askyesno("Exit", "Stop all components and exit OPRYXX?"):
            self.stop_all()
            self.root.destroy()
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_launcher)
        self.root.mainloop()

def main():
    """Main function"""
    print("OPRYXX UNIFIED MASTER LAUNCHER")
    print("=" * 50)
    print("Starting unified launcher...")
    
    launcher = UnifiedMasterLauncher()
    launcher.run()

if __name__ == "__main__":
    main()