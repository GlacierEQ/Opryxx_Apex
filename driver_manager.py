"""
Driver Manager Module for OPRYXX
Created by Cascade AI - 2025-05-20
"""
import os
import subprocess
import threading
import json
import re
import time
import tempfile
import winreg
from datetime import datetime
import requests
import zipfile
import io

class DriverManager:
    def __init__(self, update_status_callback=None, update_log_callback=None, update_progress_callback=None):
        self.update_status = update_status_callback or (lambda x: None)
        self.update_log = update_log_callback or (lambda x: None)
        self.update_progress = update_progress_callback or (lambda x: None)
        self.stop_flag = False
        self.log_file = os.path.join(os.path.expanduser("~"), "PC_Health_Results", 
                                     f"driver_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def log(self, message):
        """Log a message to both the GUI and log file"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_message = f"{timestamp} {message}"
        
        if self.update_log:
            self.update_log(log_message + "\n")
            
        # Also write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def scan_drivers(self):
        """Scan for all installed drivers and their versions"""
        self.update_status("Scanning device drivers...")
        self.log("Starting driver scan...")
        
        drivers = []
        
        try:
            # Run PowerShell command to get device information
            ps_command = "Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName, DriverVersion, Manufacturer, DriverDate | ConvertTo-Json"
            result = subprocess.run(["powershell", "-Command", ps_command], 
                              capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                try:
                    # Parse JSON output
                    driver_data = json.loads(result.stdout)
                    
                    # Handle single driver result (not in an array)
                    if not isinstance(driver_data, list):
                        driver_data = [driver_data]
                    
                    # Filter and process driver information
                    for driver in driver_data:
                        # Skip empty or unnamed drivers
                        if not driver.get('DeviceName'):
                            continue
                            
                        # Format driver information
                        driver_info = {
                            'name': driver.get('DeviceName', 'Unknown Device'),
                            'version': driver.get('DriverVersion', 'Unknown'),
                            'manufacturer': driver.get('Manufacturer', 'Unknown'),
                            'date': driver.get('DriverDate', 'Unknown'),
                            'status': 'Unknown'
                        }
                        
                        # Add to driver list
                        drivers.append(driver_info)
                        
                    self.log(f"Found {len(drivers)} device drivers")
                except json.JSONDecodeError:
                    self.log(f"Error parsing driver data: Invalid JSON format")
            else:
                self.log("No driver information returned from system")
        
        except subprocess.CalledProcessError as e:
            self.log(f"Error scanning drivers: {e}")
            return []
        
        # Categorize critical drivers
        critical_categories = [
            'display', 'video', 'nvidia', 'amd', 'intel', 'radeon', 'geforce',  # Graphics
            'network', 'ethernet', 'wireless', 'wifi', 'bluetooth',             # Network
            'audio', 'sound', 'realtek',                                        # Audio
            'storage', 'disk', 'nvme', 'ssd', 'controller'                      # Storage
        ]
        
        for driver in drivers:
            # Check if driver name contains any critical category keywords
            name_lower = driver['name'].lower()
            for category in critical_categories:
                if category in name_lower:
                    driver['priority'] = 'high'
                    break
            else:
                driver['priority'] = 'normal'
        
        # Sort drivers by priority and name
        drivers.sort(key=lambda x: (0 if x['priority'] == 'high' else 1, x['name']))
        
        # Check for outdated drivers
        self._check_driver_status(drivers)
        
        return drivers
    
    def _check_driver_status(self, drivers):
        """Check if drivers need updates based on age and version"""
        self.update_status("Checking driver status...")
        self.log("Analyzing driver versions and status...")
        
        current_year = datetime.now().year
        
        for driver in drivers:
            # Parse date info if available
            date_str = driver.get('date', '')
            driver_year = None
            
            # Extract year from different possible date formats
            if re.search(r'\d{4}', date_str):
                match = re.search(r'(\d{4})', date_str)
                if match:
                    try:
                        driver_year = int(match.group(1))
                    except ValueError:
                        pass
            
            # Determine status based on age and other factors
            if driver_year and (current_year - driver_year) > 2:
                driver['status'] = 'Outdated'
            elif 'Microsoft' in driver.get('manufacturer', '') and not any(x in driver['name'].lower() for x in ['basic', 'generic']):
                driver['status'] = 'OK'
            elif driver.get('version', '').count('.') >= 2:  # Has proper version format
                driver['status'] = 'OK'
            else:
                driver['status'] = 'Unknown'
                
            # Log status for high priority drivers
            if driver.get('priority') == 'high':
                self.log(f"Critical driver: {driver['name']} - {driver['version']} - Status: {driver['status']}")
        
        # Count outdated drivers
        outdated_count = sum(1 for d in drivers if d['status'] == 'Outdated')
        self.log(f"Found {outdated_count} potentially outdated drivers")
        
        return drivers
    
    def export_driver_list(self, drivers, export_path=None):
        """Export the driver list to CSV and HTML formats"""
        if not export_path:
            export_path = os.path.join(os.path.expanduser("~"), "PC_Health_Results")
            os.makedirs(export_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"driver_report_{timestamp}"
        
        # Export to CSV
        csv_path = os.path.join(export_path, f"{base_filename}.csv")
        try:
            with open(csv_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Device Name,Manufacturer,Version,Date,Status,Priority\n")
                
                # Write data
                for driver in drivers:
                    f.write(f"\"{driver.get('name', 'Unknown')}\",")
                    f.write(f"\"{driver.get('manufacturer', 'Unknown')}\",")
                    f.write(f"\"{driver.get('version', 'Unknown')}\",")
                    f.write(f"\"{driver.get('date', 'Unknown')}\",")
                    f.write(f"\"{driver.get('status', 'Unknown')}\",")
                    f.write(f"\"{driver.get('priority', 'normal')}\"\n")
            
            self.log(f"Exported driver list to CSV: {csv_path}")
        except Exception as e:
            self.log(f"Error exporting to CSV: {e}")
        
        # Export to HTML for better readability
        html_path = os.path.join(export_path, f"{base_filename}.html")
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Driver Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .outdated { background-color: #ffcccc; }
        .high { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Driver Report</h1>
    <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    <table>
        <tr>
            <th>Device Name</th>
            <th>Manufacturer</th>
            <th>Version</th>
            <th>Date</th>
            <th>Status</th>
        </tr>
""")
                
                for driver in drivers:
                    row_class = ""
                    if driver.get('status') == 'Outdated':
                        row_class = "outdated"
                    if driver.get('priority') == 'high':
                        row_class += " high"
                    
                    f.write(f"        <tr class=\"{row_class}\">\n")
                    f.write(f"            <td>{driver.get('name', 'Unknown')}</td>\n")
                    f.write(f"            <td>{driver.get('manufacturer', 'Unknown')}</td>\n")
                    f.write(f"            <td>{driver.get('version', 'Unknown')}</td>\n")
                    f.write(f"            <td>{driver.get('date', 'Unknown')}</td>\n")
                    f.write(f"            <td>{driver.get('status', 'Unknown')}</td>\n")
                    f.write(f"        </tr>\n")
                
                f.write("""    </table>
</body>
</html>""")
            
            self.log(f"Exported driver list to HTML: {html_path}")
        except Exception as e:
            self.log(f"Error exporting to HTML: {e}")
            
        return csv_path, html_path

    def create_restore_point(self, description="Before driver updates"):
        """Create a system restore point before making driver changes"""
        self.update_status("Creating system restore point...")
        self.log("Creating system restore point for safety")
        
        try:
            ps_command = f"""
            Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✓ System restore point created successfully")
                return True
            else:
                self.log(f"✗ Failed to create system restore point: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"✗ Error creating system restore point: {e}")
            return False
    
    def backup_drivers(self, backup_path=None):
        """Back up existing drivers to a safe location"""
        if not backup_path:
            backup_path = os.path.join(os.path.expanduser("~"), "PC_Health_Results", "DriverBackups")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(backup_path, f"driver_backup_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        self.update_status("Backing up drivers...")
        self.log(f"Backing up drivers to: {backup_folder}")
        
        try:
            # Use DISM to export drivers
            cmd = f'DISM /Online /Export-Driver /Destination:"{backup_folder}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "successfully" in result.stdout.lower() or result.returncode == 0:
                self.log("✓ Drivers backed up successfully")
                return backup_folder
            else:
                self.log(f"✗ Failed to backup drivers: {result.stderr}")
                return None
        except Exception as e:
            self.log(f"✗ Error backing up drivers: {e}")
            return None

    def restore_drivers(self, backup_folder):
        """Restore drivers from a backup folder"""
        if not os.path.exists(backup_folder):
            self.log(f"✗ Backup folder not found: {backup_folder}")
            return False
        
        self.update_status("Restoring drivers from backup...")
        self.log(f"Restoring drivers from: {backup_folder}")
        
        try:
            # Use pnputil to add drivers
            cmd = f'pnputil /add-driver "{backup_folder}\\*.inf" /subdirs /install'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "successfully" in result.stdout.lower() or result.returncode == 0:
                self.log("✓ Drivers restored successfully")
                return True
            else:
                self.log(f"✗ Failed to restore drivers: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"✗ Error restoring drivers: {e}")
            return False
    
    def disable_driver(self, device_id):
        """Disable a specific driver/device"""
        self.update_status(f"Disabling device...")
        self.log(f"Attempting to disable device: {device_id}")
        
        try:
            ps_command = f"""
            $device = Get-PnpDevice -InstanceId "{device_id}" -ErrorAction SilentlyContinue
            if ($device) {{
                Disable-PnpDevice -InstanceId "{device_id}" -Confirm:$false
                "Device disabled successfully"
            }} else {{
                "Device not found"
            }}
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True)
            
            if "successfully" in result.stdout:
                self.log(f"✓ Device disabled successfully")
                return True
            else:
                self.log(f"✗ Failed to disable device: {result.stdout}")
                return False
        except Exception as e:
            self.log(f"✗ Error disabling device: {e}")
            return False
    
    def enable_driver(self, device_id):
        """Enable a specific driver/device"""
        self.update_status(f"Enabling device...")
        self.log(f"Attempting to enable device: {device_id}")
        
        try:
            ps_command = f"""
            $device = Get-PnpDevice -InstanceId "{device_id}" -ErrorAction SilentlyContinue
            if ($device) {{
                Enable-PnpDevice -InstanceId "{device_id}" -Confirm:$false
                "Device enabled successfully"
            }} else {{
                "Device not found"
            }}
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True)
            
            if "successfully" in result.stdout:
                self.log(f"✓ Device enabled successfully")
                return True
            else:
                self.log(f"✗ Failed to enable device: {result.stdout}")
                return False
        except Exception as e:
            self.log(f"✗ Error enabling device: {e}")
            return False
    
    def update_driver(self, device_id, driver_path):
        """Update a specific driver from a path"""
        self.update_status(f"Updating driver...")
        self.log(f"Attempting to update driver from: {driver_path}")
        
        try:
            # First create a restore point
            self.create_restore_point("Before driver update")
            
            # Update driver using pnputil
            cmd = f'pnputil /add-driver "{driver_path}" /install'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "successfully" in result.stdout.lower() or result.returncode == 0:
                self.log(f"✓ Driver updated successfully")
                return True
            else:
                self.log(f"✗ Failed to update driver: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"✗ Error updating driver: {e}")
            return False
    
    def rollback_driver(self, device_id):
        """Rollback a driver to the previous version"""
        self.update_status(f"Rolling back driver...")
        self.log(f"Attempting to rollback driver for device: {device_id}")
        
        try:
            ps_command = f"""
            $device = Get-WmiObject Win32_PnPSignedDriver | Where-Object {{ $_.DeviceID -eq "{device_id}" }}
            if ($device) {{
                $deviceObj = Get-WmiObject Win32_PnPEntity | Where-Object {{ $_.DeviceID -eq "{device_id}" }}
                $deviceObj.RollbackDriver()
                "Driver rollback initiated"
            }} else {{
                "Device not found"
            }}
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                    capture_output=True, text=True)
            
            if "rollback initiated" in result.stdout:
                self.log(f"✓ Driver rollback successful")
                return True
            else:
                self.log(f"✗ Failed to rollback driver: {result.stdout}")
                return False
        except Exception as e:
            self.log(f"✗ Error rolling back driver: {e}")
            return False
    
    def scan_for_driver_issues(self):
        """Scan for common driver issues and problems"""
        self.update_status("Scanning for driver issues...")
        self.log("Checking for driver issues and conflicts...")
        
        issues = []
        
        try:
            # Check for device manager issues
            ps_command = """
            Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | 
            Select-Object Name, DeviceID, ConfigManagerErrorCode | ConvertTo-Json
            """
            
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                   capture_output=True, text=True)
            
            if result.stdout.strip():
                try:
                    # Parse JSON output
                    problem_devices = json.loads(result.stdout)
                    
                    # Handle single device result
                    if not isinstance(problem_devices, list):
                        problem_devices = [problem_devices]
                    
                    for device in problem_devices:
                        error_code = device.get('ConfigManagerErrorCode', 0)
                        issue = {
                            'device': device.get('Name', 'Unknown Device'),
                            'device_id': device.get('DeviceID', ''),
                            'error_code': error_code,
                            'description': self._get_error_description(error_code),
                            'severity': 'critical' if error_code in [1, 3, 10, 14, 22, 28] else 'warning'
                        }
                        issues.append(issue)
                        
                        self.log(f"Issue detected: {issue['device']} - {issue['description']}")
                except json.JSONDecodeError:
                    self.log(f"Error parsing device problem data: Invalid JSON format")
        except Exception as e:
            self.log(f"Error scanning for driver issues: {e}")
        
        # Additional checks could be added here
        
        return issues
    
    def _get_error_description(self, error_code):
        """Get a human-readable description of a device manager error code"""
        error_descriptions = {
            0: "Device is working properly.",
            1: "Device is not configured correctly.",
            2: "Windows cannot load the driver for this device.",
            3: "Driver may be corrupted or missing.",
            4: "Device is not working properly.",
            5: "Windows is still setting up this device.",
            6: "Windows is still setting up this device.",
            7: "Device does not have valid configuration information.",
            8: "Device is not present, not working properly, or missing driver.",
            9: "Device is not working properly.",
            10: "Device cannot start.",
            11: "Device failed.",
            12: "Device cannot find enough free resources.",
            13: "Windows cannot verify the device's resources.",
            14: "Device cannot work properly until you restart your computer.",
            15: "Device is not working properly due to re-enumeration.",
            16: "Windows cannot identify all resources device uses.",
            17: "Device is requesting an unknown resource type.",
            18: "Device drivers must be reinstalled.",
            19: "Windows registry data corrupted.",
            20: "System failure: Try changing the driver.",
            21: "Device is disabled.",
            22: "System failure: Remove or reconfigure registry entries.",
            23: "Device is present but BIOS not detecting it.",
            24: "Device is disabled. To enable, use Device Manager.",
            25: "Device functioning properly but Windows cannot detect it.",
            26: "Device functioning properly but no drivers are installed.",
            27: "Hardware not installed correctly.",
            28: "Device disabled because BIOS did not provide required resources.",
            29: "Device is causing a resource conflict.",
            30: "Cannot start this hardware device.",
            31: "Device is not working properly.",
            32: "Windows cannot determine which resources are required.",
            33: "Windows cannot specify resources for this device."
        }
        
        return error_descriptions.get(error_code, f"Unknown error code: {error_code}")
    
    def fix_common_driver_issues(self, device_id=None):
        """Attempt to fix common driver issues"""
        self.update_status("Attempting to fix driver issues...")
        self.log("Running automatic driver repair...")
        
        fixes_applied = []
        
        try:
            # Create a restore point first
            self.create_restore_point("Before driver repairs")
            
            if device_id:
                # Fix specific device
                ps_command = f"""
                $device = Get-PnpDevice -InstanceId "{device_id}" -ErrorAction SilentlyContinue
                if ($device) {{
                    # Try disabling and re-enabling
                    Disable-PnpDevice -InstanceId "{device_id}" -Confirm:$false
                    Start-Sleep -Seconds 2
                    Enable-PnpDevice -InstanceId "{device_id}" -Confirm:$false
                    "Device cycle complete"
                }}
                """
                
                subprocess.run(["powershell", "-Command", ps_command], 
                               capture_output=True, text=True)
                
                fixes_applied.append(f"Reset device: {device_id}")
                self.log(f"Applied fix: Reset device {device_id}")
            else:
                # General fixes
                
                # 1. Scan for hardware changes
                self.log("Scanning for hardware changes...")
                subprocess.run(["powershell", "-Command", 
                              "$hardwareClass = [guid]::Parse('{4d36e97d-e325-11ce-bfc1-08002be10318}'); $devcon = New-Object -ComObject DeviceManager.DeviceInfoSet; $devcon.ScanForHardwareChanges($hardwareClass);"],
                             capture_output=True)
                fixes_applied.append("Scanned for hardware changes")
                
                # 2. Reset driver installation state
                self.log("Resetting driver installation state...")
                subprocess.run(["sc", "config", "Trustedinstaller", "start=", "auto"], 
                             capture_output=True)
                subprocess.run(["sc", "start", "Trustedinstaller"], 
                             capture_output=True)
                fixes_applied.append("Reset driver installation service")
                
                # 3. Run troubleshooter (Windows 10+)
                self.log("Running hardware troubleshooter...")
                subprocess.run(["powershell", "-Command", 
                              "Get-TroubleshootingPack -Path 'C:\\Windows\\diagnostics\\system\\devices' | Invoke-TroubleshootingPack -Unattended"],
                             capture_output=True)
                fixes_applied.append("Ran hardware troubleshooter")
        
        except Exception as e:
            self.log(f"Error during driver repair: {e}")
        
        return fixes_applied
    
    def stop(self):
        """Stop any running scan or repair operations"""
        self.stop_flag = True
        self.log("Stopping driver manager operations...")
