import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import psutil
import platform
import time
import winreg
from datetime import datetime

class OPRYXXMasterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OPRYXX_LOGS2 Master GUI")
        self.geometry("1200x900")
        self.repo_path = os.getcwd()
        self.device_info = self.detect_device()
        self.create_widgets()
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Repository", command=self.select_repo)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def detect_device(self):
        info = {}
        info['system'] = platform.system()
        info['release'] = platform.release()
        info['version'] = platform.version()
        if os.name == 'nt':
            try:
                result = subprocess.run(["wmic", "computersystem", "get", "manufacturer,model"], capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    info['manufacturer'] = parts[0]
                    info['model'] = ' '.join(parts[1:]) if len(parts) > 1 else "Unknown"
            except:
                info['manufacturer'] = "Unknown"
                info['model'] = "Unknown"
        info['processor'] = platform.processor()
        info['ram'] = f"{round(psutil.virtual_memory().total / (1024**3))} GB"
        return info

    def create_widgets(self):
        repo_frame = ttk.Frame(self)
        repo_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(repo_frame, text="Repository Path:").pack(side=tk.LEFT)
        self.repo_path_entry = ttk.Entry(repo_frame, textvariable=tk.StringVar(value=self.repo_path), width=80, state='readonly')
        self.repo_path_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(repo_frame, text="Change", command=self.select_repo).pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self)
        dash_tab = ttk.Frame(self.notebook)
        self.create_dashboard(dash_tab)
        self.notebook.add(dash_tab, text="Dashboard")

        maint_tab = ttk.Frame(self.notebook)
        self.create_maintenance_tabs(maint_tab)
        self.notebook.add(maint_tab, text="PC Maintenance")

        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        console_frame = ttk.LabelFrame(self, text="Operations Log")
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.console = scrolledtext.ScrolledText(console_frame, height=10, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)

    def select_repo(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path = path
            self.repo_path_entry.config(state=tk.NORMAL)
            self.repo_path_entry.delete(0, tk.END)
            self.repo_path_entry.insert(0, path)
            self.repo_path_entry.config(state='readonly')
            self.log(f"Repository set to: {path}")

    def log(self, message):
        self.console.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.config(state=tk.DISABLED)
        self.console.see(tk.END)

    def run_powershell_script(self, script_name):
        script_path = os.path.join(self.repo_path, "powershell_scripts", script_name)
        if not os.path.exists(script_path):
            self.log(f"Error: Script not found at {script_path}")
            messagebox.showerror("Error", f"Script not found: {script_name}")
            return

        def execute():
            self.log(f"Executing PowerShell script: {script_name}")
            try:
                command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{script_path}"'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for line in process.stdout:
                    self.log(f"PS Out: {line.strip()}")
                for line in process.stderr:
                    self.log(f"PS Err: {line.strip()}")
                process.wait()
                if process.returncode == 0:
                    self.log(f"Script '{script_name}' completed successfully.")
                else:
                    self.log(f"Script '{script_name}' failed with exit code {process.returncode}.")
            except Exception as e:
                self.log(f"Error running script: {str(e)}")

        threading.Thread(target=execute, daemon=True).start()

    def create_dashboard(self, parent):
        ttk.Label(parent, text="System Overview", font=("Segoe UI", 14, "bold")).pack(pady=10)

        info_frame = ttk.LabelFrame(parent, text="Device Information")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Manufacturer: {self.device_info.get('manufacturer', 'N/A')}").pack(anchor="w", padx=5)
        ttk.Label(info_frame, text=f"Model: {self.device_info.get('model', 'N/A')}").pack(anchor="w", padx=5)
        ttk.Label(info_frame, text=f"OS: {self.device_info.get('system', 'N/A')} {self.device_info.get('release', 'N/A')} ({self.device_info.get('version', 'N/A')})").pack(anchor="w", padx=5)
        ttk.Label(info_frame, text=f"Processor: {self.device_info.get('processor', 'N/A')}").pack(anchor="w", padx=5)
        ttk.Label(info_frame, text=f"RAM: {self.device_info.get('ram', 'N/A')}").pack(anchor="w", padx=5)

        stats_frame = ttk.LabelFrame(parent, text="Live System Stats")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(stats_frame, text="CPU Usage:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.cpu_bar = ttk.Progressbar(stats_frame, length=200)
        self.cpu_bar.grid(row=0, column=1, padx=5, pady=2)
        self.cpu_percent = ttk.Label(stats_frame, text="0%")
        self.cpu_percent.grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(stats_frame, text="RAM Usage:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.ram_bar = ttk.Progressbar(stats_frame, length=200)
        self.ram_bar.grid(row=1, column=1, padx=5, pady=2)
        self.ram_percent = ttk.Label(stats_frame, text="0%")
        self.ram_percent.grid(row=1, column=2, padx=5, pady=2)

        ttk.Label(stats_frame, text="Disk Usage (C:):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.disk_bar = ttk.Progressbar(stats_frame, length=200)
        self.disk_bar.grid(row=2, column=1, padx=5, pady=2)
        self.disk_percent = ttk.Label(stats_frame, text="0%")
        self.disk_percent.grid(row=2, column=2, padx=5, pady=2)

        threading.Thread(target=self.update_stats, daemon=True).start()

    def update_stats(self):
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                self.cpu_bar['value'] = cpu
                self.cpu_percent.config(text=f"{cpu}%")

                ram = psutil.virtual_memory().percent
                self.ram_bar['value'] = ram
                self.ram_percent.config(text=f"{ram}%")

                disk = psutil.disk_usage('C:\\').percent
                self.disk_bar['value'] = disk
                self.disk_percent.config(text=f"{disk}%")
                time.sleep(1)
            except Exception as e:
                self.log(f"Error updating stats: {e}")
                time.sleep(5)

    def create_maintenance_tabs(self, parent_frame):
        maint_notebook = ttk.Notebook(parent_frame)
        maint_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # System Cleaning tab
        cleaning_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(cleaning_tab, text="System Cleaning")
        ttk.Button(cleaning_tab, text="Clear Temporary Files", command=lambda: self.run_powershell_script("01_system_cleaning.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(cleaning_tab, text="Run Disk Cleanup", command=lambda: self.run_powershell_script("01_system_cleaning.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(cleaning_tab, text="Optimize Drives", command=lambda: self.run_powershell_script("03_disk_health_opt.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(cleaning_tab, text="Clear Recycle Bin", command=lambda: self.run_powershell_script("01_system_cleaning.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # System File Repair tab
        repair_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(repair_tab, text="System Repair")
        ttk.Button(repair_tab, text="Run System File Checker (SFC)", command=lambda: self.run_powershell_script("02_system_file_repair.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(repair_tab, text="Repair Windows Image (DISM Scan)", command=lambda: self.run_powershell_script("02_system_file_repair.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(repair_tab, text="Repair Windows Image (DISM Restore)", command=lambda: self.run_powershell_script("02_system_file_repair.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Disk Health tab
        disk_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(disk_tab, text="Disk Health")
        ttk.Button(disk_tab, text="Check Disk for Errors", command=lambda: self.run_powershell_script("03_disk_health_opt.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(disk_tab, text="Optimize/Defrag Drive", command=lambda: self.run_powershell_script("03_disk_health_opt.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Performance tab
        perf_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(perf_tab, text="Performance")
        ttk.Button(perf_tab, text="Enable Ultimate Performance", command=lambda: self.run_powershell_script("04_performance_opt.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(perf_tab, text="Flush DNS Cache", command=lambda: self.run_powershell_script("05_network_reset.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(perf_tab, text="Reset Network Stack", command=lambda: self.run_powershell_script("05_network_reset.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(perf_tab, text="Reset Windows Update", command=lambda: self.run_powershell_script("04_performance_opt.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Security tab
        sec_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(sec_tab, text="Security")
        ttk.Button(sec_tab, text="Check for Windows Updates", command=lambda: self.run_powershell_script("06_security_updates.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sec_tab, text="Run Full Malware Scan", command=lambda: self.run_powershell_script("06_security_updates.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sec_tab, text="Check Security Settings", command=lambda: self.run_powershell_script("06_security_updates.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sec_tab, text="Check Firewall Status", command=lambda: self.run_powershell_script("06_security_updates.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(sec_tab, text="Enable Windows Firewall", command=lambda: self.run_powershell_script("06_security_updates.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Hardware tab
        hardware_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(hardware_tab, text="Hardware")
        ttk.Button(hardware_tab, text="Generate Battery Report", command=lambda: self.run_powershell_script("07_hardware_diagnostics.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(hardware_tab, text="List Drivers", command=lambda: self.run_powershell_script("07_hardware_diagnostics.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(hardware_tab, text="Check Memory Usage", command=lambda: self.run_powershell_script("07_hardware_diagnostics.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(hardware_tab, text="Run Memory Diagnostic", command=lambda: self.run_powershell_script("07_hardware_diagnostics.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Backup tab
        backup_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(backup_tab, text="Backup")
        ttk.Button(backup_tab, text="Create System Restore Point", command=lambda: self.run_powershell_script("08_backup_restore.ps1")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(backup_tab, text="View Restore Points", command=lambda: self.run_powershell_script("08_backup_restore.ps1")).pack(fill=tk.X, padx=5, pady=5)

        # Device Specific tab
        device_tab = ttk.Frame(maint_notebook)
        maint_notebook.add(device_tab, text="Device Specific")
        self._populate_device_specific_tab(device_tab)

        # Full Repair button in main tab
        ttk.Button(parent_frame, text="Run Full Deep PC Repair (Python)", command=self.run_deep_pc_repair_py).pack(pady=10)

    def _populate_device_specific_tab(self, frame):
        model = self.device_info.get('model', '').lower()
        manufacturer = self.device_info.get('manufacturer', '').lower()

        if "msi" in manufacturer or "summit" in model:
            ttk.Label(frame, text="MSI Summit Optimizations", font=("Segoe UI", 10, "bold")).pack(pady=5)
            ttk.Button(frame, text="MSI Center Performance Mode", command=lambda: self.run_powershell_script("09_device_specific_msi.ps1")).pack(fill=tk.X, padx=5, pady=5)
            ttk.Button(frame, text="GPU Optimization", command=lambda: self.run_powershell_script("09_device_specific_msi.ps1")).pack(fill=tk.X, padx=5, pady=5)
            ttk.Button(frame, text="Cooling Profile Adjustment", command=lambda: self.run_powershell_script("09_device_specific_msi.ps1")).pack(fill=tk.X, padx=5, pady=5)
        elif "dell" in manufacturer or "inspiron" in model:
            ttk.Label(frame, text="Dell Inspiron Optimizations", font=("Segoe UI", 10, "bold")).pack(pady=5)
            ttk.Button(frame, text="Dell Command Update", command=lambda: self.run_powershell_script("10_device_specific_dell.ps1")).pack(fill=tk.X, padx=5, pady=5)
            ttk.Button(frame, text="2-in-1 Touch Optimization", command=lambda: self.run_powershell_script("10_device_specific_dell.ps1")).pack(fill=tk.X, padx=5, pady=5)
            ttk.Button(frame, text="Dell Power Manager", command=lambda: self.run_powershell_script("10_device_specific_dell.ps1")).pack(fill=tk.X, padx=5, pady=5)
        else:
            ttk.Label(frame, text="No specific optimizations for this device detected.").pack(pady=20)

if __name__ == "__main__":
    app = OPRYXXMasterGUI()
    app.mainloop()
