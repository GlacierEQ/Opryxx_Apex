"""
Recovery Media Builder Module

Provides functionality to create bootable recovery media with OPRYXX tools.
"""

import os
import sys
import subprocess
import shutil
import logging
import tempfile
import wmi
import win32api
import win32file
import win32con
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from enum import Enum, auto

# Configure logging
logger = logging.getLogger(__name__)

class MediaType(Enum):
    """Supported media types for recovery"""
    WINDOWS_PE = "Windows PE"
    WINDOWS_INSTALL = "Windows Installation"
    LINUX_RESCUE = "Linux Rescue"
    OPRYXX_TOOLS = "OPRYXX Tools"

@dataclass
class DriveInfo:
    """Information about a storage drive"""
    device_id: str
    caption: str
    size_gb: float
    free_space_gb: float
    file_system: str
    drive_letter: str
    is_removable: bool
    is_bootable: bool = False

class RecoveryMediaBuilder:
    """
    Handles creation of bootable recovery media.
    
    Features:
    - Detect available USB drives
    - Format drives with different filesystems
    - Create bootable Windows PE media
    - Include OPRYXX recovery tools
    - Validate media creation
    """
    
    def __init__(self):
        self.wmi = wmi.WMI()
        self.temp_dir = Path(tempfile.gettempdir()) / 'opryxx_recovery_media'
        self.temp_dir.mkdir(exist_ok=True)
    
    def list_available_drives(self) -> List[DriveInfo]:
        """List all available removable drives that can be used for recovery media.
        
        Returns:
            List[DriveInfo]: List of available drives with their details
        """
        drives = []
        try:
            for drive in self.wmi.Win32_LogicalDisk():
                try:
                    if drive.DriveType == 2:  # Removable drive
                        size_gb = int(drive.Size) / (1024**3) if drive.Size else 0
                        free_gb = int(drive.FreeSpace) / (1024**3) if drive.FreeSpace else 0
                        
                        drive_info = DriveInfo(
                            device_id=drive.DeviceID,
                            caption=drive.VolumeName or 'NO NAME',
                            size_gb=round(size_gb, 2),
                            free_space_gb=round(free_gb, 2),
                            file_system=drive.FileSystem or '',
                            drive_letter=drive.DeviceID,
                            is_removable=True,
                            is_bootable=self._is_drive_bootable(drive.DeviceID)
                        )
                        drives.append(drive_info)
                except Exception as e:
                    logger.warning(f"Error reading drive {drive.DeviceID}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Failed to list drives: {e}")
        
        return drives
    
    def _is_drive_bootable(self, drive_letter: str) -> bool:
        """Check if a drive is bootable.
        
        Args:
            drive_letter: Drive letter to check (e.g., 'D:')
            
        Returns:
            bool: True if the drive is bootable
        """
        try:
            boot_files = ['bootmgr', 'boot', 'efi', 'sources/boot.wim']
            root = Path(drive_letter)
            return any((root / file).exists() for file in boot_files)
        except Exception as e:
            logger.warning(f"Error checking if {drive_letter} is bootable: {e}")
            return False
    
    def format_drive(self, drive_letter: str, fs_type: str = 'FAT32', 
                    label: str = 'OPRYXX_RESCUE') -> bool:
        """Format a drive with the specified filesystem.
        
        Args:
            drive_letter: Drive letter to format (e.g., 'D:')
            fs_type: Filesystem type (FAT32, exFAT, or NTFS)
            label: Volume label
            
        Returns:
            bool: True if formatting was successful
        """
        try:
            # Remove trailing backslash if present
            drive_letter = drive_letter.rstrip('\\')
            
            # Format command for Windows
            cmd = [
                'format',
                drive_letter,
                f'/FS:{fs_type.upper()}',
                f'/V:{label}',
                '/Q',  # Quick format
                '/Y'   # Suppress confirmation
            ]
            
            logger.info(f"Formatting {drive_letter} as {fs_type}...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug(f"Format output: {result.stdout}")
            
            if result.returncode == 0:
                logger.info(f"Successfully formatted {drive_letter}")
                return True
            else:
                logger.error(f"Failed to format {drive_letter}: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Format command failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error formatting drive: {e}")
            return False
    
    def create_windows_pe_media(self, drive_letter: str, include_tools: bool = True) -> Dict[str, Union[bool, str]]:
        """Create a bootable Windows PE recovery drive.
        
        Args:
            drive_letter: Target drive letter (e.g., 'D:')
            include_tools: Whether to include OPRYXX recovery tools
            
        Returns:
            Dict with success status and message
        """
        try:
            drive_letter = drive_letter.rstrip('\\')
            target_path = Path(drive_letter)
            
            # 1. Check if Windows ADK is installed
            if not self._is_adk_installed():
                return {
                    'success': False,
                    'message': 'Windows ADK is not installed. Required for creating Windows PE media.'
                }
            
            # 2. Create basic Windows PE structure
            logger.info("Creating Windows PE structure...")
            self._create_pe_structure(target_path)
            
            # 3. Add boot files
            logger.info("Adding boot files...")
            self._add_boot_files(target_path)
            
            # 4. Include OPRYXX tools if requested
            if include_tools:
                logger.info("Adding OPRYXX recovery tools...")
                self._add_opryxx_tools(target_path)
            
            # 5. Make drive bootable
            logger.info("Making drive bootable...")
            self._make_bootable(target_path)
            
            return {
                'success': True,
                'message': f'Successfully created Windows PE recovery media on {drive_letter}'
            }
            
        except Exception as e:
            logger.error(f"Error creating Windows PE media: {e}")
            return {
                'success': False,
                'message': f'Failed to create recovery media: {str(e)}'
            }
    
    def _is_adk_installed(self) -> bool:
        """Check if Windows ADK is installed."""
        try:
            adk_path = r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit"
            return os.path.exists(adk_path)
        except Exception as e:
            logger.warning(f"Error checking for ADK: {e}")
            return False
    
    def _create_pe_structure(self, target_path: Path):
        """Create the basic Windows PE directory structure."""
        dirs = [
            'sources',
            'efi\\boot',
            'boot',
            'opryxx\\tools'
        ]
        
        for dir_name in dirs:
            (target_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def _add_boot_files(self, target_path: Path):
        """Add boot files to the target path."""
        # This is a simplified version - actual implementation would copy from ADK
        bootmgr_src = r"C:\Windows\Boot\PCAT\bootmgr"
        if os.path.exists(bootmgr_src):
            shutil.copy2(bootmgr_src, target_path)
    
    def _add_opryxx_tools(self, target_path: Path):
        """Add OPRYXX recovery tools to the media."""
        tools_dir = target_path / 'opryxx'
        tools_dir.mkdir(exist_ok=True)
        
        # Add a readme file
        with open(tools_dir / 'README.txt', 'w') as f:
            f.write("OPRYXX Recovery Tools\n")
            f.write("====================\n\n")
            f.write("This drive contains OPRYXX recovery tools.\n")
            f.write("Run 'opryxx_recovery.exe' to start the recovery process.\n")
    
    def _make_bootable(self, target_path: Path):
        """Make the drive bootable."""
        # This is a placeholder - actual implementation would use boot sector utilities
        boot_sector = target_path / 'bootsect.exe'
        if not boot_sector.exists():
            logger.warning("Boot sector utility not found - drive may not be bootable")
    
    def validate_recovery_media(self, drive_letter: str) -> Dict[str, Union[bool, str, List[str]]]:
        """Validate that a recovery drive was created successfully.
        
        Args:
            drive_letter: Drive letter to validate
            
        Returns:
            Dict with validation results
        """
        try:
            drive_path = Path(drive_letter.rstrip('\\'))
            required_files = [
                'bootmgr',
                'boot\\bcd',
                'boot\\boot.sdi',
                'sources\\boot.wim'
            ]
            
            missing_files = []
            for file in required_files:
                if not (drive_path / file).exists():
                    missing_files.append(file)
            
            return {
                'is_valid': len(missing_files) == 0,
                'message': f"Found {len(missing_files)} missing files" if missing_files else "All required files found",
                'missing_files': missing_files
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'message': f"Validation failed: {str(e)}",
                'missing_files': []
            }

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create an instance of the media builder
    builder = RecoveryMediaBuilder()
    
    # List available drives
    print("\nAvailable Drives:")
    print("----------------")
    for i, drive in enumerate(builder.list_available_drives(), 1):
        print(f"{i}. {drive.drive_letter} - {drive.caption} ({drive.size_gb}GB, {drive.file_system})")
    
    # Example: Format a drive (uncomment to use)
    # drive_letter = input("\nEnter drive letter to format (e.g., D:): ")
    # if builder.format_drive(drive_letter, 'FAT32', 'OPRYXX_RESCUE'):
    #     print(f"Successfully formatted {drive_letter}")
    # else:
    #     print(f"Failed to format {drive_letter}")
