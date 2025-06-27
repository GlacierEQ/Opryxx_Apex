"""
OPRYXX-Todo System Integration Bridge
Combines OPRYXX recovery capabilities with autonomous todo processing
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from architecture.core import BaseRecoveryModule, RecoveryResult, RecoveryStatus

@dataclass
class TodoRecoveryTask:
    id: str
    title: str
    recovery_type: str
    priority: str
    auto_execute: bool = False

class TodoRecoveryBridge:
    def __init__(self, todo_path: str = "C:\\opryxx_logs\\files"):
        self.todo_path = todo_path
        
    def scan_recovery_todos(self) -> List[TodoRecoveryTask]:
        """Scan for recovery-related todos"""
        recovery_keywords = ["fix", "repair", "recover", "boot", "safe mode", "system", "error"]
        
        todos_dir = os.path.join(self.todo_path, "todos")
        if not os.path.exists(todos_dir):
            return []
        
        recovery_tasks = []
        
        for file in os.listdir(todos_dir):
            if file.endswith('.md'):
                file_path = os.path.join(todos_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('- [ ]'):
                        todo_text = line.strip()[5:].strip()
                        
                        if any(keyword in todo_text.lower() for keyword in recovery_keywords):
                            task = TodoRecoveryTask(
                                id=f"{file}_{i}",
                                title=todo_text,
                                recovery_type=self._classify_recovery_type(todo_text),
                                priority=self._determine_priority(todo_text),
                                auto_execute="safe mode" in todo_text.lower()
                            )
                            recovery_tasks.append(task)
        
        return recovery_tasks
    
    def _classify_recovery_type(self, todo_text: str) -> str:
        text_lower = todo_text.lower()
        if "safe mode" in text_lower or "boot" in text_lower:
            return "boot_recovery"
        elif "system" in text_lower:
            return "system_recovery"
        else:
            return "general_fix"
    
    def _determine_priority(self, todo_text: str) -> str:
        text_lower = todo_text.lower()
        if any(word in text_lower for word in ["critical", "boot", "crash"]):
            return "critical"
        elif "system" in text_lower:
            return "high"
        else:
            return "medium"
    
    def create_recovery_todo(self, recovery_result: RecoveryResult) -> Dict:
        """Create todo entry from recovery operation"""
        today = datetime.now().strftime("%Y-%m-%d")
        todo_file = os.path.join(self.todo_path, "todos", f"recovery-{today}.md")
        
        os.makedirs(os.path.dirname(todo_file), exist_ok=True)
        
        with open(todo_file, 'a', encoding='utf-8') as f:
            if recovery_result.status == RecoveryStatus.SUCCESS:
                f.write(f"- [x] {recovery_result.message}\n")
            else:
                f.write(f"- [ ] Follow up: {recovery_result.message}\n")
        
        return {"status": "created", "file": todo_file}

class AutoRecoveryModule(BaseRecoveryModule):
    def __init__(self):
        super().__init__("AutoRecovery")
        self.bridge = TodoRecoveryBridge()
    
    def validate_prerequisites(self) -> bool:
        return True
    
    def execute(self) -> RecoveryResult:
        recovery_todos = self.bridge.scan_recovery_todos()
        
        if not recovery_todos:
            return RecoveryResult(
                status=RecoveryStatus.SUCCESS,
                message="No recovery todos found",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        auto_todos = [t for t in recovery_todos if t.auto_execute]
        
        return RecoveryResult(
            status=RecoveryStatus.SUCCESS,
            message=f"Found {len(recovery_todos)} recovery todos, {len(auto_todos)} auto-executable",
            details={"total_todos": len(recovery_todos), "auto_todos": len(auto_todos)},
            timestamp=datetime.now().isoformat()
        )