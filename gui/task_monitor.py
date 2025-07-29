"""Task monitoring panel for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from ..core.task_tracker import Task, TaskStatus, TaskTracker

class TaskMonitor(ttk.Frame):
    """Panel for monitoring task execution in real-time"""
    
    STATUS_COLORS = {
        TaskStatus.PENDING: "#FFA500",  # Orange
        TaskStatus.RUNNING: "#1E90FF",  # Blue
        TaskStatus.COMPLETED: "#32CD32",  # Green
        TaskStatus.FAILED: "#FF4500",  # Red
        TaskStatus.WARNING: "#FFD700"  # Yellow
    }
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.task_tracker = TaskTracker()
        self.tasks: Dict[str, str] = {}  # task_id -> tree_item
        self._setup_ui()
        self._subscribe_to_updates()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Treeview for tasks
        columns = ('status', 'name', 'progress', 'message')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        # Configure columns
        self.tree.heading('status', text='Status')
        self.tree.heading('name', text='Task')
        self.tree.heading('progress', text='Progress')
        self.tree.heading('message', text='Message')
        
        # Column widths
        self.tree.column('status', width=100)
        self.tree.column('name', width=200)
        self.tree.column('progress', width=100)
        self.tree.column('message', width=400)
        
        # Add scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
    
    def _subscribe_to_updates(self) -> None:
        """Subscribe to task updates"""
        self.task_tracker.subscribe(self._on_task_updated)
    
    def _on_task_updated(self, task: Task) -> None:
        """Handle task update events"""
        self.after(0, self._update_task_ui, task)
    
    def _update_task_ui(self, task: Task) -> None:
        """Update the UI for a task"""
        task_id = task.id
        progress = f"{task.progress:.1f}%" if task.progress is not None else ""
        
        if task_id not in self.tasks:
            item = self.tree.insert('', 'end', values=(
                task.status.value,
                task.name,
                progress,
                task.message
            ))
            self.tasks[task_id] = item
        else:
            self.tree.item(self.tasks[task_id], values=(
                task.status.value,
                task.name,
                progress,
                task.message
            ))
        
        # Auto-scroll to show updated tasks
        self.tree.see(self.tasks[task_id])
