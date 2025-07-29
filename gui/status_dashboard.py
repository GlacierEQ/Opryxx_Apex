"""Status dashboard for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
from datetime import datetime
import psutil
import platform
import sys
import os

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

try:
    from task_tracker import TaskStatus, TaskTracker
except ImportError:
    # Fallback if task_tracker not available
    class TaskStatus:
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
    
    class TaskTracker:
        def get_all_tasks(self):
            return []

class StatusDashboard(ttk.Frame):
    """Dashboard for displaying system and task status"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.task_tracker = TaskTracker()
        self._setup_ui()
        self.update_interval = 2000  # ms
        self._schedule_updates()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        
        # System Info Frame
        sys_frame = ttk.LabelFrame(self, text="System Information", padding=5)
        sys_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # System metrics
        self.sys_info = {
            'os': ttk.Label(sys_frame, text="OS: Loading..."),
            'cpu': ttk.Label(sys_frame, text="CPU: Loading..."),
            'memory': ttk.Label(sys_frame, text="Memory: Loading..."),
            'disk': ttk.Label(sys_frame, text="Disk: Loading...")
        }
        
        for i, (_, label) in enumerate(self.sys_info.items()):
            label.grid(row=i, column=0, sticky='w', pady=2)
        
        # Task Status Frame
        task_frame = ttk.LabelFrame(self, text="Task Status", padding=5)
        task_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Task metrics
        self.task_info = {
            'total': ttk.Label(task_frame, text="Total: 0"),
            'running': ttk.Label(task_frame, text="Running: 0"),
            'completed': ttk.Label(task_frame, text="Completed: 0"),
            'failed': ttk.Label(task_frame, text="Failed: 0")
        }
        
        for i, (_, label) in enumerate(self.task_info.items()):
            label.grid(row=i, column=0, sticky='w', pady=2)
        
        # Recent Activity Frame
        activity_frame = ttk.LabelFrame(self, text="Recent Activity", padding=5)
        activity_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        self.activity_text = tk.Text(
            activity_frame, 
            height=8, 
            wrap=tk.WORD,
            state='disabled'
        )
        self.activity_text.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            activity_frame, 
            orient="vertical", 
            command=self.activity_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.activity_text['yscrollcommand'] = scrollbar.set
        
        # Configure grid weights
        for i in range(3):
            self.rowconfigure(i, weight=1)
    
    def _schedule_updates(self) -> None:
        """Schedule periodic updates"""
        self._update_system_info()
        self._update_task_info()
        self.after(self.update_interval, self._schedule_updates)
    
    def _update_system_info(self) -> None:
        """Update system information display"""
        try:
            # OS Info
            os_info = f"OS: {platform.system()} {platform.release()} ({platform.version()})"
            
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_info = f"CPU: {cpu_percent}% used"
            
            # Memory Usage
            mem = psutil.virtual_memory()
            mem_info = f"Memory: {mem.percent}% used ({self._format_bytes(mem.used)} / {self._format_bytes(mem.total)})"
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_info = f"Disk: {disk.percent}% used ({self._format_bytes(disk.used)} / {self._format_bytes(disk.total)})"
            
            # Update UI
            self.sys_info['os'].config(text=os_info)
            self.sys_info['cpu'].config(text=cpu_info)
            self.sys_info['memory'].config(text=mem_info)
            self.sys_info['disk'].config(text=disk_info)
            
        except Exception as e:
            self._log_activity(f"Error updating system info: {str(e)}")
    
    def _update_task_info(self) -> None:
        """Update task information display"""
        try:
            tasks = self.task_tracker.get_all_tasks()
            status_counts = {
                'total': len(tasks),
                'running': 0,
                'completed': 0,
                'failed': 0
            }
            
            for task in tasks:
                if task.status == TaskStatus.RUNNING:
                    status_counts['running'] += 1
                elif task.status == TaskStatus.COMPLETED:
                    status_counts['completed'] += 1
                elif task.status == TaskStatus.FAILED:
                    status_counts['failed'] += 1
            
            # Update UI
            self.task_info['total'].config(text=f"Total: {status_counts['total']}")
            self.task_info['running'].config(text=f"Running: {status_counts['running']}")
            self.task_info['completed'].config(text=f"Completed: {status_counts['completed']}")
            self.task_info['failed'].config(text=f"Failed: {status_counts['failed']}")
            
        except Exception as e:
            self._log_activity(f"Error updating task info: {str(e)}")
    
    def _log_activity(self, message: str) -> None:
        """Add a message to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.activity_text.config(state='normal')
        self.activity_text.insert('end', log_message)
        self.activity_text.see('end')
        self.activity_text.config(state='disabled')
        
        # Limit log size
        lines = int(self.activity_text.index('end-1c').split('.')[0])
        if lines > 100:  # Keep last 100 lines
            self.activity_text.config(state='normal')
            self.activity_text.delete('1.0', f"{lines-80}.0")
            self.activity_text.config(state='disabled')
    
    @staticmethod
    def _format_bytes(bytes_num: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f} PB"
