"""
AI Workbench - Main Entry Point

This module serves as the main entry point for the AI Workbench application.
It initializes all components and starts the monitoring service.
"""

import sys
import signal
import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import configuration and services
from .config import config, load_config
from .services.workbench_service import AIWorkbenchService
from .utils.logging_utils import setup_logger, log_system_info

# Set up logger
logger = logging.getLogger(__name__)

class AIWorkbench:
    """Main AI Workbench application class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AI Workbench
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Set up logging
        self._setup_logging()
        
        # Initialize services
        self.workbench_service: Optional[AIWorkbenchService] = None
        
        # Set up signal handlers
        self._setup_signal_handlers()
        
        logger.info(f"{config.app.name} v{config.app.version} initialized")
    
    def _setup_logging(self) -> None:
        """Set up logging configuration"""
        # Configure root logger
        setup_logger(
            name='ai_workbench',
            log_level=self.config.app.log_level,
            log_file=self.config.app.log_file,
            console=True
        )
        
        # Log system information
        log_system_info(logger)
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signals"""
        logger.info("Shutdown signal received. Stopping services...")
        self.stop()
        sys.exit(0)
    
    def start(self) -> None:
        """Start the AI Workbench"""
        try:
            logger.info("Starting AI Workbench...")
            
            # Initialize and start the workbench service
            self.workbench_service = AIWorkbenchService(
                monitoring_interval=self.config.monitoring.interval
            )
            
            if not self.workbench_service.start_monitoring():
                logger.error("Failed to start monitoring service")
                return
            
            logger.info("AI Workbench started successfully")
            
            # Keep the main thread alive
            if self.config.app.debug:
                logger.info("Debug mode: Press Ctrl+C to stop")
                signal.pause()
            else:
                while True:
                    signal.pause()
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
            self.stop()
        except Exception as e:
            logger.critical(f"Fatal error: {e}", exc_info=True)
            self.stop()
    
    def stop(self) -> None:
        """Stop the AI Workbench"""
        logger.info("Stopping AI Workbench...")
        
        # Stop the workbench service if it's running
        if self.workbench_service:
            self.workbench_service.stop_monitoring()
        
        logger.info("AI Workbench stopped")

def parse_args(args: List[str]) -> argparse.Namespace:
    """
    Parse command line arguments
    
    Args:
        args: Command line arguments
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="AI Workbench - Advanced system monitoring and optimization"
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f"%(prog)s {config.app.version}"
    )
    
    return parser.parse_args(args)

def main() -> int:
    """
    Main entry point for the AI Workbench
    
    Returns:
        int: Exit code
    """
    # Parse command line arguments
    args = parse_args(sys.argv[1:])
    
    try:
        # Create and start the AI Workbench
        workbench = AIWorkbench(config_path=args.config)
        workbench.start()
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
