"""
OPRYXX Task Tracker
Enhanced task tracking with operator intelligence
"""
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    task_id: str
    name: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class TaskTracker:
    def __init__(self):
        self.operator_link = "OPR-NS8-GE8-KC3-001-AI-GRS-GUID:983DE8C8-E120-1-B5A0-C6D8AF97BB09"
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.task_counter = 0
    
    def create_task(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """Create a new task"""
        with self.lock:
            self.task_counter += 1
            task_id = f"TASK_{self.task_counter:04d}_{int(time.time())}"
            
            task = Task(
                task_id=task_id,
                name=name,
                status=TaskStatus.PENDING,
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = task
            return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Start a task"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.RUNNING
                task.start_time = datetime.now()
                return True
            return False
    
    def update_progress(self, task_id: str, progress: float) -> bool:
        """Update task progress"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = max(0.0, min(100.0, progress))
                return True
            return False
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Complete a task"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now()
                task.progress = 100.0
                task.result = result
                return True
            return False
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.FAILED
                task.end_time = datetime.now()
                task.error = error
                return True
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        with self.lock:
            return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        with self.lock:
            return [task for task in self.tasks.values() if task.status == status]
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed tasks"""
        with self.lock:
            current_time = datetime.now()
            tasks_to_remove = []
            
            for task_id, task in self.tasks.items():
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                    task.end_time and 
                    (current_time - task.end_time).total_seconds() > max_age_hours * 3600):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
            
            return len(tasks_to_remove)