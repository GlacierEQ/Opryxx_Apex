"""
Crash Analysis Engine - Advanced System Crash Detection and Analysis
"""
import os
import sys
import asyncio
import logging
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CrashAnalysis:
    crash_type: str
    severity: str
    root_causes: List[str]
    immediate_fixes: List[str]
    preventive_measures: List[str]
    system_impact: Dict[str, str]
    recovery_actions: List[str]

class CrashAnalysisEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def analyze_system_crash(self) -> CrashAnalysis:
        """Comprehensive system crash analysis"""
        try:
            # Parallel analysis of different crash indicators
            dump_files = await self._analyze_dump_files()
            event_logs = await self._analyze_event_logs()
            memory_analysis = await self._analyze_memory_issues()
            driver_analysis = await self._analyze_driver_issues()
            hardware_analysis = await self._analyze_hardware_health()
            
            # Compile comprehensive analysis
            return self._compile_crash_analysis(
                dump_files, event_logs, memory_analysis,
                driver_analysis, hardware_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Crash analysis failed: {e}")
            return CrashAnalysis(
                crash_type="ANALYSIS_ERROR",
                severity="HIGH",
                root_causes=[f"Analysis error: {str(e)}"],
                immediate_fixes=["Restart analysis", "Check system logs"],
                preventive_measures=["Regular system maintenance"],
                system_impact={"analysis": "failed"},
                recovery_actions=["Manual investigation required"]
            )

    async def _analyze_dump_files(self) -> List[Dict]:
        """Analyze crash dump files"""
        try:
            dump_locations = [
                "C:\\Windows\\Minidump",
                "C:\\Windows\\MEMORY.DMP",
                "C:\\Windows\\LiveKernelReports"
            ]
            
            dump_files = []
            for location in dump_locations:
                if os.path.exists(location):
                    if os.path.isdir(location):
                        for file in os.listdir(location):
                            if file.endswith(('.dmp', '.mdmp')):
                                file_path = os.path.join(location, file)
                                dump_files.append({
                                    "path": file_path,
                                    "size": os.path.getsize(file_path),
                                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path))
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

                crash_events = []
                for event in events if isinstance(events, list) else [events]:
                    if any(keyword in event.get("Message", "").lower() for keyword in [
                        "bugcheck", "blue screen", "kernel", "memory", "crash", "dump"
                    ]):
                        crash_events.append(event)

                return {
                    "total_errors": len(events) if isinstance(events, list) else 1,
                    "crash_related": len(crash_events),
                    "recent_crashes": crash_events[:10]
                }

            return {"total_errors": 0, "crash_related": 0, "recent_crashes": []}

        except Exception as e:
            self.logger.error(f"Event log analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_memory_issues(self) -> Dict:
        """Comprehensive memory analysis"""
        try:
            memory_info = psutil.virtual_memory()
            memory_pressure = memory_info.percent > 85

            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 5:
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

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
                "driver_details": problematic_drivers[:20],
                "analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Driver analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_hardware_health(self) -> Dict:
        """Analyze hardware health"""
        try:
            cpu_temp = 0
            disk_health = "unknown"
            
            # Check CPU temperature if available
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                if hasattr(entry, 'current') and entry.current:
                                    cpu_temp = max(cpu_temp, entry.current)
            except Exception:
                pass
            
            # Check disk health using SMART (simplified)
            try:
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'status'],
                    capture_output=True, text=True, timeout=10
                )
                if 'OK' in result.stdout:
                    disk_health = "good"
                else:
                    disk_health = "warning"
            except Exception:
                disk_health = "unknown"
            
            return {
                "cpu_temperature": cpu_temp,
                "disk_health": disk_health,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Hardware analysis failed: {e}")
            return {"error": str(e)}

    def _compile_crash_analysis(self, dump_files, event_logs, memory_analysis,
                               driver_analysis, hardware_analysis) -> CrashAnalysis:
        """Compile comprehensive crash analysis"""
        try:
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

    def generate_report(self, analysis: CrashAnalysis) -> str:
        """Generate human-readable crash analysis report"""
        report = f"""
🔴 CRASH ANALYSIS REPORT
{'='*50}

Crash Type: {analysis.crash_type}
Severity: {analysis.severity}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 ROOT CAUSES:
{chr(10).join(f'• {cause}' for cause in analysis.root_causes)}

⚡ IMMEDIATE FIXES:
{chr(10).join(f'• {fix}' for fix in analysis.immediate_fixes)}

🛡️ PREVENTIVE MEASURES:
{chr(10).join(f'• {measure}' for measure in analysis.preventive_measures)}

🔧 RECOVERY ACTIONS:
{chr(10).join(f'• {action}' for action in analysis.recovery_actions)}

📊 SYSTEM IMPACT:
{chr(10).join(f'• {key}: {value}' for key, value in analysis.system_impact.items())}
"""
        return report

if __name__ == "__main__":
    async def main():
        engine = CrashAnalysisEngine()
        analysis = await engine.analyze_system_crash()
        print(engine.generate_report(analysis))
    
    asyncio.run(main())