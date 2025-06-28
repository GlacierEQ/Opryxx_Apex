"""
Example usage of the AdvancedSystemMonitor class.

This script demonstrates how to use the system monitor to collect metrics,
detect anomalies, and handle the results.
"""

import os
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path to allow importing the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitors.system_monitor import AdvancedSystemMonitor

def setup_logging(log_level=logging.INFO, log_file=None):
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_file: Optional path to log file (default: None)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[]
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

def main():
    """Main function to demonstrate system monitor usage."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='System Monitor Example')
    parser.add_argument('--interval', type=int, default=5,
                        help='Monitoring interval in seconds (default: 5)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Total monitoring duration in seconds (default: 60)')
    parser.add_argument('--db-path', type=str, default='system_metrics.db',
                        help='Path to SQLite database file')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Path to log file (default: None)')
    args = parser.parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level=log_level, log_file=args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting System Monitor Example")
    logger.info(f"Monitoring interval: {args.interval}s")
    logger.info(f"Total duration: {args.duration}s")
    logger.info(f"Database path: {os.path.abspath(args.db_path)}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(args.db_path)), exist_ok=True)
    
    try:
        # Initialize system monitor
        monitor = AdvancedSystemMonitor(db_path=args.db_path)
        logger.info("System monitor initialized successfully")
        
        # Calculate number of iterations
        num_iterations = args.duration // args.interval
        
        logger.info(f"Starting monitoring for {num_iterations} iterations...")
        
        # Main monitoring loop
        for i in range(num_iterations):
            iteration = i + 1
            logger.info(f"\n--- Iteration {iteration}/{num_iterations} ---")
            
            # Collect metrics
            try:
                metrics = monitor.collect_comprehensive_metrics()
                logger.info(f"Collected metrics at {metrics.get('timestamp')}")
                
                # Get and log a summary
                summary = monitor.get_metrics_summary()
                logger.info("\nSystem Summary:")
                logger.info(f"  CPU: {summary['cpu']['usage_percent']:.1f}%")
                logger.info(f"  Memory: {summary['memory']['percent']:.1f}% ({summary['memory']['available_gb']:.1f} GB available)")
                logger.info(f"  Disk: {len(summary['disk']['devices'])} devices")
                logger.info(f"  Processes: {summary['processes']['total']} running")
                
                # Log top CPU process
                if summary['processes']['top_cpu']:
                    top_proc = summary['processes']['top_cpu'][0]
                    logger.info(f"  Top Process: {top_proc['name']} (PID: {top_proc['pid']}, CPU: {top_proc['cpu_percent']:.1f}%)")
                
                # Check for anomalies
                anomalies = monitor.detect_anomalies(metrics)
                if anomalies:
                    logger.warning(f"\nDetected {len(anomalies)} anomalies:")
                    for anomaly in anomalies:
                        logger.warning(f"  [{anomaly['severity'].upper()}] {anomaly['anomaly_type']}: {anomaly['details']}")
                
            except Exception as e:
                logger.error(f"Error during monitoring iteration: {e}", exc_info=True)
            
            # Wait for next iteration
            if i < num_iterations - 1:  # Don't sleep on last iteration
                time.sleep(args.interval)
        
        logger.info("\nMonitoring completed successfully")
        
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        # Ensure resources are cleaned up
        if 'monitor' in locals():
            monitor.cleanup()
        logger.info("System monitor example finished")
    
    return 0

if __name__ == "__main__":
    exit(main())
