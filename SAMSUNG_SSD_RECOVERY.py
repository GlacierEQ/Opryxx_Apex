#!/usr/bin/env python3
"""
OPRYXX Samsung SSD Recovery Module
Advanced recovery for Samsung 4TB SSD with BitLocker support
"""

import os
import sys
import json
import time
import subprocess
import ctypes
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DriveInfo:
    number: int
    letter: str
    name: str
    size_gb: float
    health: str
    status: str
    filesystem: str
    encrypted: bool

class SamsungSSDRecovery:
    """Advanced Samsung SSD recovery with BitLocker support"""
    
    def __init__(self, recovery_key: str = None):
        self.recovery_key = recovery_key
        self.is_admin = self._check_admin_privileges()
        self.detected_drives = []
        self.recovery_log = []
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _run_command(self, command: List[str], timeout: int = 300) -> Tuple[bool, str]:
        """Execute command with timeout and error handling"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _log_action(self, action: str, success: bool, details: str = ""):
        """Log recovery actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'success': success,
            'details': details
        }
        self.recovery_log.append(log_entry)
        logger.info(f"{action}: {'SUCCESS' if success else 'FAILED'} - {details}")
    
    def detect_samsung_drives(self) -> List[DriveInfo]:
        """Detect all Samsung drives in the system"""
        self._log_action("Detecting Samsung drives", True, "Starting detection")
        
        drives = []
        
        # Get disk information using PowerShell
        ps_command = [
            'powershell', '-Command',
            'Get-Disk | Select-Object Number, FriendlyName, Size, HealthStatus, OperationalStatus, PartitionStyle | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if not success:
            self._log_action("PowerShell disk detection", False, output)
            return drives
        
        try:
            disk_data = json.loads(output)
            if not isinstance(disk_data, list):
                disk_data = [disk_data] if disk_data else []
            
            for disk in disk_data:
                name = disk.get('FriendlyName', '').lower()
                if 'samsung' in name:
                    size_gb = int(disk.get('Size', 0)) / (1024**3)
                    
                    # Check if it's around 4TB
                    is_4tb = 3800 <= size_gb <= 4200
                    
                    drive_info = DriveInfo(
                        number=disk.get('Number', -1),
                        letter="",  # Will be determined later
                        name=disk.get('FriendlyName', ''),
                        size_gb=size_gb,
                        health=disk.get('HealthStatus', 'Unknown'),
                        status=disk.get('OperationalStatus', 'Unknown'),
                        filesystem="Unknown",
                        encrypted=False
                    )
                    
                    drives.append(drive_info)
                    self._log_action(f"Found Samsung drive", True, 
                                   f"Disk {drive_info.number}: {drive_info.name} ({size_gb:.1f}GB)")
        
        except json.JSONDecodeError as e:
            self._log_action("JSON parsing", False, str(e))
        
        self.detected_drives = drives
        return drives
    
    def get_drive_letters(self, disk_number: int) -> List[str]:
        """Get drive letters for a specific disk"""
        ps_command = [
            'powershell', '-Command',
            f'Get-Partition -DiskNumber {disk_number} | Where-Object {{$_.DriveLetter}} | Select-Object DriveLetter | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if not success:
            return []
        
        try:
            partition_data = json.loads(output)
            if not isinstance(partition_data, list):
                partition_data = [partition_data] if partition_data else []
            
            return [p.get('DriveLetter', '') for p in partition_data if p.get('DriveLetter')]
        except:
            return []
    
    def check_bitlocker_status(self, drive_letter: str) -> Dict:
        """Check BitLocker encryption status"""
        ps_command = [
            'powershell', '-Command',
            f'Get-BitLockerVolume -MountPoint "{drive_letter}:" | Select-Object MountPoint, EncryptionPercentage, LockStatus, ProtectionStatus | ConvertTo-Json'
        ]
        
        success, output = self._run_command(ps_command)
        if not success:
            return {'encrypted': False, 'locked': False, 'error': output}
        
        try:
            bitlocker_data = json.loads(output)
            return {
                'encrypted': bitlocker_data.get('EncryptionPercentage', 0) > 0,
                'locked': bitlocker_data.get('LockStatus') == 'Locked',
                'protection_status': bitlocker_data.get('ProtectionStatus', 'Unknown'),
                'encryption_percentage': bitlocker_data.get('EncryptionPercentage', 0)
            }
        except:
            return {'encrypted': False, 'locked': False, 'error': 'Failed to parse BitLocker status'}
    
    def unlock_bitlocker_drive(self, drive_letter: str) -> bool:
        """Unlock BitLocker encrypted drive using recovery key"""
        if not self.recovery_key:
            self._log_action(f"BitLocker unlock {drive_letter}", False, "No recovery key provided")
            return False
        
        self._log_action(f"Unlocking BitLocker drive {drive_letter}", True, "Starting unlock process")
        
        # First, try with recovery password
        ps_command = [
            'powershell', '-Command',
            f'Unlock-BitLocker -MountPoint "{drive_letter}:" -RecoveryPassword "{self.recovery_key}"'
        ]
        
        success, output = self._run_command(ps_command, timeout=120)
        
        if success:
            self._log_action(f"BitLocker unlock {drive_letter}", True, "Successfully unlocked with recovery key")
            return True
        else:
            # Try alternative method with manage-bde
            cmd_command = [
                'manage-bde', '-unlock', f'{drive_letter}:', '-RecoveryPassword', self.recovery_key
            ]
            
            success2, output2 = self._run_command(cmd_command, timeout=120)
            
            if success2:
                self._log_action(f"BitLocker unlock {drive_letter}", True, "Successfully unlocked with manage-bde")
                return True
            else:
                self._log_action(f"BitLocker unlock {drive_letter}", False, f"PowerShell: {output}, manage-bde: {output2}")
                return False
    
    def repair_filesystem(self, drive_letter: str) -> bool:
        """Repair filesystem using chkdsk"""
        self._log_action(f"Filesystem repair {drive_letter}", True, "Starting chkdsk")
        
        # Run chkdsk with repair options
        chkdsk_command = [
            'chkdsk', f'{drive_letter}:', '/f', '/r', '/x'
        ]
        
        success, output = self._run_command(chkdsk_command, timeout=3600)  # 1 hour timeout
        
        if success:
            self._log_action(f"Filesystem repair {drive_letter}", True, "chkdsk completed successfully")
            return True
        else:
            self._log_action(f"Filesystem repair {drive_letter}", False, output)
            return False
    
    def create_drive_image(self, drive_letter: str, image_path: str) -> bool:
        """Create disk image for data recovery"""
        self._log_action(f"Creating drive image {drive_letter}", True, f"Target: {image_path}")
        
        # Use robocopy for file-level backup
        robocopy_command = [
            'robocopy', f'{drive_letter}:\\', image_path, '/E', '/COPYALL', '/R:3', '/W:10'
        ]
        
        success, output = self._run_command(robocopy_command, timeout=7200)  # 2 hour timeout
        
        # Robocopy returns different exit codes, 0-7 are generally success
        if success or "copied" in output.lower():
            self._log_action(f"Drive image {drive_letter}", True, "Image created successfully")
            return True
        else:
            self._log_action(f"Drive image {drive_letter}", False, output)
            return False
    
    def recover_samsung_4tb(self, target_drive_letter: str = None) -> Dict:
        """Main recovery function for Samsung 4TB SSD"""
        recovery_result = {
            'success': False,
            'drives_found': 0,
            'drives_recovered': 0,
            'errors': [],
            'actions_taken': []
        }
        
        if not self.is_admin:
            recovery_result['errors'].append("Administrator privileges required")
            return recovery_result
        
        # Step 1: Detect Samsung drives
        samsung_drives = self.detect_samsung_drives()
        recovery_result['drives_found'] = len(samsung_drives)
        
        if not samsung_drives:
            recovery_result['errors'].append("No Samsung drives detected")
            return recovery_result
        
        # Step 2: Process each Samsung drive
        for drive in samsung_drives:
            self._log_action(f"Processing drive {drive.number}", True, f"{drive.name} ({drive.size_gb:.1f}GB)")
            
            # Get drive letters
            drive_letters = self.get_drive_letters(drive.number)
            
            if not drive_letters:
                self._log_action(f"Drive {drive.number}", False, "No accessible drive letters found")
                continue
            
            # Process each partition
            for letter in drive_letters:
                if target_drive_letter and letter != target_drive_letter:
                    continue
                
                self._log_action(f"Processing partition {letter}", True, "Checking accessibility")
                
                # Check if drive is accessible
                if os.path.exists(f"{letter}:\\"):
                    self._log_action(f"Drive {letter} accessible", True, "Drive is already accessible")
                    recovery_result['drives_recovered'] += 1
                    recovery_result['actions_taken'].append(f"Drive {letter} was already accessible")
                    continue
                
                # Check BitLocker status
                bitlocker_status = self.check_bitlocker_status(letter)
                
                if bitlocker_status.get('encrypted', False):
                    self._log_action(f"BitLocker detected on {letter}", True, 
                                   f"Locked: {bitlocker_status.get('locked', False)}")
                    
                    if bitlocker_status.get('locked', False):
                        # Attempt to unlock
                        if self.unlock_bitlocker_drive(letter):
                            recovery_result['actions_taken'].append(f"Unlocked BitLocker on drive {letter}")
                            recovery_result['drives_recovered'] += 1
                        else:
                            recovery_result['errors'].append(f"Failed to unlock BitLocker on drive {letter}")
                            continue
                
                # Check if drive is now accessible
                if os.path.exists(f"{letter}:\\"):
                    self._log_action(f"Drive {letter} recovery", True, "Drive is now accessible")
                    recovery_result['drives_recovered'] += 1
                    recovery_result['actions_taken'].append(f"Successfully recovered drive {letter}")
                else:
                    # Try filesystem repair
                    if self.repair_filesystem(letter):
                        recovery_result['actions_taken'].append(f"Repaired filesystem on drive {letter}")
                        if os.path.exists(f"{letter}:\\"):
                            recovery_result['drives_recovered'] += 1
                    else:
                        recovery_result['errors'].append(f"Failed to repair filesystem on drive {letter}")
        
        recovery_result['success'] = recovery_result['drives_recovered'] > 0
        return recovery_result
    
    def get_recovery_report(self) -> str:
        """Generate detailed recovery report"""
        report = []
        report.append("SAMSUNG SSD RECOVERY REPORT")
        report.append("=" * 50)
        report.append(f"Recovery started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Administrator privileges: {'Yes' if self.is_admin else 'No'}")
        report.append(f"BitLocker recovery key provided: {'Yes' if self.recovery_key else 'No'}")
        report.append("")
        
        report.append("DETECTED DRIVES:")
        for i, drive in enumerate(self.detected_drives, 1):
            report.append(f"{i}. {drive.name}")
            report.append(f"   Size: {drive.size_gb:.1f} GB")
            report.append(f"   Health: {drive.health}")
            report.append(f"   Status: {drive.status}")
            report.append("")
        
        report.append("RECOVERY ACTIONS:")
        for i, action in enumerate(self.recovery_log, 1):
            status = "✅" if action['success'] else "❌"
            report.append(f"{i}. {status} {action['action']}")
            if action['details']:
                report.append(f"   Details: {action['details']}")
        
        return "\n".join(report)

def main():
    """Main function for Samsung SSD recovery"""
    print("OPRYXX SAMSUNG SSD RECOVERY")
    print("=" * 50)
    
    # Get recovery key from user
    recovery_key = input("Enter BitLocker recovery key (or press Enter to skip): ").strip()
    
    if not recovery_key:
        print("Warning: No BitLocker recovery key provided. Encrypted drives cannot be unlocked.")
    
    # Initialize recovery
    recovery = SamsungSSDRecovery(recovery_key=recovery_key if recovery_key else None)
    
    # Run recovery
    print("\nStarting Samsung SSD recovery...")
    result = recovery.recover_samsung_4tb()
    
    # Display results
    print("\nRECOVERY RESULTS:")
    print(f"Drives found: {result['drives_found']}")
    print(f"Drives recovered: {result['drives_recovered']}")
    print(f"Success: {'Yes' if result['success'] else 'No'}")
    
    if result['actions_taken']:
        print("\nActions taken:")
        for action in result['actions_taken']:
            print(f"  ✅ {action}")
    
    if result['errors']:
        print("\nErrors encountered:")
        for error in result['errors']:
            print(f"  ❌ {error}")
    
    # Generate report
    print("\nGenerating detailed report...")
    report = recovery.get_recovery_report()
    
    # Save report
    report_file = f"samsung_recovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Report saved to: {report_file}")
    print("\nRecovery complete!")

if __name__ == "__main__":
    main()