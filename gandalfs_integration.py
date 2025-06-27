"""
GANDALFS Integration for OPRYXX

This module provides integration with the GANDALFS recovery system.
"""

import os
import logging
import subprocess
from typing import Dict, Optional, List
from pathlib import Path

class GANDALFSRecovery:
    """
    GANDALFS Recovery Integration
    
    Handles integration with the GANDALFS recovery system for OS recovery operations.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the GANDALFS recovery integration.
        
        Args:
            config: Configuration dictionary with GANDALFS settings
        """
        self.config = config or {}
        self.logger = self._setup_logging()
        self.gandalfs_path = self.config.get('gandalfs_path', 'C:\\Program Files\\GANDALFS')
        self.recovery_image_path = self.config.get('recovery_image_path', 'E:\\RecoveryImages')
        
        # Ensure required directories exist
        os.makedirs(self.recovery_image_path, exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the GANDALFS integration."""
        logger = logging.getLogger('GANDALFS')
        logger.setLevel(logging.DEBUG)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        return logger
    
    def create_recovery_image(self, image_name: str, include_system_state: bool = True) -> bool:
        """
        Create a system recovery image using GANDALFS.
        
        Args:
            image_name: Name for the recovery image
            include_system_state: Whether to include system state in the backup
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Creating GANDALFS recovery image: {image_name}")
            
            # Build the GANDALFS command
            cmd = [
                os.path.join(self.gandalfs_path, 'gandalfs.exe'),
                'create',
                '--image', os.path.join(self.recovery_image_path, f"{image_name}.gandalfs"),
                '--compression', 'high',
                '--verify'
            ]
            
            if include_system_state:
                cmd.append('--system-state')
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.debug(f"GANDALFS output: {result.stdout}")
            
            if result.returncode == 0:
                self.logger.info("Successfully created GANDALFS recovery image")
                return True
            else:
                self.logger.error(f"Failed to create recovery image: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"GANDALFS command failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating recovery image: {e}")
            return False
    
    def restore_from_image(self, image_path: str, target_disk: str = '0') -> bool:
        """
        Restore system from a GANDALFS recovery image.
        
        Args:
            image_path: Path to the GANDALFS recovery image
            target_disk: Target disk number for restoration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Recovery image not found: {image_path}")
                return False
                
            self.logger.info(f"Restoring from GANDALFS image: {image_path}")
            
            # Build the GANDALFS restore command
            cmd = [
                os.path.join(self.gandalfs_path, 'gandalfs.exe'),
                'restore',
                '--image', image_path,
                '--target-disk', target_disk,
                '--confirm'
            ]
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.debug(f"GANDALFS restore output: {result.stdout}")
            
            if result.returncode == 0:
                self.logger.info("Successfully restored from GANDALFS image")
                return True
            else:
                self.logger.error(f"Failed to restore from image: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"GANDALFS restore command failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during restore: {e}")
            return False
    
    def list_recovery_images(self) -> List[str]:
        """
        List available recovery images in the recovery image directory.
        
        Returns:
            List of paths to available recovery images
        """
        try:
            images = []
            for file in Path(self.recovery_image_path).glob('*.gandalfs'):
                images.append(str(file.absolute()))
            return images
        except Exception as e:
            self.logger.error(f"Error listing recovery images: {e}")
            return []
    
    def get_recovery_image_info(self, image_path: str) -> Optional[Dict]:
        """
        Get information about a specific recovery image.
        
        Args:
            image_path: Path to the GANDALFS recovery image
            
        Returns:
            Dictionary with image information or None if failed
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Image not found: {image_path}")
                return None
                
            # Build the GANDALFS info command
            cmd = [
                os.path.join(self.gandalfs_path, 'gandalfs.exe'),
                'info',
                '--image', image_path
            ]
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output (simplified - adjust based on actual GANDALFS output format)
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get image info: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting image info: {e}")
            return None
