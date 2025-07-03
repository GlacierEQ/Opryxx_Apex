"""
Optimized Samsung SSD Recovery Module
"""

import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path
from core.base import BaseModule, ModuleResult
from core.logger import get_logger
from core.exceptions import RecoveryException

class SamsungRecoveryModule(BaseModule):
    """Optimized Samsung SSD recovery with BitLocker support"""
    
    def __init__(self):
        super().__init__("samsung_recovery")
        self.logger = get_logger("samsung_recovery")
        self.detected_drives = []
        
    def initialize(self) -> ModuleResult:
        """Initialize Samsung recovery module"""
        try:
            self.logger.info("Initializing Samsung recovery module")
            if not self._check_admin():
                return ModuleResult(False, "Administrator privileges required")
            return ModuleResult(True, "Samsung recovery module initialized")
        except Exception as e:
            return ModuleResult(False, f"Initialization failed: {e}", error=e)
    
    def execute(self, **kwargs) -> ModuleResult:
        """Execute Samsung SSD recovery"""
        recovery_key = kwargs.get('recovery_key')
        
        try:
            drives = self._detect_samsung_drives()
            if not drives:
                return ModuleResult(False, "No Samsung drives detected")
            
            results = []
            for drive in drives:
                result = self._recover_drive(drive, recovery_key)
                results.append(result)
            
            success_count = sum(1 for r in results if r['success'])
            return ModuleResult(
                success=success_count > 0,
                message=f"Recovered {success_count}/{len(results)} drives",
                data={'results': results}
            )
        except Exception as e:
            return ModuleResult(False, f"Recovery failed: {e}", error=e)
    
    def cleanup(self) -> ModuleResult:
        """Cleanup resources"""
        self.detected_drives.clear()
        return ModuleResult(True, "Cleanup completed")
    
    def _check_admin(self) -> bool:
        """Check administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _run_command(self, command: List[str], timeout: int = 300) -> tuple[bool, str]:
        """Execute command with error handling"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _detect_samsung_drives(self) -> List[Dict]:
        """Detect Samsung drives"""
        ps_command = [
            'powershell', '-Command',
            'Get-Disk | Where-Object {$_.FriendlyName -like "*Samsung*"} | '
            'Select-Object Number, FriendlyName, Size | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if not success:
            return []
        
        try:
            drives_data = json.loads(output) if output.strip() else []
            if not isinstance(drives_data, list):
                drives_data = [drives_data]
            
            drives = []
            for drive in drives_data:
                size_gb = int(drive.get('Size', 0)) / (1024**3)
                if 3800 <= size_gb <= 4200:
                    drives.append({
                        'number': drive.get('Number'),
                        'name': drive.get('FriendlyName'),
                        'size_gb': size_gb
                    })
            
            self.detected_drives = drives
            return drives
        except:
            return []
    
    def _recover_drive(self, drive: Dict, recovery_key: str) -> Dict:
        """Recover individual drive"""
        drive_number = drive['number']
        
        # Get drive letters
        letters = self._get_drive_letters(drive_number)
        if not letters:
            return {'success': False, 'error': 'No partitions found'}
        
        for letter in letters:
            if Path(f"{letter}:\\").exists():
                return {'success': True, 'drive_letter': letter}
            
            # Try BitLocker unlock
            if recovery_key and self._unlock_bitlocker(letter, recovery_key):
                if Path(f"{letter}:\\").exists():
                    return {'success': True, 'drive_letter': letter}
        
        return {'success': False, 'error': 'Recovery failed'}
    
    def _get_drive_letters(self, disk_number: int) -> List[str]:
        """Get drive letters for disk"""
        ps_command = [
            'powershell', '-Command',
            f'Get-Partition -DiskNumber {disk_number} | '
            'Where-Object {{$_.DriveLetter}} | Select-Object DriveLetter | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if not success:
            return []
        
        try:
            partitions = json.loads(output) if output.strip() else []
            if not isinstance(partitions, list):
                partitions = [partitions]
            return [p.get('DriveLetter', '') for p in partitions if p.get('DriveLetter')]
        except:
            return []
    
    def _unlock_bitlocker(self, drive_letter: str, recovery_key: str) -> bool:
        """Unlock BitLocker drive"""
        ps_command = [
            'powershell', '-Command',
            f'Unlock-BitLocker -MountPoint "{drive_letter}:" -RecoveryPassword "{recovery_key}"'
        ]
        
        success, _ = self._run_command(ps_command, timeout=120)
        return success