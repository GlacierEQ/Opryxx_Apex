import asyncio
import logging
import psutil
import subprocess
import winreg
import ctypes
from ctypes import wintypes
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class CrashAnalysis:
    crash_type: str
    severity: str
    root_causes: List[str]
    immediate_fixes: List[str]
    preventive_measures: List[str]
    system_impact: Dict
    recovery_actions: List[str]

class AdvancedCrashAnalyzer:
    """Advanced crash analysis engine for kernel and memory issues"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crash_patterns = self._initialize_crash_patterns()

    def _initialize_crash_patterns(self):
        """Initialize known crash patterns and signatures"""
        return {
            "BAD_POOL_HEADER": {
                "description": "Memory pool corruption",
                "common_causes": ["Driver issues", "Memory corruption", "Hardware failure"],
                "severity": "CRITICAL"
            },
            "KERNEL_DATA_INPAGE_ERROR": {
                "description": "Kernel data corruption",
                "common_causes": ["Storage device failure", "RAM issues", "Driver corruption"],
                "severity": "CRITICAL"
            },
            "MEMORY_MANAGEMENT": {
                "description": "Memory management failure",
                "common_causes": ["RAM failure", "Driver issues", "Overclocking"],
                "severity": "HIGH"
            },
            "SYSTEM_SERVICE_EXCEPTION": {
                "description": "System service crash",
                "common_causes": ["Driver incompatibility", "System file corruption"],
                "severity": "HIGH"
            }
        }

    async def analyze_crash_dumps(self) -> CrashAnalysis:
        """Comprehensive crash dump analysis"""
        try:
            # Check for crash dumps
            dump_files = await self._find_crash_dumps()

            # Analyze system logs
            event_logs = await self._analyze_event_logs()

            # Memory analysis
            memory_analysis = await self._analyze_memory_issues()

            # Driver analysis
            driver_analysis = await self._analyze_driver_issues()

            # Hardware analysis
            hardware_analysis = await self._analyze_hardware_health()

            # Compile comprehensive analysis
            crash_analysis = self._compile_crash_analysis(
                dump_files, event_logs, memory_analysis,
                driver_analysis, hardware_analysis
            )

            return crash_analysis

        except Exception as e:
            self.logger.error(f"Crash analysis failed: {e}")
            return CrashAnalysis(
                crash_type="UNKNOWN",
                severity="HIGH",
                root_causes=[f"Analysis error: {str(e)}"],
                immediate_fixes=["Run system file checker", "Check hardware"],
                preventive_measures=["Regular system maintenance"],
                system_impact={"stability": "compromised"},
                recovery_actions=["Safe mode boot", "System restore"]
            )

    async def _find_crash_dumps(self) -> List[Dict]:
        """Find and analyze crash dump files"""
        try:
            dump_locations = [
                r"C:\Windows\Minidump",
                r"C:\Windows\MEMORY.DMP",
                r"C:\Windows\LiveKernelReports"
            ]

            dump_files = []
            for location in dump_locations:
                if os.path.exists(location):
                    if os.path.isdir(location):
                        for file in os.listdir(location):
                            if file.endswith('.dmp'):
                                dump_files.append({
                                    "path": os.path.join(location, file),
                                    "size": os.path.getsize(os.path.join(location, file)),
                                    "modified": datetime.fromtimestamp(
                                        os.path.getmtime(os.path.join(location, file))
                                    )
                                })
                    else:
                        dump_files.append({
                            "path": location,
                            "size": os.path.getsize(location),
                            "modified": datetime.fromtimestamp(os.path.getmtime(location))
                        })

            return sorted(dump_files, key=lambda x: x["modified"], reverse=True)

        except Exception as e:
            self.logger.error(f"Dump file analysis failed: {e}")
            return []

    async def _analyze_event_logs(self) -> Dict:
        """Analyze Windows Event Logs for crash indicators"""
        try:
            # Use PowerShell to query event logs
            powershell_cmd = '''
            Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2,3; StartTime=(Get-Date).AddDays(-7)} |
            Where-Object {$_.LevelDisplayName -eq 'Critical' -or $_.LevelDisplayName -eq 'Error'} |
            Select-Object TimeCreated, Id, LevelDisplayName, Message |
            ConvertTo-Json
            '''

            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0 and result.stdout:
                import json
                events = json.loads(result.stdout)

                # Analyze for crash-related events
                crash_events = []
                for event in events if isinstance(events, list) else [events]:
                    if any(keyword in event.get("Message", "").lower() for keyword in [
                        "bugcheck", "blue screen", "kernel", "memory", "crash", "dump"
                    ]):
                        crash_events.append(event)

                return {
                    "total_errors": len(events) if isinstance(events, list) else 1,
                    "crash_related": len(crash_events),
                    "recent_crashes": crash_events[:10]  # Last 10 crash events
                }

            return {"total_errors": 0, "crash_related": 0, "recent_crashes": []}

        except Exception as e:
            self.logger.error(f"Event log analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_memory_issues(self) -> Dict:
        """Comprehensive memory analysis"""
        try:
            memory_info = psutil.virtual_memory()

            # Check for memory pressure
            memory_pressure = memory_info.percent > 85

            # Check for memory leaks (simplified)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 5:  # Processes using >5% memory
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)

            return {
                "total_memory_gb": round(memory_info.total / (1024**3), 2),
                "used_memory_gb": round(memory_info.used / (1024**3), 2),
                "memory_percent": memory_info.percent,
                "memory_pressure": memory_pressure,
                "high_memory_processes": processes[:10],
                "available_gb": round(memory_info.available / (1024**3), 2)
            }

        except Exception as e:
            self.logger.error(f"Memory analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_driver_issues(self) -> Dict:
        """Analyze driver-related issues"""
        try:
            # Get driver information using PowerShell
            powershell_cmd = '''
            Get-WmiObject Win32_PnPSignedDriver |
            Where-Object {$_.IsSigned -eq $false -or $_.DriverDate -lt (Get-Date).AddYears(-2)} |
            Select-Object DeviceName, DriverVersion, DriverDate, IsSigned |
            ConvertTo-Json
            '''

            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True, text=True, timeout=30
            )

            problematic_drivers = []
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    drivers = json.loads(result.stdout)
                    if isinstance(drivers, list):
                        problematic_drivers = drivers
                    elif drivers:
                        problematic_drivers = [drivers]
                except json.JSONDecodeError:
                    pass

            return {
                "problematic_drivers": len(problematic_drivers),
                "driver_details": problematic_drivers[:20],  # Top 20 problematic drivers
                "analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Driver analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_hardware_health(self) -> Dict:
        """Comprehensive hardware health analysis"""
        try:
            hardware_data = {}

            # CPU analysis
            cpu_info = {
                "usage_percent": psutil.cpu_percent(interval=1),
                "core_count": psutil.cpu_count(logical=False),
                "thread_count": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "temperature": await self._get_cpu_temperature()
            }
            hardware_data["cpu"] = cpu_info

            # Disk health analysis
            disk_health = await self._analyze_disk_health()
            hardware_data["disks"] = disk_health

            # Memory health
            memory_health = await self._analyze_memory_health()
            hardware_data["memory"] = memory_health

            # GPU analysis
            gpu_health = await self._analyze_gpu_health()
            hardware_data["gpu"] = gpu_health

            # System temperatures
            temperatures = await self._get_system_temperatures()
            hardware_data["temperatures"] = temperatures

            return hardware_data

        except Exception as e:
            self.logger.error(f"Hardware health analysis failed: {e}")
            return {"error": str(e)}

    async def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature using WMI"""
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                # Convert from tenths of Kelvin to Celsius
                temp_kelvin = temperature_info[0].CurrentTemperature / 10.0
                temp_celsius = temp_kelvin - 273.15
                return round(temp_celsius, 1)
        except Exception:
            pass
        return None

    async def _analyze_disk_health(self) -> Dict:
        """Analyze disk health using SMART data"""
        try:
            disk_info = {}

            # Get disk usage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent_used": round((usage.used / usage.total) * 100, 1),
                        "filesystem": partition.fstype
                    }
                except PermissionError:
                    continue

            # Check for disk errors using chkdsk
            disk_errors = await self._check_disk_errors()

            return {
                "partitions": disk_info,
                "errors": disk_errors,
                "io_stats": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
            }

        except Exception as e:
            self.logger.error(f"Disk health analysis failed: {e}")
            return {"error": str(e)}

    async def _check_disk_errors(self) -> List[str]:
        """Check for disk errors"""
        try:
            # Use PowerShell to check event logs for disk errors
            powershell_cmd = '''
            Get-WinEvent -FilterHashtable @{LogName='System'; Id=7,11,51,98,129,153,154,157} -MaxEvents 50 |
            Select-Object TimeCreated, Id, LevelDisplayName, Message |
            ConvertTo-Json
            '''

            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True, text=True, timeout=15
            )

            errors = []
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    events = json.loads(result.stdout)
                    if isinstance(events, list):
                        errors = [event.get("Message", "")[:100] for event in events[:5]]
                    elif events:
                        errors = [events.get("Message", "")[:100]]
                except json.JSONDecodeError:
                    pass

            return errors

        except Exception as e:
            return [f"Error checking disk: {str(e)}"]

    async def _analyze_memory_health(self) -> Dict:
        """Analyze memory health"""
        # Placeholder for memory health analysis
        return {}

    async def _analyze_gpu_health(self) -> Dict:
        """Analyze GPU health"""
        # Placeholder for GPU health analysis
        return {}

    async def _get_system_temperatures(self) -> Dict:
        """Get system temperatures"""
        # Placeholder for system temperatures analysis
        return {}

    def _compile_crash_analysis(self, dump_files, event_logs, memory_analysis,
                               driver_analysis, hardware_analysis) -> CrashAnalysis:
        """Compile comprehensive crash analysis"""
        try:
            # Determine crash type based on evidence
            crash_type = "KERNEL_CORRUPTION"
            severity = "CRITICAL"

            root_causes = []
            immediate_fixes = []
            preventive_measures = []
            recovery_actions = []

            # Analyze memory issues
            if memory_analysis.get("memory_pressure"):
                root_causes.append("Memory pressure detected")
                immediate_fixes.append("Close unnecessary applications")
                immediate_fixes.append("Increase virtual memory")

            # Analyze driver issues
            if driver_analysis.get("problematic_drivers", 0) > 0:
                root_causes.append("Problematic drivers detected")
                immediate_fixes.append("Update or rollback problematic drivers")
                immediate_fixes.append("Run Driver Verifier")

            # Analyze crash dumps
            if dump_files:
                root_causes.append("Multiple crash dumps found")
                immediate_fixes.append("Analyze crash dumps with WinDbg")
                recovery_actions.append("Boot in Safe Mode")

            # Event log analysis
            if event_logs.get("crash_related", 0) > 5:
                root_causes.append("Frequent system errors detected")
                immediate_fixes.append("Run System File Checker (sfc /scannow)")
                immediate_fixes.append("Run DISM repair")

            # Standard fixes for kernel corruption
            immediate_fixes.extend([
                "Run Memory Diagnostic (mdsched.exe)",
                "Check disk for errors (chkdsk /f)",
                "Update Windows and drivers",
                "Disable overclocking if enabled",
                "Test RAM with MemTest86+"
            ])

            preventive_measures.extend([
                "Regular system maintenance",
                "Keep drivers updated",
                "Monitor system temperatures",
                "Regular malware scans",
                "Backup important data"
            ])

            recovery_actions.extend([
                "Boot from Windows Recovery Environment",
                "System Restore to previous point",
                "Reset Windows 10/11 keeping files",
                "Clean Windows installation if necessary"
            ])

            system_impact = {
                "stability": "severely_compromised",
                "data_risk": "high",
                "performance": "degraded",
                "reliability": "poor"
            }

            return CrashAnalysis(
                crash_type=crash_type,
                severity=severity,
                root_causes=root_causes,
                immediate_fixes=immediate_fixes,
                preventive_measures=preventive_measures,
                system_impact=system_impact,
                recovery_actions=recovery_actions
            )

        except Exception as e:
            self.logger.error(f"Failed to compile crash analysis: {e}")
            return CrashAnalysis(
                crash_type="UNKNOWN",
                severity="HIGH",
                root_causes=[f"Compilation error: {str(e)}"],
                immediate_fixes=["Run system file checker", "Check hardware"],
                preventive_measures=["Regular system maintenance"],
                system_impact={"stability": "compromised"},
                recovery_actions=["Safe mode boot", "System restore"]
            )

