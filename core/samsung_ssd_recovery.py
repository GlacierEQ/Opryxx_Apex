import subprocess
import logging
import json
import os
import ctypes
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

class Samsung4TBRecovery:
    """Specialized recovery for Samsung 4TB NVMe SSD with RAW + BitLocker"""

    def __init__(self, drive_letter: str = None, recovery_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.recovery_log = []
        self.temp_mount_point = Path("temp_recovery_mount")
        self.drive_letter = drive_letter.upper() if drive_letter else None
        self.recovery_key = recovery_key
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin privileges"""
        try:
            return os.getuid() == 0 if os.name == 'posix' else ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def _run_command(self, command: List[str]) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, f"Command failed: {e.stderr or e.stdout}"
            
    def _get_disk_info(self) -> Dict:
        """Get detailed disk information using PowerShell"""
        success, output = self._run_command([
            'powershell', 
            'Get-Disk | Select-Object Number, FriendlyName, Size, HealthStatus, OperationalStatus, PartitionStyle | ConvertTo-Json'
        ])
        return json.loads(output) if success and output else {}

    def _find_samsung_4tb_drive(self) -> Optional[str]:
        """Locate the Samsung 4TB SSD by its properties"""
        try:
            disks = self._get_disk_info()
            if not isinstance(disks, list):
                disks = [disks] if disks else []
                
            for disk in disks:
                if 'FriendlyName' in disk and 'Samsung' in disk['FriendlyName']:
                    size_gb = int(disk.get('Size', 0)) / (1024**3)
                    if 3800 <= size_gb <= 4096:  # Approximate 4TB range
                        return disk['Number']
        except Exception as e:
            self.logger.error(f"Error finding Samsung drive: {e}")
        return None

    def _unlock_bitlocker(self, drive_letter: str) -> bool:
        """Unlock BitLocker volume using recovery key"""
        if not self.recovery_key:
            self.logger.error("No BitLocker recovery key provided")
            return False
            
        self.logger.info(f"Attempting to unlock drive {drive_letter} with BitLocker...")
        success, output = self._run_command([
            'powershell',
            f'Unlock-BitLocker -MountPoint "{drive_letter}:" -RecoveryPassword "{self.recovery_key}" -ErrorAction Stop'
        ])
        
        if success:
            self.logger.info(f"Successfully unlocked drive {drive_letter}")
            return True
        else:
            self.logger.error(f"Failed to unlock drive {drive_letter}: {output}")
            return False

    def _repair_volume(self, drive_letter: str) -> bool:
        """Run chkdsk to repair volume errors"""
        self.logger.info(f"Running chkdsk on drive {drive_letter}...")
        success, output = self._run_command([
            'chkdsk',
            f'{drive_letter}:',
            '/f',
            '/r',
            '/x'
        ])
        
        if success:
            self.logger.info(f"chkdsk completed successfully on drive {drive_letter}")
            return True
        else:
            self.logger.error(f"chkdsk failed on drive {drive_letter}: {output}")
            return False

    def analyze_samsung_drive(self, drive_path: str = None) -> Dict[str, Any]:
        """Comprehensive analysis of the Samsung 4TB drive"""
        drive_path = drive_path or self.drive_letter
        if not drive_path:
            return {"error": "No drive path specified"}
            
        analysis = {
            'drive_path': drive_path,
            'physical_health': self._check_physical_health(drive_path),
            'partition_table': self._analyze_partition_table(drive_path),
            'bitlocker_status': self._analyze_bitlocker_status(drive_path),
            'file_system': self._check_file_system(drive_path),
            'recovery_options': []
        }

        # Determine recovery strategy
        analysis['recovery_strategy'] = self._determine_recovery_strategy(analysis)
        return analysis

    def _check_physical_health(self, drive_path: str) -> Dict[str, Any]:
        """Check physical health of the drive using S.M.A.R.T."""
        try:
            if os.name == 'nt':
                # Windows implementation using PowerShell
                cmd = [
                    'powershell',
                    'Get-PhysicalDisk | Where-Object { $_.DeviceId -eq ' + \
                    f'"{drive_path[0].upper()}" }} | Select-Object HealthStatus, OperationalStatus | ConvertTo-Json'
                ]
                success, output = self._run_command(cmd)
                if success and output:
                    return json.loads(output)
            else:
                # Linux implementation using smartctl
                cmd = ['sudo', 'smartctl', '-H', f'/dev/{drive_path}']
                success, output = self._run_command(cmd)
                if success:
                    return {"status": "healthy" if "PASSED" in output else "warning"}
        except Exception as e:
            self.logger.error(f"Error checking physical health: {e}")
        return {"status": "unknown", "error": "Failed to check physical health"}

    def _analyze_partition_table(self, drive_path: str) -> Dict[str, Any]:
        """Analyze the partition table"""
        try:
            if os.name == 'nt':
                cmd = ['powershell', f'Get-Partition -DiskNumber {drive_path} | ConvertTo-Json']
            else:
                cmd = ['lsblk', '-f', '-J', f'/dev/{drive_path}']
                
            success, output = self._run_command(cmd)
            if success and output:
                return json.loads(output)
        except Exception as e:
            self.logger.error(f"Error analyzing partition table: {e}")
        return {"error": "Failed to analyze partition table"}

    def _analyze_bitlocker_status(self, drive_path: str) -> Dict[str, Any]:
        """Check BitLocker status of the drive"""
        if os.name != 'nt':
            return {"status": "not_applicable", "message": "BitLocker is a Windows feature"}
            
        try:
            cmd = [
                'powershell',
                f'$vol = Get-Volume -DriveLetter {drive_path[0].upper()}; ' +
                'Get-BitLockerVolume -MountPoint $vol.UniqueId | ConvertTo-Json'
            ]
            success, output = self._run_command(cmd)
            if success and output:
                return json.loads(output)
            return {"status": "not_encrypted"}
        except Exception as e:
            self.logger.error(f"Error checking BitLocker status: {e}")
            return {"status": "error", "message": str(e)}

    def _check_file_system(self, drive_path: str) -> Dict[str, Any]:
        """Check the file system status"""
        try:
            if os.name == 'nt':
                cmd = ['fsutil', 'fsinfo', 'volumeinfo', f'{drive_path[0].upper()}:']
            else:
                cmd = ['df', '-T', f'/dev/{drive_path}']
                
            success, output = self._run_command(cmd)
            if success:
                return {"status": "ok", "details": output}
        except Exception as e:
            self.logger.error(f"Error checking file system: {e}")
        return {"status": "error", "message": "Failed to check file system"}

    def _determine_recovery_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best recovery strategy based on analysis"""
        strategy = {
            "recommended_actions": [],
            "warnings": [],
            "critical_issues": []
        }
        
        # Check for physical health issues
        if analysis['physical_health'].get('status') != 'healthy':
            strategy['critical_issues'].append("Drive health check failed - backup data immediately")
            
        # Check for BitLocker encryption
        if analysis['bitlocker_status'].get('VolumeStatus') == 'FullyEncrypted':
            if not self.recovery_key:
                strategy['critical_issues'].append("BitLocker encrypted - recovery key required")
            else:
                strategy['recommended_actions'].append("Unlock BitLocker encryption")
                
        # Check for file system issues
        if analysis['file_system'].get('status') == 'error':
            strategy['recommended_actions'].append("Repair file system")
            
        # If no critical issues, suggest data recovery
        if not strategy['critical_issues']:
            strategy['recommended_actions'].append("Attempt data recovery")
            
        return strategy

    def recover_samsung_4tb_drive(self, drive_path: str = None, recovery_key: str = None) -> Dict[str, Any]:
        """
        Full recovery process for Samsung 4TB SSD
        Returns:
            Dict with success status and recovery details
        """
        if not self.is_admin:
            return {"success": False, "error": "Administrator privileges required"}
            
        self.drive_letter = (drive_path or self.drive_letter)
        self.recovery_key = recovery_key or self.recovery_key
        
        if not self.drive_letter:
            # Try to automatically find the Samsung 4TB drive
            disk_number = self._find_samsung_4tb_drive()
            if not disk_number:
                return {"success": False, "error": "Samsung 4TB drive not found"}
            self.drive_letter = chr(65 + int(disk_number))  # Convert disk number to drive letter
        
        # Step 1: Check if drive is accessible
        if os.path.exists(f"{self.drive_letter}:\\"):
            self.logger.info(f"Drive {self.drive_letter} is accessible")
            return {"success": True, "message": f"Drive {self.drive_letter} is already accessible"}
            
        # Step 2: Try to unlock BitLocker if key is provided
        if self.recovery_key:
            if self._unlock_bitlocker(self.drive_letter):
                return {"success": True, 
                       "message": f"Successfully unlocked BitLocker on drive {self.drive_letter}"}
                        
        # Step 3: Attempt to repair the volume
        if self._repair_volume(self.drive_letter):
            return {"success": True, 
                   "message": f"Successfully repaired volume on drive {self.drive_letter}"}
                   
        # If we get here, recovery failed
        return {
            "success": False, 
            "error": "Could not recover the drive. Please check the logs for details.",
            "suggestions": [
                "Verify the drive is properly connected",
                "Check if the drive is detected in Disk Management",
                "Try using a different USB port or cable",
                "Consider professional data recovery services if data is critical"
            ]
        }
