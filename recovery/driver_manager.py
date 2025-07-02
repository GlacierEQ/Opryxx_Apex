"""
Driver backup and restore functionality for OPRYXX_LOGS recovery system.
Handles driver extraction, backup, and restoration with cloud sync capabilities.
"""
import os
import shutil
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriverManager:
    """Manages driver backup and restore operations."""
    
    def __init__(self, backup_dir: str = "C:\\OPRYXX_LOGS\\driver_backup"):
        """Initialize with backup directory."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_dir / "drivers_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load driver metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupted metadata file, creating new one.")
        return {"backups": {}, "system_info": {}}
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def backup_drivers(self, backup_name: Optional[str] = None) -> str:
        """Backup all system drivers using DISM."""
        if not backup_name:
            backup_name = f"drivers_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"Backing up drivers to {backup_path}")
        
        try:
            # Use DISM to export all drivers
            cmd = [
                'dism', '/online',
                f'/export-driver=destination:{backup_path}',
                '/recurse'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Store backup metadata
            self.metadata['backups'][backup_name] = {
                'timestamp': datetime.now().isoformat(),
                'path': str(backup_path),
                'system_info': self._get_system_info()
            }
            self._save_metadata()
            
            logger.info(f"Successfully backed up drivers to {backup_path}")
            return str(backup_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to backup drivers: {e.stderr}")
            raise
    
    def restore_drivers(self, backup_name: str) -> bool:
        """Restore drivers from a specific backup."""
        if backup_name not in self.metadata['backups']:
            logger.error(f"Backup {backup_name} not found")
            return False
            
        backup_path = Path(self.metadata['backups'][backup_name]['path'])
        if not backup_path.exists():
            logger.error(f"Backup directory not found: {backup_path}")
            return False
            
        logger.info(f"Restoring drivers from {backup_path}")
        
        try:
            # Install each driver .inf file
            for inf_file in backup_path.glob('**/*.inf'):
                cmd = ['pnputil', '/add-driver', str(inf_file), '/install']
                subprocess.run(cmd, check=True)
                
            logger.info("Successfully restored drivers")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restore drivers: {e}")
            return False
    
    def _get_system_info(self) -> Dict:
        """Get system information for backup identification."""
        try:
            import platform
            import wmi
            
            c = wmi.WMI()
            system = c.Win32_ComputerSystem()[0]
            os_info = c.Win32_OperatingSystem()[0]
            
            return {
                'system_manufacturer': system.Manufacturer,
                'system_model': system.Model,
                'os_name': os_info.Caption,
                'os_version': os_info.Version,
                'architecture': platform.machine(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Could not gather detailed system info: {e}")
            return {"error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available driver backups."""
        return [
            {"name": name, **info}
            for name, info in self.metadata['backups'].items()
        ]
    
    def cleanup_old_backups(self, keep_last: int = 3):
        """Remove old backups, keeping only the specified number of most recent."""
        backups = sorted(
            self.metadata['backups'].items(),
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )
        
        for name, _ in backups[keep_last:]:
            backup_path = Path(self.metadata['backups'][name]['path'])
            if backup_path.exists():
                shutil.rmtree(backup_path)
            del self.metadata['backups'][name]
            
        self._save_metadata()
        logger.info(f"Cleaned up old backups, keeping {keep_last} most recent")

if __name__ == "__main__":
    # Example usage
    dm = DriverManager()
    print("Backing up drivers...")
    backup_path = dm.backup_drivers()
    print(f"Backup created at: {backup_path}")
    print("\nAvailable backups:")
    for backup in dm.list_backups():
        print(f"- {backup['name']} ({backup['timestamp']})")