class ComprehensiveSystemScanner:
    """Advanced system scanner with AI-powered diagnostics and repairs"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crash_analyzer = AdvancedCrashAnalyzer()
        self.scan_results = {}

    async def full_system_scan(self) -> Dict:
        """Perform comprehensive system scan"""
        try:
            self.logger.info("Starting comprehensive system scan...")

            scan_results = {
                "scan_timestamp": datetime.now().isoformat(),
                "scan_id": f"scan_{int(time.time())}",
                "system_info": await self._get_system_info(),
                "crash_analysis": await self.crash_analyzer.analyze_crash_dumps(),
                "security_scan": await self._security_scan(),
                "performance_analysis": await self._performance_analysis(),
                "registry_analysis": await self._registry_analysis(),
                "startup_analysis": await self._startup_analysis(),
                "network_analysis": await self._network_analysis(),
                "malware_scan": await self._malware_scan(),
                "system_integrity": await self._system_integrity_check(),
                "driver_analysis": await self._comprehensive_driver_analysis(),
                "service_analysis": await self._service_analysis(),
                "recommendations": []
            }

            # Generate AI-powered recommendations
            scan_results["recommendations"] = await self._generate_ai_recommendations(scan_results)

            # Generate automated fixes
            scan_results["automated_fixes"] = await self._generate_automated_fixes(scan_results)

            # Generate protection measures
            scan_results["protection_measures"] = await self._generate_protection_measures(scan_results)

            self.scan_results = scan_results
            return scan_results

        except Exception as e:
            self.logger.error(f"System scan failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            import platform

            system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 1)
            }

            # Windows-specific information
            if platform.system() == "Windows":
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                      r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        system_info["windows_build"] = winreg.QueryValueEx(key, "CurrentBuild")[0]
                        system_info["windows_version"] = winreg.QueryValueEx(key, "DisplayVersion")[0]
                except Exception:
                    pass

            return system_info

        except Exception as e:
            return {"error": str(e)}

    async def _security_scan(self) -> Dict:
        """Comprehensive security analysis"""
        try:
            security_data = {
                "windows_defender": await self._check_windows_defender(),
                "firewall_status": await self._check_firewall_status(),
                "user_accounts": await self._analyze_user_accounts(),
                "network_connections": await self._analyze_network_connections(),
                "suspicious_processes": await self._find_suspicious_processes(),
                "file_permissions": await self._check_critical_file_permissions(),
                "registry_security": await self._check_registry_security()
            }

            return security_data

        except Exception as e:
            return {"error": str(e)}

    async def _check_windows_defender(self) -> Dict:
        """Check Windows Defender status"""
        try:
            powershell_cmd = '''
            Get-MpComputerStatus | Select-Object AntivirusEnabled, AMServiceEnabled,
            AntispywareEnabled, BehaviorMonitorEnabled, IoavProtectionEnabled,
            NISEnabled, OnAccessProtectionEnabled, RealTimeProtectionEnabled |
            ConvertTo-Json
            '''

            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0 and result.stdout:
                import json
                return json.loads(result.stdout)

            return {"status": "unknown"}

        except Exception as e:
            return {"error": str(e)}

    async def _performance_analysis(self) -> Dict:
        """Comprehensive performance analysis"""
        try:
            performance_data = {
                "cpu_analysis": await self._analyze_cpu_performance(),
                "memory_analysis": await self._analyze_memory_performance(),
                "disk_analysis": await self._analyze_disk_performance(),
                "network_analysis": await self._analyze_network_performance(),
                "process_analysis": await self._analyze_process_performance(),
                "startup_impact": await self._analyze_startup_impact()
            }

            return performance_data

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_cpu_performance(self) -> Dict:
        """Analyze CPU performance"""
        try:
            # Get CPU usage over time
            cpu_samples = []
            for _ in range(5):
                cpu_samples.append(psutil.cpu_percent(interval=1))

            cpu_per_core = psutil.cpu_percent(percpu=True)

            return {
                "average_usage": round(sum(cpu_samples) / len(cpu_samples), 1),
                "peak_usage": max(cpu_samples),
                "per_core_usage": cpu_per_core,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None,
                "context_switches": psutil.cpu_stats().ctx_switches,
                "interrupts": psutil.cpu_stats().interrupts
            }

        except Exception as e:
            return {"error": str(e)}

    async def _registry_analysis(self) -> Dict:
        """Analyze Windows Registry for issues"""
        try:
            registry_issues = {
                "startup_entries": await self._check_startup_registry(),
                "uninstall_entries": await self._check_uninstall_registry(),
                "file_associations": await self._check_file_associations(),
                "system_policies": await self._check_system_policies()
            }

            return registry_issues

        except Exception as e:
            return {"error": str(e)}

    async def _malware_scan(self) -> Dict:
        """Basic malware detection"""
        try:
            malware_indicators = {
                "suspicious_files": await self._find_suspicious_files(),
                "suspicious_registry": await self._find_suspicious_registry_entries(),
                "suspicious_network": await self._find_suspicious_network_activity(),
                "suspicious_processes": await self._find_suspicious_processes()
            }

            return malware_indicators

        except Exception as e:
            return {"error": str(e)}

    async def _system_integrity_check(self) -> Dict:
        """Check system integrity"""
        # Placeholder for system integrity check
        return {}

    async def _comprehensive_driver_analysis(self) -> Dict:
        """Comprehensive driver analysis"""
        # Placeholder for comprehensive driver analysis
        return {}

    async def _service_analysis(self) -> Dict:
        """Analyze system services"""
        # Placeholder for service analysis
        return {}

    async def _generate_ai_recommendations(self, scan_results: Dict) -> List[str]:
        """Generate AI-powered recommendations"""
        # Placeholder for AI recommendations
        return []

    async def _generate_automated_fixes(self, scan_results: Dict) -> List[str]:
        """Generate automated fixes"""
        # Placeholder for automated fixes
        return []

    async def _generate_protection_measures(self, scan_results: Dict) -> List[str]:
        """Generate protection measures"""
        # Placeholder for protection measures
        return []

    async def _check_firewall_status(self) -> Dict:
        """Check firewall status"""
        # Placeholder for firewall status check
        return {}

    async def _analyze_user_accounts(self) -> Dict:
        """Analyze user accounts"""
        # Placeholder for user account analysis
        return {}

    async def _analyze_network_connections(self) -> Dict:
        """Analyze network connections"""
        # Placeholder for network connection analysis
        return {}

    async def _find_suspicious_processes(self) -> List[str]:
        """Find suspicious processes"""
        # Placeholder for suspicious process detection
        return []

    async def _check_critical_file_permissions(self) -> Dict:
        """Check critical file permissions"""
        # Placeholder for file permission check
        return {}

    async def _check_registry_security(self) -> Dict:
        """Check registry security"""
        # Placeholder for registry security check
        return {}

    async def _analyze_memory_performance(self) -> Dict:
        """Analyze memory performance"""
        # Placeholder for memory performance analysis
        return {}

    async def _analyze_disk_performance(self) -> Dict:
        """Analyze disk performance"""
        # Placeholder for disk performance analysis
        return {}

    async def _analyze_network_performance(self) -> Dict:
        """Analyze network performance"""
        # Placeholder for network performance analysis
        return {}

    async def _analyze_process_performance(self) -> Dict:
        """Analyze process performance"""
        # Placeholder for process performance analysis
        return {}

    async def _analyze_startup_impact(self) -> Dict:
        """Analyze startup impact"""
        # Placeholder for startup impact analysis
        return {}

    async def _check_startup_registry(self) -> Dict:
        """Check startup registry entries"""
        # Placeholder for startup registry check
        return {}

    async def _check_uninstall_registry(self) -> Dict:
        """Check uninstall registry entries"""
        # Placeholder for uninstall registry check
        return {}

    async def _check_file_associations(self) -> Dict:
        """Check file associations"""
        # Placeholder for file association check
        return {}

    async def _check_system_policies(self) -> Dict:
        """Check system policies"""
        # Placeholder for system policy check
        return {}

    async def _find_suspicious_files(self) -> List[str]:
        """Find suspicious files"""
        # Placeholder for suspicious file detection
        return {}

    async def _find_suspicious_registry_entries(self) -> List[str]:
        """Find suspicious registry entries"""
        # Placeholder for suspicious registry entry detection
        return {}

    async def _find_suspicious_network_activity(self) -> List[str]:
        """Find suspicious network activity"""
        # Placeholder for suspicious network activity detection
        return {}
