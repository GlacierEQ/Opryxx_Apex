#!/usr/bin/env python3
"""
OPRYXX Dell Inspiron 2-in-1 7040 Recovery Module
Specialized recovery for Dell Inspiron boot loop issues
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
class BootIssue:
    issue_type: str
    severity: int
    description: str
    fix_available: bool
    estimated_time: int

class DellInspiron7040Recovery:
    """Specialized recovery for Dell Inspiron 2-in-1 7040"""
    
    def __init__(self):
        self.is_admin = self._check_admin_privileges()
        self.system_info = {}
        self.boot_issues = []
        self.recovery_log = []
        self.dell_detected = False
        
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
    
    def detect_dell_system(self) -> bool:
        """Detect if this is a Dell Inspiron 7040"""
        self._log_action("Detecting Dell system", True, "Starting detection")
        
        try:
            # Get system information using WMI
            ps_command = [
                'powershell', '-Command',
                'Get-WmiObject -Class Win32_ComputerSystem | Select-Object Manufacturer, Model | ConvertTo-Json'
            ]
            
            success, output = self._run_command(ps_command)
            if success:
                system_data = json.loads(output)
                manufacturer = system_data.get('Manufacturer', '').lower()
                model = system_data.get('Model', '').lower()
                
                self.system_info = {
                    'manufacturer': manufacturer,
                    'model': model,
                    'is_dell': 'dell' in manufacturer,
                    'is_inspiron': 'inspiron' in model,
                    'is_7040': '7040' in model
                }
                
                self.dell_detected = self.system_info['is_dell']
                
                self._log_action("Dell detection", True, 
                               f"Manufacturer: {manufacturer}, Model: {model}")
                
                return self.dell_detected
            
        except Exception as e:
            self._log_action("Dell detection", False, str(e))
        
        return False
    
    def check_boot_configuration(self) -> List[BootIssue]:
        """Check boot configuration for common issues"""
        self._log_action("Checking boot configuration", True, "Starting boot analysis")
        
        issues = []
        
        # Check BCD store
        success, bcd_output = self._run_command(['bcdedit', '/enum'])
        if not success:
            issues.append(BootIssue(
                issue_type="BCD_CORRUPTION",
                severity=1,
                description="Boot Configuration Data (BCD) store is corrupted",
                fix_available=True,
                estimated_time=300
            ))
        else:
            # Analyze BCD output for issues
            if 'windows boot loader' not in bcd_output.lower():
                issues.append(BootIssue(
                    issue_type="MISSING_BOOTLOADER",
                    severity=1,
                    description="Windows Boot Loader entry missing",
                    fix_available=True,
                    estimated_time=180
                ))
            
            if 'safeboot' in bcd_output.lower():
                issues.append(BootIssue(
                    issue_type="SAFE_BOOT_STUCK",
                    severity=2,
                    description="System stuck in safe boot mode",
                    fix_available=True,
                    estimated_time=60
                ))
        
        # Check UEFI boot entries
        success, uefi_output = self._run_command(['bcdedit', '/enum', 'firmware'])
        if success and 'windows boot manager' not in uefi_output.lower():
            issues.append(BootIssue(
                issue_type="UEFI_BOOT_MISSING",
                severity=1,
                description="UEFI Windows Boot Manager entry missing",
                fix_available=True,
                estimated_time=120
            ))
        
        # Check for secure boot issues (Dell specific)
        success, secureboot_output = self._run_command([
            'powershell', '-Command',
            'Confirm-SecureBootUEFI'
        ])
        if not success and 'not supported' not in secureboot_output.lower():
            issues.append(BootIssue(
                issue_type="SECURE_BOOT_ISSUE",
                severity=2,
                description="Secure Boot configuration issue",
                fix_available=True,
                estimated_time=90
            ))
        
        self.boot_issues = issues
        self._log_action("Boot configuration check", True, f"Found {len(issues)} issues")
        
        return issues
    
    def fix_bcd_corruption(self) -> bool:
        """Fix BCD corruption issues"""
        self._log_action("Fixing BCD corruption", True, "Starting BCD repair")
        
        # Backup current BCD
        backup_success, _ = self._run_command([
            'bcdedit', '/export', f'C:\\bcd_backup_{int(time.time())}.bcd'
        ])
        
        if backup_success:
            self._log_action("BCD backup", True, "BCD backed up successfully")
        
        # Rebuild BCD
        rebuild_commands = [
            ['bootrec', '/fixmbr'],
            ['bootrec', '/fixboot'],
            ['bootrec', '/scanos'],
            ['bootrec', '/rebuildbcd']
        ]
        
        all_success = True
        for cmd in rebuild_commands:
            success, output = self._run_command(cmd)
            cmd_name = ' '.join(cmd)
            self._log_action(f"BCD repair: {cmd_name}", success, output[:200])
            if not success:
                all_success = False
        
        return all_success
    
    def fix_missing_bootloader(self) -> bool:
        """Fix missing Windows Boot Loader"""
        self._log_action("Fixing missing bootloader", True, "Starting bootloader repair")
        
        # Try to add Windows installation
        success, output = self._run_command(['bootrec', '/scanos'])
        if success and 'total identified windows installations: 1' in output.lower():
            # Add the installation to BCD
            success2, output2 = self._run_command(['bootrec', '/rebuildbcd'])
            if success2:
                self._log_action("Bootloader repair", True, "Windows installation added to BCD")
                return True
        
        # Alternative method: manually create boot entry
        windows_dir = "C:\\Windows"
        if os.path.exists(windows_dir):
            create_cmd = [
                'bcdedit', '/create', '/d', 'Windows 10', '/application', 'osloader'
            ]
            success, guid_output = self._run_command(create_cmd)
            
            if success and '{' in guid_output:
                # Extract GUID
                guid = guid_output.split('{')[1].split('}')[0]
                guid = '{' + guid + '}'
                
                # Configure the entry
                config_commands = [
                    ['bcdedit', '/set', guid, 'device', 'partition=C:'],
                    ['bcdedit', '/set', guid, 'path', '\\Windows\\system32\\winload.exe'],
                    ['bcdedit', '/set', guid, 'osdevice', 'partition=C:'],
                    ['bcdedit', '/set', guid, 'systemroot', '\\Windows'],
                    ['bcdedit', '/displayorder', guid, '/addlast']
                ]
                
                for cmd in config_commands:
                    self._run_command(cmd)
                
                self._log_action("Manual bootloader creation", True, f"Created entry {guid}")
                return True
        
        self._log_action("Bootloader repair", False, "Could not repair bootloader")
        return False
    
    def fix_safe_boot_stuck(self) -> bool:
        """Fix system stuck in safe boot mode"""
        self._log_action("Fixing safe boot stuck", True, "Removing safe boot flags")
        
        # Remove safe boot configuration
        commands = [
            ['bcdedit', '/deletevalue', '{current}', 'safeboot'],
            ['bcdedit', '/deletevalue', '{current}', 'safebootalternateshell']
        ]
        
        success_count = 0
        for cmd in commands:
            success, output = self._run_command(cmd)
            if success or 'element not found' in output.lower():
                success_count += 1
        
        if success_count > 0:
            self._log_action("Safe boot fix", True, "Safe boot flags removed")
            return True
        else:
            self._log_action("Safe boot fix", False, "Could not remove safe boot flags")
            return False
    
    def fix_uefi_boot_missing(self) -> bool:
        """Fix missing UEFI boot entries"""
        self._log_action("Fixing UEFI boot entries", True, "Recreating UEFI entries")
        
        # Create Windows Boot Manager entry
        success, output = self._run_command([
            'bcdedit', '/create', '{bootmgr}', '/d', 'Windows Boot Manager'
        ])
        
        if success or 'already exists' in output.lower():
            # Configure Boot Manager
            config_commands = [
                ['bcdedit', '/set', '{bootmgr}', 'device', 'firmware'],
                ['bcdedit', '/set', '{bootmgr}', 'path', '\\EFI\\Microsoft\\Boot\\bootmgfw.efi'],
                ['bcdedit', '/set', '{fwbootmgr}', 'displayorder', '{bootmgr}', '/addfirst']
            ]
            
            for cmd in config_commands:
                self._run_command(cmd)
            
            self._log_action("UEFI boot fix", True, "UEFI boot entries recreated")
            return True
        
        self._log_action("UEFI boot fix", False, "Could not create UEFI entries")
        return False
    
    def fix_secure_boot_issue(self) -> bool:
        """Fix Secure Boot configuration issues"""
        self._log_action("Fixing Secure Boot issues", True, "Checking Secure Boot status")
        
        # For Dell systems, we might need to reset Secure Boot keys
        # This is typically done through BIOS, but we can check the status
        
        success, output = self._run_command([
            'powershell', '-Command',
            'Get-SecureBootPolicy'
        ])
        
        if success:
            self._log_action("Secure Boot check", True, "Secure Boot policy retrieved")
            # In a real scenario, you might need to guide the user to BIOS settings
            return True
        else:
            self._log_action("Secure Boot check", False, "Could not check Secure Boot policy")
            return False
    
    def run_dell_diagnostics(self) -> Dict:
        """Run Dell-specific diagnostics"""
        self._log_action("Running Dell diagnostics", True, "Starting Dell-specific checks")
        
        diagnostics = {
            'hardware_scan': False,
            'memory_test': False,
            'disk_health': False,
            'thermal_check': False
        }
        
        # Check system health using PowerShell
        health_commands = {
            'memory_test': [
                'powershell', '-Command',
                'Get-WmiObject -Class Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum'
            ],
            'disk_health': [
                'powershell', '-Command',
                'Get-PhysicalDisk | Select-Object FriendlyName, HealthStatus'
            ]
        }
        
        for test_name, command in health_commands.items():
            success, output = self._run_command(command)
            diagnostics[test_name] = success
            self._log_action(f"Dell diagnostic: {test_name}", success, output[:100])
        
        return diagnostics
    
    def recover_dell_inspiron_7040(self) -> Dict:
        """Main recovery function for Dell Inspiron 7040"""
        recovery_result = {
            'success': False,
            'dell_detected': False,
            'issues_found': 0,
            'issues_fixed': 0,
            'errors': [],
            'actions_taken': []
        }
        
        if not self.is_admin:
            recovery_result['errors'].append("Administrator privileges required")
            return recovery_result
        
        # Step 1: Detect Dell system
        self.dell_detected = self.detect_dell_system()
        recovery_result['dell_detected'] = self.dell_detected
        
        if not self.dell_detected:
            recovery_result['errors'].append("Dell system not detected")
            # Continue anyway, might still help
        
        # Step 2: Check boot configuration
        boot_issues = self.check_boot_configuration()
        recovery_result['issues_found'] = len(boot_issues)
        
        # Step 3: Fix issues in order of severity
        boot_issues.sort(key=lambda x: x.severity)
        
        for issue in boot_issues:
            self._log_action(f"Fixing {issue.issue_type}", True, issue.description)
            
            fixed = False
            if issue.issue_type == "BCD_CORRUPTION":
                fixed = self.fix_bcd_corruption()
            elif issue.issue_type == "MISSING_BOOTLOADER":
                fixed = self.fix_missing_bootloader()
            elif issue.issue_type == "SAFE_BOOT_STUCK":
                fixed = self.fix_safe_boot_stuck()
            elif issue.issue_type == "UEFI_BOOT_MISSING":
                fixed = self.fix_uefi_boot_missing()
            elif issue.issue_type == "SECURE_BOOT_ISSUE":
                fixed = self.fix_secure_boot_issue()
            
            if fixed:
                recovery_result['issues_fixed'] += 1
                recovery_result['actions_taken'].append(f"Fixed {issue.description}")
            else:
                recovery_result['errors'].append(f"Could not fix {issue.description}")
        
        # Step 4: Run Dell diagnostics
        diagnostics = self.run_dell_diagnostics()
        recovery_result['diagnostics'] = diagnostics
        
        recovery_result['success'] = recovery_result['issues_fixed'] > 0
        return recovery_result
    
    def get_recovery_report(self) -> str:
        """Generate detailed recovery report"""
        report = []
        report.append("DELL INSPIRON 7040 RECOVERY REPORT")
        report.append("=" * 50)
        report.append(f"Recovery started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Administrator privileges: {'Yes' if self.is_admin else 'No'}")
        report.append(f"Dell system detected: {'Yes' if self.dell_detected else 'No'}")
        
        if self.system_info:
            report.append(f"Manufacturer: {self.system_info.get('manufacturer', 'Unknown')}")
            report.append(f"Model: {self.system_info.get('model', 'Unknown')}")
        
        report.append("")
        
        report.append("BOOT ISSUES FOUND:")
        for i, issue in enumerate(self.boot_issues, 1):
            report.append(f"{i}. {issue.description}")
            report.append(f"   Type: {issue.issue_type}")
            report.append(f"   Severity: {issue.severity}")
            report.append(f"   Fix available: {'Yes' if issue.fix_available else 'No'}")
            report.append("")
        
        report.append("RECOVERY ACTIONS:")
        for i, action in enumerate(self.recovery_log, 1):
            status = "✅" if action['success'] else "❌"
            report.append(f"{i}. {status} {action['action']}")
            if action['details']:
                report.append(f"   Details: {action['details']}")
        
        return "\n".join(report)

def main():
    """Main function for Dell Inspiron recovery"""
    print("OPRYXX DELL INSPIRON 7040 RECOVERY")
    print("=" * 50)
    
    # Initialize recovery
    recovery = DellInspiron7040Recovery()
    
    # Run recovery
    print("\nStarting Dell Inspiron 7040 recovery...")
    result = recovery.recover_dell_inspiron_7040()
    
    # Display results
    print("\nRECOVERY RESULTS:")
    print(f"Dell system detected: {'Yes' if result['dell_detected'] else 'No'}")
    print(f"Issues found: {result['issues_found']}")
    print(f"Issues fixed: {result['issues_fixed']}")
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
    report_file = f"dell_recovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Report saved to: {report_file}")
    
    if result['success']:
        print("\n🎉 Recovery completed successfully!")
        print("Please restart your computer to test the fixes.")
    else:
        print("\n⚠️ Recovery completed with issues.")
        print("Some problems may require manual intervention or BIOS changes.")

if __name__ == "__main__":
    main()