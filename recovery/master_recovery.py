"""
Master Recovery Script for OPRYXX

Comprehensive OS recovery orchestration implementing the complete
GANDALFS recovery protocol for failed OS installations.
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import our recovery modules
try:
    from os_recovery_orchestrator import OSRecoveryOrchestrator
    from immediate_safe_mode_exit import ImmediateSafeModeExit
    from boot_diagnostics import BootDiagnostics
    from safe_mode_recovery import SafeModeRecovery
    from gandalfs_integration import GANDALFSRecovery
except ImportError as e:
    print(f"Warning: Could not import recovery module: {e}")

class MasterRecovery:
    """
    Master recovery orchestrator implementing the complete GANDALFS protocol
    Coordinates all recovery operations with smart sequencing and resilience
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.getcwd(), 'logs', 'master_recovery')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = self._setup_logging()
        self.recovery_session = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'start_time': datetime.now().isoformat(),
            'phases_completed': [],
            'current_phase': None,
            'total_attempts': 0,
            'success_rate': 0.0,
            'final_status': 'in_progress'
        }
        
        # Initialize recovery modules
        self.orchestrator = None
        self.safe_mode_exit = None
        self.diagnostics = None
        self.safe_mode_recovery = None
        self.gandalfs = None
        
        self._initialize_modules()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup master recovery logging"""
        logger = logging.getLogger('MasterRecovery')
        logger.setLevel(logging.DEBUG)
        
        # File handler
        log_file = os.path.join(self.log_dir, f'master_recovery_{self.recovery_session["session_id"]}.log')
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - MASTER - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _initialize_modules(self):
        """Initialize all recovery modules"""
        try:
            self.orchestrator = OSRecoveryOrchestrator(self.log_dir)
            self.safe_mode_exit = ImmediateSafeModeExit()
            self.diagnostics = BootDiagnostics(self.log_dir)
            self.safe_mode_recovery = SafeModeRecovery()
            self.gandalfs = GANDALFSRecovery()
            self.logger.info("All recovery modules initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing recovery modules: {e}")
    
    def execute_master_recovery(self) -> Dict:
        """Execute the complete master recovery sequence"""
        self.logger.info("=" * 60)
        self.logger.info("OPRYXX MASTER RECOVERY SYSTEM ACTIVATED")
        self.logger.info("Implementing GANDALFS Recovery Protocol")
        self.logger.info("=" * 60)
        
        recovery_result = {
            'session_id': self.recovery_session['session_id'],
            'success': False,
            'phases_executed': [],
            'final_recommendation': None,
            'recovery_summary': None
        }
        
        try:
            # Phase 1: Immediate Critical Response
            phase1_result = self._execute_phase1_immediate_response()
            recovery_result['phases_executed'].append(phase1_result)
            
            if phase1_result['success']:
                self.logger.info("Phase 1 successful - System may be recovered")
                recovery_result['success'] = True
                recovery_result['final_recommendation'] = 'reboot_and_verify'
            else:
                # Phase 2: Comprehensive Diagnostics
                phase2_result = self._execute_phase2_diagnostics()
                recovery_result['phases_executed'].append(phase2_result)
                
                # Phase 3: Targeted Recovery
                phase3_result = self._execute_phase3_targeted_recovery(phase2_result)
                recovery_result['phases_executed'].append(phase3_result)
                
                if phase3_result['success']:
                    recovery_result['success'] = True
                    recovery_result['final_recommendation'] = 'recovery_completed'
                else:
                    # Phase 4: Advanced Recovery
                    phase4_result = self._execute_phase4_advanced_recovery()
                    recovery_result['phases_executed'].append(phase4_result)
                    
                    if phase4_result['success']:
                        recovery_result['success'] = True
                        recovery_result['final_recommendation'] = 'advanced_recovery_completed'
                    else:
                        # Phase 5: Last Resort Recovery
                        phase5_result = self._execute_phase5_last_resort()
                        recovery_result['phases_executed'].append(phase5_result)
                        
                        recovery_result['success'] = phase5_result['success']
                        recovery_result['final_recommendation'] = phase5_result.get('recommendation', 'manual_intervention_required')
            
            # Generate final recovery summary
            recovery_result['recovery_summary'] = self._generate_recovery_summary(recovery_result)
            
            # Update session status
            self.recovery_session['final_status'] = 'success' if recovery_result['success'] else 'failed'
            self.recovery_session['end_time'] = datetime.now().isoformat()
            
            # Save session data
            self._save_recovery_session(recovery_result)
            
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"Critical error in master recovery: {e}")
            recovery_result['error'] = str(e)
            recovery_result['final_recommendation'] = 'critical_error_manual_intervention'
            return recovery_result
    
    def _execute_phase1_immediate_response(self) -> Dict:
        """Phase 1: Immediate Critical Response - Safe Mode Exit"""
        self.logger.info("PHASE 1: IMMEDIATE CRITICAL RESPONSE")
        self.logger.info("Executing immediate Safe Mode exit procedure...")
        
        self.recovery_session['current_phase'] = 'phase1_immediate'
        phase_result = {
            'phase': 'immediate_response',
            'success': False,
            'actions_taken': [],
            'time_taken': 0,
            'details': {}
        }
        
        start_time = time.time()
        
        try:
            # Execute immediate Safe Mode exit
            if self.safe_mode_exit:
                self.logger.info("Executing bcdedit /deletevalue {current} safeboot")
                exit_result = self.safe_mode_exit.execute_critical_command()
                
                phase_result['actions_taken'].append('immediate_safe_mode_exit')
                phase_result['details']['safe_mode_exit'] = exit_result
                
                if exit_result['success']:
                    self.logger.info("SUCCESS: Safe Mode exit command executed successfully")
                    phase_result['success'] = True
                    
                    # Prepare reboot instructions
                    reboot_prep = self.safe_mode_exit.prepare_reboot_instructions()
                    phase_result['details']['reboot_instructions'] = reboot_prep
                    
                    self.logger.info("CRITICAL: System reboot required to complete recovery")
                    self.logger.info("Please reboot the system and monitor boot process")
                    
                else:
                    self.logger.warning("Safe Mode exit command failed - proceeding to advanced recovery")
            
            phase_result['time_taken'] = time.time() - start_time
            self.recovery_session['phases_completed'].append('phase1_immediate')
            
            return phase_result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 1: {e}")
            phase_result['error'] = str(e)
            phase_result['time_taken'] = time.time() - start_time
            return phase_result
    
    def _execute_phase2_diagnostics(self) -> Dict:
        """Phase 2: Comprehensive System Diagnostics"""
        self.logger.info("PHASE 2: COMPREHENSIVE SYSTEM DIAGNOSTICS")
        self.logger.info("Gathering complete system state and failure analysis...")
        
        self.recovery_session['current_phase'] = 'phase2_diagnostics'
        phase_result = {
            'phase': 'comprehensive_diagnostics',
            'success': False,
            'diagnostics_data': {},
            'failure_analysis': {},
            'time_taken': 0
        }
        
        start_time = time.time()
        
        try:
            # Run comprehensive diagnostics
            if self.diagnostics:
                diagnostic_results = self.diagnostics.run_comprehensive_diagnostics()
                phase_result['diagnostics_data'] = diagnostic_results
                
                # Generate summary
                summary = self.diagnostics.generate_summary_report()
                self.logger.info("Diagnostics Summary:")
                for line in summary.split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")
                
                phase_result['success'] = True
            
            # Run orchestrator diagnostics
            if self.orchestrator:
                orchestrator_diagnostics = self.orchestrator.gather_system_diagnostics()
                phase_result['diagnostics_data']['orchestrator'] = orchestrator_diagnostics
                
                # Identify failure points
                failure_analysis = self.orchestrator.identify_failure_point(orchestrator_diagnostics)
                phase_result['failure_analysis'] = failure_analysis
                
                self.logger.info(f"Primary blocker identified: {failure_analysis.get('primary_blocker', 'unknown')}")
                self.logger.info(f"Recovery strategy: {failure_analysis.get('recovery_strategy', 'unknown')}")
            
            phase_result['time_taken'] = time.time() - start_time
            self.recovery_session['phases_completed'].append('phase2_diagnostics')
            
            return phase_result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 2: {e}")
            phase_result['error'] = str(e)
            phase_result['time_taken'] = time.time() - start_time
            return phase_result
    
    def _execute_phase3_targeted_recovery(self, diagnostics_result: Dict) -> Dict:
        """Phase 3: Targeted Recovery Based on Diagnostics"""
        self.logger.info("PHASE 3: TARGETED RECOVERY OPERATIONS")
        self.logger.info("Executing targeted recovery based on diagnostic findings...")
        
        self.recovery_session['current_phase'] = 'phase3_targeted'
        phase_result = {
            'phase': 'targeted_recovery',
            'success': False,
            'recovery_actions': [],
            'time_taken': 0
        }
        
        start_time = time.time()
        
        try:
            failure_analysis = diagnostics_result.get('failure_analysis', {})
            recovery_strategy = failure_analysis.get('recovery_strategy')
            
            if recovery_strategy == 'clear_safe_mode_flags':
                # Alternative Safe Mode recovery
                if self.safe_mode_recovery:
                    self.logger.info("Executing alternative Safe Mode recovery...")
                    alt_recovery = self.safe_mode_recovery.execute_alternative_recovery()
                    phase_result['recovery_actions'].append('alternative_safe_mode_recovery')
                    phase_result['success'] = alt_recovery.get('overall_success', False)
            
            elif recovery_strategy == 'disk_repair_and_reinstall':
                # Disk repair sequence
                self.logger.info("Executing disk repair and recovery...")
                if self.orchestrator:
                    repair_success = self.orchestrator._disk_repair_and_reinstall()
                    phase_result['recovery_actions'].append('disk_repair_and_reinstall')
                    phase_result['success'] = repair_success
            
            else:
                # Generic recovery sequence
                self.logger.info("Executing generic recovery sequence...")
                if self.orchestrator:
                    generic_success = self.orchestrator._generic_recovery_sequence()
                    phase_result['recovery_actions'].append('generic_recovery_sequence')
                    phase_result['success'] = generic_success
            
            phase_result['time_taken'] = time.time() - start_time
            self.recovery_session['phases_completed'].append('phase3_targeted')
            
            return phase_result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 3: {e}")
            phase_result['error'] = str(e)
            phase_result['time_taken'] = time.time() - start_time
            return phase_result
    
    def _execute_phase4_advanced_recovery(self) -> Dict:
        """Phase 4: Advanced Recovery Operations"""
        self.logger.info("PHASE 4: ADVANCED RECOVERY OPERATIONS")
        self.logger.info("Executing advanced recovery procedures...")
        
        self.recovery_session['current_phase'] = 'phase4_advanced'
        phase_result = {
            'phase': 'advanced_recovery',
            'success': False,
            'advanced_actions': [],
            'time_taken': 0
        }
        
        start_time = time.time()
        
        try:
            # Create recovery image before advanced operations
            if self.gandalfs:
                self.logger.info("Creating system recovery image...")
                image_created = self.gandalfs.create_recovery_image(
                    f"pre_advanced_recovery_{self.recovery_session['session_id']}"
                )
                if image_created:
                    phase_result['advanced_actions'].append('recovery_image_created')
            
            # Advanced boot repair
            self.logger.info("Executing advanced boot repair...")
            boot_repair_success = self._execute_advanced_boot_repair()
            phase_result['advanced_actions'].append('advanced_boot_repair')
            
            # System file repair
            self.logger.info("Executing system file repair...")
            sfc_success = self._execute_system_file_repair()
            phase_result['advanced_actions'].append('system_file_repair')
            
            # Registry repair
            self.logger.info("Executing registry repair...")
            registry_success = self._execute_registry_repair()
            phase_result['advanced_actions'].append('registry_repair')
            
            # Determine overall success
            phase_result['success'] = any([boot_repair_success, sfc_success, registry_success])
            
            phase_result['time_taken'] = time.time() - start_time
            self.recovery_session['phases_completed'].append('phase4_advanced')
            
            return phase_result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 4: {e}")
            phase_result['error'] = str(e)
            phase_result['time_taken'] = time.time() - start_time
            return phase_result
    
    def _execute_phase5_last_resort(self) -> Dict:
        """Phase 5: Last Resort Recovery"""
        self.logger.info("PHASE 5: LAST RESORT RECOVERY")
        self.logger.info("Preparing for clean installation or manual intervention...")
        
        self.recovery_session['current_phase'] = 'phase5_last_resort'
        phase_result = {
            'phase': 'last_resort',
            'success': False,
            'preparation_actions': [],
            'recommendation': 'clean_install_required',
            'time_taken': 0
        }
        
        start_time = time.time()
        
        try:
            # Backup user data
            self.logger.info("Backing up user data...")
            backup_success = self._backup_user_data()
            if backup_success:
                phase_result['preparation_actions'].append('user_data_backed_up')
            
            # Create clean install instructions
            self.logger.info("Generating clean installation instructions...")
            instructions = self._generate_clean_install_instructions()
            phase_result['clean_install_instructions'] = instructions
            phase_result['preparation_actions'].append('clean_install_instructions_generated')
            
            # Save recovery state
            self.logger.info("Saving recovery state for future reference...")
            state_saved = self._save_recovery_state()
            if state_saved:
                phase_result['preparation_actions'].append('recovery_state_saved')
            
            # Determine if any preparation was successful
            phase_result['success'] = len(phase_result['preparation_actions']) > 0
            
            phase_result['time_taken'] = time.time() - start_time
            self.recovery_session['phases_completed'].append('phase5_last_resort')
            
            return phase_result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 5: {e}")
            phase_result['error'] = str(e)
            phase_result['time_taken'] = time.time() - start_time
            return phase_result
    
    def _execute_advanced_boot_repair(self) -> bool:
        """Execute advanced boot repair operations"""
        try:
            commands = [
                ['bootrec', '/fixmbr'],
                ['bootrec', '/fixboot'],
                ['bootrec', '/scanos'],
                ['bootrec', '/rebuildbcd'],
                ['bcdedit', '/export', 'C:\\bcd_backup'],
                ['attrib', '-r', '-s', '-h', 'C:\\boot\\bcd'],
                ['ren', 'C:\\boot\\bcd', 'bcd.old']
            ]
            
            success_count = 0
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        success_count += 1
                except:
                    pass
            
            return success_count > len(commands) // 2
        except:
            return False
    
    def _execute_system_file_repair(self) -> bool:
        """Execute system file repair"""
        try:
            # SFC scan
            sfc_result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True, timeout=300)
            
            # DISM repair
            dism_result = subprocess.run(['dism', '/online', '/cleanup-image', '/restorehealth'], 
                                       capture_output=True, text=True, timeout=600)
            
            return sfc_result.returncode == 0 or dism_result.returncode == 0
        except:
            return False
    
    def _execute_registry_repair(self) -> bool:
        """Execute registry repair operations"""
        try:
            # Export current registry
            export_result = subprocess.run(['reg', 'export', 'HKLM', 'C:\\registry_backup.reg'], 
                                         capture_output=True, text=True)
            
            # Basic registry repair commands
            repair_commands = [
                ['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run', '/f'],
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Services', '/f']
            ]
            
            success_count = 0
            for cmd in repair_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except:
                    pass
            
            return success_count > 0
        except:
            return False
    
    def _backup_user_data(self) -> bool:
        """Backup user data to recovery location"""
        try:
            backup_dir = os.path.join(self.log_dir, 'user_backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Common user directories
            user_dirs = [
                os.path.expanduser('~\\Documents'),
                os.path.expanduser('~\\Desktop'),
                os.path.expanduser('~\\Downloads'),
                os.path.expanduser('~\\Pictures')
            ]
            
            backup_success = False
            for user_dir in user_dirs:
                if os.path.exists(user_dir):
                    try:
                        target_dir = os.path.join(backup_dir, os.path.basename(user_dir))
                        result = subprocess.run(['robocopy', user_dir, target_dir, '/E', '/R:3', '/W:10'], 
                                              capture_output=True, text=True)
                        if result.returncode < 8:  # Robocopy success codes
                            backup_success = True
                    except:
                        pass
            
            return backup_success
        except:
            return False
    
    def _generate_clean_install_instructions(self) -> Dict:
        """Generate clean installation instructions"""
        return {
            'preparation_steps': [
                "1. Create Windows installation media (USB/DVD)",
                "2. Download latest Windows ISO from Microsoft",
                "3. Use Rufus or Windows Media Creation Tool",
                "4. Backup important data (if not already done)"
            ],
            'installation_steps': [
                "1. Boot from Windows installation media",
                "2. Select language and keyboard layout",
                "3. Click 'Install Now'",
                "4. Enter product key or skip",
                "5. Accept license terms",
                "6. Choose 'Custom: Install Windows only (advanced)'",
                "7. Delete all partitions on system drive",
                "8. Select unallocated space and click Next",
                "9. Wait for installation to complete",
                "10. Complete initial setup (OOBE)"
            ],
            'post_installation': [
                "1. Install Windows updates",
                "2. Install device drivers",
                "3. Restore user data from backup",
                "4. Reinstall applications",
                "5. Configure system settings"
            ],
            'backup_location': os.path.join(self.log_dir, 'user_backup')
        }
    
    def _save_recovery_state(self) -> bool:
        """Save current recovery state"""
        try:
            state_file = os.path.join(self.log_dir, f'recovery_state_{self.recovery_session["session_id"]}.json')
            with open(state_file, 'w') as f:
                json.dump(self.recovery_session, f, indent=2)
            return True
        except:
            return False
    
    def _generate_recovery_summary(self, recovery_result: Dict) -> Dict:
        """Generate comprehensive recovery summary"""
        summary = {
            'session_overview': {
                'session_id': self.recovery_session['session_id'],
                'total_phases': len(recovery_result['phases_executed']),
                'successful_phases': sum(1 for phase in recovery_result['phases_executed'] if phase.get('success')),
                'total_time': self._calculate_total_time(),
                'overall_success': recovery_result['success']
            },
            'phase_breakdown': recovery_result['phases_executed'],
            'final_status': recovery_result['final_recommendation'],
            'next_steps': self._generate_next_steps(recovery_result),
            'files_created': self._list_created_files()
        }
        
        return summary
    
    def _calculate_total_time(self) -> float:
        """Calculate total recovery time"""
        try:
            start = datetime.fromisoformat(self.recovery_session['start_time'])
            end = datetime.fromisoformat(self.recovery_session.get('end_time', datetime.now().isoformat()))
            return (end - start).total_seconds()
        except:
            return 0.0
    
    def _generate_next_steps(self, recovery_result: Dict) -> List[str]:
        """Generate next steps based on recovery result"""
        if recovery_result['success']:
            return [
                "1. Reboot the system",
                "2. Verify normal Windows startup",
                "3. Complete any pending OS installation steps",
                "4. Install Windows updates",
                "5. Create new recovery point"
            ]
        else:
            return [
                "1. Review recovery logs for detailed error information",
                "2. Consider clean Windows installation",
                "3. Check hardware compatibility",
                "4. Contact technical support if needed",
                "5. Use recovery backup if available"
            ]
    
    def _list_created_files(self) -> List[str]:
        """List files created during recovery"""
        created_files = []
        try:
            for root, dirs, files in os.walk(self.log_dir):
                for file in files:
                    created_files.append(os.path.join(root, file))
        except:
            pass
        return created_files
    
    def _save_recovery_session(self, recovery_result: Dict):
        """Save complete recovery session data"""
        try:
            session_file = os.path.join(self.log_dir, f'recovery_session_{self.recovery_session["session_id"]}.json')
            complete_session = {
                'session_info': self.recovery_session,
                'recovery_result': recovery_result
            }
            
            with open(session_file, 'w') as f:
                json.dump(complete_session, f, indent=2, default=str)
            
            self.logger.info(f"Recovery session saved to: {session_file}")
        except Exception as e:
            self.logger.error(f"Failed to save recovery session: {e}")

def main():
    """Main entry point for master recovery"""
    print("OPRYXX MASTER RECOVERY SYSTEM")
    print("=" * 50)
    print("Comprehensive OS Recovery Implementation")
    print("GANDALFS Protocol Active")
    print("=" * 50)
    print()
    
    # Check admin privileges
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("ERROR: Administrator privileges required")
            print("Please run this script as Administrator")
            return 1
    except:
        print("WARNING: Could not verify administrator privileges")
    
    # Initialize and execute master recovery
    master_recovery = MasterRecovery()
    
    try:
        # Execute complete recovery sequence
        result = master_recovery.execute_master_recovery()
        
        # Display results
        print("\nRECOVERY OPERATION COMPLETED")
        print("=" * 40)
        print(f"Session ID: {result['session_id']}")
        print(f"Overall Success: {result['success']}")
        print(f"Phases Executed: {len(result['phases_executed'])}")
        print(f"Final Recommendation: {result['final_recommendation']}")
        
        if result.get('recovery_summary'):
            summary = result['recovery_summary']
            print(f"\nTotal Time: {summary['session_overview']['total_time']:.2f} seconds")
            print(f"Successful Phases: {summary['session_overview']['successful_phases']}")
            
            print("\nNext Steps:")
            for step in summary['next_steps']:
                print(f"  {step}")
        
        print(f"\nDetailed logs available in: {master_recovery.log_dir}")
        
        return 0 if result['success'] else 1
        
    except KeyboardInterrupt:
        print("\nRecovery interrupted by user")
        return 2
    except Exception as e:
        print(f"\nCritical error in master recovery: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())