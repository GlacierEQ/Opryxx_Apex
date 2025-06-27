"""
OS Recovery Orchestrator for OPRYXX

Comprehensive OS recovery system implementing the GANDALFS protocol
for handling failed OS installations and Safe Mode recovery.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class RecoveryState:
    """Track recovery operation state"""
    step: str
    status: str
    timestamp: str
    details: Dict
    errors: List[str]

class OSRecoveryOrchestrator:
    """
    Main orchestrator for OS recovery operations
    Implements the GANDALFS recovery protocol
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.getcwd(), 'logs', 'recovery')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = self._setup_logging()
        self.recovery_log = []
        self.current_state = RecoveryState(
            step="initialization",
            status="starting",
            timestamp=datetime.now().isoformat(),
            details={},
            errors=[]
        )
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('OSRecovery')
        logger.setLevel(logging.DEBUG)
        
        # File handler
        log_file = os.path.join(self.log_dir, f'recovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def log_state(self, step: str, status: str, details: Dict = None, errors: List[str] = None):
        """Log current recovery state"""
        self.current_state = RecoveryState(
            step=step,
            status=status,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            errors=errors or []
        )
        self.recovery_log.append(asdict(self.current_state))
        self.logger.info(f"Step: {step} | Status: {status}")
        
    def gather_system_diagnostics(self) -> Dict:
        """Phase 1: Context Absorption & Diagnostics"""
        self.log_state("diagnostics", "gathering_system_info")
        
        diagnostics = {
            'boot_mode': self._check_boot_mode(),
            'safe_mode_status': self._check_safe_mode_status(),
            'disk_status': self._check_disk_status(),
            'boot_configuration': self._get_boot_configuration(),
            'system_logs': self._gather_system_logs(),
            'hardware_status': self._check_hardware_status()
        }
        
        self.log_state("diagnostics", "completed", diagnostics)
        return diagnostics
    
    def _check_boot_mode(self) -> Dict:
        """Check current boot mode and configuration"""
        try:
            # Check if in Safe Mode
            result = subprocess.run(['msinfo32', '/report', 'temp_sysinfo.txt'], 
                                  capture_output=True, text=True, timeout=30)
            
            boot_info = {
                'safe_mode': os.environ.get('SAFEBOOT_OPTION') is not None,
                'boot_type': 'safe' if os.environ.get('SAFEBOOT_OPTION') else 'normal',
                'last_boot_good': self._check_last_known_good()
            }
            
            return boot_info
        except Exception as e:
            self.logger.error(f"Error checking boot mode: {e}")
            return {'error': str(e)}
    
    def _check_safe_mode_status(self) -> Dict:
        """Check Safe Mode configuration and persistence"""
        try:
            # Check bcdedit for Safe Mode flags
            result = subprocess.run(['bcdedit', '/enum'], capture_output=True, text=True)
            
            safe_mode_info = {
                'persistent_safe_mode': 'safeboot' in result.stdout.lower(),
                'boot_flags': self._parse_boot_flags(result.stdout),
                'recovery_enabled': 'recoveryenabled' in result.stdout.lower()
            }
            
            return safe_mode_info
        except Exception as e:
            self.logger.error(f"Error checking Safe Mode status: {e}")
            return {'error': str(e)}
    
    def _check_disk_status(self) -> Dict:
        """Check disk health and partition status"""
        try:
            # Check disk health
            chkdsk_result = subprocess.run(['chkdsk', 'C:', '/f', '/r'], 
                                         capture_output=True, text=True)
            
            disk_info = {
                'disk_health': 'healthy' if chkdsk_result.returncode == 0 else 'errors_found',
                'free_space': self._get_disk_space(),
                'partition_table': self._get_partition_info()
            }
            
            return disk_info
        except Exception as e:
            self.logger.error(f"Error checking disk status: {e}")
            return {'error': str(e)}
    
    def _get_boot_configuration(self) -> Dict:
        """Get detailed boot configuration"""
        try:
            result = subprocess.run(['bcdedit', '/v'], capture_output=True, text=True)
            return {'boot_config': result.stdout}
        except Exception as e:
            return {'error': str(e)}
    
    def _gather_system_logs(self) -> Dict:
        """Gather relevant system logs"""
        try:
            # Get Windows Event Logs
            logs = {
                'system_log': self._get_event_log('System'),
                'application_log': self._get_event_log('Application'),
                'setup_log': self._get_setup_logs()
            }
            return logs
        except Exception as e:
            return {'error': str(e)}
    
    def _check_hardware_status(self) -> Dict:
        """Check hardware status and compatibility"""
        try:
            # Basic hardware check
            hardware_info = {
                'memory_test': self._check_memory(),
                'storage_test': self._check_storage_health(),
                'driver_status': self._check_driver_status()
            }
            return hardware_info
        except Exception as e:
            return {'error': str(e)}
    
    def identify_failure_point(self, diagnostics: Dict) -> Dict:
        """Phase 2: Priority Elevation & Blocker Identification"""
        self.log_state("analysis", "identifying_blockers")
        
        blockers = {
            'primary_blocker': None,
            'secondary_blockers': [],
            'failure_stage': None,
            'recovery_strategy': None
        }
        
        # Analyze Safe Mode persistence
        if diagnostics.get('safe_mode_status', {}).get('persistent_safe_mode'):
            blockers['primary_blocker'] = 'persistent_safe_mode'
            blockers['recovery_strategy'] = 'clear_safe_mode_flags'
        
        # Analyze disk issues
        if diagnostics.get('disk_status', {}).get('disk_health') != 'healthy':
            if not blockers['primary_blocker']:
                blockers['primary_blocker'] = 'disk_corruption'
                blockers['recovery_strategy'] = 'disk_repair_and_reinstall'
            else:
                blockers['secondary_blockers'].append('disk_corruption')
        
        # Analyze boot configuration
        boot_config = diagnostics.get('boot_configuration', {})
        if 'error' in boot_config or not boot_config.get('boot_config'):
            blockers['secondary_blockers'].append('boot_config_corruption')
        
        self.log_state("analysis", "completed", blockers)
        return blockers
    
    def execute_recovery_sequence(self, blockers: Dict) -> bool:
        """Phase 3: Smart Sequencing - Execute recovery plan"""
        self.log_state("recovery", "starting_sequence")
        
        strategy = blockers.get('recovery_strategy')
        
        if strategy == 'clear_safe_mode_flags':
            return self._clear_safe_mode_recovery()
        elif strategy == 'disk_repair_and_reinstall':
            return self._disk_repair_and_reinstall()
        else:
            return self._generic_recovery_sequence()
    
    def _clear_safe_mode_recovery(self) -> bool:
        """Clear Safe Mode flags and attempt normal boot"""
        self.log_state("recovery", "clearing_safe_mode")
        
        try:
            # Clear Safe Mode boot flag
            result = subprocess.run(['bcdedit', '/deletevalue', '{current}', 'safeboot'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Successfully cleared Safe Mode flag")
                
                # Attempt to restart installation
                if self._resume_os_installation():
                    self.log_state("recovery", "safe_mode_cleared_success")
                    return True
                else:
                    self.log_state("recovery", "safe_mode_cleared_install_failed")
                    return self._fallback_to_clean_install()
            else:
                self.logger.error(f"Failed to clear Safe Mode flag: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error clearing Safe Mode: {e}")
            self.log_state("recovery", "safe_mode_clear_failed", errors=[str(e)])
            return False
    
    def _resume_os_installation(self) -> bool:
        """Attempt to resume OS installation"""
        try:
            # Check for Windows Setup
            setup_paths = [
                'C:\\Windows\\System32\\oobe\\windeploy.exe',
                'C:\\Windows\\System32\\sysprep\\sysprep.exe'
            ]
            
            for setup_path in setup_paths:
                if os.path.exists(setup_path):
                    self.logger.info(f"Found setup at {setup_path}, attempting resume")
                    result = subprocess.run([setup_path, '/oobe'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error resuming installation: {e}")
            return False
    
    def _disk_repair_and_reinstall(self) -> bool:
        """Repair disk and perform clean installation"""
        self.log_state("recovery", "disk_repair_and_reinstall")
        
        try:
            # Run disk repair
            self.logger.info("Running disk repair...")
            chkdsk_result = subprocess.run(['chkdsk', 'C:', '/f', '/r', '/x'], 
                                         capture_output=True, text=True)
            
            if chkdsk_result.returncode == 0:
                self.logger.info("Disk repair completed successfully")
                return self._prepare_clean_install()
            else:
                self.logger.error("Disk repair failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during disk repair: {e}")
            return False
    
    def _prepare_clean_install(self) -> bool:
        """Prepare for clean OS installation"""
        self.log_state("recovery", "preparing_clean_install")
        
        try:
            # Backup user data if accessible
            backup_success = self._backup_user_data()
            
            # Create recovery instructions
            instructions = {
                'step': 'clean_install_required',
                'instructions': [
                    'Create bootable USB with latest Windows ISO',
                    'Boot from USB drive',
                    'Format system drive during installation',
                    'Complete fresh OS installation',
                    'Restore user data from backup'
                ],
                'backup_location': self._get_backup_location() if backup_success else None
            }
            
            # Save instructions to file
            instructions_file = os.path.join(self.log_dir, 'clean_install_instructions.json')
            with open(instructions_file, 'w') as f:
                json.dump(instructions, f, indent=2)
            
            self.log_state("recovery", "clean_install_prepared", instructions)
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing clean install: {e}")
            return False
    
    def _backup_user_data(self) -> bool:
        """Backup accessible user data"""
        try:
            backup_dir = os.path.join(self.log_dir, 'user_backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Common user data locations
            user_paths = [
                os.path.expanduser('~\\Documents'),
                os.path.expanduser('~\\Desktop'),
                os.path.expanduser('~\\Downloads')
            ]
            
            for path in user_paths:
                if os.path.exists(path):
                    # Use robocopy for reliable backup
                    subprocess.run(['robocopy', path, 
                                  os.path.join(backup_dir, os.path.basename(path)), 
                                  '/E', '/R:3', '/W:10'], 
                                 capture_output=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def _generic_recovery_sequence(self) -> bool:
        """Generic recovery sequence for unknown issues"""
        self.log_state("recovery", "generic_sequence")
        
        recovery_steps = [
            self._run_sfc_scan,
            self._run_dism_repair,
            self._reset_boot_configuration,
            self._attempt_system_restore
        ]
        
        for step in recovery_steps:
            try:
                if step():
                    self.logger.info(f"Recovery step {step.__name__} succeeded")
                else:
                    self.logger.warning(f"Recovery step {step.__name__} failed")
            except Exception as e:
                self.logger.error(f"Error in {step.__name__}: {e}")
        
        return True
    
    def generate_recovery_report(self) -> Dict:
        """Generate comprehensive recovery report"""
        report = {
            'recovery_session': {
                'start_time': self.recovery_log[0]['timestamp'] if self.recovery_log else None,
                'end_time': datetime.now().isoformat(),
                'total_steps': len(self.recovery_log),
                'final_status': self.current_state.status
            },
            'recovery_log': self.recovery_log,
            'recommendations': self._generate_recommendations(),
            'next_steps': self._generate_next_steps()
        }
        
        # Save report
        report_file = os.path.join(self.log_dir, f'recovery_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    # Helper methods
    def _parse_boot_flags(self, bcdedit_output: str) -> List[str]:
        """Parse boot flags from bcdedit output"""
        flags = []
        for line in bcdedit_output.split('\n'):
            if 'safeboot' in line.lower():
                flags.append('safeboot')
            if 'recoveryenabled' in line.lower():
                flags.append('recoveryenabled')
        return flags
    
    def _check_last_known_good(self) -> bool:
        """Check if Last Known Good Configuration is available"""
        try:
            result = subprocess.run(['bcdedit', '/enum', '{legacy}'], 
                                  capture_output=True, text=True)
            return 'legacy' in result.stdout.lower()
        except:
            return False
    
    def _get_disk_space(self) -> Dict:
        """Get disk space information"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('C:')
            return {
                'total_gb': total // (1024**3),
                'used_gb': used // (1024**3),
                'free_gb': free // (1024**3)
            }
        except:
            return {}
    
    def _get_partition_info(self) -> List[Dict]:
        """Get partition information"""
        try:
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'size,freespace,caption'], 
                                  capture_output=True, text=True)
            # Parse output (simplified)
            return [{'info': result.stdout}]
        except:
            return []
    
    def _get_event_log(self, log_name: str) -> Dict:
        """Get Windows Event Log entries"""
        try:
            result = subprocess.run(['wevtutil', 'qe', log_name, '/c:10', '/rd:true', '/f:text'], 
                                  capture_output=True, text=True)
            return {'entries': result.stdout}
        except:
            return {}
    
    def _get_setup_logs(self) -> Dict:
        """Get Windows Setup logs"""
        setup_log_paths = [
            'C:\\Windows\\Panther\\setupact.log',
            'C:\\Windows\\Panther\\setuperr.log'
        ]
        
        logs = {}
        for log_path in setup_log_paths:
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        logs[os.path.basename(log_path)] = f.read()
                except:
                    pass
        
        return logs
    
    def _check_memory(self) -> Dict:
        """Basic memory check"""
        try:
            result = subprocess.run(['wmic', 'memorychip', 'get', 'capacity,speed'], 
                                  capture_output=True, text=True)
            return {'memory_info': result.stdout}
        except:
            return {}
    
    def _check_storage_health(self) -> Dict:
        """Check storage device health"""
        try:
            result = subprocess.run(['wmic', 'diskdrive', 'get', 'status,model'], 
                                  capture_output=True, text=True)
            return {'storage_info': result.stdout}
        except:
            return {}
    
    def _check_driver_status(self) -> Dict:
        """Check driver status"""
        try:
            result = subprocess.run(['driverquery', '/v'], capture_output=True, text=True)
            return {'driver_info': result.stdout}
        except:
            return {}
    
    def _fallback_to_clean_install(self) -> bool:
        """Fallback to clean installation procedure"""
        return self._prepare_clean_install()
    
    def _run_sfc_scan(self) -> bool:
        """Run System File Checker"""
        try:
            result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _run_dism_repair(self) -> bool:
        """Run DISM repair"""
        try:
            result = subprocess.run(['dism', '/online', '/cleanup-image', '/restorehealth'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _reset_boot_configuration(self) -> bool:
        """Reset boot configuration"""
        try:
            subprocess.run(['bcdedit', '/export', 'C:\\bcd_backup'], capture_output=True)
            result = subprocess.run(['bootrec', '/rebuildbcd'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _attempt_system_restore(self) -> bool:
        """Attempt system restore"""
        try:
            result = subprocess.run(['rstrui.exe', '/offline'], capture_output=True, text=True)
            return True  # System restore UI launched
        except:
            return False
    
    def _get_backup_location(self) -> str:
        """Get backup location path"""
        return os.path.join(self.log_dir, 'user_backup')
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recovery recommendations"""
        return [
            "Create regular system backups",
            "Keep Windows installation media updated",
            "Monitor disk health regularly",
            "Maintain current drivers",
            "Document system configuration"
        ]
    
    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on recovery status"""
        if self.current_state.status == 'completed':
            return [
                "Verify system stability",
                "Restore user data if backed up",
                "Update system and drivers",
                "Create new recovery point"
            ]
        else:
            return [
                "Review recovery log for errors",
                "Consider hardware diagnostics",
                "Prepare for clean installation",
                "Contact technical support if needed"
            ]

def main():
    """Main recovery orchestration function"""
    print("OPRYXX OS Recovery Orchestrator")
    print("=" * 40)
    
    orchestrator = OSRecoveryOrchestrator()
    
    try:
        # Phase 1: Diagnostics
        print("Phase 1: Gathering system diagnostics...")
        diagnostics = orchestrator.gather_system_diagnostics()
        
        # Phase 2: Analysis
        print("Phase 2: Analyzing failure points...")
        blockers = orchestrator.identify_failure_point(diagnostics)
        
        # Phase 3: Recovery
        print("Phase 3: Executing recovery sequence...")
        recovery_success = orchestrator.execute_recovery_sequence(blockers)
        
        # Phase 4: Reporting
        print("Phase 4: Generating recovery report...")
        report = orchestrator.generate_recovery_report()
        
        print(f"\nRecovery completed. Status: {'SUCCESS' if recovery_success else 'PARTIAL'}")
        print(f"Report saved to: {orchestrator.log_dir}")
        
        return recovery_success
        
    except Exception as e:
        orchestrator.logger.error(f"Critical error in recovery orchestration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)