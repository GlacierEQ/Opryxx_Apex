import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import time
import platform
import sys
import shutil
import ctypes
from datetime import datetime
import webbrowser

class OPRYXXRepairGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🜏 OPRYXX Repair Daemon — BlackEcho Sync")
        self.geometry("800x600")
        self.configure(bg="#1e1e2f")
        self.resizable(False, False)

        # Set app icon if available
        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
        except:
            pass

        # Create modules and logs directories
        for directory in ["modules", "logs"]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Create repair modules
        self._create_repair_modules()

        # Initialize variables
        self.running = False
        self.log_file = os.path.join("logs", f"OPRYXX_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.dark_theme = True
        self.module_vars = {}
        self._setup_ui()

    def _setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#1e1e2f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(main_frame, bg="#1e1e2f")
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text="OPRYXX: Oblivion Repair Chain", font=("Consolas", 18, "bold"),
                 bg="#1e1e2f", fg="#e0e0e0").pack(side=tk.LEFT, padx=10)
        tk.Label(header_frame, text="v4.1 Ultimate Supernova", font=("Consolas", 10),
                 bg="#1e1e2f", fg="#98fb98").pack(side=tk.RIGHT, padx=10, pady=5)

        # Hardware cleaning reminder
        tk.Label(main_frame, text="🛠️ REMINDER: Clean PC fans/vents to prevent overheating!",
                 font=("Consolas", 10, "italic"), bg="#1e1e2f", fg="#FFFF00").pack(fill=tk.X, pady=5)

        # Status and progress frame
        status_frame = tk.Frame(main_frame, bg="#1e1e2f")
        status_frame.pack(fill=tk.X, pady=5)
        self.status = tk.Label(status_frame, text="Status: Idle", font=("Consolas", 12),
                               bg="#1e1e2f", fg="#98fb98")
        self.status.pack(side=tk.LEFT, padx=10)
        self.time_estimate = tk.Label(status_frame, text="Est. Time: --:--", font=("Consolas", 12),
                                     bg="#1e1e2f", fg="#98fb98")
        self.time_estimate.pack(side=tk.RIGHT, padx=10)

        # Progress bar
        progress_frame = tk.Frame(main_frame, bg="#1e1e2f")
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=700, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.progress_percent = tk.Label(progress_frame, text="0%", font=("Consolas", 10),
                                        bg="#1e1e2f", fg="#e0e0e0", width=5)
        self.progress_percent.pack(side=tk.RIGHT, padx=5)

        # Log output
        log_frame = tk.Frame(main_frame, bg="#1e1e2f")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=90, height=20,
                                            font=("Consolas", 10), bg="#121212", fg="#00FFCC",
                                            insertbackground="white")
        self.log.pack(fill=tk.BOTH, expand=True, padx=10)
        self.create_context_menu()

        # Module selection
        module_frame = tk.Frame(main_frame, bg="#1e1e2f")
        module_frame.pack(fill=tk.X, pady=5)
        tk.Label(module_frame, text="Select Modules:", font=("Consolas", 10),
                 bg="#1e1e2f", fg="#e0e0e0").pack(side=tk.LEFT, padx=10)

        # Module checkboxes
        modules = [
            ("temp_clean", "Temp Cleanup", "Cleans temporary files and folders"),
            ("disk_cleanup", "Disk Cleanup", "Runs Windows Disk Cleanup tool"),
            ("disk_check", "Disk Check", "Checks C: for errors (may require reboot)"),
            ("syscheck", "SFC + DISM", "Repairs system files and Windows image"),
            ("net_repair", "Network Reset", "Resets network settings and DNS"),
            ("explorer_clean", "Explorer Cache", "Clears Explorer icon/thumbnail cache"),
            ("pagefile_reset", "Memory/Pagefile", "Optimizes virtual memory settings"),
            ("power_plan", "Power Plan", "Sets High Performance power plan"),
            ("file_organize", "File Organization", "Organizes Desktop and Downloads"),
            ("win_update", "Windows Update", "Checks for system updates"),
            ("antivirus", "Antivirus Scan", "Runs Windows Defender quick scan")
        ]

        checkbox_frame = tk.Frame(module_frame, bg="#1e1e2f")
        checkbox_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        for i, (mod_id, mod_name, tooltip) in enumerate(modules):
            self.module_vars[mod_id] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(checkbox_frame, text=mod_name, variable=self.module_vars[mod_id],
                               bg="#1e1e2f", fg="#e0e0e0", selectcolor="#282c34",
                               activebackground="#1e1e2f", activeforeground="#e0e0e0")
            cb.grid(row=i//3, column=i%3, sticky="w", padx=5)
            cb.bind("<Enter>", lambda e, t=tooltip: self._show_tooltip(e, t))
            cb.bind("<Leave>", self._hide_tooltip)

        # Select All/None button
        select_all_btn = tk.Button(module_frame, text="Select All/None", font=("Consolas", 10),
                                   bg="#282c34", fg="white", command=self._toggle_all_modules)
        select_all_btn.pack(side=tk.RIGHT, padx=10)
        select_all_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Toggle all modules on/off"))
        select_all_btn.bind("<Leave>", self._hide_tooltip)

        # Action buttons
        action_frame = tk.Frame(main_frame, bg="#1e1e2f")
        action_frame.pack(fill=tk.X, pady=10)
        self.execute_btn = tk.Button(action_frame, text="🌀 Execute Repair Chain", font=("Consolas", 12),
                                     bg="#282c34", fg="white", command=self._confirm_run_repair)
        self.execute_btn.pack(side=tk.LEFT, padx=10)
        self.execute_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Start selected repair tasks"))
        self.execute_btn.bind("<Leave>", self._hide_tooltip)

        self.stop_btn = tk.Button(action_frame, text="⏹️ Stop", font=("Consolas", 12),
                                  bg="#8B0000", fg="white", command=self._stop_repair, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Stop the repair process"))
        self.stop_btn.bind("<Leave>", self._hide_tooltip)

        self.save_log_btn = tk.Button(action_frame, text="💾 Save Log", font=("Consolas", 12),
                                      bg="#282c34", fg="white", command=self._save_log)
        self.save_log_btn.pack(side=tk.RIGHT, padx=10)
        self.save_log_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Save log to file"))
        self.save_log_btn.bind("<Leave>", self._hide_tooltip)

        self.view_log_btn = tk.Button(action_frame, text="📄 View Log", font=("Consolas", 12),
                                      bg="#282c34", fg="white", command=self._view_log)
        self.view_log_btn.pack(side=tk.RIGHT, padx=10)
        self.view_log_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Open log file in default editor"))
        self.view_log_btn.bind("<Leave>", self._hide_tooltip)

        theme_btn = tk.Button(action_frame, text="🌓 Toggle Theme", font=("Consolas", 12),
                              bg="#282c34", fg="white", command=self._toggle_theme)
        theme_btn.pack(side=tk.RIGHT, padx=10)
        theme_btn.bind("<Enter>", lambda e: self._show_tooltip(e, "Switch between dark and light themes"))
        theme_btn.bind("<Leave>", self._hide_tooltip)

        # Set theme style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TProgressbar", thickness=20, background='#00FFCC')

        # Tooltip setup
        self.tooltip = None

    def _show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.destroy()
        x, y = event.widget.winfo_pointerxy()
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip, text=text, bg="#FFFFCC", fg="#000000", 
                         relief="solid", borderwidth=1, font=("Consolas", 8))
        label.pack()

    def _hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.log, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self._copy_log)
        self.context_menu.add_command(label="Select All", command=self._select_all_log)
        self.context_menu.add_command(label="Clear", command=self._clear_log)
        self.log.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def _copy_log(self):
        try:
            selected_text = self.log.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except:
            pass

    def _select_all_log(self):
        self.log.tag_add(tk.SEL, "1.0", tk.END)
        self.log.mark_set(tk.INSERT, "1.0")
        self.log.see(tk.INSERT)

    def _clear_log(self):
        self.log.delete(1.0, tk.END)

    def _toggle_all_modules(self):
        all_selected = all(var.get() for var in self.module_vars.values())
        for var in self.module_vars.values():
            var.set(not all_selected)

    def _toggle_theme(self):
        if self.dark_theme:
            # Light theme
            self.configure(bg="#f0f0f0")
            self.log.config(bg="#ffffff", fg="#000000")
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg="#f0f0f0")
                    for child in widget.winfo_children():
                        if isinstance(child, (tk.Label, tk.Checkbutton)):
                            child.configure(bg="#f0f0f0", fg="#000000", activebackground="#f0f0f0", 
                                            activeforeground="#000000", selectcolor="#dddddd")
                        elif isinstance(child, tk.Button):
                            child.configure(bg="#dddddd", fg="#000000")
                        elif isinstance(child, tk.Frame):
                            child.configure(bg="#f0f0f0")
                            for subchild in child.winfo_children():
                                if isinstance(subchild, (tk.Label, tk.Checkbutton)):
                                    subchild.configure(bg="#f0f0f0", fg="#000000", activebackground="#f0f0f0",
                                                       activeforeground="#000000", selectcolor="#dddddd")
                                elif isinstance(subchild, tk.Button):
                                    subchild.configure(bg="#dddddd", fg="#000000")
            self.style.configure("TProgressbar", background='#4CAF50')
            self.dark_theme = False
        else:
            # Dark theme
            self.configure(bg="#1e1e2f")
            self.log.config(bg="#121212", fg="#00FFCC")
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg="#1e1e2f")
                    for child in widget.winfo_children():
                        if isinstance(child, (tk.Label, tk.Checkbutton)):
                            child.configure(bg="#1e1e2f", fg="#e0e0e0", activebackground="#1e1e2f",
                                            activeforeground="#e0e0e0", selectcolor="#282c34")
                        elif isinstance(child, tk.Button):
                            child.configure(bg="#282c34", fg="white")
                        elif isinstance(child, tk.Frame):
                            child.configure(bg="#1e1e2f")
                            for subchild in child.winfo_children():
                                if isinstance(subchild, (tk.Label, tk.Checkbutton)):
                                    subchild.configure(bg="#1e1e2f", fg="#e0e0e0", activebackground="#1e1e2f",
                                                       activeforeground="#e0e0e0", selectcolor="#282c34")
                                elif isinstance(subchild, tk.Button):
                                    subchild.configure(bg="#282c34", fg="white")
            self.style.configure("TProgressbar", background='#00FFCC')
            self.dark_theme = True

    def _confirm_run_repair(self):
        if not self._check_admin():
            messagebox.showwarning("Admin Rights Required",
                                   "This repair tool requires administrator privileges.\n"
                                   "Please restart the application as administrator.")
            return
        if not any(var.get() for var in self.module_vars.values()):
            messagebox.showwarning("No Modules Selected", "Please select at least one module to run.")
            return
        if messagebox.askyesno("Confirm Execution", "Are you sure you want to run the selected repair modules?"):
            self._run_repair()

    def _run_repair(self):
        self.execute_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.running = True
        thread = threading.Thread(target=self._execute_chain, daemon=True)
        thread.start()

    def _stop_repair(self):
        self.running = False
        self.log_message("⚠️ Stopping repair process...", "warning")

    def _save_log(self):
        content = self.log.get(1.0, tk.END)
        try:
            with open(self.log_file, 'w') as f:
                f.write(content)
            self.log_message(f"Log saved to: {self.log_file}", "success")
        except Exception as e:
            self.log_message(f"❌ Error saving log: {str(e)}", "error")

    def _view_log(self):
        try:
            os.startfile(self.log_file)
        except Exception as e:
            self.log_message(f"❌ Error opening log: {str(e)}", "error")

    def _check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _create_repair_modules(self):
        """Create batch files for repair modules."""
        modules_dir = "modules"

        # Temp cleaner
        with open(os.path.join(modules_dir, "temp_clean.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting temporary files cleanup...\n')
            f.write('for %%D in (%TEMP% %SystemRoot%\\Temp %USERPROFILE%\\AppData\\Local\\Temp) do (\n')
            f.write('    if exist "%%D" (\n')
            f.write('        del /q /f "%%D\\*.*" 2>nul\n')
            f.write('        for /d %%p in ("%%D\\*.*") do rd /s /q "%%p" 2>nul\n')
            f.write('    )\n')
            f.write(')\n')
            f.write('echo [%time%] Temp cleanup completed.\n')

        # Disk cleanup
        with open(os.path.join(modules_dir, "disk_cleanup.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Running Disk Cleanup...\n')
            f.write('cleanmgr /sagerun:1\n')
            f.write('echo [%time%] Disk Cleanup completed.\n')

        # Disk check
        with open(os.path.join(modules_dir, "disk_check.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Checking C: for disk errors...\n')
            f.write('chkdsk C: /f /r\n')
            f.write('if %errorlevel% neq 0 (\n')
            f.write('    echo [%time%] Disk errors found. Scheduling check for next reboot...\n')
            f.write('    echo y | chkdsk C: /f /r\n')
            f.write(')\n')
            f.write('echo [%time%] Disk check completed.\n')

        # System file checker
        with open(os.path.join(modules_dir, "syscheck.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting system file integrity check...\n')
            f.write('DISM /Online /Cleanup-Image /RestoreHealth\n')
            f.write('sfc /scannow\n')
            f.write('echo [%time%] System file check completed.\n')

        # Network repair
        with open(os.path.join(modules_dir, "net_repair.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting network stack reset...\n')
            f.write('netsh winsock reset\n')
            f.write('netsh int ip reset\n')
            f.write('ipconfig /flushdns\n')
            f.write('ipconfig /release\n')
            f.write('ipconfig /renew\n')
            f.write('echo [%time%] Network stack reset completed.\n')

        # Explorer cache cleaner
        with open(os.path.join(modules_dir, "explorer_clean.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting Explorer cache cleanup...\n')
            f.write('taskkill /f /im explorer.exe 2>nul\n')
            f.write('del /f "%userprofile%\\AppData\\Local\\IconCache.db" 2>nul\n')
            f.write('del /f "%userprofile%\\AppData\\Local\\Microsoft\\Windows\\Explorer\\iconcache*" 2>nul\n')
            f.write('del /f "%userprofile%\\AppData\\Local\\Microsoft\\Windows\\Explorer\\thumbcache*" 2>nul\n')
            f.write('start explorer.exe\n')
            f.write('echo [%time%] Explorer cache cleanup completed.\n')

        # Pagefile reset
        with open(os.path.join(modules_dir, "pagefile_reset.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting memory management optimization...\n')
            f.write('powershell -Command "& {Clear-DnsClientCache; Write-Host \'DNS Cache cleared\'}"\n')
            f.write('wmic computersystem where name="%computername%" set AutomaticManagedPagefile=True\n')
            f.write('echo [%time%] Memory management optimization completed.\n')

        # Power plan
        with open(os.path.join(modules_dir, "power_plan.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Setting High Performance power plan...\n')
            f.write('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c\n')
            f.write('echo [%time%] Power plan set.\n')

        # File organization
        with open(os.path.join(modules_dir, "file_organize.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting file organization...\n')
            f.write('set "DESKTOP=%USERPROFILE%\\Desktop"\n')
            f.write('set "DOWNLOADS=%USERPROFILE%\\Downloads"\n')
            f.write('mkdir "%DESKTOP%\\Shortcuts" 2>nul\n')
            f.write('move /Y "%DESKTOP%\\*.lnk" "%DESKTOP%\\Shortcuts\\" 2>nul\n')
            f.write('mkdir "%DOWNLOADS%\\Images" "%DOWNLOADS%\\Documents" "%DOWNLOADS%\\Videos" "%DOWNLOADS%\\Music" "%DOWNLOADS%\\Others" 2>nul\n')
            f.write('move /Y "%DOWNLOADS%\\*.jpg" "%DOWNLOADS%\\*.png" "%DOWNLOADS%\\*.gif" "%DOWNLOADS%\\Images\\" 2>nul\n')
            f.write('move /Y "%DOWNLOADS%\\*.doc" "%DOWNLOADS%\\*.docx" "%DOWNLOADS%\\*.pdf" "%DOWNLOADS%\\*.txt" "%DOWNLOADS%\\Documents\\" 2>nul\n')
            f.write('move /Y "%DOWNLOADS%\\*.mp4" "%DOWNLOADS%\\*.avi" "%DOWNLOADS%\\*.mkv" "%DOWNLOADS%\\Videos\\" 2>nul\n')
            f.write('move /Y "%DOWNLOADS%\\*.mp3" "%DOWNLOADS%\\*.wav" "%DOWNLOADS%\\*.flac" "%DOWNLOADS%\\Music\\" 2>nul\n')
            f.write('move /Y "%DOWNLOADS%\\*.*" "%DOWNLOADS%\\Others\\" 2>nul\n')
            f.write('echo [%time%] File organization completed.\n')

        # Windows update
        with open(os.path.join(modules_dir, "win_update.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Checking for Windows updates...\n')
            f.write('powershell -Command "Install-WindowsUpdate -AcceptAll -AutoReboot"\n')
            f.write('echo [%time%] Windows update check completed.\n')

        # Antivirus scan
        with open(os.path.join(modules_dir, "antivirus.bat"), 'w') as f:
            f.write('@echo off\n')
            f.write('echo [%time%] Starting Windows Defender quick scan...\n')
            f.write('if exist "%ProgramFiles%\\Windows Defender\\MpCmdRun.exe" (\n')
            f.write('    "%ProgramFiles%\\Windows Defender\\MpCmdRun.exe" -Scan -ScanType 1\n')
            f.write(') else (\n')
            f.write('    echo Windows Defender not found.\n')
            f.write(')\n')
            f.write('echo [%time%] Antivirus scan completed.\n')

    def log_message(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if not hasattr(self, 'tag_colors_defined'):
            self.log.tag_configure("info", foreground="#00FFCC")
            self.log.tag_configure("warning", foreground="#FFFF00")
            self.log.tag_configure("error", foreground="#FF5555")
            self.log.tag_configure("success", foreground="#55FF55")
            self.tag_colors_defined = True
        self.log.insert(tk.END, f"[{timestamp}] ", "info")
        self.log.insert(tk.END, f"{message}\n", level)
        self.log.see(tk.END)
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        self.update_idletasks()

    def _execute_chain(self):
        selected_modules = [(name, f"modules\\{name}.bat") for name, var in self.module_vars.items() if var.get()]
        if not selected_modules:
            self.log_message("⚠️ No modules selected. Please select at least one module.", "warning")
            self.execute_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            return

        self.progress["maximum"] = len(selected_modules) * 100
        self.progress["value"] = 0
        self.log_message("🧠 Starting Oblivion Repair Chain...", "info")

        estimated_times = {
            "temp_clean": 10, "disk_cleanup": 30, "disk_check": 300, "syscheck": 300,
            "net_repair": 30, "explorer_clean": 10, "pagefile_reset": 20,
            "power_plan": 5, "file_organize": 15, "win_update": 600, "antivirus": 120
        }

        total_estimated_seconds = sum(estimated_times.get(name, 60) for name, _ in selected_modules)
        mins, secs = divmod(total_estimated_seconds, 60)
        self.time_estimate.config(text=f"Est. Time: {mins}:{secs:02d}")

        start_time = time.time()
        for i, (name, script) in enumerate(selected_modules, 1):
            if not self.running:
                self.log_message("⚠️ Repair process stopped by user.", "warning")
                break

            module_name = name.replace("_", " ").title()
            self.status.config(text=f"🔄 {module_name}")
            self.log_message(f"▶️ Running: {module_name} ({script})", "info")

            if not os.path.exists(script):
                self.log_message(f"❌ ERROR: Script {script} not found.", "error")
                continue

            try:
                # Check disk type for disk_check module
                if name == "disk_check":
                    disk_type = subprocess.check_output(
                        'powershell -command "Get-PhysicalDisk | Where-Object {$_.DeviceId -eq 0} | Select-Object -ExpandProperty MediaType"',
                        universal_newlines=True
                    ).strip()
                    if disk_type == "SSD":
                        self.log_message("⚠️ C: is an SSD. Skipping disk check to avoid wear.", "warning")
                        self.progress["value"] = i * 100
                        continue

                process = subprocess.Popen(
                    script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    universal_newlines=True, bufsize=1
                )

                line_count = 0
                module_progress_base = (i - 1) * 100
                for line in iter(process.stdout.readline, ''):
                    if not self.running:
                        process.terminate()
                        break
                    line = line.strip()
                    if line:
                        self.log_message(f"  {line}")
                    line_count += 1
                    if line_count % 5 == 0:
                        module_progress = min(int(line_count / 2), 100)
                        self.progress["value"] = module_progress_base + module_progress
                        progress_percent = int((self.progress["value"] / self.progress["maximum"]) * 100)
                        self.progress_percent.config(text=f"{progress_percent}%")
                        elapsed = time.time() - start_time
                        if progress_percent > 0:
                            total_estimated = (elapsed / progress_percent) * 100
                            remaining = max(0, total_estimated - elapsed)
                            mins, secs = divmod(int(remaining), 60)
                            self.time_estimate.config(text=f"Est. Time: {mins}:{secs:02d}")

                process.wait(timeout=estimated_times.get(name, 60) * 2)
                self.progress["value"] = i * 100
                progress_percent = int((self.progress["value"] / self.progress["maximum"]) * 100)
                self.progress_percent.config(text=f"{progress_percent}%")

                if process.returncode == 0:
                    self.log_message(f"✅ {module_name} completed successfully.", "success")
                else:
                    self.log_message(f"⚠️ {module_name} completed with return code {process.returncode}.", "warning")

            except Exception as e:
                self.log_message(f"❌ ERROR in {module_name}: {str(e)}", "error")

        elapsed_time = time.time() - start_time
        mins, secs = divmod(int(elapsed_time), 60)

        if self.running:
            self.status.config(text="✅ Repair Complete")
            self.log_message(f"✅ All operations complete in {mins}m {secs}s.", "success")
            self.log_message("🔁 System optimized. A restart is recommended.", "info")
            self._show_final_tips()
            if messagebox.askyesno("Restart Recommended", "Repair complete. Restart now?"):
                self.log_message("🔄 Initiating system restart...", "info")
                try:
                    os.system('shutdown /r /t 10 /c "OPRYXX Repair complete - restarting system"')
                    self.log_message("⏱️ System will restart in 10 seconds.", "info")
                except Exception as e:
                    self.log_message(f"❌ Failed to initiate restart: {str(e)}", "error")
        else:
            self.status.config(text="⚠️ Repair Stopped")
            self.log_message(f"⚠️ Operations stopped after {mins}m {secs}s.", "warning")

        self.execute_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.running = False

    def _show_final_tips(self):
        tips = (
            "🛡️ Maintenance Tips:\n"
            "- Back up data to an external drive or cloud (e.g., Google Drive).\n"
            "- Update drivers via Device Manager or manufacturer's website.\n"
            "- Uninstall unnecessary programs via Control Panel.\n"
            "- Schedule this tool with Task Scheduler for regular maintenance:\n"
            "  Open Task Scheduler, create a task, set a trigger (e.g., weekly), and "
            "point the action to this script's executable."
        )
        messagebox.showinfo("Maintenance Tips", tips)
        self.log_message("📝 Final maintenance tips displayed.", "info")

if __name__ == "__main__":
    if platform.system() == 'Windows' and not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = OPRYXXRepairGUI()
        app.mainloop()