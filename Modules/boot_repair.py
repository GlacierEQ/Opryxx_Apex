"""
Boot Repair Module
Handles boot configuration repair
"""

import subprocess
from datetime import datetime
from architecture.core import BaseRecoveryModule, RecoveryResult, RecoveryStatus

class BootRepairModule(BaseRecoveryModule):
    def __init__(self):
        super().__init__("BootRepair")
    
    def validate_prerequisites(self) -> bool:
        tools = ['bootrec', 'bcdedit']
        return all(self._tool_available(tool) for tool in tools)
    
    def _tool_available(self, tool: str) -> bool:
        try:
            subprocess.run([tool, '/?'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def execute(self) -> RecoveryResult:
        repairs = [
            ('fixmbr', self._fix_mbr),
            ('fixboot', self._fix_boot),
            ('rebuildbcd', self._rebuild_bcd)
        ]
        
        results = {}
        overall_success = True
        
        for name, repair_func in repairs:
            success = repair_func()
            results[name] = success
            if not success:
                overall_success = False
        
        status = RecoveryStatus.SUCCESS if overall_success else RecoveryStatus.PARTIAL
        
        return RecoveryResult(
            status=status,
            message=f"Boot repair completed: {sum(results.values())}/{len(results)} successful",
            details=results,
            timestamp=datetime.now().isoformat()
        )
    
    def _fix_mbr(self) -> bool:
        try:
            result = subprocess.run(['bootrec', '/fixmbr'], 
                                  capture_output=True, timeout=60)
            return result.returncode == 0
        except:
            return False
    
    def _fix_boot(self) -> bool:
        try:
            result = subprocess.run(['bootrec', '/fixboot'], 
                                  capture_output=True, timeout=60)
            return result.returncode == 0
        except:
            return False
    
    def _rebuild_bcd(self) -> bool:
        try:
            result = subprocess.run(['bootrec', '/rebuildbcd'], 
                                  capture_output=True, timeout=120)
            return result.returncode == 0
        except:
            return False