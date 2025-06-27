"""
Safe Mode Recovery Module
Implements safe mode detection and clearing
"""

import subprocess
import os
from datetime import datetime
from architecture.core import BaseRecoveryModule, RecoveryResult, RecoveryStatus

class SafeModeModule(BaseRecoveryModule):
    def __init__(self):
        super().__init__("SafeMode")
    
    def validate_prerequisites(self) -> bool:
        try:
            subprocess.run(['bcdedit', '/?'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def execute(self) -> RecoveryResult:
        if self._is_safe_mode_active():
            return self._clear_safe_mode()
        
        return RecoveryResult(
            status=RecoveryStatus.SUCCESS,
            message="System not in safe mode",
            details={},
            timestamp=datetime.now().isoformat()
        )
    
    def _is_safe_mode_active(self) -> bool:
        return (os.environ.get('SAFEBOOT_OPTION') is not None or 
                self._check_boot_flags())
    
    def _check_boot_flags(self) -> bool:
        try:
            result = subprocess.run(['bcdedit', '/enum'], 
                                  capture_output=True, text=True)
            return 'safeboot' in result.stdout.lower()
        except:
            return False
    
    def _clear_safe_mode(self) -> RecoveryResult:
        try:
            result = subprocess.run(['bcdedit', '/deletevalue', '{current}', 'safeboot'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return RecoveryResult(
                    status=RecoveryStatus.SUCCESS,
                    message="Safe mode flags cleared",
                    details={'reboot_required': True},
                    timestamp=datetime.now().isoformat()
                )
            else:
                return RecoveryResult(
                    status=RecoveryStatus.FAILED,
                    message="Failed to clear safe mode flags",
                    details={'error': result.stderr},
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return RecoveryResult(
                status=RecoveryStatus.FAILED,
                message="Exception clearing safe mode",
                details={'error': str(e)},
                timestamp=datetime.now().isoformat()
            )