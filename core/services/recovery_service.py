"""
Recovery Service
High-level recovery orchestration service
"""

from typing import List
from core.architecture.core import RecoveryOrchestrator, RecoveryResult
from core.architecture.config import ConfigManager
from core.modules.safe_mode import SafeModeModule
from core.modules.boot_repair import BootRepairModule
import logging

class RecoveryService:
    def __init__(self):
        self.config = ConfigManager().config
        self.orchestrator = RecoveryOrchestrator()
        self._setup_modules()
        self._setup_logging()
    
    def _setup_modules(self):
        modules = [
            SafeModeModule(),
            BootRepairModule()
        ]
        
        for module in modules:
            self.orchestrator.register_module(module)
    
    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config.system.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def execute_recovery(self) -> List[RecoveryResult]:
        return self.orchestrator.execute_recovery()
    
    def get_system_status(self) -> dict:
        return {
            'modules_registered': len(self.orchestrator.modules),
            'config_loaded': True,
            'version': self.config.system.version
        }