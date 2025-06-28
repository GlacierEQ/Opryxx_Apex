"""
AI Workbench Service

This module implements the core functionality of the AI Workbench,
including system monitoring, health checks, and optimizations.
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable

# Import database service and models
from .database_service import WorkbenchDatabaseService
from ..models.workbench_models import SystemMetric, SystemAction, FailurePrediction, OptimizationRule
from ..utils import system_utils
from ..config import config

# Set up logging
logger = logging.getLogger(__name__)


class AIWorkbenchService:
    """
    Main service class for the AI Workbench
    
    Handles system monitoring, health checks, and optimizations.
    """
    
    def __init__(self, monitoring_interval: int = 300):
        """
        Initialize the AI Workbench service
        
        Args:
            monitoring_interval: Interval in seconds between monitoring cycles
        """
        self.monitoring_interval = monitoring_interval
        self._running = False
        self._monitor_thread = None
        self._db_service = WorkbenchDatabaseService()
        self._callbacks = {
            'on_metric': [],
            'on_action': [],
            'on_prediction': [],
            'on_error': []
        }
        
        logger.info(f"AI Workbench Service initialized with {monitoring_interval}s monitoring interval")
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Register a callback for a specific event
        
        Args:
            event_type: Type of event to register for
                        ('on_metric', 'on_action', 'on_prediction', 'on_error')
            callback: Callback function to register
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        if event_type not in self._callbacks:
            logger.error(f"Unknown event type: {event_type}")
            return False
            
        self._callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for {event_type}")
        return True
    
    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """
        Trigger all registered callbacks for an event
        
        Args:
            event_type: Type of event to trigger
            data: Data to pass to callbacks
        """
        if event_type not in self._callbacks:
            return
            
        for callback in self._callbacks[event_type]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in {event_type} callback: {e}", exc_info=True)
    
    def start_monitoring(self) -> bool:
        """
        Start the monitoring service
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        if self._running:
            logger.warning("Monitoring is already running")
            return False
            
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="AIWorkbenchMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Started AI Workbench monitoring")
        return True
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring service"""
        if not self._running:
            return
            
        self._running = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        logger.info("Stopped AI Workbench monitoring")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        try:
            while self._running:
                cycle_start = time.time()
                
                try:
                    # Collect and process system metrics
                    metrics = self._collect_metrics()
                    self._process_metrics(metrics)
                    
                    # Run health checks
                    self._run_health_checks(metrics)
                    
                    # Run optimizations if enabled
                    if config.optimization.auto_optimize:
                        self._run_optimizations(metrics)
                    
                    # Run predictive analysis if enabled
                    if config.predictive_analysis.enabled:
                        self._run_predictive_analysis(metrics)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring cycle: {e}", exc_info=True)
                    self._trigger_callbacks('on_error', {
                        'timestamp': datetime.utcnow(),
                        'error': str(e),
                        'context': 'monitoring_cycle'
                    })
                
                # Calculate sleep time to maintain the monitoring interval
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.monitoring_interval - cycle_time)
                
                # Sleep in small chunks to allow for graceful shutdown
                for _ in range(int(sleep_time)):
                    if not self._running:
                        break
                    time.sleep(1)
                
        except Exception as e:
            logger.critical(f"Fatal error in monitoring loop: {e}", exc_info=True)
            self._running = False
            raise
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collect system metrics
        
        Returns:
            Dict containing collected metrics
        """
        logger.debug("Collecting system metrics")
        
        try:
            # Get system metrics
            metrics = system_utils.get_system_metrics()
            
            # Save to database
            metric = SystemMetric(**metrics)
            self._db_service.save_metric(metric)
            
            # Trigger callbacks
            self._trigger_callbacks('on_metric', metric.to_dict())
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}", exc_info=True)
            self._trigger_callbacks('on_error', {
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'context': 'collect_metrics'
            })
            raise
    
    def _process_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Process collected metrics and trigger appropriate actions
        
        Args:
            metrics: Dictionary of collected metrics
        """
        logger.debug("Processing metrics")
        
        try:
            # Check for critical conditions
            if metrics.get('cpu_usage', 0) > config.monitoring.cpu_warning:
                self._handle_high_cpu_usage(metrics)
                
            if metrics.get('memory_usage', 0) > config.monitoring.memory_warning:
                self._handle_high_memory_usage(metrics)
                
            # Add more metric processing as needed
            
        except Exception as e:
            logger.error(f"Error processing metrics: {e}", exc_info=True)
            self._trigger_callbacks('on_error', {
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'context': 'process_metrics'
            })
    
    def _run_health_checks(self, metrics: Dict[str, Any]) -> None:
        """
        Run system health checks
        
        Args:
            metrics: Current system metrics
        """
        logger.debug("Running health checks")
        
        try:
            # Example: Check disk space
            for disk in metrics.get('disks', []):
                if disk.get('percent_used', 0) > config.monitoring.disk_warning:
                    self._handle_low_disk_space(disk)
            
            # Add more health checks as needed
            
        except Exception as e:
            logger.error(f"Error in health checks: {e}", exc_info=True)
            self._trigger_callbacks('on_error', {
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'context': 'health_checks'
            })
    
    def _run_optimizations(self, metrics: Dict[str, Any]) -> None:
        """
        Run system optimizations based on current metrics
        
        Args:
            metrics: Current system metrics
        """
        logger.debug("Running optimizations")
        
        try:
            # Get active optimization rules
            rules = self._db_service.get_active_optimization_rules()
            
            for rule in rules:
                # Check if rule conditions are met
                if self._evaluate_rule_conditions(rule, metrics):
                    self._apply_optimization_rule(rule, metrics)
                    
        except Exception as e:
            logger.error(f"Error in optimizations: {e}", exc_info=True)
            self._trigger_callbacks('on_error', {
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'context': 'run_optimizations'
            })
    
    def _run_predictive_analysis(self, metrics: Dict[str, Any]) -> None:
        """
        Run predictive analysis on system metrics
        
        Args:
            metrics: Current system metrics
        """
        logger.debug("Running predictive analysis")
        
        try:
            # Get historical metrics for analysis
            history = self._db_service.get_metrics_history(hours=24)
            
            # Example: Predict disk failure
            self._predict_disk_failures(metrics, history)
            
            # Add more predictive analysis as needed
            
        except Exception as e:
            logger.error(f"Error in predictive analysis: {e}", exc_info=True)
            self._trigger_callbacks('on_error', {
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'context': 'predictive_analysis'
            })
    
    def _evaluate_rule_conditions(self, rule: OptimizationRule, metrics: Dict[str, Any]) -> bool:
        """
        Evaluate if optimization rule conditions are met
        
        Args:
            rule: Optimization rule to evaluate
            metrics: Current system metrics
            
        Returns:
            bool: True if conditions are met, False otherwise
        """
        # TODO: Implement rule condition evaluation
        return False
    
    def _apply_optimization_rule(self, rule: OptimizationRule, metrics: Dict[str, Any]) -> None:
        """
        Apply an optimization rule
        
        Args:
            rule: Optimization rule to apply
            metrics: Current system metrics
        """
        # TODO: Implement rule application
        pass
    
    def _predict_disk_failures(self, current_metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> None:
        """
        Predict potential disk failures based on metrics
        
        Args:
            current_metrics: Current system metrics
            history: List of historical metrics
        """
        # TODO: Implement disk failure prediction
        pass
    
    def _handle_high_cpu_usage(self, metrics: Dict[str, Any]) -> None:
        """Handle high CPU usage"""
        logger.warning(f"High CPU usage detected: {metrics.get('cpu_usage')}%")
        
        # Example action: Log the top CPU-consuming processes
        top_processes = sorted(
            metrics.get('processes', []),
            key=lambda p: p.get('cpu_percent', 0),
            reverse=True
        )[:5]
        
        for proc in top_processes:
            logger.info(f"Process {proc.get('name')} (PID: {proc.get('pid')}): {proc.get('cpu_percent')}% CPU")
        
        # Record the action
        action = SystemAction(
            metric_id=metrics.get('id'),
            action_type='high_cpu_usage',
            description=f"High CPU usage detected: {metrics.get('cpu_usage')}%",
            status='completed',
            success=True,
            details={
                'top_processes': [
                    {
                        'pid': p.get('pid'),
                        'name': p.get('name'),
                        'cpu_percent': p.get('cpu_percent')
                    } for p in top_processes
                ]
            }
        )
        self._db_service.record_action(action)
        
        # Trigger callbacks
        self._trigger_callbacks('on_action', action.to_dict())
    
    def _handle_high_memory_usage(self, metrics: Dict[str, Any]) -> None:
        """Handle high memory usage"""
        logger.warning(f"High memory usage detected: {metrics.get('memory_usage')}%")
        
        # Example action: Log the top memory-consuming processes
        top_processes = sorted(
            metrics.get('processes', []),
            key=lambda p: p.get('memory_percent', 0),
            reverse=True
        )[:5]
        
        for proc in top_processes:
            logger.info(f"Process {proc.get('name')} (PID: {proc.get('pid')}): {proc.get('memory_percent')}% memory")
        
        # Record the action
        action = SystemAction(
            metric_id=metrics.get('id'),
            action_type='high_memory_usage',
            description=f"High memory usage detected: {metrics.get('memory_usage')}%",
            status='completed',
            success=True,
            details={
                'top_processes': [
                    {
                        'pid': p.get('pid'),
                        'name': p.get('name'),
                        'memory_percent': p.get('memory_percent')
                    } for p in top_processes
                ]
            }
        )
        self._db_service.record_action(action)
        
        # Trigger callbacks
        self._trigger_callbacks('on_action', action.to_dict())
    
    def _handle_low_disk_space(self, disk: Dict[str, Any]) -> None:
        """Handle low disk space"""
        logger.warning(f"Low disk space on {disk.get('device')}: {disk.get('percent_used')}% used")
        
        # Record the action
        action = SystemAction(
            action_type='low_disk_space',
            description=f"Low disk space on {disk.get('device')}: {disk.get('percent_used')}% used",
            status='completed',
            success=True,
            details=disk
        )
        self._db_service.record_action(action)
        
        # Trigger callbacks
        self._trigger_callbacks('on_action', action.to_dict())
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.stop_monitoring()
        self._db_service.close()
        logger.info("AI Workbench Service cleaned up")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
