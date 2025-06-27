"""
OPRYXX Core Architecture
Base classes and interfaces following best practices
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol
from enum import Enum
import logging

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
    def __init__(self):
        self.modules: List[BaseRecoveryModule] = []
        self.logger = logging.getLogger("OPRYXX.Orchestrator")
    
    def register_module(self, module: BaseRecoveryModule):
        self.modules.append(module)
    
    def execute_recovery(self) -> List[RecoveryResult]:
        results = []
        for module in self.modules:
            if module.validate_prerequisites():
                result = module.execute()
                results.append(result)
                if result.status == RecoveryStatus.FAILED:
                    break
        return results