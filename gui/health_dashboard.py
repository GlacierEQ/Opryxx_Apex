"""Health Dashboard for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import psutil
import platform
import socket
from typing import Dict, List, Tuple, Optional
import threading

class HealthDashboard(ttk.Frame):
    """Dashboard for monitoring system health metrics"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.metrics = {}
        self._setup_ui()
        self._update_interval = 5000  # 5 seconds
        self._schedule_updates()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(
            header,
            text="System Health Dashboard",
            font=('Helvetica', 12, 'bold')
        ).pack(side='left')
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            header,
            text="Refresh",
            command=self._update_metrics
        )
        self.refresh_btn.pack(side='right', padx=5)
        
        # Main content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        
        # Left panel - System Info
        sys_info = ttk.LabelFrame(content, text="System Information", padding=5)
        sys_info.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        sys_info.columnconfigure(1, weight=1)
        
        # System info labels
        self._add_info_row(sys_info, 0, "Hostname:", "")
        self._add_info_row(sys_info, 1, "OS:", "")
        self._add_info_row(sys_info, 2, "Platform:", "")
        self._add_info_row(sys_info, 3, "Processor:", "")
        self._add_info_row(sys_info, 4, "CPU Cores:", "")
        self._add_info_row(sys_info, 5, "Total RAM:", "")
        
        # Right panel - Health Status
        health_status = ttk.LabelFrame(content, text="Health Status", padding=5)
        health_status.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
        health_status.columnconfigure(1, weight=1)
        
        # Health metrics
        self._add_health_metric(health_status, 0, "CPU Usage:", "cpu_percent")
        self._add_health_metric(health_status, 1, "Memory Usage:", "memory_percent")
        self._add_health_metric(health_status, 2, "Disk Usage (C:):", "disk_percent")
        self._add_health_metric(health_status, 3, "CPU Temperature:", "cpu_temp")
        self._add_health_metric(health_status, 4, "Network I/O:", "network_io")
        self._add_health_metric(health_status, 5, "Processes:", "process_count")
        
        # Bottom panel - Warnings
        self.warnings_frame = ttk.LabelFrame(
            self,
            text="System Warnings",
            padding=5
        )
        self.warnings_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.warnings_frame.columnconfigure(0, weight=1)
        
        self.warnings_text = tk.Text(
            self.warnings_frame,
            height=4,
            wrap=tk.WORD,
            state='disabled'
        )
        self.warnings_text.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.warnings_frame,
            orient="vertical",
            command=self.warnings_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.warnings_text['yscrollcommand'] = scrollbar.set
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        ).grid(row=3, column=0, sticky='ew', padx=5, pady=2)
        
        # Initial update
        self._update_system_info()
        self._update_metrics()
    
    def _add_info_row(self, parent: ttk.Frame, row: int, label: str, value: str) -> None:
        """Add a row to the system info panel"""
        ttk.Label(parent, text=label, font=('TkDefaultFont', 9, 'bold')) \
            .grid(row=row, column=0, sticky='w', padx=2, pady=1)
        
        var = tk.StringVar(value=value)
        ttk.Label(parent, textvariable=var) \
            .grid(row=row, column=1, sticky='w', padx=5, pady=1)
        
        # Store reference to the variable
        setattr(self, f'info_{label.lower().replace(":", "").replace(" ", "_")}', var)
    
    def _add_health_metric(self, parent: ttk.Frame, row: int, label: str, metric_key: str) -> None:
        """Add a health metric row with progress bar"""
        # Label
        ttk.Label(parent, text=label) \
            .grid(row=row, column=0, sticky='w', padx=2, pady=1)
        
        # Progress bar
        progress = ttk.Progressbar(
            parent,
            orient='horizontal',
            length=150,
            mode='determinate'
        )
        progress.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        # Value label
        value_var = tk.StringVar(value="0%")
        ttk.Label(parent, textvariable=value_var, width=6) \
            .grid(row=row, column=2, padx=2, pady=1)
        
        # Status icon
        status_icon = ttk.Label(parent, text="●", foreground="gray")
        status_icon.grid(row=row, column=3, padx=2, pady=1)
        
        # Store references
        self.metrics[metric_key] = {
            'progress': progress,
            'value': value_var,
            'icon': status_icon
        }
    
    def _schedule_updates(self) -> None:
        """Schedule periodic updates"""
        self._update_metrics()
        self.after(self._update_interval, self._schedule_updates)
    
    def _update_system_info(self) -> None:
        """Update static system information"""
        try:
            # Hostname
            hostname = socket.gethostname()
            self.info_hostname.set(hostname)
            
            # OS info
            self.info_os.set(f"{platform.system()} {platform.release()} ({platform.version()})")
            
            # Platform
            self.info_platform.set(platform.platform())
            
            # CPU info
            self.info_processor.set(platform.processor() or "N/A")
            self.info_cpu_cores.set(str(psutil.cpu_count(logical=True)))
            
            # Memory info
            mem = psutil.virtual_memory()
            self.info_total_ram.set(f"{self._format_bytes(mem.total)} (Available: {self._format_bytes(mem.available)})")
            
        except Exception as e:
            self._show_error(f"Error updating system info: {str(e)}")
    
    def _update_metrics(self) -> None:
        """Update dynamic health metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._update_metric('cpu_percent', cpu_percent, 100, 75, 90)
            
            # Memory usage
            mem = psutil.virtual_memory()
            self._update_metric('memory_percent', mem.percent, 100, 75, 90)
            
            # Disk usage
            try:
                disk = psutil.disk_usage('/')
                self._update_metric('disk_percent', disk.percent, 100, 85, 95)
            except Exception:
                self._update_metric('disk_percent', 0, 100, 0, 0, available=False)
            
            # CPU temperature (platform-specific)
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if 'coretemp' in temps:
                        temp = max(t.current for t in temps['coretemp'] if hasattr(t, 'current'))
                        self._update_metric('cpu_temp', temp, 100, 70, 90, suffix="°C")
                    else:
                        raise Exception("Temperature sensors not available")
                else:
                    raise Exception("Platform not supported")
            except Exception:
                self._update_metric('cpu_temp', 0, 100, 0, 0, available=False, value_text="N/A")
            
            # Network I/O
            net_io = psutil.net_io_counters()
            net_usage = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            self._update_metric('network_io', net_usage, 1000, 500, 800, suffix=" MB")
            
            # Process count
            proc_count = len(psutil.pids())
            self._update_metric('process_count', proc_count, 500, 300, 400, show_percent=False)
            
            # Update status
            self.status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Check for warnings
            self._check_warnings()
            
        except Exception as e:
            self._show_error(f"Error updating metrics: {str(e)}")
    
    def _update_metric(self, 
                      metric_key: str, 
                      value: float, 
                      max_value: float, 
                      warn_threshold: float, 
                      crit_threshold: float,
                      show_percent: bool = True,
                      available: bool = True,
                      value_text: Optional[str] = None,
                      suffix: str = "%") -> None:
        """Update a single metric display"""
        if metric_key not in self.metrics:
            return
            
        metric = self.metrics[metric_key]
        
        if not available:
            metric['progress'].configure(value=0, mode='indeterminate')
            metric['value'].set("N/A")
            metric['icon'].config(foreground="gray")
            return
        
        # Calculate percentage for progress bar
        percent = min(100, (value / max_value) * 100) if max_value > 0 else 0
        
        # Update progress bar
        metric['progress'].configure(
            value=percent,
            mode='determinate',
            style=f"{'danger' if percent > crit_threshold else 'warning' if percent > warn_threshold else ''}.Horizontal.TProgressbar"
        )
        
        # Update value text
        if value_text is None:
            value_text = f"{value:.1f}{suffix}"
            if show_percent and max_value > 0:
                value_text += f" ({percent:.0f}%)"
        metric['value'].set(value_text)
        
        # Update status icon
        if percent > crit_threshold:
            metric['icon'].config(foreground="red")
        elif percent > warn_threshold:
            metric['icon'].config(foreground="orange")
        else:
            metric['icon'].config(foreground="green")
    
    def _check_warnings(self) -> None:
        """Check for system warnings and display them"""
        warnings = []
        
        # CPU warning
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            warnings.append(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
        
        # Memory warning
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            warnings.append(f"⚠️ High memory usage: {mem.percent:.1f}%")
        
        # Disk warning
        try:
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                warnings.append(f"⚠️ Low disk space: {disk.percent:.1f}% used")
        except Exception:
            pass
        
        # CPU temperature warning (if available)
        if 'cpu_temp' in self.metrics and self.metrics['cpu_temp']['icon'].cget('foreground') in ('orange', 'red'):
            temp = float(self.metrics['cpu_temp']['value'].get().split('°')[0])
            warnings.append(f"⚠️ High CPU temperature: {temp}°C")
        
        # Update warnings display
        self.warnings_text.config(state='normal')
        self.warnings_text.delete('1.0', 'end')
        
        if warnings:
            self.warnings_text.insert('1.0', '\n'.join(warnings))
            self.warnings_frame.config(style='Warning.TLabelframe')
        else:
            self.warnings_text.insert('1.0', 'No critical issues detected.')
            self.warnings_frame.config(style='')
        
        self.warnings_text.config(state='disabled')
    
    def _show_error(self, message: str) -> None:
        """Display an error message in the status bar"""
        self.status_var.set(f"Error: {message}")
    
    @staticmethod
    def _format_bytes(bytes_num: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f} PB"

# Add custom styles
def configure_styles():
    """Configure custom styles for the health dashboard"""
    style = ttk.Style()
    
    # Warning frame style
    style.configure(
        'Warning.TLabelframe',
        background='#fff3cd',
        bordercolor='#ffeeba'
    )
    style.configure(
        'Warning.TLabelframe.Label',
        background='#fff3cd',
        foreground='#856404'
    )
    
    # Progress bar styles
    style.configure(
        'danger.Horizontal.TProgressbar',
        background='#dc3545',  # Red for critical
        troughcolor='#f8d7da',
        bordercolor='#f5c6cb'
    )
    
    style.configure(
        'warning.Horizontal.TProgressbar',
        background='#ffc107',  # Yellow/orange for warning
        troughcolor='#fff3cd',
        bordercolor='#ffeeba'
    )
    
    # Default style is used for normal state

# Call this when initializing your application
configure_styles()
