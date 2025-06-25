# OPRYXX_RepairGUI.py - Enhanced Transcendent Edition with PC Optimizer and Mem0 Integration
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import os
import sys
import time
import queue
import json
import shutil
from datetime import datetime
import logging
import psutil  # For system metrics
from opryxx_optimizer_tab import setup_optimizer_tab  # Import PC Optimizer tab

# Add the current directory to the path to allow local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Mem0 integration
try:
    from mem0_integration import get_mem0_client
except ImportError as e:
    print(f"Warning: Mem0 integration not available: {e}")
    get_mem0_client = None

class OPRYXXRepairGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🜏 OPRYXX Transcendent - BlackEcho Fusion")
        self.geometry("820x680")  # Expanded for more features
        self.configure(bg="#1e1e2f")
        self.resizable(False, False)
        
        # Configuration
        self.config_file = "opryxx_config.json"
        self.load_config()
        
        # Setup queues for thread-safe updates
        self.status_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.metrics_queue = queue.Queue()
        
        # Initialize Mem0 client if available
        self.mem0_client = None
        self._init_mem0()
        
        # Setup UI components
        self._setup_ui()
        
        # Start queue processing and system monitoring
        self.after(50, self._process_queue)
        self.after(1000, self._update_system_metrics)

    def _init_mem0(self):
        """Initialize Mem0 client if enabled in config"""
        if not get_mem0_client:
            self.log("Mem0 integration not available")
            return
            
        try:
            # Load config
            if hasattr(self, 'config') and 'mem0' in self.config:
                self.mem0_client = get_mem0_client(self.config['mem0'])
                if self.mem0_client and self.mem0_client.enabled:
                    self.log("Mem0 client initialized successfully")
                    # Add initial context
                    self._update_mem0_context("system", {"event": "application_started"})
        except Exception as e:
            self.log(f"Error initializing Mem0: {e}")
    
    def _update_mem0_context(self, context_type: str, data: dict):
        """Update Mem0 context with current application state"""
        if not self.mem0_client or not self.mem0_client.enabled:
            return
            
        try:
            timestamp = datetime.utcnow().isoformat()
            context = {
                "type": context_type,
                "timestamp": timestamp,
                "data": data
            }
            
            # Store in knowledge base
            self.mem0_client.store_knowledge(
                f"context_{context_type}_{int(time.time())}",
                context,
                {"type": context_type, "timestamp": timestamp}
            )
            
            # Also add to conversation history if it's a user interaction
            if context_type == "user_interaction":
                self.mem0_client.add_conversation_turn(
                    role="user",
                    content=data.get("message", ""),
                    metadata={"context": context_type, "timestamp": timestamp}
                )
                
        except Exception as e:
            self.log(f"Error updating Mem0 context: {e}")
    
    def get_context_aware_response(self, query: str) -> str:
        """Get a context-aware response using Mem0"""
        if not self.mem0_client or not self.mem0_client.enabled:
            return "Mem0 integration is not available"
            
        try:
            # Add user query to conversation history
            self.mem0_client.add_conversation_turn(
                role="user",
                content=query,
                metadata={"context": "user_query"}
            )
            
            # Get relevant context
            context = self.mem0_client.get_context()
            
            # In a real implementation, you would send this to an AI model
            # For now, we'll just return the context
            return f"Context for '{query}':\n{context}"
            
        except Exception as e:
            self.log(f"Error getting context-aware response: {e}")
            return "Error processing your request"
    
    def log(self, message: str, level: str = "info"):
        """Log a message to both the GUI and Mem0 if available"""
        # Log to GUI
        if level.lower() == "error":
            logging.error(message)
        elif level.lower() == "warning":
            logging.warning(message)
        else:
            logging.info(message)
            
        # Update Mem0 context if it's an important event
        if level.lower() in ["error", "warning"] and self.mem0_client and self.mem0_client.enabled:
            self._update_mem0_context(
                "system_event",
                {"level": level.upper(), "message": message}
            )
    
    def load_config(self):
        """Load configuration or create default if not exists"""
        default_config = {
            "modules_dir": "modules",
            "logs_dir": "logs\\oblivion",
            "backup_dir": os.path.join(os.environ.get("USERPROFILE", ""), "OpryxxBackups"),
            "modules": [
                {"name": "Temp + Cache Purge", "script": "temp_clean.bat", "enabled": True},
                {"name": "SFC + DISM", "script": "syscheck.bat", "enabled": True},
                {"name": "Network Repair", "script": "net_repair.bat", "enabled": True},
                {"name": "Explorer Cache", "script": "explorer_clean.bat", "enabled": True},
                {"name": "Memory/Pagefile", "script": "pagefile_reset.bat", "enabled": True},
                {"name": "File Sorter/Renamer", "script": "file_sorter_rename.bat", "enabled": True},
                {"name": "Deep Analysis", "script": "deep_analysis.bat", "enabled": False}
            ],
            "theme": "dark",
            "enable_safe_mode": False,
            "enable_chkdsk": False,
            "auto_backup": True,
            "symbolic_mode": False, # Added symbolic mode setting
             "directive_base_dir": "C:\\PRIME_DIRECTIVE_250516" # Added directive base dir
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self._save_config()
                
            # Ensure directories exist
            os.makedirs(self.config.get("modules_dir", "modules"), exist_ok=True)
            os.makedirs(self.config.get("logs_dir", "logs\\oblivion"), exist_ok=True)
            os.makedirs(self.config.get("backup_dir", os.path.join(os.environ.get("USERPROFILE", ""), "OpryxxBackups")), exist_ok=True)
             # Ensure directive base directory exists
            os.makedirs(self.config.get("directive_base_dir", "C:\\PRIME_DIRECTIVE_250516"), exist_ok=True)
                
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Error loading configuration: {str(e)}")
            self.config = default_config

    def _save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self._update_log(f"[ERROR] Failed to save configuration: {str(e)}\n")

    def _setup_ui(self):
        """Create the enhanced UI with tabs and more controls"""
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main repair tab
        self.repair_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.repair_tab, text="Repair Chain")
        
        # Modules tab
        self.modules_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.modules_tab, text="Modules")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # System metrics tab
        self.metrics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.metrics_tab, text="System Metrics")

        # Legal Intelligence tab (Placeholder)
        self.legal_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.legal_tab, text="Legal Intelligence")
        self._setup_legal_tab()

        # PC Optimizer tab
        self.optimizer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.optimizer_tab, text="💻 PC Optimizer")
        self._setup_optimizer_tab()

        # Setup each tab
        self._setup_repair_tab()
        self._setup_modules_tab()
        self._setup_settings_tab()
        self._setup_metrics_tab()

    def _setup_repair_tab(self):
        """Setup the main repair tab"""
        tk.Label(self.repair_tab, text="OPRYXX: Oblivion Repair Chain",
                 font=("Consolas", 18, "bold"), bg="#1e1e2f", fg="#e0e0e0").pack(pady=10)
        
        # Status indicator
        status_frame = tk.Frame(self.repair_tab, bg="#1e1e2f")
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="Status:", font=("Consolas", 12),
                 bg="#1e1e2f", fg="#e0e0e0").pack(side=tk.LEFT, padx=10)
        
        self.status = tk.Label(status_frame, text="Idle", font=("Consolas", 12),
                              bg="#1e1e2f", fg="#98fb98")
        self.status.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.repair_tab, orient="horizontal",
                                      length=700, mode="determinate")
        self.progress.pack(pady=10, padx=10, fill=tk.X)
        
        # Log area with search capability
        log_frame = tk.Frame(self.repair_tab, bg="#1e1e2f")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Search bar
        search_frame = tk.Frame(log_frame, bg="#1e1e2f")
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:", bg="#1e1e2f", fg="#e0e0e0").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Find", command=self._search_log).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Clear", command=self._clear_search).pack(side=tk.LEFT, padx=5)
        
        # Log text area
        self.log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=85, height=20,
                                          font=("Consolas", 10), bg="#121212", fg="#00FFCC",
                                          insertbackground="white")
        self.log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.repair_tab, bg="#1e1e2f")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.run_button = tk.Button(button_frame, text="🌀 Execute Repair Chain",
                                  font=("Consolas", 12), bg="#282c34", fg="white",
                                  command=self._run_repair)
        self.run_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="⏹ Stop", font=("Consolas", 12),
                                   bg="#8B0000", fg="white", state=tk.DISABLED,
                                   command=self._stop_repair)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.save_log_button = tk.Button(button_frame, text="💾 Save Log",
                                       font=("Consolas", 12), bg="#282c34", fg="white",
                                       command=self._save_log)
        self.save_log_button.pack(side=tk.RIGHT, padx=10)

    def _setup_modules_tab(self):
        """Setup the modules configuration tab"""
        tk.Label(self.modules_tab, text="Configure Repair Modules",
                 font=("Consolas", 14, "bold")).pack(pady=10)
        
        # Create a frame for the module list
        modules_frame = tk.Frame(self.modules_tab)
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable canvas for modules
        canvas = tk.Canvas(modules_frame)
        scrollbar = ttk.Scrollbar(modules_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add module entries
        self.module_vars = []
        for i, module in enumerate(self.config["modules"]):
            var = tk.BooleanVar(value=module["enabled"])
            self.module_vars.append(var)
            
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Checkbutton(frame, text="", variable=var,
                         command=self._update_module_status).grid(row=0, column=0)
            
            tk.Label(frame, text=self._get_module_display_name(module), width=30, anchor="w").grid(row=0, column=1, padx=5) # Increased width
            tk.Label(frame, text=module["script"], width=30, anchor="w").grid(row=0, column=2, padx=5)
            
            edit_btn = tk.Button(frame, text="Edit",
                               command=lambda idx=i: self._edit_module(idx))
            edit_btn.grid(row=0, column=3, padx=5)
            
            test_btn = tk.Button(frame, text="Test",
                               command=lambda idx=i: self._test_module(idx))
            test_btn.grid(row=0, column=4, padx=5)
        
        # Buttons for module management
        btn_frame = tk.Frame(self.modules_tab)
        btn_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Button(btn_frame, text="Add Module",
                command=self._add_module).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Reorder Modules",
                command=self._reorder_modules).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Reset to Default",
                command=self._reset_modules).pack(side=tk.RIGHT, padx=5)

    def _setup_settings_tab(self):
        """Setup the settings configuration tab"""
        tk.Label(self.settings_tab, text="OPRYXX Settings",
                 font=("Consolas", 14, "bold")).pack(pady=10)
        
        # Directory settings
        dir_frame = tk.LabelFrame(self.settings_tab, text="Directories")
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Modules directory
        tk.Label(dir_frame, text="Modules Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.modules_dir_var = tk.StringVar(value=self.config.get("modules_dir", "modules")) # Use .get with default
        tk.Entry(dir_frame, textvariable=self.modules_dir_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(dir_frame, text="Browse",
                command=lambda: self._browse_directory("modules_dir_var")).grid(row=0, column=2, padx=5, pady=5)
        
        # Logs directory
        tk.Label(dir_frame, text="Logs Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.logs_dir_var = tk.StringVar(value=self.config.get("logs_dir", "logs\\oblivion")) # Use .get with default
        tk.Entry(dir_frame, textvariable=self.logs_dir_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(dir_frame, text="Browse",
                command=lambda: self._browse_directory("logs_dir_var")).grid(row=1, column=2, padx=5, pady=5)
        
        # Backup directory
        tk.Label(dir_frame, text="Backup Directory:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.backup_dir_var = tk.StringVar(value=self.config.get("backup_dir", os.path.join(os.environ.get("USERPROFILE", ""), "OpryxxBackups"))) # Use .get with default
        tk.Entry(dir_frame, textvariable=self.backup_dir_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(dir_frame, text="Browse",
                command=lambda: self._browse_directory("backup_dir_var")).grid(row=2, column=2, padx=5, pady=5)

        # Directive Base Directory
        tk.Label(dir_frame, text="Directive Base Dir:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.directive_base_dir_var = tk.StringVar(value=self.config.get("directive_base_dir", "C:\\PRIME_DIRECTIVE_250516")) # Use .get with default
        tk.Entry(dir_frame, textvariable=self.directive_base_dir_var, width=40).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(dir_frame, text="Browse",
                command=lambda: self._browse_directory("directive_base_dir_var")).grid(row=3, column=2, padx=5, pady=5)


        # Operation settings
        op_frame = tk.LabelFrame(self.settings_tab, text="Operation Settings")
        op_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Theme selection
        tk.Label(op_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.config.get("theme", "dark")) # Use .get with default
        theme_menu = tk.OptionMenu(op_frame, self.theme_var, "dark", "light", "system")
        theme_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Safe Mode checkbox
        self.safe_mode_var = tk.BooleanVar(value=self.config.get("enable_safe_mode", False)) # Use .get with default
        tk.Checkbutton(op_frame, text="Enable Safe Mode Reboot",
                     variable=self.safe_mode_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # CHKDSK checkbox
        self.chkdsk_var = tk.BooleanVar(value=self.config.get("enable_chkdsk", False)) # Use .get with default
        tk.Checkbutton(op_frame, text="Run CHKDSK on Reboot",
                     variable=self.chkdsk_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Auto backup checkbox
        self.backup_var = tk.BooleanVar(value=self.config.get("auto_backup", True)) # Use .get with default
        tk.Checkbutton(op_frame, text="Create Automatic Backups",
                     variable=self.backup_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

         # Symbolic Mode checkbox
        self.symbolic_mode_var = tk.BooleanVar(value=self.config.get("symbolic_mode", False)) # Use .get with default
        tk.Checkbutton(op_frame, text="Enable Symbolic Mode",
                     variable=self.symbolic_mode_var, command=self._toggle_symbolic_mode).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)


        # Save settings button
        tk.Button(self.settings_tab, text="Save Settings",
                command=self._save_settings).pack(pady=10)

    def _setup_metrics_tab(self):
        """Setup the system metrics monitoring tab"""
        tk.Label(self.metrics_tab, text="System Metrics",
                 font=("Consolas", 14, "bold")).pack(pady=10)
        
        # Create frames for different metric categories
        cpu_frame = tk.LabelFrame(self.metrics_tab, text="CPU")
        cpu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        memory_frame = tk.LabelFrame(self.metrics_tab, text="Memory")
        memory_frame.pack(fill=tk.X, padx=10, pady=5)
        
        disk_frame = tk.LabelFrame(self.metrics_tab, text="Disk")
        disk_frame.pack(fill=tk.X, padx=10, pady=5)
        
        network_frame = tk.LabelFrame(self.metrics_tab, text="Network")
        network_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # CPU metrics
        tk.Label(cpu_frame, text="CPU Usage:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cpu_usage = tk.Label(cpu_frame, text="0%")
        self.cpu_usage.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(cpu_frame, text="CPU Temperature:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cpu_temp = tk.Label(cpu_frame, text="N/A")
        self.cpu_temp.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Memory metrics
        tk.Label(memory_frame, text="Memory Usage:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mem_usage = tk.Label(memory_frame, text="0%")
        self.mem_usage.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(memory_frame, text="Available Memory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mem_avail = tk.Label(memory_frame, text="0 GB")
        self.mem_avail.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Disk metrics
        tk.Label(disk_frame, text="Disk Usage (C:):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.disk_usage = tk.Label(disk_frame, text="0%")
        self.disk_usage.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(disk_frame, text="Free Space:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.disk_free = tk.Label(disk_frame, text="0 GB")
        self.disk_free.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Network metrics
        tk.Label(network_frame, text="Network Send:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.net_send = tk.Label(network_frame, text="0 KB/s")
        self.net_send.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(network_frame, text="Network Receive:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.net_recv = tk.Label(network_frame, text="0 KB/s")
        self.net_recv.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Refresh button
        tk.Button(self.metrics_tab, text="Refresh Metrics",
                command=self._refresh_metrics).pack(pady=10)

    def _setup_legal_tab(self):
        """Setup the legal intelligence tab - Placeholder for future development"""
        legal_label = tk.Label(self.legal_tab, text="Legal Intelligence - Coming Soon",
                             font=("Consolas", 14, "bold"), bg="#1e1e2f", fg="#e0e0e0")
        legal_label.pack(pady=20)
        
        legal_desc = tk.Label(self.legal_tab, text="This tab will provide legal insights and analysis functionality.",
                             font=("Consolas", 10), bg="#1e1e2f", fg="#a0a0a0", wraplength=600)
        legal_desc.pack(pady=10)
        
    def _setup_optimizer_tab(self):
        """Setup the PC Optimizer tab - integrates the comprehensive system optimization tool"""
        self.optimizer_tab, self.optimizer, self.optimizer_widgets = setup_optimizer_tab(
            self, 
            self.notebook, 
            self.status_queue, 
            self.log_queue, 
            self.progress_queue,
            self.metrics_queue
        )

    def _process_queue(self):
        """Process messages from queues"""
        try:
            # Process status updates
            while not self.status_queue.empty():
                status = self.status_queue.get_nowait()
                self.status.config(text=status)
                # Update Mem0 with important status changes
                if any(keyword in status.lower() for keyword in ["error", "warning", "complete", "started"]):
                    self._update_mem0_context(
                        "system_status",
                        {"status": status, "timestamp": datetime.utcnow().isoformat()}
                    )
                self.status_queue.task_done()
                
            # Process log messages
            while not self.log_queue.empty():
                log_msg = self.log_queue.get_nowait()
                self.log.insert(tk.END, log_msg)
                self.log.see(tk.END)
                
                # Log important events to Mem0
                if any(keyword in log_msg.lower() for keyword in ["error", "warning", "exception"]):
                    self._update_mem0_context(
                        "system_log",
                        {"message": log_msg.strip(), "level": "ERROR" if "error" in log_msg.lower() else "WARNING"}
                    )
                    
                self.log_queue.task_done()
                
            # Process progress updates
            while not self.progress_queue.empty():
                progress = self.progress_queue.get_nowait()
                self.progress["value"] = progress
                # Update Mem0 with progress for long-running tasks
                if isinstance(progress, (int, float)) and (progress % 10 == 0 or progress >= 100):
                    self._update_mem0_context(
                        "task_progress",
                        {"progress": progress, "timestamp": datetime.utcnow().isoformat()}
                    )
                self.progress_queue.task_done()
                
            # Process metrics updates
            while not self.metrics_queue.empty():
                metrics = self.metrics_queue.get_nowait()
                self._update_metric_displays(metrics)
                # Periodically update Mem0 with system metrics
                if time.time() % 300 < 0.1:  # Every ~5 minutes
                    self._update_mem0_context(
                        "system_metrics",
                        {
                            "cpu_percent": metrics.get("cpu_percent", 0),
                            "memory_percent": metrics.get("mem_percent", 0),
                            "disk_percent": metrics.get("disk_percent", 0),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                self.metrics_queue.task_done()
                
        except Exception as e:
            error_msg = f"Error processing queue: {e}"
            # print(f"Error processing queue: {e}") # Avoid printing in background thread
            if self.mem0_client and self.mem0_client.enabled:
                self._update_mem0_context(
                    "error",
                    {"message": error_msg, "type": "queue_processing"}
                )
            
        # Schedule the next check
        self.after(100, self._process_queue)

    def _update_status(self, text):
        """Thread-safe status update"""
        self.status_queue.put(text)

{{ ... }}
    def _update_log(self, text):
        """Thread-safe log update"""
        self.log_queue.put(text)

    def _update_progress(self, value):
        """Thread-safe progress update"""
        self.progress_queue.put(value)

    def _update_system_metrics(self):
        """Update system metrics in the background"""
        try:
            # Get CPU metrics
            cpu_percent = psutil.cpu_percent()
            
            # Get memory metrics
            memory = psutil.virtual_memory()
            mem_percent = memory.percent
            mem_avail = memory.available / (1024 * 1024 * 1024)  # Convert to GB
            
            # Get disk metrics
            disk = psutil.disk_usage('C:\\')
            disk_percent = disk.percent
            disk_free = disk.free / (1024 * 1024 * 1024)  # Convert to GB
            
            # Get network metrics (simple approximation)
            net_io_counters = psutil.net_io_counters()
            # Calculate speed based on change over time (requires storing previous values)
            # For simplicity, just report total for now
            net_sent = net_io_counters.bytes_sent / 1024  # Convert to KB
            net_recv = net_io_counters.bytes_recv / 1024  # Convert to KB
            
            # Package metrics
            metrics = {
                'cpu_percent': cpu_percent,
                'cpu_temp': 'N/A',  # CPU temperature requires additional libraries and permissions
                'mem_percent': mem_percent,
                'mem_avail': mem_avail,
                'disk_percent': disk_percent,
                'disk_free': disk_free,
                'net_sent': net_sent,
                'net_recv': net_recv
            }
            
            # Update metrics display
            self.metrics_queue.put(metrics)
            
        except Exception as e:
            # print(f"Error updating metrics: {str(e)}") # Avoid printing in background thread
            pass # Suppress errors for now
        
        # Schedule next update
        self.after(2000, self._update_system_metrics)

    def _update_metric_displays(self, metrics):
        """Update the metric displays with new values"""
        self.cpu_usage.config(text=f"{metrics['cpu_percent']:.1f}%")
        self.cpu_temp.config(text=metrics['cpu_temp'])
        self.mem_usage.config(text=f"{metrics['mem_percent']:.1f}%")
        self.mem_avail.config(text=f"{metrics['mem_avail']:.2f} GB")
        self.disk_usage.config(text=f"{metrics['disk_percent']:.1f}%")
        self.disk_free.config(text=f"{metrics['disk_free']:.2f} GB")
        # Display KB/s or MB/s based on magnitude
        self.net_send.config(text=f"{metrics['net_sent']:.2f} KB") # Display total for simplicity
        self.net_recv.config(text=f"{metrics['net_recv']:.2f} KB") # Display total for simplicity


    def _run_repair(self):
        """Start the repair chain in a separate thread"""
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log.delete('1.0', tk.END)
        self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧠 Starting Oblivion Repair Chain...\n")
        self._update_progress(0)
        
        # Create backup if enabled
        if self.config.get("auto_backup", True): # Use .get with default
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📦 Creating system backup...\n")
            backup_thread = threading.Thread(target=self._create_backup, daemon=True)
            backup_thread.start()
        
        # Start repair thread
        self.repair_thread = threading.Thread(target=self._execute_chain, daemon=True)
        self.repair_thread.start()

    def _stop_repair(self):
        """Stop the currently running repair chain"""
        self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ User requested stop. Terminating processes...\n")
        # Set a flag to stop the thread
        self.stop_requested = True
        self.stop_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.NORMAL)

    def _create_backup(self):
        """Create a backup of important system files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.config.get("backup_dir", os.path.join(os.environ.get("USERPROFILE", ""), "OpryxxBackups")), f"backup_{timestamp}") # Use .get with default
            os.makedirs(backup_dir, exist_ok=True)
            
            # Example backup items (customize as needed)
            backup_items = [
                (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32", "config", "system"), "system_registry"), # Use .get with default
                (os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Recent"), "recent_files"), # Use .get with default
                (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Windows\\Explorer"), "explorer_settings") # Use .get with default
            ]
            
            for src, dest_name in backup_items:
                dest = os.path.join(backup_dir, dest_name)
                if os.path.exists(src):
                    if os.path.isdir(src):
                        # Create a sample of the directory (not a full copy)
                        os.makedirs(dest, exist_ok=True)
                        # Copy a few files as samples
                        try:
                            items_to_copy = [item for item in os.listdir(src) if os.path.isfile(os.path.join(src, item))]
                            for i, item in enumerate(items_to_copy):
                                if i >= 5:  # Limit to 5 items per directory
                                    break
                                src_item = os.path.join(src, item)
                                shutil.copy2(src_item, dest)
                        except Exception as copy_e:
                             self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to sample backup directory {src}: {str(copy_e)}\n")

                    else:
                        # Copy the file
                        try:
                            shutil.copy2(src, dest)
                        except PermissionError:
                            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Permission denied when backing up {src}\n")
                        except Exception as copy_e:
                             self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to backup file {src}: {str(copy_e)}\n")

            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Backup created at {backup_dir}\n")
        except Exception as e:
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Backup failed: {str(e)}\n")

    def _execute_chain(self):
        """Execute the repair chain modules"""
        # Reset stop flag
        self.stop_requested = False
        
        # Get enabled modules
        enabled_modules = []
        for i, module in enumerate(self.config["modules"]):
            if module.get("enabled", True): # Use .get with default
                script_path = os.path.join(self.config.get("modules_dir", "modules"), module.get("script", "")) # Use .get with default
                if os.path.exists(script_path):
                     enabled_modules.append((module.get("name", "Unnamed Module"), script_path)) # Use .get with default
                else:
                     self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Skipping disabled or missing module: {module.get('name', 'Unnamed Module')} ({module.get('script', 'N/A')})\n")


        if not enabled_modules:
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ No modules enabled or found. Please enable/add at least one module.\n")
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return
        
        self.progress["maximum"] = len(enabled_modules)
        
        # Create log directory if it doesn't exist - now within the Directive structure
        directive_logs_dir = os.path.join(self.config.get("directive_base_dir", "C:\\PRIME_DIRECTIVE_250516"), "25. COURT REACTIONS + CLERK ACTIVITY MAPS")
        os.makedirs(directive_logs_dir, exist_ok=True)

        # Create a log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(directive_logs_dir, f"opryxx_repair_log_{timestamp}.log")

        # Setup file logger
        file_logger = logging.getLogger("opryxx_repair")
        # Prevent adding multiple handlers if execute_chain is called again
        if file_logger.hasHandlers():
             file_logger.handlers.clear()
        file_logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        file_logger.addHandler(file_handler)

        self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📝 Logging to {log_file}\n")

        # Run each module
        for i, (name, script) in enumerate(enabled_modules, 1):
            if self.stop_requested:
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⛔ Repair chain stopped by user.\n")
                file_logger.info("Repair chain stopped by user.")
                break
                
            display_name = self._get_module_display_name({"name": name}) # Get symbolic name if enabled
            self._update_status(f"🔄 {display_name}")
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Running: {display_name} ({script})...\n")
            file_logger.info(f"Running module: {name} ({script})")
            
            try:
                # Check if script exists again, just in case
                if not os.path.exists(script):
                    self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Script not found at {script}\n")
                    file_logger.error(f"Script not found at {script}")
                    continue
                
                process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                # Stream the output
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if self.stop_requested:
                        try:
                            process.terminate()
                        except OSError: # Process might already be terminated
                            pass
                        break
                        
                    if line.startswith("[OPRYXX_STATUS]"):
                        self._update_status(self._get_symbolic_status(line.replace("[OPRYXX_STATUS]", "").strip())) # Apply symbolic status
                    else:
                        self._update_log(line + "\n")
                    file_logger.info(f"SCRIPT_OUTPUT: {line}") # Log script output separately
                
                if self.stop_requested:
                     self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏹ Module {name} terminated.\n")
                     file_logger.warning(f"Module {name} terminated by user.")
                else:
                    process.wait() # Wait for the process to finish naturally

                    if process.returncode != 0:
                         self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Script {script} exited with code {process.returncode}\n")
                         file_logger.error(f"Script {script} exited with code {process.returncode}")
                    else:
                         self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Script {script} finished successfully.\n")
                         file_logger.info(f"Script {script} finished successfully")
            except Exception as e:
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERROR during {name}: {str(e)}\n")
                file_logger.error(f"ERROR during {name}: {str(e)}")
            
            self._update_progress(i)
        
        # Handle safe mode reboot if enabled
        if not self.stop_requested and self.config.get("enable_safe_mode", False): # Use .get with default
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔁 Preparing for Safe Mode reboot...\n")
            file_logger.info("Preparing for Safe Mode reboot")
            
            try:
                # Schedule CHKDSK if enabled
                if self.config.get("enable_chkdsk", False): # Use .get with default
                    self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Scheduling CHKDSK on C: drive...\n")
                    # Note: Running chkdsk /f /r /x requires elevation and can block boot.
                    # A safer approach for scheduling is 'schtasks' or a registry key.
                    # This command attempts to schedule on next boot if drive is in use.
                    subprocess.run("echo Y | chkdsk C: /F /R /X", shell=True, check=True, capture_output=True, text=True) # Added capture_output
                    self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CHKDSK scheduling command output: {result.stdout.strip()}\n") # Log output


                # Enable safe mode
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔒 Enabling Safe Mode for next boot...\n")
                # Note: bcdedit requires elevation.
                result = subprocess.run("bcdedit /set {current} safeboot minimal", shell=True, check=True, capture_output=True, text=True) # Added capture_output
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BCDEDIT command output: {result.stdout.strip()}\n") # Log output

                # Schedule reboot
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Scheduling reboot in 60 seconds...\n")
                subprocess.Popen("shutdown /r /t 60", shell=True)
                
                messagebox.showinfo("Reboot Scheduled",
                                   "Your computer will reboot in Safe Mode in 60 seconds.\n\nTo cancel, run 'shutdown /a' in Command Prompt.", parent=self) # Added parent
            except Exception as e:
                self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to schedule reboot: {str(e)}\n")
                file_logger.error(f"Failed to schedule reboot: {str(e)}")
        
        # Clean up and finalize
        file_logger.removeHandler(file_handler)
        file_handler.close()
        
        self._update_status("✅ Repair Complete" if not self.stop_requested else "⚠️ Repair Stopped")
        self._update_log(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ All operations complete.\n")
        
        # Create a BlackEcho index entry
        self._create_blackecho_index(log_file)

        # Trigger Mem0 Bridge (Conceptual)
        self._trigger_mem0_bridge(log_file)

        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def _create_blackecho_index(self, log_file):
        """Create an entry in the BlackEcho index file, now within Directive structure"""
        try:
            index_file = os.path.join(self.config.get("directive_base_dir", "C:\\PRIME_DIRECTIVE_250516"), "1. MEMORY SYSTEM PRIMING & STRATEGIC INTRODUCTION", "1.2. Forensic Context & Multilayer Strategic Summary", "blackecho_index.md") # Location within Directive structure
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create index file if it doesn't exist
            if not os.path.exists(os.path.dirname(index_file)): # Ensure directory exists
                 os.makedirs(os.path.dirname(index_file), exist_ok=True)

            if not os.path.exists(index_file):
                with open(index_file, 'w') as f:
                    f.write("# OPRYXX BlackEcho Index\n\n")
                    f.write("| Timestamp | Event Type | Status | Log File | Notes |\n")
                    f.write("|-----------|------------|--------|----------|-------|\n")
            
            # Add entry
            with open(index_file, 'a') as f:
                log_name = os.path.basename(log_file)
                # Use relative path to log file if within the same base directory
                try:
                    relative_log_path = os.path.relpath(log_file, os.path.dirname(index_file))
                except ValueError: # Handles cases on different drives
                     relative_log_path = log_file

                f.write(f"| {timestamp} | REPAIR | {'COMPLETED' if not getattr(self, 'stop_requested', False) else 'STOPPED'} | [{log_name}]({relative_log_path.replace(os.sep, '/')}) | Transcendent Edition |\n") # Use forward slashes for markdown links
            
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📝 BlackEcho index updated.\n")
        except Exception as e:
            self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to update BlackEcho index: {str(e)}\n")

    def _trigger_mem0_bridge(self, log_file):
        """Conceptual: Trigger sending log summary to Mem0"""
        # This is a placeholder. Actual implementation would involve:
        # 1. Summarizing the log file (e.g., using Nemotron/DeepSeek Coder)
        # 2. Formatting the summary and metadata (timestamp, status, module hashes)
        # 3. Sending the data to the Mem0 system via its API or a designated method
        
        self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌉 Triggering Mem0 Bridge (Conceptual)... Sending summary for {os.path.basename(log_file)}...\n")
        # Example: Call an external script or function that handles the Mem0 interaction
        # try:
        #     subprocess.Popen(["python", "mem0_bridge.py", log_file], shell=True)
        # except Exception as e:
        #     self._update_log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to trigger Mem0 bridge: {str(e)}\n")


    def _search_log(self):
        """Search for text in the log area"""
        search_text = self.search_entry.get()
        if not search_text:
            return
            
        # Remove any existing tags
        self.log.tag_remove("search", "1.0", tk.END)
        
        # Search and tag
        start_pos = "1.0"
        while True:
            start_pos = self.log.search(search_text, start_pos, tk.END, nocase=1) # Added nocase for case-insensitive search
            if not start_pos:
                break
                
            end_pos = f"{start_pos}+{len(search_text)}c"
            self.log.tag_add("search", start_pos, end_pos)
            start_pos = end_pos
        
        # Configure the tag
        self.log.tag_config("search", background="yellow", foreground="black")

    def _clear_search(self):
        """Clear search highlighting"""
        self.log.tag_remove("search", "1.0", tk.END)
        self.search_entry.delete(0, tk.END)

    def _save_log(self):
        """Save the current log content to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.config.get("logs_dir", "logs\\oblivion"), # Use .get with default
            parent=self # Added parent
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Log saved to {file_path}", parent=self) # Added parent
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}", parent=self) # Added parent

    def _toggle_symbolic_mode(self):
        """Toggle symbolic mode and update module names"""
        self.config["symbolic_mode"] = self.symbolic_mode_var.get()
        self._save_config()
        self._refresh_modules_tab_display() # Refresh the modules tab to show changes

    def _get_module_display_name(self, module):
        """Get module name based on symbolic mode"""
        if self.config.get("symbolic_mode", False): # Use .get with default
            # Define symbolic names (expand as needed)
            symbolic_names = {
                "Temp + Cache Purge": "Ashfall Protocol",
                "SFC + DISM": "Veritas Integrity Scan",
                "Network Repair": "Nexus Sync Alignment",
                "Explorer Cache": "Vision Cache Scouring",
                "Memory/Pagefile": "Cognitive Core Resync",
                "File Sorter/Renamer": "Archival Reclassification",
                "Deep Analysis": "Chronos Deep Dive",
                "BRAINS Processor": "Neural Matrix Ingestion",
                "Nemotron Analyzer": "Semantic Resonance Analysis",
                "DeepSeek Generator": "Codex Generation Engine",
                "PRIME DIRECTIVE Folder Structure": "Macrostructure Genesis"
            }
            return symbolic_names.get(module.get("name", "Unnamed Module"), module.get("name", "Unnamed Module")) # Use .get with default
        else:
            return module.get("name", "Unnamed Module") # Use .get with default

    def _get_symbolic_status(self, status_text):
        """Get symbolic status based on symbolic mode"""
        if self.config.get("symbolic_mode", False): # Use .get with default
             symbolic_statuses = {
                 "Running custom module...": "Initiating Oracle...",
                 "Custom module completed.": "Oracle Manifested.",
                 "Purging temporary files...": "Cleansing Aetheric Residue...",
                 "Temp + Cache Purge Complete.": "Aetheric Purified.",
                 "Running SFC and DISM system checks...": "Initiating Veritas Protocols...",
                 "SFC + DISM Complete.": "Veritas Integrity Restored.",
                 "Resetting network stack...": "Aligning Nexus Channels...",
                 "Network Repair Complete.": "Nexus Channels Aligned.",
                 "Cleaning Explorer cache...": "Scouring Vision Residue...",
                 "Explorer Cleanup Complete.": "Vision Scoured.",
                 "Resetting memory/pagefile settings...": "Resyncing Cognitive Core...",
                 "Memory/Pagefile Reset Complete.": "Cognitive Core Synced.",
                 "Starting File Sorting and Renaming...": "Commencing Archival Reclassification...",
                 "File Sorting and Renaming Complete.": "Archival Reclassified.",
                 "Starting Deep System Analysis...": "Initiating Chronos Deep Dive...",
                 "Deep System Analysis Complete.": "Chronos Deep Dive Completed.",
                 "Processing BRAINS directory...": "Ingesting Neural Matrix...",
                 "BRAINS Processing Complete.": "Neural Matrix Ingested.",
                 "Running Nemotron Semantic Analysis...": "Initiating Semantic Resonance...",
                 "Nemotron Analysis Complete.": "Semantic Resonance Achieved.",
                 "Running DeepSeek Coder Generation...": "Commencing Codex Genesis...",
                 "DeepSeek Generation Complete.": "Codex Generated.",
                 "Creating PRIME DIRECTIVE Folder Structure...": "Manifesting Macrostructure...",
                 "Folder Structure Creation Complete.": "Macrostructure Genesis Complete."

             }
             return symbolic_statuses.get(status_text, status_text)
        else:
            return status_text


    def _refresh_modules_tab_display(self):
        """Refresh the display of the modules tab"""
        # Clear existing display
        for widget in self.modules_tab.winfo_children():
            widget.destroy()
        # Re-setup the tab
        self._setup_modules_tab()


    def _update_module_status(self):
        """Update the enabled status of modules based on checkboxes"""
        for i, var in enumerate(self.module_vars):
            self.config["modules"][i]["enabled"] = var.get()
        self._save_config()

    def _edit_module(self, idx):
        """Open a dialog to edit the selected module"""
        module = self.config["modules"][idx]
        
        # Create a dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Module: {self._get_module_display_name(module)}") # Use display name
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Module fields
        tk.Label(dialog, text="Module Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_var = tk.StringVar(value=module.get("name", "")) # Use .get
        tk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Script File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        script_var = tk.StringVar(value=module.get("script", "")) # Use .get
        script_entry = tk.Entry(dialog, textvariable=script_var, width=40)
        script_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Button(dialog, text="Browse",
                command=lambda: self._browse_script(script_var)).grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(dialog, text="Enabled:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        enabled_var = tk.BooleanVar(value=module.get("enabled", True)) # Use .get
        tk.Checkbutton(dialog, variable=enabled_var).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Script content editor
        tk.Label(dialog, text="Script Content:").grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        
        script_content = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=50, height=15)
        script_content.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        
        # Load script content if it exists
        script_path = os.path.join(self.config.get("modules_dir", "modules"), module.get("script", "")) # Use .get
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r') as f:
                    script_content.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read script: {str(e)}", parent=dialog) # Added parent
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Save", command=lambda: self._save_module_edit(
            idx, name_var.get(), script_var.get(), enabled_var.get(), script_content.get("1.0", tk.END), dialog
        )).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _browse_script(self, var):
        """Browse for a script file"""
        initial_dir = self.config.get("modules_dir", "modules") # Use .get
        if not os.path.exists(initial_dir):
             initial_dir = "." # Fallback to current directory

        file_path = filedialog.askopenfilename(
            filetypes=[("Batch files", "*.bat"), ("Python files", "*.py"), ("All files", "*.*")],
            initialdir=initial_dir,
            parent=self # Added parent
        )
        
        if file_path:
            # Get just the filename if it's in the modules directory
            modules_abs_dir = os.path.abspath(self.config.get("modules_dir", "modules")) # Use .get
            if os.path.dirname(os.path.abspath(file_path)) == modules_abs_dir:
                var.set(os.path.basename(file_path))
            else:
                # Ask if the user wants to copy the file to the modules directory
                if messagebox.askyesno("Copy File",
                                     f"Copy {os.path.basename(file_path)} to the modules directory?", parent=self): # Added parent
                    try:
                        dest_path = os.path.join(self.config.get("modules_dir", "modules"), os.path.basename(file_path)) # Use .get
                        shutil.copy2(file_path, dest_path)
                        var.set(os.path.basename(file_path))
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy file: {str(e)}", parent=self) # Added parent
                else:
                    var.set(file_path)

    def _save_module_edit(self, idx, name, script, enabled, content, dialog):
        """Save the edited module"""
        try:
            # Update config
            self.config["modules"][idx]["name"] = name
            self.config["modules"][idx]["script"] = script
            self.config["modules"][idx]["enabled"] = enabled
            self._save_config()
            
            # Update module file
            script_path = os.path.join(self.config.get("modules_dir", "modules"), script) # Use .get
            # Ensure modules directory exists before writing
            os.makedirs(os.path.dirname(script_path) or ".", exist_ok=True) # Ensure directory exists, handle case where script is just a filename

            if os.path.exists(script_path):
                if not messagebox.askyesno("File Exists", f"Script file '{script}' already exists. Overwrite?", parent=dialog): # Added parent
                    return

            with open(script_path, 'w') as f:
                f.write(content)
            
            # Update UI
            self.module_vars[idx].set(enabled)
            
            # Close dialog
            dialog.destroy()
            
            # Refresh modules tab
            self._refresh_modules_tab_display() # Use the refresh method

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save module: {str(e)}", parent=dialog) # Added parent

    def _test_module(self, idx):
        """Test run a single module"""
        module = self.config["modules"][idx]
        script_path = os.path.join(self.config.get("modules_dir", "modules"), module.get("script", "")) # Use .get

        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Script not found: {script_path}", parent=self) # Added parent
            return
            
        # Create a dialog to show output
        dialog = tk.Toplevel(self)
        dialog.title(f"Testing Module: {self._get_module_display_name(module)}") # Use display name
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set() # Grab focus

        # Output area
        output = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=70, height=15) # Reduced height slightly
        output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status label
        status = tk.Label(dialog, text="Running...")
        status.pack(pady=5)
        
        # Close button (disabled during test)
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy, state=tk.DISABLED)
        close_btn.pack(pady=10)
        
        # Run the module in a thread
        def run_test():
            try:
                output.insert(tk.END, f"Running {self._get_module_display_name(module)} ({script_path})...\n\n") # Use display name
                
                process = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                # Stream the output
                for line in iter(process.stdout.readline, ''):
                    output.insert(tk.END, line)
                    output.see(tk.END)
                    dialog.update() # Update dialog to show new text
                
                process.wait()
                
                if process.returncode == 0:
                    output.insert(tk.END, f"\n\nModule completed successfully.")
                    status.config(text="Completed successfully")
                else:
                    output.insert(tk.END, f"\n\nModule failed with exit code {process.returncode}.")
                    status.config(text=f"Failed (Exit code {process.returncode})")
            except Exception as e:
                output.insert(tk.END, f"\n\nError: {str(e)}")
                status.config(text="Error")
            
            # Enable close button
            close_btn.config(state=tk.NORMAL)
            dialog.grab_release() # Release grab

        threading.Thread(target=run_test, daemon=True).start()

    def _add_module(self):
        """Add a new module"""
        # Create a dialog
        dialog = tk.Toplevel(self)
        dialog.title("Add New Module")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Module fields
        tk.Label(dialog, text="Module Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Script File:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        script_var = tk.StringVar()
        script_entry = tk.Entry(dialog, textvariable=script_var, width=40)
        script_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Button(dialog, text="Browse",
                command=lambda: self._browse_script(script_var)).grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(dialog, text="Enabled:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(dialog, variable=enabled_var).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Script content editor
        tk.Label(dialog, text="Script Content:").grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        
        script_content = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=50, height=10) # Reduced height slightly
        script_content.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        
        # Add template script content
        template = """@echo off
echo [OPRYXX_STATUS] Running custom module...

REM Your commands here
REM Example: del /s /f /q "%TEMP%\\*.*" 2>&1

echo [OPRYXX_STATUS] Custom module completed.
exit /b 0
"""
        script_content.insert(tk.END, template)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Create", command=lambda: self._create_new_module(
            name_var.get(), script_var.get(), enabled_var.get(), script_content.get("1.0", tk.END), dialog
        )).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _create_new_module(self, name, script, enabled, content, dialog):
        """Create a new module"""
        if not name or not script:
            messagebox.showerror("Error", "Module name and script file are required.", parent=dialog) # Added parent
            return
            
        try:
            # Ensure script has the right extension
            if not script.lower().endswith(".bat") and not script.lower().endswith(".py"):
                script += ".bat"  # Default to batch file
            
            # Create the script file
            script_path = os.path.join(self.config.get("modules_dir", "modules"), script) # Use .get
            # Ensure modules directory exists before writing
            os.makedirs(os.path.dirname(script_path) or ".", exist_ok=True) # Ensure directory exists, handle case where script is just a filename

            if os.path.exists(script_path):
                if not messagebox.askyesno("File Exists", f"Script file '{script}' already exists. Overwrite?", parent=dialog): # Added parent
                    return

            with open(script_path, 'w') as f:
                f.write(content)
            
            # Add to config
            self.config["modules"].append({
                "name": name,
                "script": script,
                "enabled": enabled
            })
            self._save_config()
            
            # Refresh modules tab
            self._refresh_modules_tab_display() # Use the refresh method
            
            # Close dialog
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create module: {str(e)}", parent=dialog) # Added parent

    def _reorder_modules(self):
        """Open a dialog to reorder modules"""
        # Create a dialog
        dialog = tk.Toplevel(self)
        dialog.title("Reorder Modules")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Create a listbox
        tk.Label(dialog, text="Drag and drop to reorder modules:").pack(pady=10)
        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE, height=15, width=40)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Populate listbox
        for module in self.config["modules"]:
            listbox.insert(tk.END, f"{module.get('name', 'Unnamed')} ({module.get('script', 'N/A')})") # Use .get

        # Add up/down buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="Move Up",
                command=lambda: self._move_module(listbox, -1)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Move Down",
                command=lambda: self._move_module(listbox, 1)).pack(side=tk.LEFT, padx=10)
        
        # Add save/cancel buttons
        action_frame = tk.Frame(dialog)
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(action_frame, text="Save Order",
                command=lambda: self._save_module_order(listbox, dialog)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, text="Cancel",
                command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def _move_module(self, listbox, direction):
        """Move a module up or down in the listbox"""
        selected = listbox.curselection()
        if not selected:
            return
            
        index = selected[0]
        if direction == -1 and index == 0:
            return  # Already at the top
        if direction == 1 and index == listbox.size() - 1:
            return  # Already at the bottom
            
        # Get the text
        text = listbox.get(index)
        
        # Delete from current position
        listbox.delete(index)
        
        # Insert at new position
        new_index = index + direction
        listbox.insert(new_index, text)
        
        # Select the moved item
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(new_index)
        listbox.activate(new_index)
        listbox.see(new_index)

    def _save_module_order(self, listbox, dialog):
        """Save the new module order"""
        # Get the current order
        current_order_text = [listbox.get(i) for i in range(listbox.size())]
        
        # Map to module config based on name and script
        module_map = {}
        for module in self.config["modules"]:
            key = f"{module.get('name', 'Unnamed')} ({module.get('script', 'N/A')})" # Use .get
            module_map[key] = module
        
        # Create new module list based on the order in the listbox
        new_modules = []
        for item_text in current_order_text:
            if item_text in module_map:
                new_modules.append(module_map[item_text])
        
        # Update config
        self.config["modules"] = new_modules
        self._save_config()
        
        # Refresh modules tab
        self._refresh_modules_tab_display() # Use the refresh method
        
        # Close dialog
        dialog.destroy()

    def _reset_modules(self):
        """Reset modules to default configuration"""
        if not messagebox.askyesno("Confirm Reset",
                                 "Are you sure you want to reset all modules to default?\n\nThis will not delete your custom script files, but will reset their order and enabled status.", parent=self): # Added parent
            return
            
        default_modules = [
            {"name": "Temp + Cache Purge", "script": "temp_clean.bat", "enabled": True},
            {"name": "SFC + DISM", "script": "syscheck.bat", "enabled": True},
            {"name": "Network Repair", "script": "net_repair.bat", "enabled": True},
            {"name": "Explorer Cache", "script": "explorer_clean.bat", "enabled": True},
            {"name": "Memory/Pagefile", "script": "pagefile_reset.bat", "enabled": True},
            {"name": "File Sorter/Renamer", "script": "file_sorter_rename.bat", "enabled": True},
            {"name": "Deep Analysis", "script": "deep_analysis.bat", "enabled": False} # Include Deep Analysis in default
        ]
        
        self.config["modules"] = default_modules
        self._save_config()
        
        # Refresh modules tab
        self._refresh_modules_tab_display() # Use the refresh method

    def _browse_directory(self, var_name):
        """Browse for a directory"""
        current_dir = getattr(self, var_name).get()
        if not os.path.exists(current_dir):
             current_dir = "." # Fallback

        directory = filedialog.askdirectory(initialdir=current_dir, parent=self) # Added parent
        
        if directory:
            getattr(self, var_name).set(directory)

    def _save_settings(self):
        """Save the current settings"""
        try:
            # Update config from variables
            self.config["modules_dir"] = self.modules_dir_var.get()
            self.config["logs_dir"] = self.logs_dir_var.get()
            self.config["backup_dir"] = self.backup_dir_var.get()
            self.config["directive_base_dir"] = self.directive_base_dir_var.get() # Save directive base dir
            self.config["theme"] = self.theme_var.get()
            self.config["enable_safe_mode"] = self.safe_mode_var.get()
            self.config["enable_chkdsk"] = self.chkdsk_var.get()
            self.config["auto_backup"] = self.backup_var.get()
            self.config["symbolic_mode"] = self.symbolic_mode_var.get() # Save symbolic mode

            # Ensure directories exist
            os.makedirs(self.config.get("modules_dir", "modules"), exist_ok=True)
            os.makedirs(self.config.get("logs_dir", "logs\\oblivion"), exist_ok=True)
            os.makedirs(self.config.get("backup_dir", os.path.join(os.environ.get("USERPROFILE", ""), "OpryxxBackups")), exist_ok=True)
            os.makedirs(self.config.get("directive_base_dir", "C:\\PRIME_DIRECTIVE_250516"), exist_ok=True) # Ensure directive base dir exists

            # Save config
            self._save_config()

            # Refresh modules display in case symbolic mode changed
            self._refresh_modules_tab_display()

            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.", parent=self) # Added parent
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}", parent=self) # Added parent

    def _refresh_metrics(self):
        """Force refresh of system metrics"""
        self._update_system_metrics()
        messagebox.showinfo("Metrics Refreshed", "System metrics have been refreshed.", parent=self) # Added parent


# Create default batch files if they don't exist
def create_default_batch_files(modules_dir):
    """Create default batch files if they don't exist"""
    # Define default scripts
    default_scripts = {
        "temp_clean.bat": """@echo off
echo [OPRYXX_STATUS] Purging temporary files...
del /s /f /q "%TEMP%\\*.*" 2>&1
del /s /f /q "%SystemRoot%\\Temp\\*.*" 2>&1
rd /s /q "%TEMP%" 2>&1
md "%TEMP%" 2>&1
echo [OPRYXX_STATUS] Temp + Cache Purge Complete.
exit /b 0
""",
        "syscheck.bat": """@echo off
echo [OPRYXX_STATUS] Running SFC and DISM system checks...
sfc /scannow 2>&1
DISM /Online /Cleanup-Image /RestoreHealth 2>&1
echo [OPRYXX_STATUS] SFC + DISM Complete.
exit /b 0
""",
        "net_repair.bat": """@echo off
echo [OPRYXX_STATUS] Resetting network stack...
ipconfig /flushdns 2>&1
netsh winsock reset 2>&1
netsh int ip reset 2>&1
echo [OPRYXX_STATUS] Network Repair Complete.
exit /b 0
""",
        "explorer_clean.bat": """@echo off
echo [OPRYXX_STATUS] Cleaning Explorer cache...
taskkill /f /im explorer.exe >nul 2>&1
timeout /t 2 /nobreak >nul 2>&1
del /f /s /q "%LocalAppData%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" 2>&1
start explorer.exe
echo [OPRYXX_STATUS] Explorer Cleanup Complete.
exit /b 0
""",
        "pagefile_reset.bat": """@echo off
echo [OPRYXX_STATUS] Resetting memory/pagefile settings...
wmic pagefile set AutomaticManagedPagefile=True 2>&1
echo [OPRYXX_STATUS] Memory/Pagefile Reset Complete.
exit /b 0
""",
        "file_sorter_rename.bat": """@echo off
echo [OPRYXX_STATUS] Starting File Sorting and Renaming...

:: This is a placeholder script.
:: Implement your logic here to sort and rename files
:: based on the PRIME DIRECTIVE 250516 folder structure.
:: You might use Python scripts called from here for complex logic.
:: Example: python sort_script.py "%USERPROFILE%\\Downloads" "C:\\PRIME_DIRECTIVE_250516"

echo Placeholder: Implement your file sorting and renaming logic in this script.

echo [OPRYXX_STATUS] File Sorting and Renaming Complete (Placeholder).
exit /b 0
""",
        "deep_analysis.bat": """@echo off
echo [OPRYXX_STATUS] Starting Deep System Analysis...

:: System Information
echo Gathering system information...
systeminfo > "%TEMP%\\opryxx_sysinfo.txt" 2>&1

:: Disk Information
echo Analyzing disk space...
wmic logicaldisk get caption,description,providername,size,freespace > "%TEMP%\\opryxx_disk.txt" 2>&1

:: Running Processes
echo Analyzing running processes...
tasklist /v > "%TEMP%\\opryxx_processes.txt" 2>&1

:: Network Information
echo Analyzing network configuration...
ipconfig /all > "%TEMP%\\opryxx_network.txt" 2>&1
netstat -ano > "%TEMP%\\opryxx_netstat.txt" 2>&1

:: System Event Logs (Last 5 entries)
echo Extracting system event logs...
wevtutil qe System /c:5 /rd:true /f:text > "%TEMP%\\opryxx_syslog.txt" 2>&1
wevtutil qe Application /c:5 /rd:true /f:text > "%TEMP%\\opryxx_applog.txt" 2>&1

:: Startup Items
echo Analyzing startup items...
wmic startup get caption,command,location,user > "%TEMP%\\opryxx_startup.txt" 2>&1

echo [OPRYXX_STATUS] Deep System Analysis Complete.
exit /b 0
""",
    }
    
    os.makedirs(modules_dir, exist_ok=True)
    
    for filename, content in default_scripts.items():
        filepath = os.path.join(modules_dir, filename)
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"Created default module script: {filepath}")
            except Exception as e:
                print(f"Error creating default script {filepath}: {str(e)}")


if __name__ == "__main__":
    # Check if PC Optimizer dependencies are installed
    try:
        import win32com.client
    except ImportError:
        print("Installing required dependencies for PC Optimizer...")
        subprocess.run(["pip", "install", "pywin32"], capture_output=True)
        print("Dependencies installed successfully.")
    
    # Ensure default modules directory exists
    modules_dir = "modules"
    os.makedirs(modules_dir, exist_ok=True)
    
    # Create default batch files
    create_default_batch_files(modules_dir)

    # Load configuration after ensuring default files exist
    app = OPRYXXRepairGUI()
    app.mainloop()