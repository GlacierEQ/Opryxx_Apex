import asyncio
import logging
import json
import threading
import time
import os
import subprocess
import winreg
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import requests

@dataclass
class SystemIssue:
    issue_id: str
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    impact: str
    auto_fixable: bool
    fix_commands: List[str] = field(default_factory=list)
    manual_steps: List[str] = field(default_factory=list)
    prevention_measures: List[str] = field(default_factory=list)

@dataclass
class RepairAction:
    action_id: str
    name: str
    description: str
    commands: List[str]
    requires_admin: bool
    estimated_time: int  # seconds
    success_criteria: List[str]
    rollback_commands: List[str] = field(default_factory=list)

class DynamicRepairEngine:
    """Advanced repair engine with dynamic automatic execution"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repair_queue = asyncio.Queue()
        self.active_repairs = {}
        self.repair_history = []
        self.protection_monitors = {}

        # Initialize repair templates
        self.repair_templates = self._initialize_repair_templates()

        # Start background repair processor
        self._start_repair_processor()

    def _initialize_repair_templates(self) -> Dict[str, RepairAction]:
        """Initialize comprehensive repair action templates"""
        return {
            "system_file_repair": RepairAction(
                action_id="sfc_scan",
                name="System File Checker Repair",
                description="Scan and repair corrupted system files",
                commands=[
                    "sfc /scannow",
                    "DISM /Online /Cleanup-Image /RestoreHealth"
                ],
                requires_admin=True,
                estimated_time=1800,  # 30 minutes
                success_criteria=["Windows Resource Protection did not find any integrity violations"]
            ),

            "memory_diagnostic": RepairAction(
                action_id="memory_test",
                name="Memory Diagnostic",
                description="Test system memory for errors",
                commands=["mdsched.exe /f"],
                requires_admin=True,
                estimated_time=3600,  # 1 hour
                success_criteria=["No memory errors detected"]
            ),

            "disk_repair": RepairAction(
                action_id="chkdsk_repair",
                name="Disk Error Repair",
                description="Check and repair disk errors",
                commands=["chkdsk C: /f /r /x"],
                requires_admin=True,
                estimated_time=7200,  # 2 hours
                success_criteria=["Windows has checked the file system and found no problems"]
            ),

            "registry_cleanup": RepairAction(
                action_id="registry_clean",
                name="Registry Cleanup",
                description="Clean and optimize Windows Registry",
                commands=[
                    "reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v * /f",
                    "cleanmgr /sagerun:1"
                ],
                requires_admin=True,
                estimated_time=600,  # 10 minutes
                success_criteria=["Registry cleanup completed successfully"]
            ),

            "driver_update": RepairAction(
                action_id="driver_update",
                name="Driver Update",
                description="Update problematic drivers",
                commands=[
                    "pnputil /scan-devices",
                    "powershell "Get-WmiObject Win32_PnPEntity | Where-Object {$_.ConfigManagerErrorCode -ne 0} | ForEach-Object {pnputil /add-driver $_.DeviceID}""
                ],
                requires_admin=True,
                estimated_time=900,  # 15 minutes
                success_criteria=["All drivers updated successfully"]
            ),

            "temp_cleanup": RepairAction(
                action_id="temp_clean",
                name="Temporary Files Cleanup",
                description="Remove temporary and junk files",
                commands=[
                    "del /q /f /s %TEMP%\\*",
                    "del /q /f /s C:\\Windows\\Temp\\*",
                    "cleanmgr /sagerun:1"
                ],
                requires_admin=False,
                estimated_time=300,  # 5 minutes
                success_criteria=["Temporary files cleaned successfully"]
            ),

            "service_optimization": RepairAction(
                action_id="service_opt",
                name="Service Optimization",
                description="Optimize Windows services",
                commands=[
                    "sc config Themes start= auto",
                    "sc config AudioSrv start= auto",
                    "sc config Spooler start= auto"
                ],
                requires_admin=True,
                estimated_time=120,  # 2 minutes
                success_criteria=["Services optimized successfully"]
            ),

            "network_reset": RepairAction(
                action_id="network_reset",
                name="Network Stack Reset",
                description="Reset network configuration",
                commands=[
                    "netsh winsock reset",
                    "netsh int ip reset",
                    "ipconfig /flushdns",
                    "ipconfig /release",
                    "ipconfig /renew"
                ],
                requires_admin=True,
                estimated_time=180,  # 3 minutes
                success_criteria=["Network stack reset successfully"]
            ),

            "startup_optimization": RepairAction(
                action_id="startup_opt",
                name="Startup Optimization",
                description="Optimize system startup",
                commands=[
                    "msconfig",
                    "powershell "Get-CimInstance Win32_StartupCommand | Where-Object {$_.Location -notlike '*Microsoft*'} | ForEach-Object {Disable-ScheduledTask -TaskName $_.Name}""
                ],
                requires_admin=True,
                estimated_time=300,  # 5 minutes
                success_criteria=["Startup optimized successfully"]
            )
        }

    def _start_repair_processor(self):
        """Start background repair processor"""
        threading.Thread(target=self._repair_processor_loop, daemon=True).start()

    def _repair_processor_loop(self):
        """Background loop for processing repairs"""
        while True:
            try:
                # Process repair queue (simplified for sync context)
                time.sleep(5)
                self._check_protection_monitors()
            except Exception as e:
                self.logger.error(f"Repair processor error: {e}")
                time.sleep(30)

    async def execute_repair(self, repair_action: RepairAction,
                           progress_callback: Optional[Callable] = None) -> Dict:
        """Execute a repair action with progress tracking"""
        try:
            repair_id = f"repair_{int(time.time())}"
            self.active_repairs[repair_id] = {
                "action": repair_action,
                "start_time": datetime.now(),
                "status": "running",
                "progress": 0
            }

            if progress_callback:
                progress_callback(f"Starting {repair_action.name}...", 0)

            results = []
            total_commands = len(repair_action.commands)

            for i, command in enumerate(repair_action.commands):
                if progress_callback:
                    progress = int((i / total_commands) * 100)
                    progress_callback(f"Executing: {command[:50]}...", progress)

                # Execute command
                result = await self._execute_command(command, repair_action.requires_admin)
                results.append(result)

                # Update progress
                self.active_repairs[repair_id]["progress"] = int(((i + 1) / total_commands) * 100)

            # Check success criteria
            success = self._check_success_criteria(results, repair_action.success_criteria)

            # Update repair status
            self.active_repairs[repair_id].update({
                "status": "completed" if success else "failed",
                "end_time": datetime.now(),
                "results": results,
                "success": success
            })

            # Add to history
            self.repair_history.append(self.active_repairs[repair_id].copy())

            if progress_callback:
                status = "completed successfully" if success else "failed"
                progress_callback(f"Repair {status}", 100)

            return {
                "repair_id": repair_id,
                "success": success,
                "results": results,
                "duration": (datetime.now() - self.active_repairs[repair_id]["start_time"]).total_seconds()
            }

        except Exception as e:
            self.logger.error(f"Repair execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_command(self, command: str, requires_admin: bool) -> Dict:
        """Execute a system command"""
        try:
            start_time = time.time()

            if requires_admin:
                # Execute with admin privileges
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minute timeout
                )

            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time() - start_time,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "error": "Command timed out",
                "success": False
            }
        except Exception as e:
            return {
                "command": command,
                "error": str(e),
                "success": False
            }

    def _check_success_criteria(self, results: List[Dict], criteria: List[str]) -> bool:
        """Check if repair was successful based on criteria"""
        try:
            for criterion in criteria:
                found = False
                for result in results:
                    if criterion.lower() in result.get("stdout", "").lower():
                        found = True
                        break
                if not found:
                    return False
            return True
        except Exception:
            return False

class ProtectionEngine:
    """Advanced protection engine with real-time monitoring"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protection_rules = self._initialize_protection_rules()
        self.active_protections = {}
        self.threat_database = self._load_threat_database()

        # Start protection monitors
        self._start_protection_monitors()

    def _initialize_protection_rules(self) -> Dict:
        """Initialize protection rules"""
        return {
            "file_integrity": {
                "monitor_paths": [
                    "C:\\Windows\\System32",
                    "C:\\Windows\\SysWOW64",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)"
                ],
                "check_interval": 300,  # 5 minutes
                "action": "alert_and_quarantine"
            },

            "registry_protection": {
                "monitor_keys": [
                    "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
                ],
                "check_interval": 300,  # 5 minutes
                "action": "alert_and_quarantine"
            }
        }

    def _load_threat_database(self) -> Dict:
        """Load threat database from file or API"""
        try:
            # Try to load from local file first
            threat_db_path = os.path.join(os.getcwd(), "data", "threat_database.json")
            if os.path.exists(threat_db_path):
                with open(threat_db_path, 'r') as f:
                    return json.load(f)

            # If no local database, create a basic one
            basic_db = {
                "malicious_hashes": [],
                "suspicious_domains": [
                    "malware.com",
                    "phishing.net",
                    "trojan.org"
                ],
                "known_malware_signatures": [],
                "last_updated": datetime.now().isoformat()
            }

            # Save basic database
            os.makedirs(os.path.dirname(threat_db_path), exist_ok=True)
            with open(threat_db_path, 'w') as f:
                json.dump(basic_db, f, indent=2)

            return basic_db

        except Exception as e:
            self.logger.error(f"Failed to load threat database: {e}")
            return {}

    def _start_protection_monitors(self):
        """Start protection monitors"""
        try:
            # Start file integrity monitor
            threading.Thread(
                target=self._file_integrity_monitor,
                daemon=True
            ).start()

            # Start registry protection monitor
            threading.Thread(
                target=self._registry_protection_monitor,
                daemon=True
            ).start()

            # Start process monitor
            threading.Thread(
                target=self._process_monitor,
                daemon=True
            ).start()

            self.logger.info("Protection monitors started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start protection monitors: {e}")

    def _file_integrity_monitor(self):
        """Monitor file integrity in critical system paths"""
        while True:
            try:
                for rule_name, rule in self.protection_rules.items():
                    if rule_name == "file_integrity":
                        for path in rule["monitor_paths"]:
                            if os.path.exists(path):
                                self._check_path_integrity(path, rule["action"])

                time.sleep(self.protection_rules["file_integrity"]["check_interval"])

            except Exception as e:
                self.logger.error(f"File integrity monitor error: {e}")
                time.sleep(60)

    def _registry_protection_monitor(self):
        """Monitor registry keys for unauthorized changes"""
        while True:
            try:
                for rule_name, rule in self.protection_rules.items():
                    if rule_name == "registry_protection":
                        for key_path in rule["monitor_keys"]:
                            self._check_registry_key(key_path, rule["action"])

                time.sleep(self.protection_rules["registry_protection"]["check_interval"])

            except Exception as e:
                self.logger.error(f"Registry protection monitor error: {e}")
                time.sleep(60)

    def _process_monitor(self):
        """Monitor running processes for suspicious activity"""
        known_processes = set()

        while True:
            try:
                current_processes = set()

                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                    try:
                        proc_info = proc.info
                        proc_signature = f"{proc_info['name']}:{proc_info['exe']}"
                        current_processes.add(proc_signature)

                        # Check for new processes
                        if proc_signature not in known_processes:
                            self._analyze_new_process(proc_info)

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                known_processes = current_processes
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Process monitor error: {e}")
                time.sleep(60)

    def _check_path_integrity(self, path: str, action: str):
        """Check integrity of files in a given path"""
        try:
            for root, dirs, files in os.walk(path):
                for file in files[:10]:  # Limit to prevent performance issues
                    file_path = os.path.join(root, file)
                    if self._is_suspicious_file(file_path):
                        self._handle_threat(file_path, "suspicious_file", action)

        except Exception as e:
            self.logger.error(f"Path integrity check failed for {path}: {e}")

    def _check_registry_key(self, key_path: str, action: str):
        """Check registry key for unauthorized entries"""
        try:
            # Parse registry path
            if key_path.startswith("HKLM"):
                root_key = winreg.HKEY_LOCAL_MACHINE
                sub_key = key_path.replace("HKLM\", "")
            elif key_path.startswith("HKCU"):
                root_key = winreg.HKEY_CURRENT_USER
                sub_key = key_path.replace("HKCU\", "")
            else:
                return

            # Open and check registry key
            with winreg.OpenKey(root_key, sub_key) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if self._is_suspicious_registry_entry(name, value):
                            self._handle_threat(f"{key_path}\\{name}", "suspicious_registry", action)
                        i += 1
                    except WindowsError:
                        break

        except Exception as e:
            self.logger.error(f"Registry check failed for {key_path}: {e}")

    def _analyze_new_process(self, proc_info: Dict):
        """Analyze newly started process for threats"""
        try:
            process_name = proc_info.get('name', '').lower()
            process_exe = proc_info.get('exe', '')

            # Check against threat database
            if self._is_suspicious_process(process_name, process_exe):
                self._handle_threat(
                    process_exe,
                    "suspicious_process",
                    "alert_and_quarantine"
                )

        except Exception as e:
            self.logger.error(f"Process analysis failed: {e}")

    def _is_suspicious_file(self, file_path: str) -> bool:
        """Check if file is suspicious"""
        try:
            # Check file hash against threat database
            file_hash = self._calculate_file_hash(file_path)
            if file_hash in self.threat_database.get('malicious_hashes', []):
                return True

            # Check file extension
            suspicious_extensions = ['.exe', '.scr', '.bat', '.cmd', '.pif']
            if any(file_path.lower().endswith(ext) for ext in suspicious_extensions):
                # Additional checks for executable files
                return self._check_executable_suspicious(file_path)

            return False

        except Exception:
            return False

    def _is_suspicious_registry_entry(self, name: str, value: str) -> bool:
        """Check if registry entry is suspicious"""
        try:
            # Check for known malicious entries
            suspicious_patterns = [
                'temp',
                'download',
                'appdata\\roaming',
                '.tmp',
                '.exe'
            ]

            value_lower = str(value).lower()
            return any(pattern in value_lower for pattern in suspicious_patterns)

        except Exception:
            return False

    def _is_suspicious_process(self, process_name: str, process_exe: str) -> bool:
        """Check if process is suspicious"""
        try:
            # Check against known malicious process names
            suspicious_names = [
                'cryptolocker',
                'wannacry',
                'ransomware',
                'keylogger',
                'trojan'
            ]

            return any(name in process_name for name in suspicious_names)

        except Exception:
            return False

    def _check_executable_suspicious(self, file_path: str) -> bool:
        """Additional checks for executable files"""
        try:
            # Check file size (very small or very large executables can be suspicious)
            file_size = os.path.getsize(file_path)
            if file_size < 1024 or file_size > 100 * 1024 * 1024:  # < 1KB or > 100MB
                return True

            # Check if file is signed (unsigned executables in system folders are suspicious)
            if "system32" in file_path.lower() or "syswow64" in file_path.lower():
                return not self._is_file_signed(file_path)

            return False

        except Exception:
            return False

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""

    def _is_file_signed(self, file_path: str) -> bool:
        """Check if file has valid digital signature"""
        try:
            # Use PowerShell to check file signature
            cmd = f'powershell "Get-AuthenticodeSignature '{file_path}' | Select-Object Status"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return "Valid" in result.stdout
        except Exception:
            return False

    def _handle_threat(self, threat_path: str, threat_type: str, action: str):
        """Handle detected threat based on action policy"""
        try:
            threat_info = {
                "timestamp": datetime.now().isoformat(),
                "path": threat_path,
                "type": threat_type,
                "action": action
            }

            self.logger.warning(f"Threat detected: {threat_info}")

            if action == "alert_and_quarantine":
                self._quarantine_threat(threat_path, threat_type)
            elif action == "alert_only":
                self._alert_threat(threat_info)
            elif action == "auto_remove":
                self._remove_threat(threat_path, threat_type)

        except Exception as e:
            self.logger.error(f"Threat handling failed: {e}")

    def _quarantine_threat(self, threat_path: str, threat_type: str):
        """Quarantine detected threat"""
        try:
            quarantine_dir = os.path.join(os.getcwd(), "quarantine")
            os.makedirs(quarantine_dir, exist_ok=True)

            # Create quarantine entry
            quarantine_file = os.path.join(
                quarantine_dir,
                f"{int(time.time())}_{os.path.basename(threat_path)}.quarantine"
            )

            if threat_type == "suspicious_file":
                # Move file to quarantine
                os.rename(threat_path, quarantine_file)
            elif threat_type == "suspicious_registry":
                # Backup and remove registry entry
                self._backup_registry_entry(threat_path, quarantine_file)

            self.logger.info(f"Threat quarantined: {threat_path} -> {quarantine_file}")

        except Exception as e:
            self.logger.error(f"Quarantine failed for {threat_path}: {e}")

    def _alert_threat(self, threat_info: Dict):
        """Send threat alert"""
        try:
            # Log the alert
            self.logger.warning(f"SECURITY ALERT: {threat_info}")

            # Could integrate with notification system here
            # For now, just log the alert

        except Exception as e:
            self.logger.error(f"Alert failed: {e}")

    def _remove_threat(self, threat_path: str, threat_type: str):
        """Remove detected threat"""
        try:
            if threat_type == "suspicious_file" and os.path.exists(threat_path):
                os.remove(threat_path)
                self.logger.info(f"Threat removed: {threat_path}")
            elif threat_type == "suspicious_process":
                # Terminate suspicious process
                self._terminate_process_by_path(threat_path)

        except Exception as e:
            self.logger.error(f"Threat removal failed for {threat_path}: {e}")

    def _backup_registry_entry(self, reg_path: str, backup_file: str):
        """Backup registry entry before removal"""
        try:
            # Export registry entry to backup file
            cmd = f'reg export "{reg_path}" "{backup_file}"'
            subprocess.run(cmd, shell=True, check=True)

            # Delete the registry entry
            cmd = f'reg delete "{reg_path}" /f'
            subprocess.run(cmd, shell=True, check=True)

        except Exception as e:
            self.logger.error(f"Registry backup/removal failed: {e}")

    def _terminate_process_by_path(self, process_path: str):
        """Terminate process by executable path"""
        try:
            for proc in psutil.process_iter(['pid', 'exe']):
                try:
                    if proc.info['exe'] == process_path:
                        proc.terminate()
                        self.logger.info(f"Process terminated: {process_path}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Process termination failed: {e}")

    def update_threat_database(self):
        """Update threat database from external sources"""
        try:
            # This could integrate with threat intelligence APIs
            # For now, just update timestamp
            self.threat_database["last_updated"] = datetime.now().isoformat()

            # Save updated database
            threat_db_path = os.path.join(os.getcwd(), "data", "threat_database.json")
            with open(threat_db_path, 'w') as f:
                json.dump(self.threat_database, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to update threat database: {e}")
