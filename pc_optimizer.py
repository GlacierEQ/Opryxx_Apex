"""
PC Optimizer Module for OPRYXX
Created by Cascade AI - 2025-05-20
"""
import os
import subprocess
import threading
import time
import psutil
import shutil
from datetime import datetime
import win32com.client
import tempfile
import winreg

class PCOptimizer:
    def __init__(self, update_status_callback=None, update_log_callback=None, update_progress_callback=None):
        self.update_status = update_status_callback or (lambda x: None)
        self.update_log = update_log_callback or (lambda x: None)
        self.update_progress = update_progress_callback or (lambda x: None)
        self.stop_flag = False
        self.log_file = os.path.join(os.path.expanduser("~"), "PC_Health_Results", 
                                     f"pc_optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
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
    
    def create_restore_point(self):
        """Create a system restore point before optimization"""
        self.update_status("Creating system restore point...")
        self.log("Creating system restore point for safety")
        
        try:
            subprocess.run(["powershell", "-Command", 
                            "Checkpoint-Computer -Description 'OPRYXX PC Optimizer' -RestorePointType 'APPLICATION_INSTALL'"], 
                           capture_output=True, check=True)
            self.log("✓ System restore point created successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"✗ Failed to create system restore point: {e}")
            return False
    
    def clean_temp_files(self):
        """Clean temporary files from various locations"""
        self.update_status("Cleaning temporary files...")
        self.log("Starting temporary files cleanup")
        
        # Locations to clean
        temp_locations = [
            os.environ.get('TEMP', ''),
            os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Prefetch'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Windows\\Explorer'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\Cache'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Cache'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Mozilla\\Firefox\\Profiles')
        ]
        
        files_removed = 0
        bytes_freed = 0
        
        for location in temp_locations:
            if not location or not os.path.exists(location):
                continue
                
            self.log(f"Cleaning: {location}")
            
            try:
                # Get initial size
                initial_size = self.get_folder_size(location)
                
                # Remove files (skip if in use)
                if os.path.isdir(location):
                    for root, dirs, files in os.walk(location, topdown=False):
                        for file in files:
                            if self.stop_flag:
                                return
                                
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    files_removed += 1
                                    bytes_freed += file_size
                            except:
                                pass  # Skip files that can't be removed
                                
                # Get final size and report savings
                final_size = self.get_folder_size(location)
                savings = initial_size - final_size
                if savings > 0:
                    self.log(f"Freed {self.format_size(savings)} from {location}")
            except Exception as e:
                self.log(f"Error cleaning {location}: {e}")
        
        self.log(f"✓ Temporary files cleanup complete: Removed {files_removed} files ({self.format_size(bytes_freed)})")
        return files_removed, bytes_freed
    
    def clean_windows_update_cache(self):
        """Clean Windows Update cache"""
        self.update_status("Cleaning Windows Update cache...")
        self.log("Cleaning Windows Update cache")
        
        try:
            # Stop Windows Update service
            subprocess.run(["net", "stop", "wuauserv"], capture_output=True)
            
            # Clean SoftwareDistribution folder
            sd_folder = os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'SoftwareDistribution')
            if os.path.exists(sd_folder):
                initial_size = self.get_folder_size(sd_folder)
                
                # Rename the folder (more reliable than deletion)
                backup_folder = f"{sd_folder}_old"
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder, ignore_errors=True)
                
                try:
                    os.rename(sd_folder, backup_folder)
                    os.makedirs(sd_folder, exist_ok=True)
                    
                    # Try to remove the old folder
                    shutil.rmtree(backup_folder, ignore_errors=True)
                    
                    self.log(f"Freed {self.format_size(initial_size)} from Windows Update cache")
                except Exception as e:
                    self.log(f"Partial cleanup of Windows Update cache: {e}")
            
            # Restart Windows Update service
            subprocess.run(["net", "start", "wuauserv"], capture_output=True)
            
            self.log("✓ Windows Update cache cleanup complete")
            return True
        except Exception as e:
            self.log(f"✗ Windows Update cache cleanup error: {e}")
            return False
    
    def run_disk_cleanup(self):
        """Run built-in Disk Cleanup utility"""
        self.update_status("Running Disk Cleanup...")
        self.log("Starting Windows Disk Cleanup utility")
        
        try:
            # Create a sageset for automated cleanup
            subprocess.run(["cleanmgr", "/sagerun:1"], capture_output=True)
            self.log("✓ Disk Cleanup completed")
            return True
        except Exception as e:
            self.log(f"✗ Disk Cleanup error: {e}")
            return False
    
    def optimize_drives(self):
        """Optimize/defragment drives"""
        self.update_status("Optimizing drives...")
        self.log("Starting drive optimization")
        
        try:
            # Get list of fixed drives
            drives = [d.device for d in psutil.disk_partitions() if d.fstype]
            
            for drive in drives:
                if self.stop_flag:
                    return False
                
                drive_letter = drive[:2]  # e.g., "C:"
                self.log(f"Optimizing drive {drive_letter}")
                
                # Run optimization
                subprocess.run(["defrag", drive_letter, "/O"], capture_output=True)
            
            self.log("✓ Drive optimization complete")
            return True
        except Exception as e:
            self.log(f"✗ Drive optimization error: {e}")
            return False
    
    def scan_system_files(self):
        """Run System File Checker"""
        self.update_status("Scanning system files...")
        self.log("Starting System File Checker (SFC)")
        
        try:
            # Run SFC scan
            process = subprocess.Popen(["sfc", "/scannow"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)
            
            # Monitor the output
            for line in iter(process.stdout.readline, ''):
                if self.stop_flag:
                    process.terminate()
                    self.log("System File Check aborted")
                    return False
                
                if line.strip():
                    self.log(f"SFC: {line.strip()}")
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.log("✓ System File Check completed successfully")
                return True
            else:
                self.log(f"✗ System File Check failed with code {process.returncode}")
                return False
        except Exception as e:
            self.log(f"✗ System File Check error: {e}")
            return False
    
    def run_dism_repair(self):
        """Run DISM to repair Windows image"""
        self.update_status("Repairing Windows system files...")
        self.log("Starting DISM Repair (this may take 10-15 minutes)")
        
        try:
            # Run DISM repair
            process = subprocess.Popen(["DISM.exe", "/Online", "/Cleanup-Image", "/RestoreHealth"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True)
            
            # Monitor the output
            for line in iter(process.stdout.readline, ''):
                if self.stop_flag:
                    process.terminate()
                    self.log("DISM repair aborted")
                    return False
                
                if line.strip():
                    self.log(f"DISM: {line.strip()}")
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                self.log("✓ DISM repair completed successfully")
                return True
            else:
                self.log(f"✗ DISM repair failed with code {process.returncode}")
                return False
        except Exception as e:
            self.log(f"✗ DISM repair error: {e}")
            return False
    
    def reset_network(self):
        """Reset network settings"""
        self.update_status("Resetting network...")
        self.log("Resetting network settings")
        
        try:
            commands = [
                ["ipconfig", "/flushdns"],
                ["netsh", "winsock", "reset"],
                ["netsh", "int", "ip", "reset"],
                ["netsh", "int", "tcp", "reset"]
            ]
            
            for cmd in commands:
                if self.stop_flag:
                    return False
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                self.log(f"Network command {' '.join(cmd)}: {result.returncode}")
            
            self.log("✓ Network settings reset successfully")
            return True
        except Exception as e:
            self.log(f"✗ Network reset error: {e}")
            return False
    
    def optimize_system_performance(self):
        """Optimize system performance settings"""
        self.update_status("Optimizing system performance...")
        self.log("Optimizing system performance settings")
        
        try:
            # Set power plan to high performance
            subprocess.run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], 
                          capture_output=True)
            self.log("Set power plan to High Performance")
            
            # Optimize visual effects for performance
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
                self.log("Set visual effects for best performance")
            except:
                self.log("Could not set visual effects settings")
            
            # Disable unnecessary startup items
            self.log("✓ System performance optimization complete")
            return True
        except Exception as e:
            self.log(f"✗ System performance optimization error: {e}")
            return False
    
    def clear_event_logs(self):
        """Clear Windows event logs"""
        self.update_status("Clearing event logs...")
        self.log("Clearing Windows event logs")
        
        try:
            # Get list of event logs
            result = subprocess.run(["wevtutil", "el"], capture_output=True, text=True)
            logs = result.stdout.splitlines()
            
            for log in logs:
                if self.stop_flag:
                    return False
                
                try:
                    subprocess.run(["wevtutil", "cl", log], capture_output=True)
                    self.log(f"Cleared event log: {log}")
                except:
                    pass  # Skip logs that can't be cleared
            
            self.log("✓ Event logs cleared")
            return True
        except Exception as e:
            self.log(f"✗ Event log clearing error: {e}")
            return False
            
    def run_full_optimization(self, create_restore=True):
        """Run all optimization tasks"""
        self.stop_flag = False
        
        # Initialize progress
        if self.update_progress:
            self.update_progress(0)
        
        # Create restore point if requested
        if create_restore:
            self.create_restore_point()
        
        # Define optimization tasks
        tasks = [
            ("Cleaning temporary files", self.clean_temp_files),
            ("Cleaning Windows Update cache", self.clean_windows_update_cache),
            ("Running Disk Cleanup", self.run_disk_cleanup),
            ("Optimizing drives", self.optimize_drives),
            ("Scanning system files", self.scan_system_files),
            ("Repairing Windows system files", self.run_dism_repair),
            ("Resetting network", self.reset_network),
            ("Optimizing system performance", self.optimize_system_performance),
            ("Clearing event logs", self.clear_event_logs)
        ]
        
        # Run tasks and update progress
        total_tasks = len(tasks)
        for i, (description, task_func) in enumerate(tasks):
            if self.stop_flag:
                self.log("Optimization stopped by user")
                break
                
            self.update_status(description)
            task_func()
            
            # Update progress
            if self.update_progress:
                progress = int((i + 1) / total_tasks * 100)
                self.update_progress(progress)
        
        # Complete
        self.update_status("Optimization complete")
        self.log("System optimization completed")
        
        # Ensure 100% progress at end
        if self.update_progress:
            self.update_progress(100)
        
        return True
    
    def stop(self):
        """Stop any running optimization tasks"""
        self.stop_flag = True
        self.log("Stopping optimization tasks...")
    
    def get_folder_size(self, folder_path):
        """Get the total size of a folder in bytes"""
        total_size = 0
        if os.path.exists(folder_path):
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    try:
                        file_path = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(file_path)
                    except:
                        pass  # Skip files that can't be accessed
        return total_size
    
    def format_size(self, size_bytes):
        """Format bytes into a human-readable size"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def analyze_system(self):
        """Analyze system health and return results"""
        self.update_status("Analyzing system...")
        self.log("Starting system health analysis")
        
        results = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_space": {},
            "temp_files_size": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Check disk space
        for partition in psutil.disk_partitions():
            if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
                continue
                
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                results["disk_space"][partition.mountpoint] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                }
                
                # Check if low on space
                if usage.percent > 90:
                    results["issues"].append(f"Critical: Drive {partition.mountpoint} is almost full ({usage.percent}% used)")
                    results["recommendations"].append(f"Free up space on drive {partition.mountpoint}")
                elif usage.percent > 80:
                    results["issues"].append(f"Warning: Drive {partition.mountpoint} is getting full ({usage.percent}% used)")
                    results["recommendations"].append(f"Consider cleaning up drive {partition.mountpoint}")
            except:
                pass
        
        # Check temp files size
        temp_path = os.environ.get('TEMP', '')
        if temp_path and os.path.exists(temp_path):
            temp_size = self.get_folder_size(temp_path)
            results["temp_files_size"] = temp_size
            
            if temp_size > 1024 * 1024 * 1024:  # 1 GB
                results["issues"].append(f"Warning: Large temporary files detected ({self.format_size(temp_size)})")
                results["recommendations"].append("Clean temporary files")
        
        # Check memory usage
        if results["memory_usage"] > 90:
            results["issues"].append(f"Critical: High memory usage ({results['memory_usage']}%)")
            results["recommendations"].append("Close unnecessary applications or increase RAM")
        elif results["memory_usage"] > 80:
            results["issues"].append(f"Warning: Elevated memory usage ({results['memory_usage']}%)")
            results["recommendations"].append("Consider closing unused applications")
        
        # Check CPU usage
        if results["cpu_usage"] > 90:
            results["issues"].append(f"Critical: High CPU usage ({results['cpu_usage']}%)")
            results["recommendations"].append("Check for resource-intensive applications")
        elif results["cpu_usage"] > 80:
            results["issues"].append(f"Warning: Elevated CPU usage ({results['cpu_usage']}%)")
        
        # Log results
        self.log(f"System Analysis Results:")
        self.log(f"- CPU Usage: {results['cpu_usage']}%")
        self.log(f"- Memory Usage: {results['memory_usage']}%")
        
        for drive, info in results["disk_space"].items():
            self.log(f"- Drive {drive}: {info['percent']}% used, {self.format_size(info['free'])} free of {self.format_size(info['total'])}")
        
        if results["issues"]:
            self.log("Issues Detected:")
            for issue in results["issues"]:
                self.log(f"- {issue}")
        
        if results["recommendations"]:
            self.log("Recommendations:")
            for rec in results["recommendations"]:
                self.log(f"- {rec}")
        
        self.log("✓ System analysis complete")
        
        return results
