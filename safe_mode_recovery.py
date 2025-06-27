"""
Safe Mode Recovery for OPRYXX

This module provides functionality to recover from Safe Mode boot issues
on Dell Inspiron 2-in-1 devices during OS installation.
"""

import os
import sys
import logging
import subprocess
import ctypes
import time
from typing import Optional, Dict, List
from pathlib import Path

class SafeModeRecovery:
    """Handle Safe Mode recovery operations for Dell Inspiron 2-in-1 devices."""
    
    def __init__(self, log_level: int = logging.INFO):
        """Initialize the Safe Mode recovery handler.
        
        Args:
            log_level: Logging level (default: INFO)
        """
        self.logger = self._setup_logging(log_level)
        self.is_admin = self._check_admin_rights()
        self.system_root = os.environ.get('SystemRoot', 'C:\\Windows')
        self.boot_config_path = os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'bootstat.dat')
        self.bcdedit_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows\\System32'), 'bcdedit.exe')
    
    def _setup_logging(self, log_level: int) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('SafeModeRecovery')
        logger.setLevel(log_level)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        return logger
    
    def _check_admin_rights(self) -> bool:
        """Check if the script is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            self.logger.error(f"Error checking admin rights: {e}")
            return False
    
    def _run_command(self, command: List[str], capture_output: bool = True) -> Dict:
        """Run a command and return the result."""
        try:
            self.logger.debug(f"Executing command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Command failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.warning(f"Error: {result.stderr.strip()}")
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout.strip() if result.stdout else '',
                'stderr': result.stderr.strip() if result.stderr else ''
            }
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_safe_mode(self) -> bool:
        """Check if the system is currently in Safe Mode."""
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\SafeBoot\Option"
            ) as key:
                safe_boot = winreg.QueryValueEx(key, 'OptionValue')[0]
                return safe_boot != 0
        except WindowsError:
            # If the key doesn't exist, we're not in Safe Mode
            return False
        except Exception as e:
            self.logger.error(f"Error checking Safe Mode status: {e}")
            return False
    
    def disable_safe_mode(self) -> bool:
        """Disable Safe Mode boot options."""
        if not self.is_admin:
            self.logger.error("Administrator privileges required to disable Safe Mode")
            return False
        
        self.logger.info("Disabling Safe Mode boot options...")
        
        # Disable Safe Mode boot using bcdedit
        commands = [
            [self.bcdedit_path, '/deletevalue', '{current}', 'safeboot'],
            [self.bcdedit_path, '/deletevalue', '{default}', 'safeboot'],
            [self.bcdedit_path, '/deletevalue', '{current}', 'safebootalternateshell'],
            [self.bcdedit_path, '/deletevalue', '{default}', 'safebootalternateshell']
        ]
        
        success = True
        for cmd in commands:
            result = self._run_command(cmd)
            if not result['success']:
                success = False
                self.logger.warning(f"Failed to disable Safe Mode option: {' '.join(cmd)}")
        
        if success:
            self.logger.info("Successfully disabled Safe Mode boot options")
        else:
            self.logger.warning("Some Safe Mode options might still be enabled")
        
        return success
    
    def repair_boot_configuration(self) -> bool:
        """Repair the boot configuration."""
        if not self.is_admin:
            self.logger.error("Administrator privileges required to repair boot configuration")
            return False
        
        self.logger.info("Repairing boot configuration...")
        
        # Run bootrec commands
        bootrec_commands = [
            ['bootrec', '/fixmbr'],
            ['bootrec', '/fixboot'],
            ['bootrec', '/scanos'],
            ['bootrec', '/rebuildbcd']
        ]
        
        success = True
        for cmd in bootrec_commands:
            result = self._run_command(cmd)
            if not result['success']:
                success = False
                self.logger.warning(f"Boot repair command failed: {' '.join(cmd)}")
        
        # Rebuild BCD
        bcd_commands = [
            [self.bcdedit_path, '/export', 'C:\\bcdbackup'],
            ['attrib', '-r', '-s', '-h', 'C:\\boot\\bcd'],
            ['ren', 'C:\\boot\\bcd', 'bcd.old'],
            [self.bcdedit_path, '/createstore', 'C:\\boot\\bcd'],
            [self.bcdedit_path, '/store', 'C:\\boot\\bcd', '/create', '{bootmgr}', '/d', 'Windows Boot Manager'],
            [self.bcdedit_path, '/store', 'C:\\boot\\bcd', '/set', '{bootmgr}', 'device', 'boot']
        ]
        
        for cmd in bcd_commands:
            result = self._run_command(cmd)
            if not result['success']:
                success = False
                self.logger.warning(f"BCD repair command failed: {' '.join(cmd)}")
        
        if success:
            self.logger.info("Successfully repaired boot configuration")
        else:
            self.logger.warning("Some boot repair operations might have failed")
        
        return success
    
    def complete_os_installation(self) -> bool:
        """Attempt to complete the OS installation process."""
        if not self.is_admin:
            self.logger.error("Administrator privileges required to complete OS installation")
            return False
        
        self.logger.info("Attempting to complete OS installation...")
        
        # Check for pending file renames (common after interrupted installs)
        pending_renames = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'winsxs', 'pending.xml')
        if os.path.exists(pending_renames):
            self.logger.info("Found pending file renames - attempting to process...")
            result = self._run_command(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager', 
                                     '/v', 'PendingFileRenameOperations', '/d', '', '/f'])
            if not result['success']:
                self.logger.warning("Failed to clear pending file renames")
        
        # Run Windows Update to complete any pending updates
        self.logger.info("Running Windows Update to complete installation...")
        update_result = self._run_command(['usoclient', 'StartScan'])
        if not update_result['success']:
            self.logger.warning("Failed to start Windows Update scan")
        
        # Reset Windows Update components
        self.logger.info("Resetting Windows Update components...")
        reset_commands = [
            ['net', 'stop', 'wuauserv'],
            ['net', 'stop', 'cryptSvc'],
            ['net', 'stop', 'bits'],
            ['net', 'stop', 'msiserver'],
            ['ren', 'C:\\Windows\\SoftwareDistribution', 'SoftwareDistribution.old'],
            ['ren', 'C:\\Windows\\System32\\catroot2', 'catroot2.old'],
            ['net', 'start', 'wuauserv'],
            ['net', 'start', 'cryptSvc'],
            ['net', 'start', 'bits'],
            ['net', 'start', 'msiserver']
        ]
        
        for cmd in reset_commands:
            self._run_command(cmd)
        
        self.logger.info("OS installation completion process finished")
        return True
    
    def create_recovery_point(self) -> bool:
        """Create a system restore point before making changes."""
        if not self.is_admin:
            self.logger.error("Administrator privileges required to create restore points")
            return False
        
        self.logger.info("Creating system restore point...")
        
        try:
            import ctypes
            from ctypes import wintypes
            
            # Define necessary constants and functions
            class GUID(ctypes.Structure):
                _fields_ = [
                    ('Data1', wintypes.DWORD),
                    ('Data2', wintypes.WORD),
                    ('Data3', wintypes.WORD),
                    ('Data4', wintypes.BYTE * 8)
                ]
            
            SRP_ACTION = wintypes.DWORD
            PSRP_ACTION = ctypes.POINTER(SRP_ACTION)
            
            # Initialize COM
            ctypes.windll.ole32.CoInitialize(0)
            
            # Create System Restore object
            sr = ctypes.windll.srclient.SRNewClientSid
            
            # Define restore point info
            class RESTOREPOINTINFO(ctypes.Structure):
                _fields_ = [
                    ('dwEventType', wintypes.DWORD),
                    ('dwRestorePtType', wintypes.DWORD),
                    ('llSequenceNumber', wintypes.INT64),
                    ('szDescription', wintypes.WCHAR * 256)
                ]
            
            class STATEMGRSTATUS(ctypes.Structure):
                _fields_ = [
                    ('nStatus', wintypes.DWORD),
                    ('llSequenceNumber', wintypes.INT64)
                ]
            
            # Set up restore point info
            rpi = RESTOREPOINTINFO()
            rpi.dwEventType = 100  # BEGIN_SYSTEM_CHANGE
            rpi.dwRestorePtType = 0  # APPLICATION_INSTALL
            rpi.llSequenceNumber = 0
            rpi.szDescription = "OPRYXX Safe Mode Recovery"
            
            smStatus = STATEMGRSTATUS()
            
            # Create the restore point
            result = ctypes.windll.srclient.SRSetRestorePointW(
                ctypes.byref(rpi),
                ctypes.byref(smStatus)
            )
            
            if result == 1:  # ERROR_SUCCESS
                self.logger.info("Successfully created system restore point")
                return True
            else:
                self.logger.error(f"Failed to create restore point. Error code: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating restore point: {e}")
            return False
    
    def recover_system(self) -> bool:
        """
        Perform complete system recovery from Safe Mode boot issues.
        
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        self.logger.info("Starting system recovery process...")
        
        # Create a restore point before making changes
        if not self.create_recovery_point():
            self.logger.warning("Failed to create restore point, continuing anyway...")
        
        # Check if we're in Safe Mode
        if not self.check_safe_mode():
            self.logger.info("System is not in Safe Mode. No recovery needed.")
            return True
        
        self.logger.info("System is in Safe Mode. Starting recovery...")
        
        # Disable Safe Mode boot
        if not self.disable_safe_mode():
            self.logger.error("Failed to disable Safe Mode boot options")
            return False
        
        # Repair boot configuration
        if not self.repair_boot_configuration():
            self.logger.error("Failed to repair boot configuration")
            return False
        
        # Complete OS installation if needed
        if not self.complete_os_installation():
            self.logger.warning("Failed to complete OS installation. Manual intervention may be required.")
        
        self.logger.info("Recovery process completed. Please restart your computer.")
        return True


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OPRYXX Safe Mode Recovery Tool')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set the logging level')
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    recovery = SafeModeRecovery(log_level=log_level)
    
    # Check for admin rights
    if not recovery.is_admin:
        print("This script requires administrator privileges. Please run as administrator.")
        return 1
    
    # Perform recovery
    success = recovery.recover_system()
    
    if success:
        print("\nRecovery completed successfully!")
        print("Please restart your computer to complete the process.")
        return 0
    else:
        print("\nRecovery failed. Please check the logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
