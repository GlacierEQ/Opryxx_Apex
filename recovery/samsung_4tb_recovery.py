#!/usr/bin/env python3
"""
Samsung 4TB SSD BitLocker Recovery
Specialized recovery for Samsung 4TB SSD with BitLocker encryption
"""

import subprocess
import os
import ctypes
import json
import time
from pathlib import Path
from typing import Dict, Tuple, Optional, List

class Samsung4TBRecovery:
    def __init__(self, drive_letter: str = None, recovery_key: str = None):
        self.drive_letter = drive_letter.upper() if drive_letter else None
        self.recovery_key = recovery_key
        self.is_admin = self._check_admin_privileges()
        self.recovery_log = []
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _run_command(self, command: str) -> Tuple[bool, str]:
        """Execute command and return success status and output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            self.recovery_log.append(f"{command}: {'SUCCESS' if success else 'FAILED'}")
            return success, output.strip()
        except Exception as e:
            self.recovery_log.append(f"{command}: ERROR - {str(e)}")
            return False, str(e)
    
    def detect_samsung_drives(self) -> List[Dict]:
        """Detect Samsung drives in the system"""
        print("[SCAN] Detecting Samsung drives...")
        
        samsung_drives = []
        
        try:
            # Use PowerShell to get disk information
            cmd = 'powershell "Get-Disk | Where-Object {$_.FriendlyName -like \'*Samsung*\'} | Select-Object Number, FriendlyName, Size, HealthStatus | ConvertTo-Json"'
            success, output = self._run_command(cmd)
            
            if success and output:
                drives_data = json.loads(output)
                if not isinstance(drives_data, list):
                    drives_data = [drives_data]
                
                for drive in drives_data:
                    size_gb = int(drive.get('Size', 0)) / (1024**3)
                    if 3500 <= size_gb <= 4500:  # 4TB range
                        samsung_drives.append({
                            'number': drive.get('Number'),
                            'name': drive.get('FriendlyName'),
                            'size_gb': round(size_gb, 1),
                            'health': drive.get('HealthStatus')
                        })
                        print(f"[FOUND] Samsung 4TB: {drive.get('FriendlyName')} ({size_gb:.1f}GB)")
        
        except Exception as e:
            print(f"[ERROR] Drive detection failed: {e}")
        
        return samsung_drives
    
    def get_drive_letters(self) -> List[str]:
        """Get all available drive letters"""
        drive_letters = []
        
        try:
            cmd = 'powershell "Get-Volume | Where-Object {$_.DriveLetter} | Select-Object DriveLetter, FileSystemLabel, Size | ConvertTo-Json"'
            success, output = self._run_command(cmd)
            
            if success and output:
                volumes = json.loads(output)
                if not isinstance(volumes, list):
                    volumes = [volumes]
                
                for volume in volumes:
                    drive_letter = volume.get('DriveLetter')
                    if drive_letter:
                        drive_letters.append(drive_letter)
        
        except Exception as e:
            print(f"[ERROR] Drive letter detection failed: {e}")
        
        return drive_letters
    
    def check_bitlocker_status(self, drive_letter: str) -> Dict:
        """Check BitLocker status for a drive"""
        print(f"[CHECK] BitLocker status for {drive_letter}:")
        
        cmd = f'manage-bde -status {drive_letter}:'
        success, output = self._run_command(cmd)
        
        status = {
            'encrypted': False,
            'locked': False,
            'protection_on': False,
            'conversion_status': 'Unknown'
        }
        
        if success:
            if 'BitLocker Drive Encryption' in output:
                status['encrypted'] = True
            if 'Locked' in output:
                status['locked'] = True
            if 'Protection On' in output:
                status['protection_on'] = True
            
            # Extract conversion status
            for line in output.split('\n'):
                if 'Conversion Status' in line:
                    status['conversion_status'] = line.split(':')[-1].strip()
        
        return status
    
    def unlock_with_recovery_key(self, drive_letter: str, recovery_key: str) -> bool:
        """Unlock BitLocker drive with recovery key"""
        print(f"[UNLOCK] Attempting to unlock {drive_letter}: with recovery key...")
        
        if not recovery_key:
            print("[ERROR] No recovery key provided")
            return False
        
        # Format recovery key (remove spaces and dashes)
        formatted_key = recovery_key.replace(' ', '').replace('-', '')
        
        # Try different unlock methods
        unlock_commands = [
            f'manage-bde -unlock {drive_letter}: -recoverypassword {formatted_key}',
            f'manage-bde -unlock {drive_letter}: -rp {formatted_key}',
            f'powershell "Unlock-BitLocker -MountPoint {drive_letter}: -RecoveryPassword {formatted_key}"'
        ]
        
        for cmd in unlock_commands:
            print(f"[TRY] {cmd.split()[0]}...")
            success, output = self._run_command(cmd)
            
            if success:
                print(f"[SUCCESS] Drive {drive_letter}: unlocked!")
                return True
            else:
                print(f"[FAILED] {output}")
        
        return False
    
    def repair_samsung_ssd(self, drive_letter: str) -> bool:
        """Repair Samsung SSD file system"""
        print(f"[REPAIR] Repairing Samsung SSD {drive_letter}:...")
        
        repair_commands = [
            f'chkdsk {drive_letter}: /f /r /x',
            f'sfc /scannow',
            f'dism /online /cleanup-image /restorehealth'
        ]
        
        repair_success = True
        
        for cmd in repair_commands:
            print(f"[CMD] {cmd}")
            success, output = self._run_command(cmd)
            
            if not success:
                print(f"[WARNING] Command failed: {cmd}")
                repair_success = False
            else:
                print(f"[OK] {cmd}")
        
        return repair_success
    
    def backup_bitlocker_keys(self, drive_letter: str) -> bool:
        """Backup BitLocker recovery keys"""
        print(f"[BACKUP] Backing up BitLocker keys for {drive_letter}:...")
        
        backup_dir = Path("C:\\OPRYXX_RECOVERY\\BitLocker_Keys")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get recovery key information
            cmd = f'manage-bde -protectors {drive_letter}: -get -type recoverypassword'
            success, output = self._run_command(cmd)
            
            if success:
                backup_file = backup_dir / f"Samsung_4TB_{drive_letter}_Recovery_Keys.txt"
                
                with open(backup_file, 'w') as f:
                    f.write(f"Samsung 4TB SSD BitLocker Recovery Keys\n")
                    f.write(f"Drive: {drive_letter}:\n")
                    f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(output)
                
                print(f"[OK] Keys backed up to: {backup_file}")
                return True
            else:
                print(f"[ERROR] Failed to get recovery keys: {output}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False
    
    def full_samsung_recovery(self) -> Dict:
        """Complete Samsung 4TB SSD recovery process"""
        print("SAMSUNG 4TB SSD RECOVERY")
        print("=" * 40)
        
        if not self.is_admin:
            return {
                'success': False,
                'error': 'Administrator privileges required',
                'log': self.recovery_log
            }
        
        # Step 1: Detect Samsung drives
        samsung_drives = self.detect_samsung_drives()
        
        if not samsung_drives:
            return {
                'success': False,
                'error': 'No Samsung 4TB drives detected',
                'log': self.recovery_log
            }
        
        # Step 2: Get drive letters if not specified
        if not self.drive_letter:
            drive_letters = self.get_drive_letters()
            print(f"[INFO] Available drives: {', '.join(drive_letters)}")
            
            # Try to find the Samsung drive
            for letter in drive_letters:
                status = self.check_bitlocker_status(letter)
                if status['encrypted']:
                    self.drive_letter = letter
                    print(f"[FOUND] BitLocker encrypted drive: {letter}:")
                    break
        
        if not self.drive_letter:
            return {
                'success': False,
                'error': 'Could not determine drive letter',
                'log': self.recovery_log
            }
        
        # Step 3: Check BitLocker status
        bitlocker_status = self.check_bitlocker_status(self.drive_letter)
        print(f"[STATUS] BitLocker status: {bitlocker_status}")
        
        # Step 4: Unlock if encrypted and locked
        if bitlocker_status['encrypted'] and bitlocker_status['locked']:
            if not self.recovery_key:
                return {
                    'success': False,
                    'error': 'Drive is locked and no recovery key provided',
                    'log': self.recovery_log
                }
            
            if not self.unlock_with_recovery_key(self.drive_letter, self.recovery_key):
                return {
                    'success': False,
                    'error': 'Failed to unlock BitLocker drive',
                    'log': self.recovery_log
                }
        
        # Step 5: Backup recovery keys
        self.backup_bitlocker_keys(self.drive_letter)
        
        # Step 6: Repair file system
        repair_success = self.repair_samsung_ssd(self.drive_letter)
        
        # Step 7: Verify access
        try:
            if os.path.exists(f"{self.drive_letter}:\\"):
                print(f"[SUCCESS] Drive {self.drive_letter}: is now accessible!")
                
                # List some files to verify
                try:
                    files = os.listdir(f"{self.drive_letter}:\\")
                    print(f"[INFO] Found {len(files)} items in root directory")
                except:
                    pass
                
                return {
                    'success': True,
                    'message': f'Samsung 4TB SSD recovery completed successfully',
                    'drive_letter': self.drive_letter,
                    'repair_success': repair_success,
                    'log': self.recovery_log
                }
            else:
                return {
                    'success': False,
                    'error': 'Drive still not accessible after recovery',
                    'log': self.recovery_log
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Access verification failed: {e}',
                'log': self.recovery_log
            }

def main():
    print("SAMSUNG 4TB SSD BITLOCKER RECOVERY")
    print("=" * 40)
    
    # Get recovery key from user
    recovery_key = input("Enter BitLocker recovery key (or press Enter to skip): ").strip()
    
    # Get drive letter (optional)
    drive_letter = input("Enter drive letter (e.g., E) or press Enter for auto-detect: ").strip()
    
    # Create recovery instance
    recovery = Samsung4TBRecovery(
        drive_letter=drive_letter if drive_letter else None,
        recovery_key=recovery_key if recovery_key else None
    )
    
    # Run recovery
    result = recovery.full_samsung_recovery()
    
    print("\n" + "=" * 40)
    print("RECOVERY RESULT")
    print("=" * 40)
    
    if result['success']:
        print(f"[SUCCESS] {result['message']}")
        if 'drive_letter' in result:
            print(f"[INFO] Drive accessible at: {result['drive_letter']}:\\")
    else:
        print(f"[FAILED] {result['error']}")
    
    print(f"\n[LOG] Operations performed: {len(result['log'])}")
    for log_entry in result['log'][-5:]:  # Show last 5 log entries
        print(f"  {log_entry}")

if __name__ == "__main__":
    main()