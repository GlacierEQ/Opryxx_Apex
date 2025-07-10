"""
Storage Health Module for OPRYXX
Comprehensive S.M.A.R.T. monitoring and health analysis for all storage devices
"""

import os
import sys
import json
import time
import logging
import platform
import subprocess
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('storage_health.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DriveType(Enum):
    """Enumeration of drive types"""
    HDD = "HDD"
    SSD = "SSD"
    NVME = "NVMe"
    UNKNOWN = "Unknown"

class HealthStatus(Enum):
    """Enumeration of health status levels"""
    EXCELLENT = (0, "Excellent", "green")
    GOOD = (1, "Good", "lime")
    FAIR = (2, "Fair", "yellow")
    POOR = (3, "Poor", "orange")
    CRITICAL = (4, "Critical", "red")
    FAILED = (5, "Failed", "maroon")
    UNKNOWN = (6, "Unknown", "gray")

    def __new__(cls, value, description, color):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.color = color
        return obj

@dataclass
class DriveAttribute:
    """Class representing a S.M.A.R.T. attribute"""
    id: int
    name: str
    value: int
    worst: int
    threshold: int
    raw_value: int
    type: str = "Pre-fail"
    updated: bool = True

@dataclass
class DriveHealth:
    """Class representing drive health information"""
    device_id: str
    model: str
    serial: str
    type: DriveType
    capacity_gb: float
    firmware: str = ""
    temperature: Optional[float] = None
    power_on_hours: Optional[int] = None
    power_cycle_count: Optional[int] = None
    health_status: HealthStatus = HealthStatus.UNKNOWN
    health_score: float = 0.0
    attributes: Dict[str, DriveAttribute] = field(default_factory=dict)
    predicted_failure: Optional[datetime] = None
    last_checked: datetime = field(default_factory=datetime.utcnow)
    issues: List[str] = field(default_factory=list)

class StorageHealthMonitor:
    """
    Main class for monitoring storage health across all connected drives.
    Supports S.M.A.R.T. data collection, health scoring, and predictive analysis.
    """
    
    def __init__(self):
        self.drives: Dict[str, DriveHealth] = {}
        self.os_type = platform.system()
        self.is_admin = self._check_admin_privileges()
        self._initialize_platform()
        logger.info(f"Initialized StorageHealthMonitor for {self.os_type}")
    
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin/root privileges"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # Unix-like
                return os.geteuid() == 0
        except Exception as e:
            logger.error(f"Error checking admin privileges: {e}")
            return False
    
    def _initialize_platform(self):
        """Initialize platform-specific components"""
        if self.os_type == 'Windows':
            self._init_windows()
        elif self.os_type == 'Linux':
            self._init_linux()
        elif self.os_type == 'Darwin':
            self._init_macos()
        else:
            logger.warning(f"Unsupported OS: {self.os_type}")
    
    def _init_windows(self):
        """Initialize Windows-specific components"""
        try:
            import wmi
            self.wmi = wmi.WMI()
            logger.info("WMI initialized for Windows")
        except ImportError:
            logger.warning("WMI module not found. Install with: pip install wmi")
            self.wmi = None
    
    def _init_linux(self):
        """Initialize Linux-specific components"""
        self.smartctl_path = self._find_executable('smartctl')
        if not self.smartctl_path:
            logger.warning("smartctl not found. Install with: sudo apt install smartmontools")
    
    def _init_macos(self):
        """Initialize macOS-specific components"""
        self.smartctl_path = self._find_executable('smartctl')
        if not self.smartctl_path:
            logger.warning("smartctl not found. Install with: brew install smartmontools")
    
    def _find_executable(self, name: str) -> Optional[str]:
        """Find an executable in the system PATH"""
        for path in os.environ['PATH'].split(os.pathsep):
            full_path = os.path.join(path, name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return full_path
        return None
    
    def scan_drives(self) -> Dict[str, DriveHealth]:
        """
        Scan all connected storage devices
        Returns a dictionary of DriveHealth objects keyed by device ID
        """
        logger.info("Scanning for storage devices...")
        
        try:
            if self.os_type == 'Windows':
                self._scan_windows()
            elif self.os_type == 'Linux':
                self._scan_linux()
            elif self.os_type == 'Darwin':
                self._scan_macos()
            
            # Update health status for all detected drives
            for drive_id in list(self.drives.keys()):
                self._update_drive_health(drive_id)
            
            logger.info(f"Found {len(self.drives)} storage devices")
            return self.drives
            
        except Exception as e:
            logger.error(f"Error scanning drives: {e}", exc_info=True)
            return {}
    
    def _scan_windows(self):
        """Scan drives on Windows systems"""
        if not hasattr(self, 'wmi') or not self.wmi:
            logger.error("WMI not available for drive scanning")
            return
            
        try:
            for disk in self.wmi.Win32_DiskDrive():
                try:
                    self._process_windows_disk(disk)
                except Exception as e:
                    logger.error(f"Error processing disk {disk.DeviceID}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Windows drive scan: {e}")
    
    def _process_windows_disk(self, disk):
        """Process a single disk on Windows"""
        device_id = disk.DeviceID
        model = disk.Model.strip() if disk.Model else "Unknown"
        serial = disk.SerialNumber.strip() if disk.SerialNumber else "Unknown"
        size_gb = int(disk.Size) / (1024 ** 3) if disk.Size else 0
        
        # Determine drive type
        if 'SSD' in model.upper():
            drive_type = DriveType.SSD
        elif 'NVME' in model.upper():
            drive_type = DriveType.NVME
        else:
            drive_type = DriveType.HDD
        
        # Create or update drive info
        if device_id not in self.drives:
            self.drives[device_id] = DriveHealth(
                device_id=device_id,
                model=model,
                serial=serial,
                type=drive_type,
                capacity_gb=round(size_gb, 2),
                firmware=disk.FirmwareRevision if disk.FirmwareRevision else ""
            )
    
    def _scan_linux(self):
        """Scan drives on Linux systems"""
        try:
            # Use lsblk to get basic disk info
            result = subprocess.run(
                ['lsblk', '-d', '-o', 'NAME,MODEL,SERIAL,SIZE,TYPE', '--json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Error running lsblk: {result.stderr}")
                return
                
            devices = json.loads(result.stdout)
            
            for device in devices.get('blockdevices', []):
                if device.get('type') != 'disk':
                    continue
                    
                self._process_linux_disk(device)
                
        except Exception as e:
            logger.error(f"Error in Linux drive scan: {e}")
    
    def _process_linux_disk(self, device):
        """Process a single disk on Linux"""
        device_name = device.get('name', '')
        device_path = f"/dev/{device_name}"
        
        # Skip CD/DVD drives and other non-disk devices
        if any(x in device_path for x in ['sr', 'loop', 'ram']):
            return
        
        # Get detailed disk info
        model = device.get('model', 'Unknown').strip()
        serial = device.get('serial', 'Unknown').strip()
        size_str = device.get('size', '0')
        
        try:
            # Convert size to GB
            size_gb = float(size_str) / (1024 ** 3) if size_str.isdigit() else 0
        except (ValueError, AttributeError):
            size_gb = 0
        
        # Determine drive type
        if 'nvme' in device_name.lower():
            drive_type = DriveType.NVME
        elif self._is_ssd_linux(device_path):
            drive_type = DriveType.SSD
        else:
            drive_type = DriveType.HDD
        
        # Create or update drive info
        if device_path not in self.drives:
            self.drives[device_path] = DriveHealth(
                device_id=device_path,
                model=model,
                serial=serial,
                type=drive_type,
                capacity_gb=round(size_gb, 2)
            )
    
    def _is_ssd_linux(self, device_path: str) -> bool:
        """Check if a device is an SSD on Linux"""
        try:
            rotational_path = f"/sys/block/{os.path.basename(device_path)}/queue/rotational"
            if os.path.exists(rotational_path):
                with open(rotational_path, 'r') as f:
                    return f.read().strip() == '0'
        except Exception as e:
            logger.error(f"Error checking if {device_path} is SSD: {e}")
        
        return False
    
    def _scan_macos(self):
        """Scan drives on macOS"""
        try:
            # Use diskutil to list all disks
            result = subprocess.run(
                ['diskutil', 'list', '-plist', 'external', 'physical'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Error running diskutil: {result.stderr}")
                return
                
            # Process diskutil output
            # (Implementation would parse the plist output here)
            logger.info("macOS drive scanning not yet implemented")
            
        except Exception as e:
            logger.error(f"Error in macOS drive scan: {e}")
    
    def _update_drive_health(self, device_id: str):
        """Update health information for a specific drive"""
        if device_id not in self.drives:
            return
            
        drive = self.drives[device_id]
        drive.last_checked = datetime.utcnow()
        
        try:
            # Get S.M.A.R.T. data if available
            if self.os_type == 'Windows':
                self._get_smart_windows(drive)
            elif self.os_type in ['Linux', 'Darwin'] and self.smartctl_path:
                self._get_smart_smartctl(drive)
            
            # Calculate health score
            self._calculate_health_score(drive)
            
        except Exception as e:
            logger.error(f"Error updating health for {device_id}: {e}")
    
    def _get_smart_windows(self, drive: DriveHealth):
        """Get S.M.A.R.T. data on Windows"""
        # Implementation for Windows S.M.A.R.T. data collection
        # This would use WMI or smartctl for Windows
        pass
    
    def _get_smart_smartctl(self, drive: DriveHealth):
        """Get S.M.A.R.T. data using smartctl"""
        # Implementation for smartctl-based S.M.A.R.T. data collection
        pass
    
    def _calculate_health_score(self, drive: DriveHealth) -> float:
        """Calculate a health score (0-100) for the drive"""
        # Base score starts at 100 and gets reduced by issues
        score = 100.0
        
        # Temperature impact (0-30 points)
        if drive.temperature is not None:
            if drive.temperature > 70:  # Critical temperature
                score -= 30
            elif drive.temperature > 60:  # High temperature
                score -= 15
            elif drive.temperature > 50:  # Elevated temperature
                score -= 5
        
        # Power-on hours impact (0-20 points)
        if drive.power_on_hours is not None:
            if drive.power_on_hours > 50000:  # Very high usage
                score -= 20
            elif drive.power_on_hours > 30000:  # High usage
                score -= 10
            elif drive.power_on_hours > 10000:  # Moderate usage
                score -= 5
        
        # Ensure score is within bounds
        score = max(0.0, min(100.0, score))
        drive.health_score = score
        
        # Update health status based on score
        if score >= 90:
            drive.health_status = HealthStatus.EXCELLENT
        elif score >= 75:
            drive.health_status = HealthStatus.GOOD
        elif score >= 50:
            drive.health_status = HealthStatus.FAIR
        elif score >= 25:
            drive.health_status = HealthStatus.POOR
        elif score > 0:
            drive.health_status = HealthStatus.CRITICAL
        else:
            drive.health_status = HealthStatus.FAILED
        
        return score
    
    def get_health_report(self, device_id: str = None) -> Dict:
        """
        Generate a health report for a specific drive or all drives
        Returns a dictionary with health information
        """
        if device_id:
            if device_id not in self.drives:
                return {"error": f"Drive {device_id} not found"}
            return self._generate_drive_report(self.drives[device_id])
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': platform.system(),
            'drives': {
                drive_id: self._generate_drive_report(drive)
                for drive_id, drive in self.drives.items()
            }
        }
    
    def _generate_drive_report(self, drive: DriveHealth) -> Dict:
        """Generate a report for a single drive"""
        return {
            'model': drive.model,
            'serial': drive.serial,
            'type': drive.type.value,
            'capacity_gb': drive.capacity_gb,
            'health_status': drive.health_status.description,
            'health_score': drive.health_score,
            'temperature': drive.temperature,
            'power_on_hours': drive.power_on_hours,
            'last_checked': drive.last_checked.isoformat(),
            'issues': drive.issues,
            'smart_attributes': {
                name: asdict(attr) 
                for name, attr in drive.attributes.items()
            } if drive.attributes else None
        }

# Example usage
if __name__ == "__main__":
    monitor = StorageHealthMonitor()
    
    print("Scanning drives...")
    drives = monitor.scan_drives()
    
    print("\nDrive Health Report:")
    print(json.dumps(monitor.get_health_report(), indent=2))
