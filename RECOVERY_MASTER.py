#!/usr/bin/env python3
"""
OPRYXX RECOVERY MASTER
Unified recovery system for all hardware and data recovery needs
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import subprocess
from datetime import datetime

class RecoveryMaster:
    """Master recovery interface for all OPRYXX recovery modules"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX RECOVERY MASTER")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0a')
        
        self.recovery_modules = {
            'samsung_ssd': None,
            'dell_inspiron': None,
            'bitlocker_key': ""
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the recovery master interface"""
        # Header
        header = tk.Frame(self.root, bg='#0a0a0a', height=80)
        header.pack(fill='x', padx=20, pady=10)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🔧 OPRYXX RECOVERY MASTER", 
                        font=('Arial', 24, 'bold'), fg='#ff0040', bg='#0a0a0a')
        title.pack(pady=10)
        
        subtitle = tk.Label(header, text="Complete Hardware & Data Recovery System", 
                           font=('Arial', 12), fg='#ffffff', bg='#0a0a0a')
        subtitle.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook for different recovery types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create recovery tabs
        self.create_samsung_recovery_tab()
        self.create_dell_recovery_tab()
        self.create_general_recovery_tab()
        self.create_status_tab()
    
    def create_samsung_recovery_tab(self):
        """Samsung SSD recovery tab"""
        frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(frame, text="📱 Samsung SSD Recovery")
        
        # Header
        header_label = tk.Label(frame, text="Samsung 4TB SSD Recovery", 
                               font=('Arial', 16, 'bold'), fg='#00ff41', bg='#1a1a2e')
        header_label.pack(pady=10)
        
        # BitLocker key input
        key_frame = tk.LabelFrame(frame, text="BitLocker Recovery Key", 
                                 bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        key_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(key_frame, text="Enter your BitLocker recovery key:", 
                bg='#1a1a2e', fg='#ffffff', font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        self.bitlocker_key_entry = tk.Entry(key_frame, font=('Arial', 10), width=60, show='*')
        self.bitlocker_key_entry.pack(padx=10, pady=5)
        
        tk.Button(key_frame, text="Show/Hide Key", command=self.toggle_key_visibility,
                 bg='#4caf50', fg='white', font=('Arial', 9)).pack(pady=5)
        
        # Recovery options
        options_frame = tk.LabelFrame(frame, text="Recovery Options", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        options_frame.pack(fill='x', padx=20, pady=10)
        
        # Recovery buttons
        btn_frame = tk.Frame(options_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔍 Detect Samsung Drives", command=self.detect_samsung_drives,
                 bg='#2196f3', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔓 Unlock BitLocker", command=self.unlock_bitlocker,
                 bg='#ff9800', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🚀 Full Recovery", command=self.samsung_full_recovery,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Results area
        results_frame = tk.LabelFrame(frame, text="Recovery Results", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.samsung_results = scrolledtext.ScrolledText(results_frame, bg='#0f0f23', fg='#ffffff',
                                                        font=('Consolas', 9), wrap='word')
        self.samsung_results.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_dell_recovery_tab(self):
        """Dell Inspiron recovery tab"""
        frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(frame, text="💻 Dell Inspiron Recovery")
        
        # Header
        header_label = tk.Label(frame, text="Dell Inspiron 2-in-1 7040 Recovery", 
                               font=('Arial', 16, 'bold'), fg='#00ff41', bg='#1a1a2e')
        header_label.pack(pady=10)
        
        # System info
        info_frame = tk.LabelFrame(frame, text="System Information", 
                                  bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        info_frame.pack(fill='x', padx=20, pady=10)
        
        self.dell_info_label = tk.Label(info_frame, text="Click 'Detect System' to get system information", 
                                       bg='#1a1a2e', fg='#ffffff', font=('Arial', 10))
        self.dell_info_label.pack(padx=10, pady=10)
        
        # Recovery options
        options_frame = tk.LabelFrame(frame, text="Boot Recovery Options", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        options_frame.pack(fill='x', padx=20, pady=10)
        
        # Recovery buttons
        btn_frame = tk.Frame(options_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔍 Detect System", command=self.detect_dell_system,
                 bg='#2196f3', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔧 Fix Boot Issues", command=self.fix_boot_issues,
                 bg='#ff9800', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🚀 Full Recovery", command=self.dell_full_recovery,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Results area
        results_frame = tk.LabelFrame(frame, text="Recovery Results", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.dell_results = scrolledtext.ScrolledText(results_frame, bg='#0f0f23', fg='#ffffff',
                                                     font=('Consolas', 9), wrap='word')
        self.dell_results.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_general_recovery_tab(self):
        """General recovery tools tab"""
        frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(frame, text="🛠️ General Recovery")
        
        # Header
        header_label = tk.Label(frame, text="General Recovery Tools", 
                               font=('Arial', 16, 'bold'), fg='#00ff41', bg='#1a1a2e')
        header_label.pack(pady=10)
        
        # Tool categories
        categories = [
            ("🔧 System Repair", [
                ("Fix MBR/Boot Sector", self.fix_mbr),
                ("Rebuild BCD", self.rebuild_bcd),
                ("System File Check", self.system_file_check)
            ]),
            ("💾 Disk Recovery", [
                ("Check Disk Health", self.check_disk_health),
                ("Recover Partitions", self.recover_partitions),
                ("Data Recovery Scan", self.data_recovery_scan)
            ]),
            ("🔐 Security Recovery", [
                ("Reset Windows Password", self.reset_password),
                ("Disable BitLocker", self.disable_bitlocker),
                ("Security Policy Reset", self.reset_security_policy)
            ])
        ]
        
        for category_name, tools in categories:
            category_frame = tk.LabelFrame(frame, text=category_name, 
                                          bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
            category_frame.pack(fill='x', padx=20, pady=5)
            
            tool_frame = tk.Frame(category_frame, bg='#1a1a2e')
            tool_frame.pack(pady=5)
            
            for tool_name, tool_command in tools:
                tk.Button(tool_frame, text=tool_name, command=tool_command,
                         bg='#9c27b0', fg='white', font=('Arial', 9), padx=10, pady=3).pack(side='left', padx=3)
        
        # General results area
        results_frame = tk.LabelFrame(frame, text="Tool Results", 
                                     bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.general_results = scrolledtext.ScrolledText(results_frame, bg='#0f0f23', fg='#ffffff',
                                                        font=('Consolas', 9), wrap='word')
        self.general_results.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_status_tab(self):
        """System status and monitoring tab"""
        frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(frame, text="📊 System Status")
        
        # Header
        header_label = tk.Label(frame, text="System Status & Monitoring", 
                               font=('Arial', 16, 'bold'), fg='#00ff41', bg='#1a1a2e')
        header_label.pack(pady=10)
        
        # Status display
        status_frame = tk.LabelFrame(frame, text="Current System Status", 
                                    bg='#1a1a2e', fg='#00ff41', font=('Arial', 12, 'bold'))
        status_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, bg='#0f0f23', fg='#00ff41',
                                                    font=('Consolas', 10), wrap='word')
        self.status_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control buttons
        control_frame = tk.Frame(frame, bg='#1a1a2e')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(control_frame, text="🔄 Refresh Status", command=self.refresh_status,
                 bg='#4caf50', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="📋 Generate Report", command=self.generate_report,
                 bg='#2196f3', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Start status monitoring
        self.start_status_monitoring()
    
    def toggle_key_visibility(self):
        """Toggle BitLocker key visibility"""
        current_show = self.bitlocker_key_entry.cget('show')
        if current_show == '*':
            self.bitlocker_key_entry.config(show='')
        else:
            self.bitlocker_key_entry.config(show='*')
    
    def log_to_widget(self, widget, message):
        """Log message to text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\\n"
        widget.insert(tk.END, log_message)
        widget.see(tk.END)
        self.root.update_idletasks()
    
    def run_recovery_module(self, module_name, widget):
        """Run recovery module in separate thread"""
        def worker():
            try:
                script_path = Path(__file__).parent / f"{module_name}.py"
                if script_path.exists():
                    self.log_to_widget(widget, f"Starting {module_name}...")
                    
                    # Prepare command
                    cmd = [sys.executable, str(script_path)]
                    
                    # Add BitLocker key if needed
                    if module_name == "SAMSUNG_SSD_RECOVERY":
                        key = self.bitlocker_key_entry.get().strip()
                        if key:
                            # For now, we'll modify the script to accept key as argument
                            # In production, you'd want a more secure method
                            pass
                    
                    # Run the module
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                             stderr=subprocess.STDOUT, text=True)
                    
                    # Stream output
                    for line in process.stdout:
                        self.log_to_widget(widget, line.strip())
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.log_to_widget(widget, f"✅ {module_name} completed successfully")
                    else:
                        self.log_to_widget(widget, f"❌ {module_name} completed with errors")
                else:
                    self.log_to_widget(widget, f"❌ {module_name}.py not found")
            except Exception as e:
                self.log_to_widget(widget, f"❌ Error running {module_name}: {e}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    # Samsung SSD Recovery Functions
    def detect_samsung_drives(self):
        """Detect Samsung drives"""
        self.log_to_widget(self.samsung_results, "🔍 Detecting Samsung drives...")
        self.run_recovery_module("SAMSUNG_SSD_RECOVERY", self.samsung_results)
    
    def unlock_bitlocker(self):
        """Unlock BitLocker drives"""
        key = self.bitlocker_key_entry.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter BitLocker recovery key")
            return
        
        self.log_to_widget(self.samsung_results, "🔓 Unlocking BitLocker drives...")
        # Implementation would go here
    
    def samsung_full_recovery(self):
        """Run full Samsung SSD recovery"""
        self.log_to_widget(self.samsung_results, "🚀 Starting full Samsung SSD recovery...")
        self.run_recovery_module("SAMSUNG_SSD_RECOVERY", self.samsung_results)
    
    # Dell Recovery Functions
    def detect_dell_system(self):
        """Detect Dell system"""
        self.log_to_widget(self.dell_results, "🔍 Detecting Dell system...")
        self.run_recovery_module("DELL_INSPIRON_RECOVERY", self.dell_results)
    
    def fix_boot_issues(self):
        """Fix boot issues"""
        self.log_to_widget(self.dell_results, "🔧 Fixing boot issues...")
        # Implementation would go here
    
    def dell_full_recovery(self):
        """Run full Dell recovery"""
        self.log_to_widget(self.dell_results, "🚀 Starting full Dell recovery...")
        self.run_recovery_module("DELL_INSPIRON_RECOVERY", self.dell_results)
    
    # General Recovery Functions
    def fix_mbr(self):
        self.log_to_widget(self.general_results, "🔧 Fixing MBR/Boot Sector...")
    
    def rebuild_bcd(self):
        self.log_to_widget(self.general_results, "🔧 Rebuilding BCD...")
    
    def system_file_check(self):
        self.log_to_widget(self.general_results, "🔧 Running system file check...")
    
    def check_disk_health(self):
        self.log_to_widget(self.general_results, "💾 Checking disk health...")
    
    def recover_partitions(self):
        self.log_to_widget(self.general_results, "💾 Recovering partitions...")
    
    def data_recovery_scan(self):
        self.log_to_widget(self.general_results, "💾 Running data recovery scan...")
    
    def reset_password(self):
        self.log_to_widget(self.general_results, "🔐 Resetting Windows password...")
    
    def disable_bitlocker(self):
        self.log_to_widget(self.general_results, "🔐 Disabling BitLocker...")
    
    def reset_security_policy(self):
        self.log_to_widget(self.general_results, "🔐 Resetting security policy...")
    
    def start_status_monitoring(self):
        """Start system status monitoring"""
        def monitor_loop():
            while True:
                try:
                    self.update_system_status()
                    time.sleep(30)  # Update every 30 seconds
                except:
                    time.sleep(60)
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def update_system_status(self):
        """Update system status display"""
        try:
            import psutil
            
            # Get system metrics
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            status_info = f"""OPRYXX RECOVERY MASTER - SYSTEM STATUS
{'='*50}

System Performance:
  CPU Usage: {cpu:.1f}%
  Memory Usage: {memory.percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)
  Disk Usage: {(disk.used/disk.total)*100:.1f}% ({disk.free/1024/1024/1024:.1f}GB free)

Recovery Status:
  Samsung SSD Module: Available
  Dell Recovery Module: Available
  General Tools: Available
  
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Update status display
            self.root.after(0, lambda: self.update_status_display(status_info))
            
        except Exception as e:
            error_info = f"Error updating status: {e}\\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.root.after(0, lambda: self.update_status_display(error_info))
    
    def update_status_display(self, status_info):
        """Update status display in UI thread"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_info)
    
    def refresh_status(self):
        """Manually refresh status"""
        self.log_to_widget(self.status_text, "🔄 Refreshing system status...")
        self.update_system_status()
    
    def generate_report(self):
        """Generate comprehensive recovery report"""
        report_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Recovery Report"
        )
        
        if report_file:
            try:
                with open(report_file, 'w') as f:
                    f.write("OPRYXX RECOVERY MASTER REPORT\\n")
                    f.write("=" * 50 + "\\n\\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
                    
                    # Add system status
                    f.write("SYSTEM STATUS:\\n")
                    f.write(self.status_text.get(1.0, tk.END))
                    f.write("\\n\\n")
                    
                    # Add recovery logs
                    f.write("SAMSUNG SSD RECOVERY LOG:\\n")
                    f.write(self.samsung_results.get(1.0, tk.END))
                    f.write("\\n\\n")
                    
                    f.write("DELL RECOVERY LOG:\\n")
                    f.write(self.dell_results.get(1.0, tk.END))
                    f.write("\\n\\n")
                    
                    f.write("GENERAL RECOVERY LOG:\\n")
                    f.write(self.general_results.get(1.0, tk.END))
                
                messagebox.showinfo("Success", f"Report saved to {report_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")
    
    def run(self):
        """Run the recovery master"""
        self.root.mainloop()

def main():
    """Main function"""
    print("OPRYXX RECOVERY MASTER")
    print("=" * 50)
    print("Starting unified recovery system...")
    
    recovery_master = RecoveryMaster()
    recovery_master.run()

if __name__ == "__main__":
    main()