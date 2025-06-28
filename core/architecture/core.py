"""
OPRYXX Core Architecture
Base classes and interfaces following best practices
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import time
from typing import Dict, List, Optional, Protocol, Set, Tuple, Type, Any, Callable

class RecoveryStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class RecoveryResult:
    status: RecoveryStatus
    message: str
    details: Dict
    timestamp: str

class RecoveryOperation(Protocol):
    def execute(self) -> RecoveryResult: ...
    def validate(self) -> bool: ...
    def rollback(self) -> bool: ...

class BaseRecoveryModule(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"OPRYXX.{name}")
    
    @abstractmethod
    def execute(self) -> RecoveryResult: ...
    
    @abstractmethod
    def validate_prerequisites(self) -> bool: ...

class RecoveryOrchestrator:
    """
    Manages the execution of recovery modules with support for parallel execution,
    dependency management, and timeouts.
    
    Features:
    - Parallel execution of independent modules
    - Module dependencies support
    - Configurable timeouts
    - Comprehensive error handling
    - Detailed execution metrics
    """
    
    def __init__(self, max_workers: int = 4, module_timeout: int = 300):
        """
        Initialize the RecoveryOrchestrator.
        
        Args:
            max_workers: Maximum number of modules to execute in parallel
            module_timeout: Default timeout in seconds for module execution
        """
        self.modules: Dict[str, BaseRecoveryModule] = {}
        self.dependencies: Dict[str, Set[str]] = {}  # module_name -> set of dependencies
        self.logger = logging.getLogger("OPRYXX.Orchestrator")
        self.max_workers = max_workers
        self.module_timeout = module_timeout
        self.execution_metrics: Dict[str, Dict[str, Any]] = {}
    
    def register_module(self, module: BaseRecoveryModule, 
                       dependencies: Optional[List[str]] = None):
        """
        Register a recovery module with optional dependencies.
        
        Args:
            module: The module to register
            dependencies: List of module names this module depends on
        """
        self.modules[module.name] = module
        self.dependencies[module.name] = set(dependencies or [])
        self.logger.debug(f"Registered module: {module.name} with dependencies: {dependencies}")
    
    def _validate_dependencies(self) -> bool:
        """Validate that all dependencies exist."""
        for module_name, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.modules:
                    self.logger.error(f"Dependency {dep} not found for module {module_name}")
                    return False
        return True
    
    def _get_ready_modules(self, executed: Set[str]) -> List[BaseRecoveryModule]:
        """Get modules that have all their dependencies satisfied and are ready to execute."""
        ready = []
        for name, module in self.modules.items():
            if name not in executed and all(dep in executed for dep in self.dependencies[name]):
                ready.append(module)
        return ready
    
    def _execute_module(self, module: BaseRecoveryModule) -> Tuple[str, RecoveryResult]:
        """Execute a single module with timeout and error handling."""
        start_time = time.time()
        result = None
        status = RecoveryStatus.FAILED
        
        try:
            self.logger.info(f"Executing module: {module.name}")
            if module.validate_prerequisites():
                result = module.execute()
                status = result.status
            else:
                result = RecoveryResult(
                    status=RecoveryStatus.FAILED,
                    message=f"Prerequisites not met for module: {module.name}",
                    details={"module": module.name},
                    timestamp=datetime.utcnow().isoformat()
                )
        except Exception as e:
            self.logger.error(f"Error executing module {module.name}: {str(e)}", exc_info=True)
            result = RecoveryResult(
                status=RecoveryStatus.FAILED,
                message=f"Error executing module {module.name}: {str(e)}",
                details={"module": module.name, "error": str(e)},
                timestamp=datetime.utcnow().isoformat()
            )
        finally:
            duration = time.time() - start_time
            self.execution_metrics[module.name] = {
                "status": status,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.logger.info(f"Completed module {module.name} in {duration:.2f}s with status: {status}")
        
        return module.name, result
    
    def execute_recovery(self) -> Dict[str, RecoveryResult]:
        """
        Execute recovery modules respecting dependencies and with parallel execution.
        
        Returns:
            Dictionary mapping module names to their execution results
        """
        if not self._validate_dependencies():
            raise ValueError("Invalid module dependencies detected")
        
        results: Dict[str, RecoveryResult] = {}
        executed: Set[str] = set()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Continue while there are modules left to execute
            while len(executed) < len(self.modules):
                # Get modules that are ready to execute
                ready_modules = self._get_ready_modules(executed)
                
                if not ready_modules:
                    # No modules are ready to execute due to circular dependencies or errors
                    break
                
                # Submit ready modules for execution
                future_to_module = {
                    executor.submit(self._execute_module, module): module
                    for module in ready_modules
                }
                
                # Process completed modules
                for future in as_completed(future_to_module, timeout=self.module_timeout):
                    module = future_to_module[future]
                    try:
                        module_name, result = future.result()
                        results[module_name] = result
                        executed.add(module_name)
                        
                        # If any module fails, mark all remaining modules as failed
                        if result.status == RecoveryStatus.FAILED:
                            for name in self.modules:
                                if name not in executed and name not in results:
                                    results[name] = RecoveryResult(
                                        status=RecoveryStatus.FAILED,
                                        message=f"Skipped due to failure in {module_name}",
                                        details={"dependency_failure": module_name},
                                        timestamp=datetime.utcnow().isoformat()
                                    )
                            return results
                            
                    except FutureTimeoutError:
                        self.logger.error(f"Module {module.name} timed out after {self.module_timeout}s")
                        results[module.name] = RecoveryResult(
                            status=RecoveryStatus.FAILED,
                            message=f"Module timed out after {self.module_timeout}s",
                            details={"module": module.name, "timeout_seconds": self.module_timeout},
                            timestamp=datetime.utcnow().isoformat()
                        )
                        return results
                    except Exception as e:
                        self.logger.error(f"Unexpected error executing module {module.name}: {str(e)}")
                        results[module.name] = RecoveryResult(
                            status=RecoveryStatus.FAILED,
                            message=f"Unexpected error: {str(e)}",
                            details={"module": module.name, "error": str(e)},
                            timestamp=datetime.utcnow().isoformat()
                        )
                        return results
        
        return results
    
    def get_execution_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics about module execution."""
        return self.execution_metrics