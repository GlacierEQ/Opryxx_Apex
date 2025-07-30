"""
OPRYXX_LOGS2 Master GUI with OPRYXX Monitoring Integration
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import logging
from opryxx_monitor import SystemMonitor

class OPRYXXMasterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OPRYXX_LOGS2 - OPRYXX Edition")
        self.geometry("1200x800")
        
        # Initialize monitoring
        self.monitor = SystemMonitor()
        self.monitor.start()
        
        self.setup_logging()
        self.create_widgets()
        self.after(1000, self.update_ui)
        
    def setup_logging(self):
        logging.basicConfig(
            filename='opryxx_gui.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('OPRYXX.GUI')
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Performance dashboard
        self.create_dashboard(main_frame)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="System Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_dashboard(self, parent):
        dash_frame = ttk.LabelFrame(parent, text="Performance Dashboard")
        dash_frame.pack(fill=tk.X, pady=5)
        
        # CPU
        ttk.Label(dash_frame, text="CPU:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.cpu_bar = ttk.Progressbar(dash_frame, length=200, mode='determinate')
        self.cpu_bar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.cpu_var = tk.StringVar(value="0%")
        ttk.Label(dash_frame, textvariable=self.cpu_var).grid(row=0, column=2, padx=5)
        
        # Memory
        ttk.Label(dash_frame, text="Memory:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.mem_bar = ttk.Progressbar(dash_frame, length=200, mode='determinate')
        self.mem_bar.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.mem_var = tk.StringVar(value="0%")
        ttk.Label(dash_frame, textvariable=self.mem_var).grid(row=1, column=2, padx=5)
        
        # Performance Score
        ttk.Label(dash_frame, text="Perf Score:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.score_bar = ttk.Progressbar(dash_frame, length=200, mode='determinate')
        self.score_bar.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.score_var = tk.StringVar(value="0/100")
        ttk.Label(dash_frame, textvariable=self.score_var).grid(row=2, column=2, padx=5)
        
        # Configure grid weights
        dash_frame.columnconfigure(1, weight=1)
    
    def update_ui(self):
        try:
            status = self.monitor.get_system_status()
            
            # Update CPU
            cpu = status.get('cpu_percent', 0)
            self.cpu_bar['value'] = cpu
            self.cpu_var.set(f"{cpu:.1f}%")
            
            # Update Memory
            mem = status.get('memory_percent', 0)
            self.mem_bar['value'] = mem
            self.mem_var.set(f"{status.get('memory_mb', 0):.1f} MB ({mem:.1f}%)")
            
            # Update Score
            score = status.get('score', 0)
            self.score_bar['value'] = score
            self.score_var.set(f"{int(score)}/100")
            
            # Update status
            self.status_var.set(
                f"Status: {status.get('status', 'unknown')} | "
                f"CPU: {cpu:.1f}% | Mem: {mem:.1f}% | "
                f"Score: {score:.1f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
        
        self.after(1000, self.update_ui)
    
    def cleanup(self):
        self.monitor.stop()
        self.quit()

if __name__ == "__main__":
    app = OPRYXXMasterGUI()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.cleanup()
