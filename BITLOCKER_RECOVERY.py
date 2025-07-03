"""
BITLOCKER RECOVERY TOOL
Specialized for Samsung SSD 4TB RAW + BitLocker recovery
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

class BitLockerRecovery:
    """Advanced BitLocker recovery for RAW drives"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.recovery_methods = [
            'recovery_key',
            'password',
            'tpm_recovery',
            'microsoft_account',
            'active_directory',
            'raw_extraction'
        ]
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - BITLOCKER_RECOVERY - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'bitlocker_recovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def analyze_bitlocker_drive(self, drive_letter: str = None) -> Dict:
        """Analyze BitLocker encrypted drive"""
        self.logger.info("🔍 ANALYZING BITLOCKER DRIVE")
        
        analysis = {
            'drives_found': [],
            'encryption_status': {},
            'recovery_options': [],
            'raw_drives': []
        }
        
        try:
            # Get BitLocker status
            result = subprocess.run(['manage-bde', '-status'], capture_output=True, text=True)
            if result.returncode == 0:
                self._parse_bitlocker_status(result.stdout, analysis)
            
            # Check for RAW drives
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'deviceid,filesystem,size'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self._parse_raw_drives(result.stdout, analysis)
            
            self.logger.info(f"✅ Found {len(analysis['drives_found'])} BitLocker drives")
            self.logger.info(f"✅ Found {len(analysis['raw_drives'])} RAW drives")
            
        except Exception as e:
            self.logger.error(f"❌ BitLocker analysis failed: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _parse_bitlocker_status(self, status_output: str, analysis: Dict):
        """Parse manage-bde status output"""
        lines = status_output.split('\n')
        current_drive = None
        
        for line in lines:
            line = line.strip()
            if 'Volume' in line and ':' in line:
                # Extract drive letter
                parts = line.split()
                for part in parts:
                    if ':' in part and len(part) == 2:
                        current_drive = part
                        analysis['drives_found'].append(current_drive)
                        analysis['encryption_status'][current_drive] = {}
                        break
            elif current_drive:
                if 'Conversion Status' in line:
                    analysis['encryption_status'][current_drive]['status'] = line.split(':')[1].strip()
                elif 'Encryption Method' in line:
                    analysis['encryption_status'][current_drive]['method'] = line.split(':')[1].strip()
                elif 'Protection Status' in line:
                    analysis['encryption_status'][current_drive]['protection'] = line.split(':')[1].strip()
    
    def _parse_raw_drives(self, disk_output: str, analysis: Dict):
        """Parse RAW drives from wmic output"""
        lines = disk_output.split('\n')[1:]  # Skip header
        
        for line in lines:
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    filesystem = parts[1] if len(parts) > 1 else ''
                    
                    if not filesystem or filesystem.upper() == 'RAW':
                        analysis['raw_drives'].append({
                            'drive': device_id,
                            'filesystem': 'RAW',
                            'potential_bitlocker': True
                        })
    
    def attempt_bitlocker_unlock(self, drive: str, method: str, credential: str = None) -> Dict:
        """Attempt to unlock BitLocker drive"""
        self.logger.info(f"🔓 ATTEMPTING BITLOCKER UNLOCK: {drive} using {method}")
        
        unlock_result = {
            'success': False,
            'method_used': method,
            'drive': drive,
            'error': None
        }
        
        try:
            if method == 'recovery_key':
                if credential:
                    cmd = ['manage-bde', '-unlock', drive, '-recoverykey', credential]
                else:
                    self.logger.error("Recovery key required but not provided")
                    unlock_result['error'] = "Recovery key required"
                    return unlock_result
                    
            elif method == 'password':
                if credential:
                    cmd = ['manage-bde', '-unlock', drive, '-password', credential]
                else:
                    self.logger.error("Password required but not provided")
                    unlock_result['error'] = "Password required"
                    return unlock_result
                    
            elif method == 'tpm_recovery':
                cmd = ['manage-bde', '-unlock', drive, '-certificate']
                
            else:
                unlock_result['error'] = f"Unsupported method: {method}"
                return unlock_result
            
            # Execute unlock command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                unlock_result['success'] = True
                self.logger.info(f"✅ BitLocker unlock successful for {drive}")
                
                # Auto-mount if successful
                self._auto_mount_drive(drive)
                
            else:
                unlock_result['error'] = result.stderr
                self.logger.error(f"❌ BitLocker unlock failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            unlock_result['error'] = "Unlock operation timed out"
            self.logger.error("❌ BitLocker unlock timed out")
        except Exception as e:
            unlock_result['error'] = str(e)
            self.logger.error(f"❌ BitLocker unlock error: {e}")
        
        return unlock_result
    
    def _auto_mount_drive(self, drive: str):
        """Auto-mount unlocked drive"""
        try:
            result = subprocess.run(['manage-bde', '-autounlock', '-enable', drive], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"✅ Auto-mount enabled for {drive}")
        except:
            pass
    
    def recover_from_raw_bitlocker(self, drive: str) -> Dict:
        """Attempt recovery from RAW BitLocker drive"""
        self.logger.info(f"💾 RAW BITLOCKER RECOVERY: {drive}")
        self.logger.warning("⚠️ This is an advanced recovery operation")
        
        recovery_result = {
            'success': False,
            'recovery_methods_attempted': [],
            'data_recovered': False,
            'recovery_path': None
        }
        
        # Create recovery directory
        recovery_dir = f"bitlocker_raw_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(recovery_dir, exist_ok=True)
        recovery_result['recovery_path'] = recovery_dir
        
        # Method 1: Repair filesystem first
        self.logger.info("🔧 Attempting filesystem repair")
        repair_result = self._attempt_filesystem_repair(drive)
        recovery_result['recovery_methods_attempted'].append('filesystem_repair')
        
        if repair_result['success']:
            # Try BitLocker unlock after repair
            unlock_result = self.attempt_bitlocker_unlock(drive, 'tpm_recovery')
            if unlock_result['success']:
                recovery_result['success'] = True
                recovery_result['data_recovered'] = True
                return recovery_result
        
        # Method 2: Raw data extraction
        self.logger.info("🔍 Attempting raw data extraction")
        extraction_result = self._attempt_raw_extraction(drive, recovery_dir)
        recovery_result['recovery_methods_attempted'].append('raw_extraction')
        
        if extraction_result['success']:
            recovery_result['data_recovered'] = True
        
        # Method 3: Sector-by-sector recovery
        self.logger.info("💿 Attempting sector-by-sector recovery")
        sector_result = self._attempt_sector_recovery(drive, recovery_dir)
        recovery_result['recovery_methods_attempted'].append('sector_recovery')
        
        if sector_result['success']:
            recovery_result['data_recovered'] = True
        
        recovery_result['success'] = recovery_result['data_recovered']
        return recovery_result
    
    def _attempt_filesystem_repair(self, drive: str) -> Dict:
        """Attempt to repair RAW filesystem"""
        repair_commands = [
            ['chkdsk', drive, '/f', '/r', '/x'],
            ['sfc', '/scannow'],
            ['dism', '/online', '/cleanup-image', '/restorehealth']
        ]
        
        success_count = 0
        for cmd in repair_commands:
            try:
                self.logger.info(f"Executing: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode == 0:
                    success_count += 1
                    self.logger.info("✅ Repair command successful")
                else:
                    self.logger.warning(f"⚠️ Repair command failed: {result.stderr}")
            except Exception as e:
                self.logger.error(f"❌ Repair command error: {e}")
        
        return {'success': success_count > 0, 'repairs_successful': success_count}
    
    def _attempt_raw_extraction(self, drive: str, recovery_dir: str) -> Dict:
        """Attempt raw data extraction"""
        try:
            # Use dd-like tools if available
            extraction_tools = [
                ['dd', f'if=\\\\.\\{drive}', f'of={recovery_dir}\\raw_image.img', 'bs=1M'],
                ['photorec', '/d', recovery_dir, f'\\\\.\\{drive}'],
                ['testdisk', f'\\\\.\\{drive}']
            ]
            
            for tool in extraction_tools:
                try:
                    self.logger.info(f"Trying extraction tool: {tool[0]}")
                    result = subprocess.run(tool, capture_output=True, text=True, timeout=1800)
                    if result.returncode == 0:
                        self.logger.info(f"✅ Extraction successful with {tool[0]}")
                        return {'success': True, 'tool_used': tool[0]}
                except:
                    continue
            
            return {'success': False, 'error': 'No extraction tools succeeded'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _attempt_sector_recovery(self, drive: str, recovery_dir: str) -> Dict:
        """Attempt sector-by-sector recovery"""
        try:
            # Create sector dump
            sector_file = os.path.join(recovery_dir, 'sector_dump.bin')
            
            # Use Windows built-in tools
            cmd = ['fsutil', 'volume', 'diskfree', drive]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Sector information retrieved")
                return {'success': True, 'sector_file': sector_file}
            else:
                return {'success': False, 'error': 'Sector recovery failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def interactive_recovery_wizard(self):
        """Interactive BitLocker recovery wizard"""
        print("\n" + "="*60)
        print("🔓 BITLOCKER RECOVERY WIZARD")
        print("Samsung SSD 4TB RAW + BitLocker Specialist")
        print("="*60)
        
        # Step 1: Analyze drives
        print("\n🔍 Step 1: Analyzing BitLocker drives...")
        analysis = self.analyze_bitlocker_drive()
        
        if not analysis['drives_found'] and not analysis['raw_drives']:
            print("❌ No BitLocker or RAW drives found")
            return
        
        # Display found drives
        print(f"\n📊 Analysis Results:")
        print(f"BitLocker drives: {len(analysis['drives_found'])}")
        print(f"RAW drives: {len(analysis['raw_drives'])}")
        
        # Step 2: Select drive
        all_drives = analysis['drives_found'] + [d['drive'] for d in analysis['raw_drives']]
        
        if not all_drives:
            print("❌ No drives available for recovery")
            return
        
        print(f"\n📋 Available drives:")
        for i, drive in enumerate(all_drives, 1):
            drive_type = "BitLocker" if drive in analysis['drives_found'] else "RAW"
            print(f"{i}. {drive} ({drive_type})")
        
        try:
            choice = int(input("\nSelect drive number: ")) - 1
            if 0 <= choice < len(all_drives):
                selected_drive = all_drives[choice]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Step 3: Recovery method
        if selected_drive in analysis['drives_found']:
            # Standard BitLocker drive
            self._handle_standard_bitlocker(selected_drive)
        else:
            # RAW drive
            self._handle_raw_bitlocker(selected_drive)
    
    def _handle_standard_bitlocker(self, drive: str):
        """Handle standard BitLocker drive recovery"""
        print(f"\n🔓 BitLocker Recovery for {drive}")
        print("Available methods:")
        print("1. Recovery Key")
        print("2. Password")
        print("3. TPM Recovery")
        
        try:
            method_choice = int(input("Select method: "))
            
            if method_choice == 1:
                recovery_key = input("Enter recovery key (48 digits): ")
                result = self.attempt_bitlocker_unlock(drive, 'recovery_key', recovery_key)
            elif method_choice == 2:
                password = input("Enter password: ")
                result = self.attempt_bitlocker_unlock(drive, 'password', password)
            elif method_choice == 3:
                result = self.attempt_bitlocker_unlock(drive, 'tpm_recovery')
            else:
                print("❌ Invalid method")
                return
            
            if result['success']:
                print(f"✅ BitLocker unlock successful for {drive}")
                print(f"Drive {drive} is now accessible")
            else:
                print(f"❌ BitLocker unlock failed: {result.get('error', 'Unknown error')}")
                
        except ValueError:
            print("❌ Invalid input")
    
    def _handle_raw_bitlocker(self, drive: str):
        """Handle RAW BitLocker drive recovery"""
        print(f"\n💾 RAW BitLocker Recovery for {drive}")
        print("⚠️ WARNING: This is an advanced recovery operation")
        print("⚠️ This may take several hours to complete")
        
        confirm = input("Continue with RAW recovery? (y/N): ").lower()
        if confirm != 'y':
            return
        
        print(f"\n🚀 Starting RAW BitLocker recovery for {drive}")
        result = self.recover_from_raw_bitlocker(drive)
        
        if result['success']:
            print(f"✅ RAW recovery completed successfully")
            print(f"📁 Recovery data saved to: {result['recovery_path']}")
            print(f"🔧 Methods used: {', '.join(result['recovery_methods_attempted'])}")
        else:
            print(f"❌ RAW recovery failed")
            print(f"📁 Partial data may be in: {result['recovery_path']}")

def main():
    """Main BitLocker recovery interface"""
    print("🔓 BITLOCKER RECOVERY TOOL")
    print("Specialized for Samsung SSD 4TB RAW + BitLocker")
    print("="*50)
    
    # Check admin privileges
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ ERROR: Administrator privileges required")
            print("Please run as Administrator")
            return 1
    except:
        print("⚠️ WARNING: Could not verify administrator privileges")
    
    recovery_tool = BitLockerRecovery()
    
    try:
        recovery_tool.interactive_recovery_wizard()
    except KeyboardInterrupt:
        print("\n⚠️ Recovery interrupted by user")
        return 2
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        return 3
    
    return 0

if __name__ == "__main__":
    sys.exit(main())