#!/usr/bin/env python3
"""
Hardware Rescue System
Specialized recovery for Dell Inspiron 2-in-1 7040, MSI Summit 16 2024, Samsung SSDs, and WD drives
"""

import os
import sys
import subprocess
import platform
import wmi
from pathlib import Path
from typing import Dict, List, Optional

class HardwareRescue:
    def __init__(self):
        self.detected_hardware = {}
        self.recovery_log = []
        
    def detect_hardware(self) -> Dict:
        """Detect specific hardware configurations"""
        print("[SCAN] Detecting hardware...")
        
        if platform.system() == "Windows":
            c = wmi.WMI()
            
            # Detect system manufacturer/model
            for system in c.Win32_ComputerSystem():
                manufacturer = system.Manufacturer.lower()
                model = system.Model.lower()
                
                if "dell" in manufacturer and "7040" in model:
                    self.detected_hardware['system'] = "Dell Inspiron 2-in-1 7040"
                    self.detected_hardware['boot_fix'] = "dell_uefi"
                elif "msi" in manufacturer and "summit" in model:
                    self.detected_hardware['system'] = "MSI Summit 16 2024"
                    self.detected_hardware['boot_fix'] = "msi_uefi"
                else:
                    self.detected_hardware['system'] = f"{system.Manufacturer} {system.Model}"
            
            # Detect drives
            self._detect_drives(c)
            
        return self.detected_hardware
    
    def _detect_drives(self, wmi_conn):
        """Detect Samsung SSDs and WD drives"""
        drives = []
        
        for disk in wmi_conn.Win32_DiskDrive():
            drive_info = {
                'model': disk.Model or "Unknown",
                'size_gb': int(disk.Size) // (1024**3) if disk.Size else 0,
                'interface': disk.InterfaceType or "Unknown",
                'status': disk.Status or "Unknown"
            }
            
            model_lower = drive_info['model'].lower()
            
            if "samsung" in model_lower:
                if "4tb" in model_lower or drive_info['size_gb'] > 3500:
                    drive_info['type'] = "Samsung 4TB SSD"
                    drive_info['recovery_method'] = "samsung_ssd_rescue"
                else:
                    drive_info['type'] = "Samsung SSD"
                    drive_info['recovery_method'] = "samsung_ssd_rescue"
            elif "wd" in model_lower or "western digital" in model_lower:
                drive_info['type'] = "WD Drive"
                drive_info['recovery_method'] = "wd_drive_rescue"
            
            drives.append(drive_info)
        
        self.detected_hardware['drives'] = drives
    
    def rescue_dell_boot_loop(self):
        """Fix Dell Inspiron 2-in-1 7040 boot loop"""
        print("[RESCUE] Dell Inspiron 2-in-1 7040 Boot Loop Fix")
        
        commands = [
            # Boot repair commands
            'bootrec /fixmbr',
            'bootrec /fixboot', 
            'bootrec /scanos',
            'bootrec /rebuildbcd',
            # UEFI repair
            'bcdboot C:\\Windows /s C: /f UEFI',
            # Dell specific
            'sfc /scannow',
            'dism /online /cleanup-image /restorehealth'
        ]
        
        for cmd in commands:
            try:
                print(f"[CMD] {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"[OK] {cmd}")
                else:
                    print(f"[ERROR] {cmd}: {result.stderr}")
                self.recovery_log.append(f"{cmd}: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
            except Exception as e:
                print(f"[ERROR] {cmd}: {e}")
    
    def rescue_samsung_ssd(self, drive_letter: str = None):
        """Rescue Samsung 4TB SSD with BitLocker"""
        print("[RESCUE] Samsung SSD Recovery")
        
        # BitLocker unlock attempts
        bitlocker_commands = [
            f'manage-bde -unlock {drive_letter}: -recoverypassword',
            f'manage-bde -unlock {drive_letter}: -password',
            f'manage-bde -status {drive_letter}:'
        ]
        
        # Samsung SSD specific recovery
        samsung_commands = [
            'chkdsk /f /r',
            'sfc /scannow',
            # Samsung Magician equivalent commands
            'defrag /c /h /o',
            'fsutil repair initiate'
        ]
        
        for cmd in bitlocker_commands + samsung_commands:
            try:
                if drive_letter and '{drive_letter}' in cmd:
                    cmd = cmd.replace('{drive_letter}', drive_letter)
                
                print(f"[CMD] {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                self.recovery_log.append(f"Samsung SSD - {cmd}: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
            except Exception as e:
                print(f"[ERROR] {cmd}: {e}")
    
    def rescue_wd_drives(self):
        """Rescue WD notebook drives"""
        print("[RESCUE] WD Drive Recovery")
        
        wd_commands = [
            # WD specific recovery
            'chkdsk /f /r /x',
            'sfc /scannow',
            # Data recovery attempts
            'wmic diskdrive get status',
            'diskpart list disk',
            # File system repair
            'fsutil dirty query',
            'fsutil repair initiate'
        ]
        
        for cmd in wd_commands:
            try:
                print(f"[CMD] {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                self.recovery_log.append(f"WD Drive - {cmd}: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
            except Exception as e:
                print(f"[ERROR] {cmd}: {e}")
    
    def create_recovery_usb(self, usb_drive: str):
        """Create recovery USB for Dell/MSI systems"""
        print(f"[CREATE] Recovery USB on {usb_drive}")
        
        recovery_commands = [
            f'format {usb_drive}: /fs:fat32 /q /v:RECOVERY',
            f'bcdboot C:\\Windows /s {usb_drive}: /f UEFI',
            # Copy recovery tools
            f'xcopy C:\\Windows\\System32\\Recovery {usb_drive}:\\Recovery\\ /e /h /r /y'
        ]
        
        for cmd in recovery_commands:
            try:
                print(f"[CMD] {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                self.recovery_log.append(f"Recovery USB - {cmd}: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
            except Exception as e:
                print(f"[ERROR] {cmd}: {e}")
    
    def emergency_data_recovery(self):
        """Emergency data recovery for RAW drives"""
        print("[EMERGENCY] Data Recovery Mode")
        
        # Create recovery directory
        recovery_dir = Path("C:\\OPRYXX_RECOVERY")
        recovery_dir.mkdir(exist_ok=True)
        
        recovery_commands = [
            # Stop unnecessary services
            'net stop "Windows Search"',
            'net stop "Superfetch"',
            # Enable recovery mode
            'bcdedit /set {default} safeboot minimal',
            # Scan for recoverable data
            f'dir /s /a C:\\ > {recovery_dir}\\file_scan.txt',
            # Export registry for recovery
            f'reg export HKLM {recovery_dir}\\registry_backup.reg',
            # Create system info dump
            f'systeminfo > {recovery_dir}\\system_info.txt'
        ]
        
        for cmd in recovery_commands:
            try:
                print(f"[CMD] {cmd}")
                subprocess.run(cmd, shell=True, capture_output=True, text=True)
            except Exception as e:
                print(f"[ERROR] {cmd}: {e}")
    
    def run_full_rescue(self):
        """Run complete hardware rescue sequence"""
        print("HARDWARE RESCUE SYSTEM")
        print("=" * 40)
        
        # Detect hardware
        hardware = self.detect_hardware()
        
        print(f"[DETECTED] System: {hardware.get('system', 'Unknown')}")
        print(f"[DETECTED] Drives: {len(hardware.get('drives', []))}")
        
        # Run appropriate rescue based on detected hardware
        if "Dell Inspiron" in hardware.get('system', ''):
            self.rescue_dell_boot_loop()
        
        # Rescue drives
        for drive in hardware.get('drives', []):
            if drive.get('type') == "Samsung 4TB SSD":
                self.rescue_samsung_ssd()
            elif drive.get('type') == "WD Drive":
                self.rescue_wd_drives()
        
        # Emergency recovery
        self.emergency_data_recovery()
        
        # Generate report
        self._generate_rescue_report()
    
    def _generate_rescue_report(self):
        """Generate rescue operation report"""
        report_path = Path("C:\\OPRYXX_RECOVERY\\rescue_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("OPRYXX HARDWARE RESCUE REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("DETECTED HARDWARE:\n")
            for key, value in self.detected_hardware.items():
                f.write(f"  {key}: {value}\n")
            
            f.write("\nRECOVERY OPERATIONS:\n")
            for log_entry in self.recovery_log:
                f.write(f"  {log_entry}\n")
        
        print(f"[REPORT] Rescue report saved to: {report_path}")

def main():
    rescue = HardwareRescue()
    
    print("OPRYXX HARDWARE RESCUE")
    print("=" * 30)
    print("1. Full Auto Rescue")
    print("2. Dell Boot Loop Fix")
    print("3. Samsung SSD Recovery")
    print("4. WD Drive Recovery")
    print("5. Create Recovery USB")
    print("6. Emergency Data Recovery")
    
    try:
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            rescue.run_full_rescue()
        elif choice == '2':
            rescue.rescue_dell_boot_loop()
        elif choice == '3':
            drive = input("Enter drive letter (e.g., D): ").strip()
            rescue.rescue_samsung_ssd(drive)
        elif choice == '4':
            rescue.rescue_wd_drives()
        elif choice == '5':
            usb = input("Enter USB drive letter (e.g., E): ").strip()
            rescue.create_recovery_usb(usb)
        elif choice == '6':
            rescue.emergency_data_recovery()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nRescue operation cancelled")
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    main()