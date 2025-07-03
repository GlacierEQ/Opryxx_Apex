"""
Optimized Dell Recovery Module
"""

import subprocess
import json
from typing import Dict, List
from core.base import BaseModule, ModuleResult
from core.logger import get_logger

class DellRecoveryModule(BaseModule):
    """Dell Inspiron boot recovery module"""
    
    def __init__(self):
        super().__init__("dell_recovery")
        self.logger = get_logger("dell_recovery")
        self.system_info = {}
        
    def initialize(self) -> ModuleResult:
        """Initialize Dell recovery module"""
        try:
            if not self._check_admin():
                return ModuleResult(False, "Administrator privileges required")
            
            self.system_info = self._detect_dell_system()
            return ModuleResult(True, "Dell recovery module initialized")
        except Exception as e:
            return ModuleResult(False, f"Initialization failed: {e}", error=e)
    
    def execute(self, **kwargs) -> ModuleResult:
        """Execute Dell recovery"""
        try:
            issues = self._check_boot_issues()
            if not issues:
                return ModuleResult(True, "No boot issues detected")
            
            fixed_issues = []
            for issue in issues:
                if self._fix_issue(issue):
                    fixed_issues.append(issue)
            
            return ModuleResult(
                success=len(fixed_issues) > 0,
                message=f"Fixed {len(fixed_issues)}/{len(issues)} issues",
                data={'fixed': fixed_issues, 'total': issues}
            )
        except Exception as e:
            return ModuleResult(False, f"Recovery failed: {e}", error=e)
    
    def cleanup(self) -> ModuleResult:
        """Cleanup resources"""
        return ModuleResult(True, "Cleanup completed")
    
    def _check_admin(self) -> bool:
        """Check administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _run_command(self, command: List[str]) -> tuple[bool, str]:
        """Execute command"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def _detect_dell_system(self) -> Dict:
        """Detect Dell system"""
        ps_command = [
            'powershell', '-Command',
            'Get-WmiObject -Class Win32_ComputerSystem | '
            'Select-Object Manufacturer, Model | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if success:
            try:
                data = json.loads(output)
                return {
                    'manufacturer': data.get('Manufacturer', '').lower(),
                    'model': data.get('Model', '').lower(),
                    'is_dell': 'dell' in data.get('Manufacturer', '').lower()
                }
            except:
                pass
        
        return {'is_dell': False}
    
    def _check_boot_issues(self) -> List[str]:
        """Check for boot issues"""
        issues = []
        
        # Check BCD
        success, output = self._run_command(['bcdedit', '/enum'])
        if not success:
            issues.append('bcd_corruption')
        elif 'windows boot loader' not in output.lower():
            issues.append('missing_bootloader')
        elif 'safeboot' in output.lower():
            issues.append('safe_boot_stuck')
        
        # Check UEFI
        success, output = self._run_command(['bcdedit', '/enum', 'firmware'])
        if success and 'windows boot manager' not in output.lower():
            issues.append('uefi_missing')
        
        return issues
    
    def _fix_issue(self, issue: str) -> bool:
        """Fix specific boot issue"""
        if issue == 'bcd_corruption':
            return self._fix_bcd_corruption()
        elif issue == 'missing_bootloader':
            return self._fix_missing_bootloader()
        elif issue == 'safe_boot_stuck':
            return self._fix_safe_boot()
        elif issue == 'uefi_missing':
            return self._fix_uefi_boot()
        return False
    
    def _fix_bcd_corruption(self) -> bool:
        """Fix BCD corruption"""
        commands = [
            ['bootrec', '/fixmbr'],
            ['bootrec', '/fixboot'],
            ['bootrec', '/rebuildbcd']
        ]
        
        for cmd in commands:
            success, _ = self._run_command(cmd)
            if not success:
                return False
        return True
    
    def _fix_missing_bootloader(self) -> bool:
        """Fix missing bootloader"""
        success, _ = self._run_command(['bootrec', '/rebuildbcd'])
        return success
    
    def _fix_safe_boot(self) -> bool:
        """Fix safe boot stuck"""
        success, _ = self._run_command(['bcdedit', '/deletevalue', '{current}', 'safeboot'])
        return success
    
    def _fix_uefi_boot(self) -> bool:
        """Fix UEFI boot"""
        commands = [
            ['bcdedit', '/set', '{fwbootmgr}', 'displayorder', '{bootmgr}', '/addfirst'],
            ['bcdboot', 'C:\\Windows', '/s', 'C:', '/f', 'UEFI']
        ]
        
        for cmd in commands:
            success, _ = self._run_command(cmd)
            if not success:
                return False
        return True