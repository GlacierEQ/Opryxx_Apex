#!/usr/bin/env python3
"""
OPRYXX Launcher
A unified entry point for the OPRYXX system.
"""
import os
import sys
import subprocess
import signal
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('opryxx_launcher.log')
    ]
)
logger = logging.getLogger('opryxx_launcher')

class OPRYXXLauncher:
    """Main launcher for the OPRYXX system."""
    
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent.absolute()
        self.log_dir = self.base_dir / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            'api': {
                'enabled': True,
                'command': [sys.executable, '-m', 'uvicorn', 'ai_workbench.api.app:create_app', '--host', '0.0.0.0', '--port', '8000'],
                'cwd': str(self.base_dir),
                'env': os.environ.copy()
            },
            'monitor': {
                'enabled': True,
                'command': [sys.executable, '-m', 'ai_workbench.monitors.system_monitor'],
                'cwd': str(self.base_dir),
                'env': os.environ.copy()
            },
            'scheduler': {
                'enabled': True,
                'command': [sys.executable, '-m', 'ai_workbench.tasks.scheduler'],
                'cwd': str(self.base_dir),
                'env': os.environ.copy()
            }
        }
        
        # Update environment variables
        for service in self.config.values():
            if service['enabled']:
                service['env']['PYTHONPATH'] = str(self.base_dir)
                service['env']['LOG_DIR'] = str(self.log_dir)
    
    def start_service(self, service_name: str) -> bool:
        """Start a single service."""
        if service_name not in self.config:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        if not self.config[service_name]['enabled']:
            logger.info(f"Service {service_name} is disabled")
            return False
            
        if service_name in self.processes:
            logger.warning(f"Service {service_name} is already running")
            return True
            
        try:
            logger.info(f"Starting {service_name}...")
            
            # Create log file for this service
            log_file = open(self.log_dir / f"{service_name}.log", 'a')
            
            # Start the process
            process = subprocess.Popen(
                self.config[service_name]['command'],
                cwd=self.config[service_name]['cwd'],
                env=self.config[service_name]['env'],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.processes[service_name] = {
                'process': process,
                'log_file': log_file
            }
            
            logger.info(f"Started {service_name} with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a single service."""
        if service_name not in self.processes:
            logger.warning(f"Service {service_name} is not running")
            return True
            
        try:
            logger.info(f"Stopping {service_name}...")
            process_info = self.processes[service_name]
            process = process_info['process']
            log_file = process_info['log_file']
            
            # Send CTRL+C on Windows or SIGTERM on Unix
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)
            else:
                process.send_signal(signal.SIGTERM)
            
            # Wait for the process to terminate
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}...")
                process.kill()
            
            # Close the log file
            log_file.close()
            
            # Remove from running processes
            del self.processes[service_name]
            
            logger.info(f"Stopped {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {service_name}: {e}")
            return False
    
    def start_all(self) -> bool:
        """Start all enabled services."""
        success = True
        for service_name in self.config:
            if self.config[service_name]['enabled']:
                if not self.start_service(service_name):
                    success = False
        return success
    
    def stop_all(self) -> bool:
        """Stop all running services."""
        success = True
        for service_name in list(self.processes.keys()):
            if not self.stop_service(service_name):
                success = False
        return success
    
    def status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {}
        for service_name in self.config:
            is_running = service_name in self.processes
            pid = self.processes[service_name]['process'].pid if is_running else None
            
            status[service_name] = {
                'enabled': self.config[service_name]['enabled'],
                'running': is_running,
                'pid': pid
            }
        return status
    
    def monitor_services(self) -> None:
        """Monitor services and restart if they crash."""
        logger.info("Starting service monitor...")
        
        try:
            while True:
                # Check each service
                for service_name in list(self.processes.keys()):
                    process_info = self.processes[service_name]
                    process = process_info['process']
                    
                    # Check if process has terminated
                    if process.poll() is not None:
                        logger.warning(f"Service {service_name} has terminated with code {process.returncode}")
                        
                        # Close old log file
                        process_info['log_file'].close()
                        
                        # Restart the service
                        if self.config[service_name]['enabled']:
                            logger.info(f"Restarting {service_name}...")
                            del self.processes[service_name]
                            self.start_service(service_name)
                
                # Sleep for a bit before checking again
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Service monitor stopped")
            self.stop_all()

def main():
    """Main entry point for the launcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OPRYXX System Launcher')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start services')
    start_parser.add_argument('services', nargs='*', help='Services to start (default: all)')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop services')
    stop_parser.add_argument('services', nargs='*', help='Services to stop (default: all)')
    
    # Status command
    subparsers.add_parser('status', help='Show service status')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the full system with monitoring')
    run_parser.add_argument('--no-monitor', action='store_true', help='Disable service monitoring')
    
    args = parser.parse_args()
    
    launcher = OPRYXXLauncher()
    
    if args.command == 'start':
        if args.services:
            for service in args.services:
                launcher.start_service(service)
        else:
            launcher.start_all()
            
    elif args.command == 'stop':
        if args.services:
            for service in args.services:
                launcher.stop_service(service)
        else:
            launcher.stop_all()
            
    elif args.command == 'status':
        status = launcher.status()
        for service, info in status.items():
            state = "RUNNING" if info['running'] else "STOPPED"
            enabled = "(enabled)" if info['enabled'] else "(disabled)"
            pid = f" [PID: {info['pid']}]" if info['pid'] else ""
            print(f"{service}: {state} {enabled}{pid}")
            
    elif args.command == 'run':
        # Start all services
        if launcher.start_all():
            print("OPRYXX system started successfully")
            print("Press Ctrl+C to stop")
            
            # Start monitoring if enabled
            if not args.no_monitor:
                launcher.monitor_services()
            else:
                try:
                    # Keep the main thread alive
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nShutting down...")
                    launcher.stop_all()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
