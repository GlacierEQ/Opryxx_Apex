"""
GANDALFS Maintenance Script for OPRYXX

This script handles the automated maintenance of GANDALFS components,
including scheduled updates, integrity checks, and system compatibility
verification.
"""
import os
import sys
import time
import json
import logging
import smtplib
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path to import GandalfsUpdateManager
sys.path.append(str(Path(__file__).parent.absolute()))
from gandalfs_update_manager import GandalfsUpdateManager

# Configuration
CONFIG = {
    "log_file": "C:\\OPRYXX\\logs\\gandalfs_maintenance.log",
    "config_file": "C:\\OPRYXX\\config\\gandalfs_config.json",
    "email": {
        "enabled": False,  # Set to True to enable email notifications
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "user@example.com",
        "smtp_password": "your_password",
        "from_addr": "noreply@opryxx.com",
        "to_addrs": ["admin@example.com"]
    },
    "backup": {
        "enabled": True,
        "max_backups": 5,
        "backup_dir": "C:\\OPRYXX\\backups"
    },
    "integrity_checks": {
        "enabled": True,
        "check_interval_hours": 24
    },
    "cleanup": {
        "enabled": True,
        "max_log_age_days": 30,
        "max_temp_files_age_days": 7
    }
}

class GandalfsMaintenance:
    """Maintenance operations for GANDALFS components."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the maintenance manager."""
        self.config = config or CONFIG
        self._setup_logging()
        self.update_manager = GandalfsUpdateManager(self.config["config_file"])
        self.logger = logging.getLogger("GANDALFS_Maintenance")
    
    def _setup_logging(self) -> None:
        """Configure logging for the maintenance script."""
        log_dir = os.path.dirname(self.config["log_file"])
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config["log_file"], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def run_maintenance(self) -> bool:
        """Run all configured maintenance tasks."""
        self.logger.info("Starting GANDALFS maintenance tasks")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": self._get_system_info(),
            "tasks": {}
        }
        
        try:
            # Check for updates
            update_result = self.check_for_updates()
            results["tasks"]["update_check"] = update_result
            
            # Run integrity checks
            if self.config["integrity_checks"]["enabled"]:
                integrity_result = self.run_integrity_checks()
                results["tasks"]["integrity_checks"] = integrity_result
            
            # Clean up old files
            if self.config["cleanup"]["enabled"]:
                cleanup_result = self.cleanup_old_files()
                results["tasks"]["cleanup"] = cleanup_result
            
            # Backup configuration
            if self.config["backup"]["enabled"]:
                backup_result = self.backup_configuration()
                results["tasks"]["backup"] = backup_result
            
            # Check system compatibility
            compat_result = self.check_system_compatibility()
            results["tasks"]["compatibility_check"] = compat_result
            
            self.logger.info("Maintenance tasks completed successfully")
            results["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"Error during maintenance: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
            
            # Send error notification
            self.send_notification(
                "GANDALFS Maintenance Error",
                f"An error occurred during maintenance:\n\n{str(e)}",
                is_error=True
            )
        
        # Send summary notification
        self.send_maintenance_summary(results)
        
        return results["status"] == "success"
    
    def check_for_updates(self) -> Dict:
        """Check for and apply available updates."""
        self.logger.info("Checking for GANDALFS updates")
        
        result = {
            "status": "success",
            "updates_applied": False,
            "details": {}
        }
        
        try:
            # Check for updates
            check_result = self.update_manager.check_for_updates()
            
            if check_result.get("status") != "success":
                result["status"] = "error"
                result["error"] = check_result.get("message", "Unknown error checking for updates")
                return result
            
            if not check_result.get("updates_available", False):
                self.logger.info("No updates available")
                result["up_to_date"] = True
                return result
            
            self.logger.info("Updates available, downloading...")
            
            # Download updates
            download_result = self.update_manager.download_updates()
            result["download"] = download_result
            
            # Apply updates if download was successful
            if all(d.get("status") == "success" for d in download_result.values()):
                self.logger.info("Applying updates...")
                apply_result = self.update_manager.apply_updates()
                result["apply"] = apply_result
                
                if all(a.get("status") == "success" for a in apply_result.values()):
                    result["updates_applied"] = True
                    self.logger.info("Updates applied successfully")
                else:
                    result["status"] = "warning"
                    result["message"] = "Some updates could not be applied"
            else:
                result["status"] = "error"
                result["message"] = "Failed to download some updates"
            
        except Exception as e:
            self.logger.error(f"Error during update check: {e}", exc_info=True)
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def run_integrity_checks(self) -> Dict:
        """Run integrity checks on GANDALFS components."""
        self.logger.info("Running integrity checks")
        
        result = {
            "status": "success",
            "checks": {}
        }
        
        try:
            # Check if GANDALFS components exist
            components = self.update_manager.config.get("components", {})
            
            for name, info in components.items():
                path = info.get("path")
                if not path:
                    result["checks"][name] = {"status": "error", "message": "No path specified"}
                    continue
                
                if not os.path.exists(path):
                    result["checks"][name] = {"status": "error", "message": f"File not found: {path}"}
                    continue
                
                # In a real implementation, verify checksum or signature
                result["checks"][name] = {
                    "status": "success",
                    "path": path,
                    "size": os.path.getsize(path)
                }
            
            # If any checks failed, update overall status
            if any(c.get("status") != "success" for c in result["checks"].values()):
                result["status"] = "warning"
                
        except Exception as e:
            self.logger.error(f"Error during integrity checks: {e}", exc_info=True)
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def cleanup_old_files(self) -> Dict:
        """Clean up old log and temporary files."""
        self.logger.info("Cleaning up old files")
        
        result = {
            "status": "success",
            "files_removed": 0,
            "errors": []
        }
        
        try:
            # Clean up old log files
            log_dir = os.path.dirname(self.config["log_file"])
            if os.path.exists(log_dir):
                max_age = self.config["cleanup"]["max_log_age_days"] * 24 * 3600
                removed = self._remove_old_files(log_dir, "*.log", max_age)
                result["log_files_removed"] = removed
                result["files_removed"] += removed
            
            # Clean up temporary files
            temp_dirs = [
                os.environ.get("TEMP", "C:\\Windows\\Temp"),
                os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "OPRYXX\\temp")
            ]
            
            max_temp_age = self.config["cleanup"]["max_temp_files_age_days"] * 24 * 3600
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    removed = self._remove_old_files(temp_dir, "*", max_temp_age, recursive=True)
                    result[f"temp_files_removed_{os.path.basename(temp_dir)}"] = removed
                    result["files_removed"] += removed
            
        except Exception as e:
            error_msg = f"Error during cleanup: {e}"
            self.logger.error(error_msg, exc_info=True)
            result["status"] = "error"
            result["errors"].append(error_msg)
        
        return result
    
    def backup_configuration(self) -> Dict:
        """Back up GANDALFS configuration and important files."""
        self.logger.info("Backing up configuration")
        
        result = {
            "status": "success",
            "backups_created": 0,
            "backup_files": []
        }
        
        try:
            backup_dir = self.config["backup"]["backup_dir"]
            os.makedirs(backup_dir, exist_ok=True)
            
            # Files to back up
            files_to_backup = [
                self.config["config_file"],
                self.config["log_file"]
            ]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for file_path in files_to_backup:
                if not os.path.exists(file_path):
                    self.logger.warning(f"File not found for backup: {file_path}")
                    continue
                
                try:
                    file_name = os.path.basename(file_path)
                    backup_path = os.path.join(
                        backup_dir,
                        f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
                    )
                    
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    
                    result["backup_files"].append({
                        "original": file_path,
                        "backup": backup_path,
                        "status": "success"
                    })
                    result["backups_created"] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to back up {file_path}: {e}"
                    self.logger.error(error_msg, exc_info=True)
                    result["backup_files"].append({
                        "original": file_path,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Clean up old backups
            self._cleanup_old_backups(backup_dir)
            
        except Exception as e:
            error_msg = f"Error during backup: {e}"
            self.logger.error(error_msg, exc_info=True)
            result["status"] = "error"
            result["error"] = error_msg
        
        return result
    
    def check_system_compatibility(self) -> Dict:
        """Check system compatibility with GANDALFS components."""
        self.logger.info("Checking system compatibility")
        
        result = {
            "status": "success",
            "system": {},
            "requirements": {},
            "warnings": []
        }
        
        try:
            # Get system information
            system_info = self._get_system_info()
            result["system"] = system_info
            
            # Check OS version
            if system_info["os"] != "Windows":
                result["status"] = "error"
                result["error"] = "GANDALFS is only supported on Windows"
                return result
            
            # Check Windows version (Windows 10/11)
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                    current_build = int(winreg.QueryValueEx(key, "CurrentBuild")[0])
                    
                    result["requirements"]["windows_version"] = {
                        "status": "success",
                        "current": product_name,
                        "build": current_build
                    }
                    
                    # Check minimum build requirements
                    if current_build < 19041:  # Windows 10 2004
                        result["warnings"].append(
                            f"Windows version {product_name} (build {current_build}) "
                            "is not officially supported. Some features may not work correctly."
                        )
                        
            except Exception as e:
                self.logger.warning(f"Could not determine Windows version: {e}")
                result["requirements"]["windows_version"] = {
                    "status": "warning",
                    "message": "Could not determine Windows version"
                }
            
            # Check disk space
            try:
                import shutil
                total, used, free = shutil.disk_usage("/")
                min_required_gb = 10  # 10GB minimum free space
                
                result["requirements"]["disk_space"] = {
                    "status": "success" if free >= min_required_gb * (1024**3) else "warning",
                    "free_gb": round(free / (1024**3), 2),
                    "required_gb": min_required_gb
                }
                
                if free < min_required_gb * (1024**3):
                    result["warnings"].append(
                        f"Low disk space: {round(free / (1024**3), 2)}GB free, "
                        f"{min_required_gb}GB recommended"
                    )
                    
            except Exception as e:
                self.logger.warning(f"Could not check disk space: {e}")
                result["requirements"]["disk_space"] = {
                    "status": "warning",
                    "message": "Could not check disk space"
                }
            
            # Add more compatibility checks as needed
            
            if result["warnings"]:
                result["status"] = "warning"
            
        except Exception as e:
            error_msg = f"Error during compatibility check: {e}"
            self.logger.error(error_msg, exc_info=True)
            result["status"] = "error"
            result["error"] = error_msg
        
        return result
    
    def send_notification(self, subject: str, message: str, is_error: bool = False) -> bool:
        """Send a notification email."""
        if not self.config["email"]["enabled"]:
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["email"]["from_addr"]
            msg["To"] = ", ".join(self.config["email"]["to_addrs"])
            msg["Subject"] = f"[OPRYXX] {subject}"
            
            # Add message body
            msg.attach(MIMEText(message, "plain"))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(
                self.config["email"]["smtp_server"],
                self.config["email"]["smtp_port"]
            ) as server:
                server.starttls()
                server.login(
                    self.config["email"]["smtp_user"],
                    self.config["email"]["smtp_password"]
                )
                server.send_message(msg)
            
            self.logger.info("Notification email sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification email: {e}", exc_info=True)
            return False
    
    def send_maintenance_summary(self, results: Dict) -> None:
        """Send a summary of maintenance activities."""
        if not self.config["email"]["enabled"]:
            return
        
        try:
            subject = "GANDALFS Maintenance Summary"
            
            # Format the results as a readable message
            message = ["GANDALFS Maintenance Summary\n"]
            message.append(f"Status: {results.get('status', 'unknown')}")
            message.append(f"Timestamp: {results.get('timestamp')}\n")
            
            # Add system information
            if "system" in results:
                message.append("=== System Information ===")
                for key, value in results["system"].items():
                    message.append(f"{key}: {value}")
                message.append("")
            
            # Add task results
            if "tasks" in results:
                message.append("=== Task Results ===")
                for task_name, task_result in results["tasks"].items():
                    message.append(f"\n{task_name.upper()}:")
                    if isinstance(task_result, dict):
                        for k, v in task_result.items():
                            if k not in ["details"]:  # Skip large details in email
                                message.append(f"  {k}: {v}")
                    else:
                        message.append(f"  {task_result}")
            
            # Send the notification
            self.send_notification(
                subject,
                "\n".join(message),
                is_error=results.get("status") == "error"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send maintenance summary: {e}", exc_info=True)
    
    def _get_system_info(self) -> Dict:
        """Get basic system information."""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "username": os.getlogin(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _remove_old_files(self, directory: str, pattern: str, max_age_seconds: float, 
                         recursive: bool = False) -> int:
        """Remove files matching pattern older than max_age_seconds."""
        import glob
        import fnmatch
        
        now = time.time()
        removed_count = 0
        
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_path = os.path.join(root, file)
                        try:
                            file_age = now - os.path.getmtime(file_path)
                            if file_age > max_age_seconds:
                                os.remove(file_path)
                                removed_count += 1
                        except Exception as e:
                            self.logger.warning(f"Could not remove {file_path}: {e}")
        else:
            for file_path in glob.glob(os.path.join(directory, pattern)):
                try:
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        removed_count += 1
                except Exception as e:
                    self.logger.warning(f"Could not remove {file_path}: {e}")
        
        return removed_count
    
    def _cleanup_old_backups(self, backup_dir: str) -> None:
        """Remove old backup files, keeping only the most recent N backups."""
        try:
            max_backups = self.config["backup"]["max_backups"]
            
            # Get all backup files
            backup_files = []
            for file_name in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, file_name)
                if os.path.isfile(file_path):
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove oldest backups if we have more than max_backups
            for file_path, _ in backup_files[max_backups:]:
                try:
                    os.remove(file_path)
                    self.logger.info(f"Removed old backup: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Could not remove old backup {file_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during backup cleanup: {e}", exc_info=True)


def install_windows_task() -> bool:
    """Install a Windows Task Scheduler task to run maintenance regularly."""
    try:
        script_path = os.path.abspath(__file__)
        python_exe = sys.executable
        
        # Command to run the maintenance script
        cmd = f'"{python_exe}" "{script_path}" --run-maintenance'
        
        # Create a task that runs weekly
        schtasks_cmd = [
            'schtasks', '/Create',
            '/TN', 'OPRYXX_GANDALFS_Maintenance',
            '/TR', cmd,
            '/SC', 'WEEKLY',
            '/D', 'SUN',  # Run on Sundays
            '/ST', '03:00',  # At 3:00 AM
            '/RL', 'HIGHEST',  # Run with highest privileges
            '/F'  # Force creation (overwrite if exists)
        ]
        
        # Run the command
        result = subprocess.run(
            schtasks_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Scheduled task created successfully:")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating scheduled task: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Command-line interface for the maintenance script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GANDALFS Maintenance for OPRYXX')
    parser.add_argument('--run-maintenance', action='store_true', 
                       help='Run all maintenance tasks')
    parser.add_argument('--check-updates', action='store_true',
                       help='Check for updates only')
    parser.add_argument('--install-task', action='store_true',
                       help='Install Windows Task Scheduler task')
    parser.add_argument('--config', help='Path to config file')
    
    args = parser.parse_args()
    
    # Load config if specified
    config = CONFIG
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Error loading config file: {e}")
            return 1
    
    # Initialize maintenance manager
    maintenance = GandalfsMaintenance(config)
    
    # Run the requested action
    if args.install_task:
        if os.name != 'nt':
            print("Task scheduling is only supported on Windows")
            return 1
        return 0 if install_windows_task() else 1
    
    elif args.check_updates:
        result = maintenance.check_for_updates()
        print("Update check result:")
        print(json.dumps(result, indent=2))
        return 0 if result.get("status") != "error" else 1
    
    elif args.run_maintenance:
        success = maintenance.run_maintenance()
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
