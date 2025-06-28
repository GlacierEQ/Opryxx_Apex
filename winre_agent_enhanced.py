"""
Enhanced WinRE Agent for OPRYXX

This module provides an enhanced Windows Recovery Environment agent with GANDALFS integration
for system recovery operations.
"""

import os
import sys
import json
import logging
import subprocess
import winreg
import ctypes
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Import GANDALFS integration
from gandalfs_integration import GANDALFSRecovery

class EnhancedWinREAgent:
    """Enhanced Windows Recovery Environment Agent with GANDALFS integration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the EnhancedWinREAgent.

        Args:
            config_path: Path to the configuration file
        """
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.gandalfs = GANDALFSRecovery(self.config.get('gandalfs', {}))
        self.recovery_media_path = self.config.get('recovery_media_path', 'X:\\Recovery')
        self.system_drive = self._detect_system_drive()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('WinREAgent')
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

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'gandalfs': {
                'gandalfs_path': 'C:\\Program Files\\GANDALFS',
                'recovery_image_path': 'E:\\RecoveryImages'
            },
            'recovery_media_path': 'X:\\Recovery',
            'backup_partitions': ['EFI', 'Windows', 'Recovery']
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")

        return default_config

    def _detect_system_drive(self) -> str:
        """Detect the system drive letter in WinRE."""
        try:
            # Check common system drive locations
            for drive in ['C:', 'D:', 'E:']:
                if os.path.exists(os.path.join(drive, 'Windows', 'System32')):
                    return drive
            return 'C:'  # Default fallback
        except Exception as e:
            self.logger.error(f"Failed to detect system drive: {e}")
            return 'C:'

    def is_in_winre(self) -> bool:
        """Check if currently running in Windows Recovery Environment."""
        try:
            # Check for WinRE-specific environment variables
            return os.environ.get('SystemRoot', '').lower().endswith('\\windows\\system32')
        except Exception as e:
            self.logger.error(f"Error checking WinRE status: {e}")
            return False

    def list_recovery_images(self) -> List[str]:
        """List available recovery images."""
        try:
            # Check both the recovery media and default GANDALFS locations
            recovery_paths = [
                self.recovery_media_path,
                os.path.join(self.system_drive, 'Recovery'),
                self.gandalfs.recovery_image_path
            ]

            images = []
            for path in recovery_paths:
                if os.path.exists(path):
                    for ext in ['.gandalfs', '.wim', '.esd']:
                        images.extend(list(Path(path).glob(f'*{ext}')))

            return [str(img) for img in images]

        except Exception as e:
            self.logger.error(f"Error listing recovery images: {e}")
            return []

    def create_recovery_point(self, name: str = None) -> bool:
        """Create a system recovery point using GANDALFS."""
        try:
            if not name:
                from datetime import datetime
                name = f"WinRE_Recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.logger.info(f"Creating recovery point: {name}")
            return self.gandalfs.create_recovery_image(name)

        except Exception as e:
            self.logger.error(f"Failed to create recovery point: {e}")
            return False

    def restore_system(self, image_path: str, target_disk: str = '0') -> bool:
        """Restore system from a GANDALFS recovery image."""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Recovery image not found: {image_path}")
                return False

            self.logger.info(f"Starting system restore from: {image_path}")
            return self.gandalfs.restore_from_image(image_path, target_disk)

        except Exception as e:
            self.logger.error(f"Failed to restore system: {e}")
            return False

    def repair_boot_configuration(self) -> bool:
        """Repair the boot configuration."""
        try:
            self.logger.info("Repairing boot configuration...")

            # Run bootrec commands
            commands = [
                ['bootrec', '/fixmbr'],
                ['bootrec', '/fixboot'],
                ['bootrec', '/scanos'],
                ['bootrec', '/rebuildbcd']
            ]

            success = True
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning(f"Command failed: {' '.join(cmd)} - {result.stderr}")
                    success = False

            return success

        except Exception as e:
            self.logger.error(f"Error repairing boot configuration: {e}")
            return False

    def run_repair_sequence(self) -> bool:
        """Run a complete repair sequence."""
        try:
            self.logger.info("Starting system repair sequence...")

            # 1. Repair boot configuration
            if not self.repair_boot_configuration():
                self.logger.warning("Boot repair completed with warnings")

            # 2. Check for and apply pending updates
            self._apply_pending_updates()

            # 3. Check system files
            self._check_system_files()

            self.logger.info("System repair sequence completed")
            return True

        except Exception as e:
            self.logger.error(f"Error during repair sequence: {e}")
            return False

    def _apply_pending_updates(self) -> bool:
        """Apply any pending Windows updates."""
        try:
            self.logger.info("Checking for pending updates...")
            result = subprocess.run(
                ['dism', '/image:C:\\', '/get-packages'],
                capture_output=True,
                text=True
            )

            if 'Pending online package install' in result.stdout:
                self.logger.info("Applying pending updates...")
                subprocess.run(['dism', '/image:C:\\', '/cleanup-image', '/revertpendingactions'])
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error applying pending updates: {e}")
            return False

    def _check_system_files(self) -> bool:
        """Check and repair system files."""
        try:
            self.logger.info("Checking system files...")
            result = subprocess.run(
                ['sfc', '/scannow', '/offbootdir=C:\\', '/offwindir=C:\\Windows'],
                capture_output=True,
                text=True
            )

            if 'found corrupt files' in result.stdout:
                self.logger.info("Corrupt system files found and repaired")
            else:
                self.logger.info("No corrupt system files found")

            return True

        except Exception as e:
            self.logger.error(f"Error checking system files: {e}")
            return False


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced WinRE Agent')
    parser.add_argument('--list', action='store_true', help='List available recovery images')
    parser.add_argument('--create', metavar='NAME', help='Create a new recovery point')
    parser.add_argument('--restore', metavar='IMAGE', help='Restore from a recovery image')
    parser.add_argument('--repair', action='store_true', help='Run system repair sequence')
    parser.add_argument('--config', help='Path to configuration file')

    args = parser.parse_args()

    agent = EnhancedWinREAgent(args.config)

    if not agent.is_in_winre():
        print("Warning: Not running in Windows Recovery Environment")

    if args.list:
        print("\nAvailable recovery images:")
        for img in agent.list_recovery_images():
            print(f"- {img}")
    elif args.create:
        if agent.create_recovery_point(args.create):
            print("Recovery point created successfully")
        else:
            print("Failed to create recovery point")
            sys.exit(1)
    elif args.restore:
        print(f"WARNING: This will restore your system from {args.restore}")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() == 'yes':
            if agent.restore_system(args.restore):
                print("System restore completed successfully")
            else:
                print("System restore failed")
                sys.exit(1)
    elif args.repair:
        if agent.run_repair_sequence():
            print("System repair completed successfully")
        else:
            print("System repair completed with errors")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
