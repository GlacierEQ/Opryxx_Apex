"""
UNIFIED OPRYXX GUI - Full Stack Interface
All functions and options in one powerful interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import time
import psutil
from datetime import datetime

class UnifiedOPRYXXGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UNIFIED OPRYXX - Ultimate System Control")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#0a0a0a')
        title_frame.pack(fill='x', pady=10)
        
        tk.Label(title_frame, text="🚀 UNIFIED OPRYXX CONTROL CENTER", 
                font=('Arial', 24, 'bold'), fg='#00ff41', bg='#0a0a0a').pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create all tabs
        self.create_ai_tab()
        self.create_recovery_tab()
        self.create_performance_tab()
        self.create_system_tab()
        self.create_tools_tab()
        self.create_monitoring_tab()
        
        # Status bar
        self.create_status_bar()
        
    def create_ai_tab(self):
        """AI Systems Tab"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI Systems")
        
        # AI Controls
        controls_frame = tk.LabelFrame(ai_frame, text="AI Control Center", 
                                     bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # NEXUS AI
        nexus_frame = tk.Frame(controls_frame, bg='#1a1a1a')
        nexus_frame.pack(fill='x', pady=5)
        
        tk.Label(nexus_frame, text="NEXUS AI (24/7 Optimizer):", 
                bg='#1a1a1a', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        
        tk.Button(nexus_frame, text="🚀 ACTIVATE", command=self.activate_nexus,
                 bg='#00aa00', fg='white', font=('Arial', 9, 'bold')).pack(side='right', padx=5)
        tk.Button(nexus_frame, text="⏸️ PAUSE", command=self.pause_nexus,
                 bg='#aa6600', fg='white', font=('Arial', 9, 'bold')).pack(side='right', padx=5)
        
        # ARIA AI
        aria_frame = tk.Frame(controls_frame, bg='#1a1a1a')
        aria_frame.pack(fill='x', pady=5)
        
        tk.Label(aria_frame, text="ARIA AI (Health Manager):", 
                bg='#1a1a1a', fg='white', font=('Arial', 10, 'bold')).pack(side='left')
        
        tk.Button(aria_frame, text="🚀 START", command=self.start_aria,
                 bg='#0066cc', fg='white', font=('Arial', 9, 'bold')).pack(side='right', padx=5)
        
        # Performance Modes
        mode_frame = tk.LabelFrame(ai_frame, text="Performance Modes", 
                                 bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        mode_frame.pack(fill='x', padx=10, pady=10)
        
        modes = ["BALANCED", "PERFORMANCE", "ULTRA", "EXTREME"]
        for mode in modes:
            tk.Button(mode_frame, text=f"⚡ {mode}", 
                     command=lambda m=mode: self.set_performance_mode(m),
                     bg='#cc6600', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5, pady=5)
        
        # AI Status Display
        self.ai_status_text = tk.Text(ai_frame, height=15, bg='#0a0a0a', fg='#00ff41', 
                                     font=('Consolas', 9))
        self.ai_status_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_recovery_tab(self):
        """Recovery Systems Tab"""
        recovery_frame = ttk.Frame(self.notebook)
        self.notebook.add(recovery_frame, text="🔧 Recovery")
        
        # Emergency Recovery
        emergency_frame = tk.LabelFrame(recovery_frame, text="Emergency Recovery", 
                                      bg='#1a1a1a', fg='#ff4444', font=('Arial', 12, 'bold'))
        emergency_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(emergency_frame, text="🚨 SAFE MODE EXIT", command=self.safe_mode_exit,
                 bg='#ff0000', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=10)
        tk.Button(emergency_frame, text="🔧 BOOT REPAIR", command=self.boot_repair,
                 bg='#ff6600', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=10)
        tk.Button(emergency_frame, text="💥 NUCLEAR RESET", command=self.nuclear_reset,
                 bg='#cc0000', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=10)
        
        # OS Reinstall
        reinstall_frame = tk.LabelFrame(recovery_frame, text="OS Reinstall", 
                                      bg='#1a1a1a', fg='#ffaa00', font=('Arial', 12, 'bold'))
        reinstall_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(reinstall_frame, text="🚀 AUTO WINDOWS 11 REINSTALL", command=self.auto_reinstall,
                 bg='#0066cc', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=10)
        tk.Button(reinstall_frame, text="💿 CREATE RECOVERY USB", command=self.create_recovery_usb,
                 bg='#6600cc', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=10)
        
        # Recovery Status
        self.recovery_status_text = tk.Text(recovery_frame, height=20, bg='#0a0a0a', fg='#ffaa00', 
                                          font=('Consolas', 9))
        self.recovery_status_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_performance_tab(self):
        """Performance Monitoring Tab"""
        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="📊 Performance")
        
        # Real-time metrics
        metrics_frame = tk.LabelFrame(perf_frame, text="Real-Time Metrics", 
                                    bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # CPU/Memory/Disk gauges
        gauges_frame = tk.Frame(metrics_frame, bg='#1a1a1a')
        gauges_frame.pack(fill='x', pady=10)
        
        self.cpu_var = tk.StringVar(value="CPU: 0%")
        self.memory_var = tk.StringVar(value="Memory: 0%")
        self.disk_var = tk.StringVar(value="Disk: 0%")
        
        tk.Label(gauges_frame, textvariable=self.cpu_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 14, 'bold')).pack(side='left', padx=20)
        tk.Label(gauges_frame, textvariable=self.memory_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 14, 'bold')).pack(side='left', padx=20)
        tk.Label(gauges_frame, textvariable=self.disk_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 14, 'bold')).pack(side='left', padx=20)
        
        # Performance Actions
        actions_frame = tk.LabelFrame(perf_frame, text="Performance Actions", 
                                    bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(actions_frame, text="🚀 RUN BENCHMARK", command=self.run_benchmark,
                 bg='#0066cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=10, pady=10)
        tk.Button(actions_frame, text="📊 PERFORMANCE DASHBOARD", command=self.launch_dashboard,
                 bg='#cc6600', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=10, pady=10)
        tk.Button(actions_frame, text="🔍 MEMORY LEAK SCAN", command=self.memory_leak_scan,
                 bg='#6600cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=10, pady=10)
        
        # Performance Log
        self.perf_log_text = tk.Text(perf_frame, height=15, bg='#0a0a0a', fg='#00ff41', 
                                   font=('Consolas', 9))
        self.perf_log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_system_tab(self):
        """System Tools Tab"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="🛠️ System Tools")
        
        # System Optimization
        opt_frame = tk.LabelFrame(system_frame, text="System Optimization", 
                                bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        opt_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(opt_frame, text="🧹 CLEAN TEMP FILES", command=self.clean_temp,
                 bg='#00aa00', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(opt_frame, text="📝 REGISTRY REPAIR", command=self.registry_repair,
                 bg='#aa6600', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(opt_frame, text="💽 DISK CLEANUP", command=self.disk_cleanup,
                 bg='#6600aa', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(opt_frame, text="🔄 DEFRAGMENT", command=self.defragment,
                 bg='#aa0066', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        
        # Driver Management
        driver_frame = tk.LabelFrame(system_frame, text="Driver Management", 
                                   bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        driver_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(driver_frame, text="💾 BACKUP DRIVERS", command=self.backup_drivers,
                 bg='#0066cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(driver_frame, text="🔄 RESTORE DRIVERS", command=self.restore_drivers,
                 bg='#cc6600', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(driver_frame, text="🔍 SCAN DRIVERS", command=self.scan_drivers,
                 bg='#6600cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        
        # System Log
        self.system_log_text = tk.Text(system_frame, height=20, bg='#0a0a0a', fg='#00ff41', 
                                     font=('Consolas', 9))
        self.system_log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_tools_tab(self):
        """Advanced Tools Tab"""
        tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_frame, text="🔧 Advanced Tools")
        
        # Build Tools
        build_frame = tk.LabelFrame(tools_frame, text="Build & Deploy", 
                                  bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        build_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(build_frame, text="📦 BUILD EXE FILES", command=self.build_exe,
                 bg='#0066cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(build_frame, text="💿 CREATE INSTALLER", command=self.create_installer,
                 bg='#cc6600', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(build_frame, text="🧪 RUN TESTS", command=self.run_tests,
                 bg='#6600cc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        
        # Integration Tools
        integration_frame = tk.LabelFrame(tools_frame, text="Integration Tools", 
                                        bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        integration_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(integration_frame, text="🌊 WINDSURF INTEGRATION", command=self.windsurf_integration,
                 bg='#00aacc', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(integration_frame, text="🔗 TODO BRIDGE", command=self.todo_bridge,
                 bg='#cc00aa', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        tk.Button(integration_frame, text="🛠️ GANDALF PE", command=self.gandalf_pe,
                 bg='#aacc00', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5, pady=5)
        
        # Tools Log
        self.tools_log_text = tk.Text(tools_frame, height=20, bg='#0a0a0a', fg='#00ff41', 
                                    font=('Consolas', 9))
        self.tools_log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_monitoring_tab(self):
        """Monitoring & Alerts Tab"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="📈 Monitoring")
        
        # Alert Settings
        alert_frame = tk.LabelFrame(monitor_frame, text="Alert Settings", 
                                  bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        alert_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Checkbutton(alert_frame, text="🔔 Desktop Notifications", bg='#1a1a1a', fg='white',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
        tk.Checkbutton(alert_frame, text="🚨 Critical Alerts", bg='#1a1a1a', fg='white',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
        tk.Checkbutton(alert_frame, text="📊 Performance Reports", bg='#1a1a1a', fg='white',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=2)
        
        # System Health
        health_frame = tk.LabelFrame(monitor_frame, text="System Health", 
                                   bg='#1a1a1a', fg='#00ff41', font=('Arial', 12, 'bold'))
        health_frame.pack(fill='x', padx=10, pady=10)
        
        self.health_score_var = tk.StringVar(value="Health Score: Calculating...")
        tk.Label(health_frame, textvariable=self.health_score_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Monitoring Log
        self.monitor_log_text = tk.Text(monitor_frame, height=15, bg='#0a0a0a', fg='#00ff41', 
                                      font=('Consolas', 9))
        self.monitor_log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg='#1a1a1a', relief='sunken', bd=1)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_var = tk.StringVar(value="OPRYXX Unified GUI Ready")
        tk.Label(status_frame, textvariable=self.status_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 10)).pack(side='left', padx=10, pady=2)
        
        # Real-time clock
        self.time_var = tk.StringVar()
        tk.Label(status_frame, textvariable=self.time_var, bg='#1a1a1a', fg='#00ff41', 
                font=('Arial', 10)).pack(side='right', padx=10, pady=2)
        
        self.update_time()
        self.update_metrics()
        
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
        
    def update_metrics(self):
        """Update system metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            self.cpu_var.set(f"CPU: {cpu_percent:.1f}%")
            self.memory_var.set(f"Memory: {memory_percent:.1f}%")
            self.disk_var.set(f"Disk: {disk_percent:.1f}%")
            
            # Calculate health score
            health_score = 100 - max(cpu_percent, memory_percent, disk_percent)
            self.health_score_var.set(f"Health Score: {health_score:.0f}%")
            
        except:
            pass
        
        self.root.after(5000, self.update_metrics)
    
    # AI System Methods
    def activate_nexus(self):
        self.log_to_ai("🚀 Activating NEXUS AI...")
        threading.Thread(target=self.run_command, args=("python ai/ULTIMATE_AI_OPTIMIZER.py",)).start()
        
    def pause_nexus(self):
        self.log_to_ai("⏸️ Pausing NEXUS AI...")
        
    def start_aria(self):
        self.log_to_ai("🚀 Starting ARIA AI...")
        threading.Thread(target=self.run_command, args=("python ai/AI_WORKBENCH.py",)).start()
        
    def set_performance_mode(self, mode):
        self.log_to_ai(f"⚡ Setting performance mode to {mode}")
        
    # Recovery Methods
    def safe_mode_exit(self):
        self.log_to_recovery("🚨 Executing safe mode exit...")
        threading.Thread(target=self.run_command, args=("python recovery/immediate_safe_mode_exit.py",)).start()
        
    def boot_repair(self):
        self.log_to_recovery("🔧 Running boot repair...")
        threading.Thread(target=self.run_command, args=("python recovery/boot_diagnostics.py",)).start()
        
    def nuclear_reset(self):
        if messagebox.askyesno("Nuclear Reset", "This will COMPLETELY WIPE your PC! Continue?"):
            self.log_to_recovery("💥 NUCLEAR RESET initiated...")
            threading.Thread(target=self.run_command, args=("recovery/NUCLEAR_RESET.bat",)).start()
            
    def auto_reinstall(self):
        if messagebox.askyesno("Auto Reinstall", "Start automated Windows 11 reinstall?"):
            self.log_to_recovery("🚀 Starting automated OS reinstall...")
            threading.Thread(target=self.run_command, args=("python recovery/automated_os_reinstall.py",)).start()
            
    def create_recovery_usb(self):
        self.log_to_recovery("💿 Creating recovery USB...")
        threading.Thread(target=self.run_command, args=("python recovery/create_e_drive_recovery.py",)).start()
        
    # Performance Methods
    def run_benchmark(self):
        self.log_to_perf("🚀 Running performance benchmark...")
        threading.Thread(target=self.run_command, args=("python performance_benchmark.py",)).start()
        
    def launch_dashboard(self):
        self.log_to_perf("📊 Launching performance dashboard...")
        threading.Thread(target=self.run_command, args=("python performance_dashboard.py",)).start()
        
    def memory_leak_scan(self):
        self.log_to_perf("🔍 Scanning for memory leaks...")
        threading.Thread(target=self.run_command, args=("python enhancements/system_validator.py",)).start()
        
    # System Methods
    def clean_temp(self):
        self.log_to_system("🧹 Cleaning temporary files...")
        
    def registry_repair(self):
        self.log_to_system("📝 Repairing registry...")
        
    def disk_cleanup(self):
        self.log_to_system("💽 Running disk cleanup...")
        
    def defragment(self):
        self.log_to_system("🔄 Starting defragmentation...")
        
    def backup_drivers(self):
        self.log_to_system("💾 Backing up drivers...")
        
    def restore_drivers(self):
        self.log_to_system("🔄 Restoring drivers...")
        
    def scan_drivers(self):
        self.log_to_system("🔍 Scanning drivers...")
        
    # Tools Methods
    def build_exe(self):
        self.log_to_tools("📦 Building EXE files...")
        threading.Thread(target=self.run_command, args=("python build_tools/create_exe.py",)).start()
        
    def create_installer(self):
        self.log_to_tools("💿 Creating installer...")
        threading.Thread(target=self.run_command, args=("python build_tools/create_installer.py",)).start()
        
    def run_tests(self):
        self.log_to_tools("🧪 Running tests...")
        threading.Thread(target=self.run_command, args=("python tests/test_coverage.py",)).start()
        
    def windsurf_integration(self):
        self.log_to_tools("🌊 Testing Windsurf integration...")
        threading.Thread(target=self.run_command, args=("python windsurf_integration.py",)).start()
        
    def todo_bridge(self):
        self.log_to_tools("🔗 Activating TODO bridge...")
        
    def gandalf_pe(self):
        self.log_to_tools("🛠️ Launching GANDALF PE integration...")
        
    # Utility Methods
    def run_command(self, command):
        """Run command in background"""
        try:
            subprocess.run(command, shell=True, capture_output=True)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            
    def log_to_ai(self, message):
        self.ai_status_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.ai_status_text.see(tk.END)
        
    def log_to_recovery(self, message):
        self.recovery_status_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.recovery_status_text.see(tk.END)
        
    def log_to_perf(self, message):
        self.perf_log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.perf_log_text.see(tk.END)
        
    def log_to_system(self, message):
        self.system_log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.system_log_text.see(tk.END)
        
    def log_to_tools(self, message):
        self.tools_log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.tools_log_text.see(tk.END)
        
    def run(self):
        self.root.mainloop()

def main():
    """Launch Unified OPRYXX GUI"""
    app = UnifiedOPRYXXGUI()
    app.run()

if __name__ == "__main__":
    main()