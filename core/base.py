"""
Base classes and interfaces for OPRYXX modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import threading
import time
from datetime import datetime

class ModuleStatus(Enum):
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    STOPPING = "stopping"

@dataclass
class ModuleResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None

class BaseModule(ABC):
    """Base class for all OPRYXX modules"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = ModuleStatus.INACTIVE
        self._lock = threading.Lock()
        self._initialized = False
        self.config = {}
        
    @abstractmethod
    def initialize(self) -> ModuleResult:
        """Initialize the module"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ModuleResult:
        """Execute module functionality"""
        pass
    
    @abstractmethod
    def cleanup(self) -> ModuleResult:
        """Cleanup module resources"""
        pass
    
    def get_status(self) -> ModuleStatus:
        """Get current module status"""
        with self._lock:
            return self.status
    
    def set_status(self, status: ModuleStatus):
        """Set module status thread-safely"""
        with self._lock:
            self.status = status
    
    def is_ready(self) -> bool:
        """Check if module is ready for execution"""
        return self.status == ModuleStatus.ACTIVE

class ModuleRegistry:
    """Registry for managing OPRYXX modules"""
    
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
        self._lock = threading.Lock()
    
    def register(self, module: BaseModule) -> bool:
        """Register a module"""
        with self._lock:
            if module.name in self._modules:
                return False
            self._modules[module.name] = module
            return True
    
    def unregister(self, name: str) -> bool:
        """Unregister a module"""
        with self._lock:
            if name in self._modules:
                module = self._modules[name]
                module.cleanup()
                del self._modules[name]
                return True
            return False
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """Get module by name"""
        with self._lock:
            return self._modules.get(name)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """Get all registered modules"""
        with self._lock:
            return self._modules.copy()
    
    def initialize_all(self) -> Dict[str, ModuleResult]:
        """Initialize all registered modules"""
        results = {}
        for name, module in self._modules.items():
            try:
                module.set_status(ModuleStatus.INITIALIZING)
                result = module.initialize()
                if result.success:
                    module.set_status(ModuleStatus.ACTIVE)
                else:
                    module.set_status(ModuleStatus.ERROR)
                results[name] = result
            except Exception as e:
                module.set_status(ModuleStatus.ERROR)
                results[name] = ModuleResult(False, f"Initialization failed: {e}", error=e)
        return results
    
    def cleanup_all(self) -> Dict[str, ModuleResult]:
        """Cleanup all registered modules"""
        results = {}
        for name, module in self._modules.items():
            try:
                module.set_status(ModuleStatus.STOPPING)
                result = module.cleanup()
                module.set_status(ModuleStatus.INACTIVE)
                results[name] = result
            except Exception as e:
                results[name] = ModuleResult(False, f"Cleanup failed: {e}", error=e)
        return results