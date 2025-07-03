#!/usr/bin/env python3
"""
BitLocker Recovery System
Specialized recovery for BitLocker encrypted drives
"""

import subprocess
import os
import sys
from pathlib import Path

class BitLockerRescue:
    def __init__(self):
        self.recovery_keys = []
        self.unlocked_drives = []
    
    def scan_bitlocker_drives(self):
        """Scan for BitLocker encrypted drives"""
        print("[SCAN] Scanning for BitLocker drives...")
        
        try:
            result = subprocess.run(['manage-bde', '-status'], 
                                  capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print("[OK] BitLocker status retrieved")
                print(result.stdout)
                return result.stdout
            else:
                print(f"[ERROR] BitLocker scan failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"[ERROR] BitLocker scan error: {e}")
            return None
    
    def unlock_with_recovery_key(self, drive_letter: str, recovery_key: str):
        """Unlock drive with recovery key"""
        print(f"[UNLOCK] Attempting to unlock {drive_letter}: with recovery key")
        
        try:
            cmd = f'manage-bde -unlock {drive_letter}: -recoverykey "{recovery_key}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"[SUCCESS] Drive {drive_letter}: unlocked!")
                self.unlocked_drives.append(drive_letter)
                return True
            else:
                print(f"[FAILED] Unlock failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Unlock error: {e}")
            return False
    
    def unlock_with_password(self, drive_letter: str, password: str):
        """Unlock drive with password"""
        print(f"[UNLOCK] Attempting to unlock {drive_letter}: with password")
        
        try:
            cmd = f'manage-bde -unlock {drive_letter}: -password "{password}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"[SUCCESS] Drive {drive_letter}: unlocked!")
                self.unlocked_drives.append(drive_letter)
                return True
            else:
                print(f"[FAILED] Password unlock failed")
                return False
                
        except Exception as e:
            print(f"[ERROR] Password unlock error: {e}")
            return False
    
    def backup_recovery_info(self, drive_letter: str):
        """Backup BitLocker recovery information"""
        print(f"[BACKUP] Backing up recovery info for {drive_letter}:")
        
        backup_dir = Path("C:\\OPRYXX_RECOVERY\\BitLocker")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get recovery key
            cmd = f'manage-bde -protectors {drive_letter}: -get -type recoverypassword'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                with open(backup_dir / f"{drive_letter}_recovery_info.txt", 'w') as f:
                    f.write(f"BitLocker Recovery Information for {drive_letter}:\n")
                    f.write("=" * 50 + "\n")
                    f.write(result.stdout)
                
                print(f"[OK] Recovery info saved to {backup_dir}")
            else:
                print(f"[ERROR] Failed to get recovery info: {result.stderr}")
                
        except Exception as e:
            print(f"[ERROR] Backup error: {e}")
    
    def disable_bitlocker(self, drive_letter: str):
        """Disable BitLocker on drive (for recovery purposes)"""
        print(f"[DISABLE] Disabling BitLocker on {drive_letter}:")
        
        try:
            cmd = f'manage-bde -off {drive_letter}:'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"[OK] BitLocker decryption started on {drive_letter}:")
                print("This process may take several hours...")
                return True
            else:
                print(f"[ERROR] Failed to disable BitLocker: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Disable error: {e}")
            return False
    
    def force_decrypt(self, drive_letter: str):
        """Force decrypt BitLocker drive"""
        print(f"[FORCE] Force decrypting {drive_letter}:")
        
        try:
            # First try to unlock
            cmd = f'manage-bde -unlock {drive_letter}: -recoverypassword'
            subprocess.run(cmd, shell=True)
            
            # Then force decrypt
            cmd = f'manage-bde -off {drive_letter}: -force'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"[OK] Force decrypt initiated on {drive_letter}:")
                return True
            else:
                print(f"[ERROR] Force decrypt failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Force decrypt error: {e}")
            return False
    
    def samsung_ssd_bitlocker_rescue(self):
        """Specialized rescue for Samsung SSD with BitLocker"""
        print("[SAMSUNG] Samsung SSD BitLocker Rescue")
        
        # Common Samsung SSD drive letters
        samsung_drives = ['C', 'D', 'E', 'F']
        
        for drive in samsung_drives:
            print(f"\n[CHECK] Checking drive {drive}:")
            
            # Check if drive exists and is BitLocker encrypted
            try:
                cmd = f'manage-bde -status {drive}:'
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                
                if "BitLocker" in result.stdout:
                    print(f"[FOUND] BitLocker drive: {drive}:")
                    
                    # Try multiple unlock methods
                    self._try_all_unlock_methods(drive)
                    
            except Exception as e:
                print(f"[ERROR] Drive {drive}: check failed: {e}")
    
    def _try_all_unlock_methods(self, drive_letter: str):
        """Try all possible unlock methods"""
        print(f"[RESCUE] Trying all unlock methods for {drive_letter}:")
        
        # Method 1: Try with empty password
        if self.unlock_with_password(drive_letter, ""):
            return True
        
        # Method 2: Try common passwords
        common_passwords = ["password", "123456", "admin", "user"]
        for pwd in common_passwords:
            if self.unlock_with_password(drive_letter, pwd):
                return True
        
        # Method 3: Try to get recovery key from system
        try:
            cmd = f'manage-bde -protectors {drive_letter}: -get -type recoverypassword'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0 and "Recovery Key" in result.stdout:
                # Extract recovery key from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Recovery Key" in line and len(line) > 20:
                        key = line.split(':')[-1].strip()
                        if self.unlock_with_recovery_key(drive_letter, key):
                            return True
        except:
            pass
        
        # Method 4: Force unlock attempt
        print(f"[FORCE] Attempting force unlock for {drive_letter}:")
        return self.force_decrypt(drive_letter)

def main():
    rescue = BitLockerRescue()
    
    print("BITLOCKER RESCUE SYSTEM")
    print("=" * 30)
    print("1. Scan BitLocker Drives")
    print("2. Samsung SSD BitLocker Rescue")
    print("3. Manual Drive Unlock")
    print("4. Backup Recovery Info")
    print("5. Force Decrypt Drive")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            rescue.scan_bitlocker_drives()
        elif choice == '2':
            rescue.samsung_ssd_bitlocker_rescue()
        elif choice == '3':
            drive = input("Enter drive letter (e.g., D): ").strip().upper()
            method = input("Enter unlock method (password/key): ").strip().lower()
            
            if method == 'password':
                pwd = input("Enter password: ").strip()
                rescue.unlock_with_password(drive, pwd)
            elif method == 'key':
                key = input("Enter recovery key: ").strip()
                rescue.unlock_with_recovery_key(drive, key)
        elif choice == '4':
            drive = input("Enter drive letter (e.g., D): ").strip().upper()
            rescue.backup_recovery_info(drive)
        elif choice == '5':
            drive = input("Enter drive letter (e.g., D): ").strip().upper()
            rescue.force_decrypt(drive)
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nBitLocker rescue cancelled")
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()