"""
UEFI Boot Repair Module
Handles UEFI-specific boot repair operations
"""

import os
import re
import subprocess
import logging
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DiskPartition:
    """Represents a disk partition"""
    number: int
    label: str
    fs: str
    size: str
    type: str
    info: str

class UEFIBootRepair:
    """Handles UEFI boot repair operations"""
    
    def __init__(self):
        self.uefi = self._check_uefi()
        self.efi_partition = None
        self.system_drive = os.environ.get('SystemDrive', 'C:')
        self.windows_dir = os.path.join(self.system_drive, 'Windows')
        self.mount_point = 'S:'  # Temporary mount point for EFI partition
        
    def _check_uefi(self) -> bool:
        """Check if system is booted in UEFI mode"""
        try:
            # Check if running on Windows
            if os.name == 'nt':
                import ctypes
                firmware_type = ctypes.c_uint()
                ctypes.windll.kernel32.GetFirmwareType(ctypes.byref(firmware_type))
                return firmware_type.value == 2  # 2 = FirmwareTypeUefi
            else:
                # For Linux/Unix systems
                return os.path.exists('/sys/firmware/efi')
        except Exception as e:
            logger.warning(f"Could not determine firmware type: {e}")
            return False
    
    def _run_command(self, cmd: List[str], **kwargs) -> Tuple[bool, str]:
        """Run a command and return (success, output)"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                **kwargs
            )
            if result.returncode != 0:
                logger.error(f"Command failed ({result.returncode}): {' '.join(cmd)}")
                logger.error(f"Stderr: {result.stderr}")
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False, str(e)
    
    def _find_efi_partition(self) -> Optional[str]:
        """Find the EFI system partition"""
        try:
            if os.name == 'nt':
                # On Windows, use diskpart to find EFI partition
                script = """
                list disk
                select disk 0
                list partition
                """
                success, output = self._run_command(
                    ['diskpart', '/s', '-'],
                    input=script
                )
                
                if success:
                    # Parse diskpart output to find EFI partition
                    for line in output.split('\n'):
                        if 'System' in line and 'EFI' in line.upper():
                            # Extract partition number
                            match = re.search(r'Partition\s+(\d+)', line)
                            if match:
                                return match.group(1)
            else:
                # On Linux, check /boot/efi or /efi
                for path in ['/boot/efi', '/efi']:
                    if os.path.ismount(path):
                        return path
                        
            logger.warning("Could not find EFI partition")
            return None
            
        except Exception as e:
            logger.error(f"Error finding EFI partition: {e}")
            return None
    
    def _mount_efi_partition(self) -> bool:
        """Mount the EFI partition"""
        if not self.uefi:
            return False
            
        if os.name == 'nt':
            # On Windows, assign drive letter to EFI partition
            partition = self._find_efi_partition()
            if not partition:
                return False
                
            script = f"""
            select disk 0
            select partition {partition}
            assign letter={self.mount_point[0]}
            """
            
            success, _ = self._run_command(
                ['diskpart', '/s', '-'],
                input=script
            )
            return success
        
        # On Linux, EFI is usually already mounted
        return os.path.ismount('/boot/efi') or os.path.ismount('/efi')
    
    def _unmount_efi_partition(self) -> bool:
        """Unmount the EFI partition"""
        if not self.uefi:
            return True
            
        if os.name == 'nt':
            # On Windows, remove drive letter
            script = f"""
            select volume {self.mount_point[0]}
            remove letter={self.mount_point[0]}
            """
            
            success, _ = self._run_command(
                ['diskpart', '/s', '-'],
                input=script
            )
            return success
            
        # On Linux, nothing to do as we don't mount it
        return True
    
    def repair_bootloader(self) -> bool:
        """Repair UEFI bootloader"""
        if not self.uefi:
            logger.info("Not a UEFI system, skipping UEFI boot repair")
            return False
            
        logger.info("Starting UEFI boot repair...")
        
        try:
            # Mount EFI partition
            if not self._mount_efi_partition():
                logger.error("Failed to mount EFI partition")
                return False
            
            # Recreate boot files
            logger.info("Recreating boot files...")
            success, output = self._run_command([
                'bcdboot',
                f'{self.windows_dir}',
                '/s', f'{self.mount_point}\\',
                '/f', 'UEFI',
                '/l', 'en-us'
            ])
            
            if not success:
                logger.error("Failed to recreate boot files")
                return False
            
            # Update NVRAM
            logger.info("Updating NVRAM...")
            success, output = self._run_command([
                'bootsect',
                '/nt60',
                f'{self.mount_point[0]}:',
                '/force',
                '/mbr'
            ])
            
            if not success:
                logger.error("Failed to update NVRAM")
                return False
                
            logger.info("UEFI boot repair completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"UEFI boot repair failed: {e}", exc_info=True)
            return False
            
        finally:
            # Always try to unmount the EFI partition
            self._unmount_efi_partition()
    
    def check_secure_boot(self) -> bool:
        """Check if Secure Boot is enabled"""
        if not self.uefi:
            return False
            
        try:
            if os.name == 'nt':
                # On Windows, check registry
                import winreg
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    'SYSTEM\\CurrentControlSet\\Control\\SecureBoot\\State'
                ) as key:
                    value = winreg.QueryValueEx(key, 'UEFISecureBootEnabled')[0]
                    return value == 1
            else:
                # On Linux, check sysfs
                secure_boot = Path('/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c')
                if secure_boot.exists():
                    with secure_boot.open('rb') as f:
                        # The value is a 5-byte array where the last byte is the status
                        return f.read()[-1] == 1
                return False
                
        except Exception as e:
            logger.warning(f"Could not check Secure Boot status: {e}")
            return False
    
    def get_boot_entries(self) -> List[Dict]:
        """Get current UEFI boot entries"""
        if not self.uefi:
            return []
            
        entries = []
        try:
            if os.name == 'nt':
                # On Windows, use bcdedit
                success, output = self._run_command(['bcdedit', '/enum', 'fwbootmgr'])
                if success:
                    # Parse bcdedit output
                    current_entry = {}
                    for line in output.split('\n'):
                        line = line.strip()
                        if line.startswith('identifier'):
                            if current_entry:
                                entries.append(current_entry)
                            current_entry = {'identifier': line.split()[-1]}
                        elif ':' in line:
                            key, value = line.split(':', 1)
                            current_entry[key.strip()] = value.strip()
                    if current_entry:
                        entries.append(current_entry)
            else:
                # On Linux, use efibootmgr
                success, output = self._run_command(['efibootmgr'])
                if success:
                    for line in output.split('\n'):
                        if line.startswith('Boot'):
                            parts = line.split()
                            if len(parts) >= 2:
                                entry = {
                                    'identifier': parts[0][4:8],  # Extract boot number
                                    'description': ' '.join(parts[1:]).strip('*')
                                }
                                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get boot entries: {e}")
            return []

# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    repair = UEFIBootRepair()
    print(f"UEFI Mode: {repair.uefi}")
    print(f"Secure Boot: {repair.check_secure_boot()}")
    print("Boot Entries:")
    for entry in repair.get_boot_entries():
        print(f"  - {entry}")
    
    if repair.uefi:
        print("\nAttempting boot repair...")
        if repair.repair_bootloader():
            print("Boot repair completed successfully")
        else:
            print("Boot repair failed")
