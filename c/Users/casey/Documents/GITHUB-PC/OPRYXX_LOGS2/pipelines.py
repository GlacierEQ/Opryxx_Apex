from sentence_transformers import SentenceTransformer
import subprocess
import numpy as np
import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable
import json
import threading
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
import queue
import sys
import os

# Import existing GUI components
try:
    from gui.modern_interface import ModernInterface
    from gui.web_interface import WebInterface
    from gui.MEGA_OPRYXX import MegaOPRYXX
    from core.logging_config import setup_logging
    from core.performance_monitor import PerformanceMonitor
    from ai.AI_WORKBENCH import AIWorkbench
    from ai.ULTIMATE_AI_OPTIMIZER import UltimateAIOptimizer
    from modules.performance_benchmark import PerformanceBenchmark
    from enhancements.memory_optimization import MemoryOptimizer
except ImportError as e:
    logging.warning(f"GUI imports failed: {e}")

class OperationState(Enum):
    PENDING = "pending"
    BEGINNING = "beginning"
    PROCESSING = "processing"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class OperationContext:
    operation_id: str
    task_type: str
    command: str
    state: OperationState
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict = None

class GUIIntegrationManager:
    """Manages integration between pipelines and all GUI components"""

    def __init__(self):
        self.gui_instances = {}
        self.event_queue = queue.Queue()
        self.gui_callbacks = {}
        self.active_windows = {}

    def register_gui_component(self, name: str, instance):
        """Register a GUI component for integration"""
        self.gui_instances[name] = instance

    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific GUI events"""
        if event_type not in self.gui_callbacks:
            self.gui_callbacks[event_type] = []
        self.gui_callbacks[event_type].append(callback)

    def emit_event(self, event_type: str, data: Dict):
        """Emit event to all registered callbacks"""
        if event_type in self.gui_callbacks:
            for callback in self.gui_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logging.error(f"GUI callback error: {e}")

    def get_gui_instance(self, name: str):
        """Get registered GUI instance"""
        return self.gui_instances.get(name)

class TaskAnalyzer:
    def __init__(self, gui_callback: Optional[Callable] = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.gui_callback = gui_callback
        self.logger = setup_logging(__name__)
        self.performance_monitor = PerformanceMonitor()

        # Initialize GUI Integration Manager
        self.gui_manager = GUIIntegrationManager()
        self._initialize_gui_components()

        # Enhanced command embeddings for OPRYXX operations
        self.command_embeddings = {
            # System Operations
            "system_scan": self.model.encode("scan system for issues and problems"),
            "system_optimize": self.model.encode("optimize system performance and speed"),
            "system_repair": self.model.encode("repair system errors and fix problems"),
            "system_recovery": self.model.encode("recover system from failures"),

            # AI Operations
            "ai_analyze": self.model.encode("artificial intelligence analysis and diagnostics"),
            "ai_optimize": self.model.encode("AI powered optimization and enhancement"),
            "ai_workbench": self.model.encode("launch AI workbench and tools"),

            # Performance Operations
            "performance_test": self.model.encode("test system performance and benchmarks"),
            "memory_optimize": self.model.encode("optimize memory usage and cleanup"),
            "disk_cleanup": self.model.encode("clean disk space and remove junk"),
            "gpu_optimize": self.model.encode("optimize graphics card performance"),

            # Security Operations
            "security_scan": self.model.encode("scan for security threats and malware"),
            "firewall_config": self.model.encode("configure firewall and security settings"),

            # Network Operations
            "network_test": self.model.encode("test network connectivity and speed"),
            "network_optimize": self.model.encode("optimize network settings and performance"),

            # File Operations
            "file_list": self.model.encode("list directory contents and files"),
            "file_search": self.model.encode("search for files and folders"),
            "file_backup": self.model.encode("backup files and data"),

            # Development Operations
            "git_operations": self.model.encode("version control git operations"),
            "python_execute": self.model.encode("run python scripts and programs"),
            "docker_manage": self.model.encode("container management and docker operations"),

            # Recovery Operations
            "boot_repair": self.model.encode("repair boot problems and startup issues"),
            "registry_repair": self.model.encode("repair windows registry problems"),
            "driver_update": self.model.encode("update system drivers and hardware")
        }

        # Operation tracking
        self.active_operations: Dict[str, OperationContext] = {}
        self.operation_history: List[OperationContext] = []

    def _initialize_gui_components(self):
        """Initialize and register all GUI components"""
        try:
            # Initialize main GUI components
            self.modern_interface = ModernInterface()
            self.gui_manager.register_gui_component("modern_interface", self.modern_interface)

            # Initialize web interface if available
            try:
                self.web_interface = WebInterface()
                self.gui_manager.register_gui_component("web_interface", self.web_interface)
            except Exception as e:
                self.logger.warning(f"Web interface not available: {e}")

            # Initialize MEGA OPRYXX interface
            try:
                self.mega_opryxx = MegaOPRYXX()
                self.gui_manager.register_gui_component("mega_opryxx", self.mega_opryxx)
            except Exception as e:
                self.logger.warning(f"MEGA OPRYXX interface not available: {e}")

            # Register event callbacks
            self.gui_manager.register_callback("operation_update", self._handle_operation_update)
            self.gui_manager.register_callback("progress_update", self._handle_progress_update)
            self.gui_manager.register_callback("error_occurred", self._handle_error)

        except Exception as e:
            self.logger.error(f"GUI initialization failed: {e}")

    def analyze_task(self, query: str) -> Dict:
        """Convert natural language to executable command with full lifecycle tracking"""
        operation_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        try:
            # Begin operation
            self._update_operation_state(operation_id, OperationState.BEGINNING,
                                       task_type="task_analysis", command=query)

            # Encode the query
            query_embedding = self.model.encode(query.lower())

            # Find most similar command
            similarities = {
                cmd: np.dot(embed, query_embedding) / (np.linalg.norm(embed) * np.linalg.norm(query_embedding))
                for cmd, embed in self.command_embeddings.items()
            }

            best_match = max(similarities, key=similarities.get)
            confidence = similarities[best_match]

            # Update to processing
            self._update_operation_state(operation_id, OperationState.PROCESSING, progress=50.0)

            # Generate command based on best match
            command_result = self._generate_command(best_match, query, confidence)

            # Complete operation
            self._update_operation_state(operation_id, OperationState.COMPLETED,
                                       progress=100.0, result=command_result)

            return {
                "operation_id": operation_id,
                "command": command_result["command"],
                "task_type": best_match,
                "confidence": confidence,
                "executable": command_result["executable"],
                "gui_action": command_result.get("gui_action"),
                "parameters": command_result.get("parameters", {}),
                "state": OperationState.COMPLETED.value
            }

        except Exception as e:
            self._update_operation_state(operation_id, OperationState.FAILED, error=str(e))
            self.logger.error(f"Task analysis failed: {e}")
            return {"operation_id": operation_id, "error": str(e), "state": OperationState.FAILED.value}

    def _generate_command(self, task_type: str, original_query: str, confidence: float) -> Dict:
        """Generate executable command based on task type"""
        command_map = {
            # System Operations
            "system_scan": {
                "command": "python ai/ULTIMATE_AI_OPTIMIZER.py --scan",
                "executable": True,
                "gui_action": "launch_system_scan",
                "parameters": {"scan_type": "full", "deep_scan": True}
            },
            "system_optimize": {
                "command": "python ai/ULTIMATE_AI_OPTIMIZER.py --optimize",
                "executable": True,
                "gui_action": "launch_optimizer",
                "parameters": {"optimization_level": "aggressive"}
            },
            "system_repair": {
                "command": "python recovery/immediate_safe_mode_exit.py",
                "executable": True,
                "gui_action": "launch_repair_tools",
                "parameters": {"repair_mode": "auto"}
            },

            # AI Operations
            "ai_workbench": {
                "command": "python ai/AI_WORKBENCH.py",
                "executable": True,
                "gui_action": "launch_ai_workbench",
                "parameters": {"mode": "interactive"}
            },
            "ai_analyze": {
                "command": "python ai/ASCEND_AI.py --analyze",
                "executable": True,
                "gui_action": "launch_ai_analysis",
                "parameters": {"analysis_depth": "comprehensive"}
            },

            # Performance Operations
            "performance_test": {
                "command": "python modules/performance_benchmark.py",
                "executable": True,
                "gui_action": "launch_benchmark",
                "parameters": {"test_suite": "full"}
            },
            "memory_optimize": {
                "command": "python enhancements/memory_optimization.py",
                "executable": True,
                "gui_action": "optimize_memory",
                "parameters": {"cleanup_level": "aggressive"}
            },

            # File Operations
            "file_list": {
                "command": "Get-ChildItem" if "windows" in original_query.lower() else "ls -la",
                "executable": True,
                "gui_action": "show_file_explorer",
                "parameters": {"view": "detailed"}
            },

            # Development Operations
            "git_operations": {
                "command": self._parse_git_command(original_query),
                "executable": True,
                "gui_action": "show_git_interface",
                "parameters": {"auto_commit": False}
            },
            "python_execute": {
                "command": f"python {self._extract_script_name(original_query)}",
                "executable": True,
                "gui_action": "show_python_console",
                "parameters": {"capture_output": True}
            }
        }

        return command_map.get(task_type, {
            "command": f"# Unknown task: {original_query}",
            "executable": False,
            "gui_action": "show_help",
            "parameters": {"suggestion": "Please rephrase your request"}
        })

    def _parse_git_command(self, query: str) -> str:
        """Parse git-related queries into commands"""
        query_lower = query.lower()
        if "status" in query_lower:
            return "git status"
        elif "commit" in query_lower:
            return "git add . && git commit -m 'Auto commit'"
        elif "push" in query_lower:
            return "git push origin main"
        elif "pull" in query_lower:
            return "git pull origin main"
        else:
            return "git status"

    def _extract_script_name(self, query: str) -> str:
        """Extract script name from query"""
        words = query.split()
        for word in words:
            if word.endswith('.py'):
                return word
        return "main.py"  # Default

    def _update_operation_state(self, operation_id: str, state: OperationState,
                               task_type: str = None, command: str = None,
                               progress: float = 0.0, result: str = None, error: str = None):
        """Update operation state and notify GUI"""
        if operation_id not in self.active_operations:
            self.active_operations[operation_id] = OperationContext(
                operation_id=operation_id,
                task_type=task_type or "unknown",
                command=command or "",
                state=state,
                progress=progress,
                start_time=datetime.now()
            )
        else:
            op = self.active_operations[operation_id]
            op.state = state
            op.progress = progress
            if result:
                op.result = result
            if error:
                op.error = error
            if state in [OperationState.COMPLETED, OperationState.FAILED, OperationState.CANCELLED]:
                op.end_time = datetime.now()
                self.operation_history.append(op)
                del self.active_operations[operation_id]

        # Notify GUI through event system
        self.gui_manager.emit_event("operation_update", {
            "operation_id": operation_id,
            "state": state.value,
            "progress": progress,
            "result": result,
            "error": error,
            "task_type": task_type
        })

        # Legacy callback support
        if self.gui_callback:
            self.gui_callback({
                "type": "operation_update",
                "operation_id": operation_id,
                "state": state.value,
                "progress": progress,
                "result": result,
                "error": error
            })

    async def execute_command(self, command_info: Dict) -> Dict:
        """Execute command with full lifecycle tracking"""
        operation_id = command_info.get("operation_id")
        command = command_info.get("command")

        if not command_info.get("executable", False):
            return {"success": False, "error": "Command not executable"}

        try:
            # Begin execution
            self._update_operation_state(operation_id, OperationState.BEGINNING, progress=10.0)

            # Execute based on GUI action if available
            if command_info.get("gui_action"):
                result = await self._execute_gui_action(command_info)
            else:
                result = await self._execute_shell_command(command, operation_id)

            # Complete execution
            self._update_operation_state(operation_id, OperationState.COMPLETED,
                                       progress=100.0, result=str(result))

            return {"success": True, "result": result, "operation_id": operation_id}

        except Exception as e:
            self._update_operation_state(operation_id, OperationState.FAILED, error=str(e))
            return {"success": False, "error": str(e), "operation_id": operation_id}

    async def _execute_gui_action(self, command_info: Dict) -> str:
        """Execute GUI-specific actions"""
        gui_action = command_info.get("gui_action")
        parameters = command_info.get("parameters", {})

        # Map GUI actions to actual implementations
        gui_actions = {
            "launch_system_scan": self._launch_system_scan,
            "launch_optimizer": self._launch_optimizer,
            "launch_ai_workbench": self._launch_ai_workbench,
            "launch_benchmark": self._launch_benchmark,
            "optimize_memory": self._optimize_memory,
            "show_file_explorer": self._show_file_explorer,
            "show_git_interface": self._show_git_interface,
            "show_python_console": self._show_python_console,
            "show_help": self._show_help
        }

        action_func = gui_actions.get(gui_action)
        if action_func:
            return await action_func(parameters)
        else:
            return f"GUI action '{gui_action}' not implemented"

    async def _execute_shell_command(self, command: str, operation_id: str) -> str:
        """Execute shell command with progress tracking"""
        self._update_operation_state(operation_id, OperationState.PROCESSING, progress=30.0)

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        self._update_operation_state(operation_id, OperationState.PROCESSING, progress=70.0)

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return stdout.decode()
        else:
            raise Exception(f"Command failed: {stderr.decode()}")

    # Real GUI Action Implementations with actual component integration
    async def _launch_system_scan(self, parameters: Dict) -> str:
        """Launch system scan through actual GUI components"""
        try:
            # Update state to processing
            self._update_operation_state(parameters.get("operation_id"), OperationState.PROCESSING, progress=20.0)

            # Get MEGA OPRYXX interface for system operations
            mega_gui = self.gui_manager.get_gui_instance("mega_opryxx")
            if mega_gui and hasattr(mega_gui, 'start_system_scan'):
                result = await mega_gui.start_system_scan(parameters)

                # Also trigger modern interface if available
                modern_gui = self.gui_manager.get_gui_instance("modern_interface")
                if modern_gui and hasattr(modern_gui, 'show_scan_progress'):
                    modern_gui.show_scan_progress(parameters.get("operation_id"))

                return f"System scan completed: {result}"
            else:
                # Fallback to direct execution
                optimizer = UltimateAIOptimizer()
                result = await optimizer.run_system_scan(parameters)
                return f"System scan completed via direct execution: {result}"

        except Exception as e:
            self.logger.error(f"System scan failed: {e}")
            return f"System scan failed: {str(e)}"

    async def _launch_optimizer(self, parameters: Dict) -> str:
        """Launch optimizer through actual GUI components"""
        try:
            self._update_operation_state(parameters.get("operation_id"), OperationState.PROCESSING, progress=25.0)

            # Get optimizer instance
            mega_gui = self.gui_manager.get_gui_instance("mega_opryxx")
            if mega_gui and hasattr(mega_gui, 'launch_optimizer'):
                # Launch through MEGA OPRYXX interface
                result = await mega_gui.launch_optimizer(parameters)

                # Update modern interface
                modern_gui = self.gui_manager.get_gui_instance("modern_interface")
                if modern_gui and hasattr(modern_gui, 'update_optimization_status'):
                    modern_gui.update_optimization_status("running", parameters.get("operation_id"))

                return f"Optimizer launched successfully: {result}"
            else:
                # Direct execution fallback
                optimizer = UltimateAIOptimizer()
                result = await optimizer.optimize_system(parameters)
                return f"System optimization completed: {result}"

        except Exception as e:
            self.logger.error(f"Optimizer launch failed: {e}")
            return f"Optimizer launch failed: {str(e)}"

    async def _launch_ai_workbench(self, parameters: Dict) -> str:
        """Launch AI workbench through actual GUI components"""
        try:
            self._update_operation_state(parameters.get("operation_id"), OperationState.PROCESSING, progress=30.0)

            # Try to launch through web interface first
            web_gui = self.gui_manager.get_gui_instance("web_interface")
            if web_gui and hasattr(web_gui, 'launch_ai_workbench'):
                result = await web_gui.launch_ai_workbench(parameters)

                # Also show in modern interface
                modern_gui = self.gui_manager.get_gui_instance("modern_interface")
                if modern_gui and hasattr(modern_gui, 'show_ai_workbench_tab'):
                    modern_gui.show_ai_workbench_tab()

                return f"AI Workbench launched via web interface: {result}"
            else:
                # Direct AI workbench launch
                ai_workbench = AIWorkbench()
                result = await ai_workbench.start_interactive_session(parameters)
                return f"AI Workbench started: {result}"

        except Exception as e:
            self.logger.error(f"AI Workbench launch failed: {e}")
            return f"AI Workbench launch failed: {str(e)}"

    async def _launch_benchmark(self, parameters: Dict) -> str:
        """Launch benchmark through actual GUI components"""
        try:
            self._update_operation_state(parameters.get("operation_id"), OperationState.PROCESSING, progress=35.0)

            # Launch benchmark with GUI integration
            modern_gui = self.gui_manager.get_gui_instance("modern_interface")
            if modern_gui and hasattr(modern_gui, 'start_benchmark'):
                result = await modern_gui.start_benchmark(parameters)

                # Show results in MEGA interface
                mega_gui = self.gui_manager.get_gui_instance("mega_opryxx")
                if mega_gui and hasattr(mega_gui, 'display_benchmark_results'):
                    mega_gui.display_benchmark_results(result)

                return f"Benchmark completed: {result}"
            else:
                # Direct benchmark execution
                benchmark = PerformanceBenchmark()
                result = await benchmark.run_full_benchmark(parameters)
                return f"Benchmark completed via direct execution: {result}"

        except Exception as e:
            self.logger.error(f"Benchmark launch failed: {e}")
            return f"Benchmark launch failed: {str(e)}"

    async def _optimize_memory(self, parameters: Dict) -> str:
        """Optimize memory through actual GUI components"""
        try:
            self._update_operation_state(parameters.get("operation_id"), OperationState.PROCESSING, progress=40.0)

            # Memory optimization with GUI feedback
            mega_gui = self.gui_manager.get_gui_instance("mega_opryxx")
            if mega_gui and hasattr(mega_gui, 'optimize_memory'):
                result = await mega_gui.optimize_memory(parameters)

                # Update progress in modern interface
                modern_gui = self.gui_manager.get_gui_instance("modern_interface")
                if modern_gui and hasattr(modern_gui, 'update_memory_status'):
                    modern_gui.update_memory_status(result)

                return f"Memory optimization completed: {result}"
            else:
                # Direct memory optimization
                memory_optimizer = MemoryOptimizer()
                result = await memory_optimizer.optimize(parameters)
                return f"Memory optimization completed: {result}"

        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return f"Memory optimization failed: {str(e)}"

    async def _show_file_explorer(self, parameters: Dict) -> str:
        """Show file explorer through actual GUI components"""
        try:
            # Show file explorer in modern interface
            modern_gui = self.gui_manager.get_gui_instance("modern_interface")
            if modern_gui and hasattr(modern_gui, 'show_file_explorer'):
                result = modern_gui.show_file_explorer(parameters)
                return f"File explorer opened: {result}"
            else:
                # Fallback to system file explorer
                import subprocess
                subprocess.Popen('explorer.exe')
                return "System file explorer opened"

        except Exception as e:
            self.logger.error(f"File explorer failed: {e}")
            return f"File explorer failed: {str(e)}"

    async def _show_git_interface(self, parameters: Dict) -> str:
        """Show git interface through actual GUI components"""
        try:
            # Show git interface in web GUI
            web_gui = self.gui_manager.get_gui_instance("web_interface")
            if web_gui and hasattr(web_gui, 'show_git_interface'):
                result = await web_gui.show_git_interface(parameters)
                return f"Git interface opened: {result}"
            else:
                # Show in modern interface
                modern_gui = self.gui_manager.get_gui_instance("modern_interface")
                if modern_gui and hasattr(modern_gui, 'show_git_tab'):
                    result = modern_gui.show_git_tab(parameters)
                    return f"Git tab opened: {result}"
                else:
                    return "Git interface not available in current GUI"

        except Exception as e:
            self.logger.error(f"Git interface failed: {e}")
            return f"Git interface failed: {str(e)}"

    async def _show_python_console(self, parameters: Dict) -> str:
        """Show python console through actual GUI components"""
        try:
            # Show Python console in modern interface
            modern_gui = self.gui_manager.get_gui_instance("modern_interface")
            if modern_gui and hasattr(modern_gui, 'show_python_console'):
                result = modern_gui.show_python_console(parameters)
                return f"Python console opened: {result}"
            else:
                # Show in web interface
                web_gui = self.gui_manager.get_gui_instance("web_interface")
                if web_gui and hasattr(web_gui, 'show_console'):
                    result = await web_gui.show_console(parameters)
                    return f"Python console opened in web interface: {result}"
                else:
                    return "Python console not available in current GUI"

        except Exception as e:
            self.logger.error(f"Python console failed: {e}")
            return f"Python console failed: {str(e)}"

    async def _show_help(self, parameters: Dict) -> str:
        """Show help through actual GUI components"""
        try:
            # Show help in all available interfaces
            help_shown = []

            # Modern interface help
            modern_gui = self.gui_manager.get_gui_instance("modern_interface")
            if modern_gui and hasattr(modern_gui, 'show_help'):
                modern_gui.show_help(parameters)
                help_shown.append("modern_interface")

            # Web interface help
            web_gui = self.gui_manager.get_gui_instance("web_interface")
            if web_gui and hasattr(web_gui, 'show_help'):
                await web_gui.show_help(parameters)
                help_shown.append("web_interface")

            # MEGA interface help
            mega_gui = self.gui_manager.get_gui_instance("mega_opryxx")
            if mega_gui and hasattr(mega_gui, 'show_help'):
                mega_gui.show_help(parameters)
                help_shown.append("mega_opryxx")

            if help_shown:
                return f"Help displayed in: {', '.join(help_shown)}"
            else:
                return "Help information: Please refer to documentation or contact support"

        except Exception as e:
            self.logger.error(f"Help display failed: {e}")
            return f"Help display failed: {str(e)}"

    # Enhanced event handlers for GUI integration
    def _handle_operation_update(self, data: Dict):
        """Handle operation update events with GUI synchronization"""
        try:
            operation_id = data.get("operation_id")
            state = data.get("state")
            progress = data.get("progress", 0.0)

            self.logger.info(f"Operation {operation_id} updated to {state} ({progress}%)")

            # Update all GUI components
            self._sync_gui_components(data)

        except Exception as e:
            self.logger.error(f"Operation update handling failed: {e}")

    def _handle_progress_update(self, data: Dict):
        """Handle progress update events with GUI synchronization"""
        try:
            operation_id = data.get("operation_id")
            progress = data.get("progress", 0.0)

            # Update progress in all GUI components
            for gui_name, gui_instance in self.gui_manager.gui_instances.items():
                if hasattr(gui_instance, 'update_progress'):
                    gui_instance.update_progress(operation_id, progress)

        except Exception as e:
            self.logger.error(f"Progress update handling failed: {e}")

    def _handle_error(self, data: Dict):
        """Handle error events"""
        self.logger.error(f"Error occurred: {data}")

    def _sync_gui_components(self, data: Dict):
        """Synchronize GUI components with the latest operation data"""
        try:
            for gui_name, gui_instance in self.gui_manager.gui_instances.items():
                if hasattr(gui_instance, 'sync_with_data'):
                    gui_instance.sync_with_data(data)

        except Exception as e:
            self.logger.error(f"GUI synchronization failed: {e}")
