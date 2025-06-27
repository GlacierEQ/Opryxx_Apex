"""
Immediate Safe Mode Exit Tool for OPRYXX

Critical tool for immediate Safe Mode exit during OS installation failures.
Executes the priority command: bcdedit /deletevalue {current} safeboot
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from typing import Dict, Optional

class ImmediateSafeModeExit:
    """
    Immediate Safe Mode exit handler
    Executes critical Safe Mode exit command with comprehensive logging
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.execution_log = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup immediate logging"""
        logger = logging.getLogger('ImmediateSafeModeExit')
        logger.setLevel(logging.DEBUG)
        
        # Console handler with immediate output
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - CRITICAL - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        return logger
    
    def execute_critical_command(self) -> Dict:
        """Execute the critical Safe Mode exit command"""
        self.logger.info("EXECUTING CRITICAL SAFE MODE EXIT COMMAND")
        self.logger.info("Command: bcdedit /deletevalue {current} safeboot")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'command': 'bcdedit /deletevalue {current} safeboot',
            'executed': False,
            'success': False,
            'output': '',
            'error': '',
            'next_action': 'unknown'
        }
        
        try:
            # Execute the critical command
            process = subprocess.run(
                ['bcdedit', '/deletevalue', '{current}', 'safeboot'],
                capture_output=True,
                text=True,
                check=False
            )
            
            result['executed'] = True
            result['return_code'] = process.returncode
            result['output'] = process.stdout.strip()
            result['error'] = process.stderr.strip()
            
            if process.returncode == 0:
                result['success'] = True
                result['next_action'] = 'reboot_required'
                self.logger.info("SUCCESS: Safe Mode boot flag cleared")
                self.logger.info("NEXT ACTION: System reboot required")
            else:
                result['success'] = False
                result['next_action'] = 'alternative_recovery'
                self.logger.error(f"FAILED: Return code {process.returncode}")
                if result['error']:
                    self.logger.error(f"Error: {result['error']}")
            
            # Log execution
            self.execution_log.append(result)
            
            return result
            
        except FileNotFoundError:
            result['error'] = 'bcdedit command not found'
            result['next_action'] = 'system_recovery_required'
            self.logger.error("CRITICAL: bcdedit command not found")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            result['next_action'] = 'manual_intervention'
            self.logger.error(f"CRITICAL ERROR: {e}")
            return result
    
    def verify_safe_mode_status(self) -> Dict:
        """Verify current Safe Mode status"""
        self.logger.info("Verifying Safe Mode status...")
        
        status = {
            'in_safe_mode': False,
            'safe_mode_type': None,
            'boot_flags_present': False,
            'verification_method': []
        }
        
        # Check environment variable
        safeboot_option = os.environ.get('SAFEBOOT_OPTION')
        if safeboot_option:
            status['in_safe_mode'] = True
            status['safe_mode_type'] = safeboot_option
            status['verification_method'].append('environment_variable')
            self.logger.info(f"Safe Mode detected via environment: {safeboot_option}")
        
        # Check boot configuration
        try:
            result = subprocess.run(['bcdedit', '/enum'], capture_output=True, text=True)
            if result.returncode == 0:
                if 'safeboot' in result.stdout.lower():
                    status['boot_flags_present'] = True
                    status['verification_method'].append('bcdedit_enum')
                    self.logger.info("Safe Mode boot flags detected in boot configuration")
        except:
            pass
        
        return status
    
    def prepare_reboot_instructions(self) -> Dict:
        """Prepare reboot instructions after flag clearing"""
        instructions = {
            'immediate_actions': [
                "1. REBOOT THE SYSTEM IMMEDIATELY",
                "2. Monitor boot process for normal Windows startup",
                "3. If Safe Mode persists, proceed to alternative recovery"
            ],
            'verification_steps': [
                "1. Check if Windows boots normally (not Safe Mode)",
                "2. Verify OS installation can continue",
                "3. Complete any pending installation steps"
            ],
            'fallback_plan': [
                "1. If Safe Mode persists after reboot:",
                "2. Boot from Windows installation media",
                "3. Access Command Prompt from recovery options",
                "4. Run: bcdedit /deletevalue {default} safeboot",
                "5. Run: bootrec /rebuildbcd",
                "6. Restart and attempt normal boot"
            ]
        }
        
        return instructions
    
    def execute_immediate_recovery(self) -> bool:
        """Execute complete immediate recovery sequence"""
        print("OPRYXX IMMEDIATE SAFE MODE EXIT")
        print("=" * 50)
        print("CRITICAL RECOVERY OPERATION IN PROGRESS")
        print()
        
        # Step 1: Verify Safe Mode status
        print("Step 1: Verifying Safe Mode status...")
        status = self.verify_safe_mode_status()
        
        if status['in_safe_mode'] or status['boot_flags_present']:
            print("✓ Safe Mode detected - proceeding with exit procedure")
        else:
            print("! Safe Mode not detected - executing preventive flag clearing")
        
        print()
        
        # Step 2: Execute critical command
        print("Step 2: Executing critical Safe Mode exit command...")
        result = self.execute_critical_command()
        
        print(f"Command executed: {result['executed']}")
        print(f"Success: {result['success']}")
        print(f"Next action: {result['next_action']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        
        print()
        
        # Step 3: Provide instructions
        if result['success']:
            print("Step 3: Safe Mode exit successful - REBOOT REQUIRED")
            instructions = self.prepare_reboot_instructions()
            
            print("\nIMMEDIATE ACTIONS:")
            for action in instructions['immediate_actions']:
                print(f"  {action}")
            
            print("\nVERIFICATION STEPS:")
            for step in instructions['verification_steps']:
                print(f"  {step}")
            
            print("\nFALLBACK PLAN (if Safe Mode persists):")
            for step in instructions['fallback_plan']:
                print(f"  {step}")
            
            return True
        else:
            print("Step 3: Safe Mode exit failed - Alternative recovery required")
            print("\nALTERNATIVE RECOVERY STEPS:")
            print("  1. Boot from Windows installation USB/DVD")
            print("  2. Select 'Repair your computer'")
            print("  3. Choose 'Command Prompt'")
            print("  4. Run: bcdedit /deletevalue {current} safeboot")
            print("  5. Run: bcdedit /deletevalue {default} safeboot")
            print("  6. Run: bootrec /fixboot")
            print("  7. Run: bootrec /rebuildbcd")
            print("  8. Restart computer")
            
            return False
    
    def get_execution_summary(self) -> Dict:
        """Get summary of execution attempts"""
        return {
            'total_attempts': len(self.execution_log),
            'last_attempt': self.execution_log[-1] if self.execution_log else None,
            'overall_success': any(log['success'] for log in self.execution_log),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main execution function"""
    # Check for admin privileges
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("ERROR: Administrator privileges required")
            print("Please run this script as Administrator")
            return 1
    except:
        print("WARNING: Could not verify administrator privileges")
    
    # Execute immediate recovery
    recovery = ImmediateSafeModeExit()
    success = recovery.execute_immediate_recovery()
    
    # Save execution log
    try:
        import json
        log_file = f"safe_mode_exit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(recovery.get_execution_summary(), f, indent=2)
        print(f"\nExecution log saved to: {log_file}")
    except:
        pass
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())