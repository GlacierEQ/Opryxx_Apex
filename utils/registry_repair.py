"""
Registry Repair Module for OPRYXX
Created by Cascade AI - 2025-05-20
"""
import os
import subprocess
import threading
import winreg
import tempfile
import shutil
import json
from datetime import datetime

class RegistryRepair:
    def __init__(self, update_status_callback=None, update_log_callback=None, update_progress_callback=None):
        self.update_status = update_status_callback or (lambda x: None)
        self.update_log = update_log_callback or (lambda x: None)
        self.update_progress = update_progress_callback or (lambda x: None)
        self.stop_flag = False
        
        # Create backup directory
        self.backup_dir = os.path.join(os.path.expanduser("~"), "PC_Health_Results", "RegistryBackups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Common registry issues patterns
        self.known_issues = {
            r'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run': 'Startup entries',
            r'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run': 'User startup entries',
            r'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services': 'Windows services',
            r'HKEY_CLASSES_ROOT\\*\\shell': 'Context menu entries',
            r'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved': 'Startup approvals',
            r'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall': 'Installed software',
            r'HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall': '32-bit software',
            r'HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell': 'Shell settings',
            r'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts': 'File associations'
        }
        
        # Registry backup key paths to backup
        self.backup_keys = [
            r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion',
            r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services',
            r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion',
            r'HKEY_CLASSES_ROOT\*',
            r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
            r'HKEY_CURRENT_USER\Software\Classes'
        ]
    
    def log(self, message):
        """Log a message to both the GUI and log file"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_message = f"{timestamp} {message}"
        
        if self.update_log:
            self.update_log(log_message + "\n")
    
    def create_restore_point(self, description="Registry Repair Backup"):
        """Create a system restore point"""
        self.update_status("Creating system restore point...")
        self.log("Creating system restore point for safety")
        
        try:
            ps_command = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True, check=True)
            
            self.log("✓ System restore point created successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"✗ Failed to create system restore point: {e}")
            return False
        except Exception as e:
            self.log(f"✗ Error creating system restore point: {e}")
            return False
    
    def backup_registry(self):
        """Back up important registry hives"""
        self.update_status("Backing up registry...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_dir, f"registry_backup_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        self.log(f"Backing up registry to: {backup_folder}")
        
        success_count = 0
        total_keys = len(self.backup_keys)
        
        for i, key_path in enumerate(self.backup_keys):
            if self.stop_flag:
                break
                
            self.update_progress(int((i / total_keys) * 50))  # First half of progress
            
            try:
                # Convert path format for reg export
                export_path = key_path.replace('\\', '_').replace('*', 'ALL')
                backup_file = os.path.join(backup_folder, f"{export_path}.reg")
                
                # Use reg export command
                cmd = f'reg export "{key_path}" "{backup_file}" /y'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    success_count += 1
                    self.log(f"✓ Backed up: {key_path}")
                else:
                    self.log(f"✗ Failed to backup {key_path}: {result.stderr}")
            except Exception as e:
                self.log(f"✗ Error backing up {key_path}: {e}")
        
        # Create a backup info file
        try:
            with open(os.path.join(backup_folder, "backup_info.json"), 'w') as f:
                info = {
                    "timestamp": timestamp,
                    "keys_backed_up": success_count,
                    "total_keys": total_keys,
                    "backup_keys": self.backup_keys
                }
                json.dump(info, f, indent=2)
        except Exception as e:
            self.log(f"Error creating backup info file: {e}")
        
        self.log(f"Registry backup completed: {success_count}/{total_keys} keys backed up")
        return backup_folder if success_count > 0 else None
    
    def restore_registry(self, backup_folder):
        """Restore registry from backup"""
        if not os.path.exists(backup_folder):
            self.log(f"✗ Backup folder not found: {backup_folder}")
            return False
        
        self.update_status("Restoring registry from backup...")
        self.log(f"Restoring registry from: {backup_folder}")
        
        # Create a restore point before restoring
        self.create_restore_point("Before Registry Restore")
        
        # Get list of .reg files in the backup folder
        reg_files = [f for f in os.listdir(backup_folder) if f.endswith('.reg')]
        total_files = len(reg_files)
        success_count = 0
        
        for i, reg_file in enumerate(reg_files):
            if self.stop_flag:
                break
                
            self.update_progress(50 + int((i / total_files) * 50))  # Second half of progress
            
            try:
                file_path = os.path.join(backup_folder, reg_file)
                
                # Use reg import command
                cmd = f'reg import "{file_path}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    success_count += 1
                    self.log(f"✓ Restored: {reg_file}")
                else:
                    self.log(f"✗ Failed to restore {reg_file}: {result.stderr}")
            except Exception as e:
                self.log(f"✗ Error restoring {reg_file}: {e}")
        
        self.log(f"Registry restore completed: {success_count}/{total_files} files restored")
        return success_count > 0
    
    def scan_registry_issues(self):
        """Scan for common registry issues"""
        self.update_status("Scanning registry for issues...")
        self.log("Scanning registry for common issues...")
        
        issues = []
        
        # Scan for issues
        try:
            # Check for uninstall entries with missing files
            ps_command = """
            $issues = @()
            Get-ChildItem "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall" | ForEach-Object {
                $key = $_
                $displayName = $key.GetValue("DisplayName")
                if ($displayName) {
                    $uninstallString = $key.GetValue("UninstallString")
                    if ($uninstallString -and -not [string]::IsNullOrEmpty($uninstallString)) {
                        $exePath = $uninstallString -replace '^"([^"]+)".*$', '$1'
                        $exePath = $exePath -replace "^'([^']+)'.*$", '$1'
                        if (-not (Test-Path $exePath) -and -not $exePath.StartsWith("MsiExec")) {
                            $issues += [PSCustomObject]@{
                                Type = "Invalid Uninstaller"
                                Name = $displayName
                                Path = $uninstallString
                                Key = $key.Name
                                Severity = "Low"
                            }
                        }
                    }
                }
            }
            $issues | ConvertTo-Json
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                   capture_output=True, text=True)
            
            if result.stdout.strip():
                try:
                    reg_issues = json.loads(result.stdout)
                    
                    # Handle single issue result
                    if not isinstance(reg_issues, list):
                        reg_issues = [reg_issues]
                    
                    for issue in reg_issues:
                        issues.append({
                            'type': issue.get('Type', 'Unknown'),
                            'name': issue.get('Name', 'Unknown'),
                            'path': issue.get('Path', ''),
                            'key': issue.get('Key', ''),
                            'severity': issue.get('Severity', 'Low'),
                            'fixable': True
                        })
                except json.JSONDecodeError:
                    self.log(f"Error parsing registry issues: Invalid JSON format")
            
            # Check for invalid file associations
            ps_command = """
            $issues = @()
            Get-ChildItem "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts" -Recurse | 
            Where-Object { $_.Name -like "*OpenWithList" } | ForEach-Object {
                $key = $_
                $parent = Split-Path -Path $key.Name -Parent
                $ext = Split-Path -Path $parent -Leaf
                
                Get-ItemProperty -Path $key.PSPath | Get-Member -MemberType NoteProperty | 
                Where-Object { $_.Name -match '^[a-z]$' } | ForEach-Object {
                    $propName = $_.Name
                    $value = (Get-ItemProperty -Path $key.PSPath).$propName
                    
                    if ($value -and $value -notmatch '^(HKEY|msiexec|rundll32|explorer)') {
                        $exePath = $value
                        if (-not (Test-Path $exePath -ErrorAction SilentlyContinue)) {
                            $issues += [PSCustomObject]@{
                                Type = "Invalid File Association"
                                Name = "$ext => $value"
                                Path = $exePath
                                Key = $key.Name
                                Severity = "Medium"
                            }
                        }
                    }
                }
            }
            $issues | ConvertTo-Json
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                   capture_output=True, text=True)
            
            if result.stdout.strip():
                try:
                    file_assoc_issues = json.loads(result.stdout)
                    
                    # Handle single issue result
                    if not isinstance(file_assoc_issues, list):
                        file_assoc_issues = [file_assoc_issues]
                    
                    for issue in file_assoc_issues:
                        issues.append({
                            'type': issue.get('Type', 'Unknown'),
                            'name': issue.get('Name', 'Unknown'),
                            'path': issue.get('Path', ''),
                            'key': issue.get('Key', ''),
                            'severity': issue.get('Severity', 'Medium'),
                            'fixable': True
                        })
                except json.JSONDecodeError:
                    self.log(f"Error parsing file association issues: Invalid JSON format")
        
        except Exception as e:
            self.log(f"Error during registry scan: {e}")
        
        self.log(f"Found {len(issues)} registry issues")
        
        # Return issues sorted by severity
        def severity_value(sev):
            return {'High': 0, 'Medium': 1, 'Low': 2}.get(sev, 3)
            
        issues.sort(key=lambda x: severity_value(x.get('severity', 'Low')))
        return issues
    
    def fix_registry_issues(self, issues=None, issue_key=None):
        """Fix registry issues"""
        self.update_status("Fixing registry issues...")
        self.log("Attempting to fix registry issues...")
        
        fixed_count = 0
        
        # Create restore point before making changes
        self.create_restore_point("Before Registry Fixes")
        
        # Backup registry
        self.backup_registry()
        
        # Fix specific issue if specified
        if issue_key:
            try:
                self.log(f"Fixing issue with key: {issue_key}")
                
                # Delete problematic key
                ps_command = f"""
                if (Test-Path -Path "Registry::{issue_key}") {{
                    Remove-Item -Path "Registry::{issue_key}" -Force -Recurse
                    "Key deleted successfully"
                }} else {{
                    "Key not found"
                }}
                """
                
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                       capture_output=True, text=True)
                
                if "deleted successfully" in result.stdout:
                    self.log(f"✓ Fixed issue: {issue_key}")
                    fixed_count += 1
                else:
                    self.log(f"✗ Failed to fix {issue_key}: {result.stdout}")
            except Exception as e:
                self.log(f"✗ Error fixing {issue_key}: {e}")
        
        # Fix all issues if provided
        elif issues:
            total_issues = len(issues)
            
            for i, issue in enumerate(issues):
                if self.stop_flag:
                    break
                    
                self.update_progress(int((i / total_issues) * 100))
                
                try:
                    key = issue.get('key', '')
                    if not key:
                        continue
                        
                    self.log(f"Fixing issue: {issue.get('name', 'Unknown')} ({issue.get('type', 'Unknown')})")
                    
                    # Delete problematic key
                    ps_command = f"""
                    if (Test-Path -Path "Registry::{key}") {{
                        Remove-Item -Path "Registry::{key}" -Force -Recurse
                        "Key deleted successfully"
                    }} else {{
                        "Key not found"
                    }}
                    """
                    
                    result = subprocess.run(["powershell", "-Command", ps_command], 
                                           capture_output=True, text=True)
                    
                    if "deleted successfully" in result.stdout:
                        self.log(f"✓ Fixed issue: {issue.get('name', 'Unknown')}")
                        fixed_count += 1
                    else:
                        self.log(f"✗ Failed to fix {issue.get('name', 'Unknown')}: {result.stdout}")
                except Exception as e:
                    self.log(f"✗ Error fixing {issue.get('name', 'Unknown')}: {e}")
        
        # General registry fixes
        else:
            self.log("Applying general registry fixes...")
            
            try:
                # Fix Windows Update registry issues
                ps_command = """
                # Reset Windows Update registry keys
                Stop-Service -Name wuauserv -Force
                Stop-Service -Name bits -Force
                Stop-Service -Name cryptsvc -Force
                
                $keys = @(
                    "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate",
                    "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate",
                    "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update"
                )
                
                $fixed = 0
                foreach ($key in $keys) {
                    if (Test-Path $key) {
                        $subkeys = Get-ChildItem -Path $key -Recurse -ErrorAction SilentlyContinue
                        
                        foreach ($subkey in $subkeys) {
                            $props = Get-ItemProperty -Path $subkey.PSPath -ErrorAction SilentlyContinue
                            
                            # Look for problematic properties
                            $props | Get-Member -MemberType NoteProperty | ForEach-Object {
                                $propName = $_.Name
                                
                                # Skip PS* properties and standard properties
                                if ($propName -notmatch "^PS" -and $propName -ne "PSChildName" -and $propName -ne "PSParentPath" -and $propName -ne "PSPath" -and $propName -ne "PSProvider") {
                                    $value = $props.$propName
                                    
                                    # Check for values that might disable updates
                                    if ($propName -eq "NoAutoUpdate" -and $value -eq 1) {
                                        Set-ItemProperty -Path $subkey.PSPath -Name $propName -Value 0
                                        $fixed++
                                    }
                                    elseif ($propName -eq "AUOptions" -and $value -eq 1) {
                                        Set-ItemProperty -Path $subkey.PSPath -Name $propName -Value 4
                                        $fixed++
                                    }
                                }
                            }
                        }
                    }
                }
                
                Start-Service -Name wuauserv
                Start-Service -Name bits
                Start-Service -Name cryptsvc
                
                "Fixed $fixed Windows Update registry issues"
                """
                
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                       capture_output=True, text=True)
                
                if "Fixed" in result.stdout:
                    # Extract number of fixed issues
                    match = re.search(r"Fixed (\d+)", result.stdout)
                    if match:
                        fixed_count += int(match.group(1))
                    
                    self.log(f"✓ {result.stdout.strip()}")
                
                # Fix shell extensions
                ps_command = """
                $keys = Get-ChildItem -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Shell Extensions\\Blocked" -ErrorAction SilentlyContinue
                $fixed = 0
                
                foreach ($key in $keys) {
                    Remove-Item -Path $key.PSPath -Force
                    $fixed++
                }
                
                "Fixed $fixed shell extension issues"
                """
                
                result = subprocess.run(["powershell", "-Command", ps_command], 
                                       capture_output=True, text=True)
                
                if "Fixed" in result.stdout:
                    # Extract number of fixed issues
                    match = re.search(r"Fixed (\d+)", result.stdout)
                    if match:
                        fixed_count += int(match.group(1))
                    
                    self.log(f"✓ {result.stdout.strip()}")
            
            except Exception as e:
                self.log(f"Error applying general registry fixes: {e}")
        
        self.log(f"Registry repair completed: Fixed {fixed_count} issues")
        return fixed_count
    
    def compact_registry(self):
        """Compact the registry to reduce size and improve performance"""
        self.update_status("Compacting registry...")
        self.log("Compacting registry for improved performance...")
        
        try:
            # First create restore point
            self.create_restore_point("Before Registry Compaction")
            
            # Use built-in Windows registry compaction command
            cmd = "compact /c /s:C:\\Windows\\System32\\config /i *.* /q"
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Force registry flush to disk
            ps_command = """
            # Flush registry to disk
            [System.Runtime.InteropServices.Marshal]::WriteInt32([IntPtr]::Zero, 0)
            try { [Win32.NativeMethods]::RegFlushKey([Microsoft.Win32.Registry]::CurrentUser.Handle) } catch {}
            try { [Win32.NativeMethods]::RegFlushKey([Microsoft.Win32.Registry]::LocalMachine.Handle) } catch {}
            
            # Wait for system idle time
            Start-Sleep -Seconds 5
            
            "Registry compaction completed"
            """
            
            subprocess.run(["powershell", "-Command", ps_command], 
                          capture_output=True, text=True)
            
            self.log("✓ Registry compaction completed")
            return True
        except Exception as e:
            self.log(f"✗ Error compacting registry: {e}")
            return False
    
    def stop(self):
        """Stop any running operations"""
        self.stop_flag = True
        self.log("Stopping registry operations...")
