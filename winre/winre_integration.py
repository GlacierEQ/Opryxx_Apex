"""
WinRE Integration for Opryxx

This module provides integration between the EnhancedWinREAgent and the Opryxx orchestrator.
"""

import os
import shutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import the enhanced WinRE agent
from winre_agent_enhanced import EnhancedWinREAgent

class WinREIntegration:
    """Integration layer between EnhancedWinREAgent and Opryxx."""
    
    def __init__(self, orchestrator, config: Optional[Dict[str, Any]] = None):
        """Initialize the WinRE integration.
        
        Args:
            orchestrator: Reference to the Opryxx orchestrator
            config: Configuration dictionary
        """
        self.orchestrator = orchestrator
        self.config = config or {}
        self.logger = self._setup_logging()
        self.winre_agent = None
        
        # Set up temporary directory (default to E: drive if available)
        self.temp_dir = self.config.get('temp_dir', 'E:\\Temp\\WinRE_Recovery')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize the WinRE agent
        self._init_winre_agent()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the integration."""
        logger = logging.getLogger('WinREIntegration')
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
    
    def _log(self, message: str, level: str = 'info') -> None:
        """Log a message with the specified level."""
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message)
        
        # Also pass to orchestrator's log callback if available
        if hasattr(self.orchestrator, 'log_callback'):
            self.orchestrator.log_callback(f"[WinRE] {message}")
    
    def _init_winre_agent(self) -> None:
        """Initialize the WinRE agent with proper configuration."""
        try:
            self._log("Initializing EnhancedWinREAgent...")
            self.winre_agent = EnhancedWinREAgent(
                log_callback=self._log,
                temp_dir=self.temp_dir
            )
            self._log("EnhancedWinREAgent initialized successfully")
        except Exception as e:
            self._log(f"Failed to initialize EnhancedWinREAgent: {str(e)}", 'error')
            raise
    
    def check_winre_health(self) -> Dict[str, Any]:
        """Check the health of the WinRE environment.
        
        Returns:
            Dict containing health check results
        """
        self._log("Performing WinRE health check...")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'details': {}
        }
        
        try:
            # Check basic WinRE status
            status = self.winre_agent.check_winre_status()
            result['status'] = 'healthy' if status else 'unhealthy'
            result['details']['basic_status'] = status
            
            # Verify integrity
            integrity = self.winre_agent.verify_integrity()
            result['details']['integrity_check'] = integrity
            
            # Update overall status based on checks
            if status and integrity:
                result['status'] = 'healthy'
            else:
                result['status'] = 'unhealthy'
                
            self._log(f"WinRE health check completed: {result['status']}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self._log(f"Error during WinRE health check: {str(e)}", 'error')
        
        return result
    
    def repair_winre(self) -> Dict[str, Any]:
        """Repair the WinRE environment.
        
        Returns:
            Dict containing repair results
        """
        self._log("Starting WinRE repair...")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'details': {}
        }
        
        try:
            # First check current status
            health = self.check_winre_health()
            result['initial_health'] = health
            
            if health['status'] == 'healthy':
                self._log("WinRE appears healthy, no repair needed")
                result['success'] = True
                result['details']['message'] = 'No repair needed - WinRE is healthy'
                return result
            
            # Perform repair
            self._log("Attempting to repair WinRE...")
            repair_success = self.winre_agent.repair_winre()
            
            # Verify repair
            if repair_success:
                health_after = self.check_winre_health()
                result['final_health'] = health_after
                result['success'] = health_after['status'] == 'healthy'
                
                if result['success']:
                    self._log("WinRE repair completed successfully")
                else:
                    self._log("WinRE repair completed but health check failed", 'warning')
            else:
                self._log("WinRE repair failed", 'error')
            
        except Exception as e:
            result['error'] = str(e)
            self._log(f"Error during WinRE repair: {str(e)}", 'error')
        
        return result
    
    def create_recovery_media(self, target_path: Optional[str] = None) -> Dict[str, Any]:
        """Create WinRE recovery media.
        
        Args:
            target_path: Optional target path for recovery media
            
        Returns:
            Dict containing recovery media creation results
        """
        target_path = target_path or os.path.join(self.temp_dir, 'RecoveryMedia')
        self._log(f"Creating recovery media at {target_path}...")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'target_path': target_path,
            'details': {}
        }
        
        try:
            # Ensure WinRE is healthy first
            health = self.check_winre_health()
            if health['status'] != 'healthy':
                self._log("WinRE is not healthy, attempting repair...", 'warning')
                repair_result = self.repair_winre()
                if not repair_result['success']:
                    raise RuntimeError("Failed to repair WinRE before creating recovery media")
            
            # Create recovery media
            os.makedirs(target_path, exist_ok=True)
            success = self.winre_agent.create_recovery_media(target_path)
            
            if success:
                result['success'] = True
                result['details']['message'] = 'Recovery media created successfully'
                self._log(f"Recovery media created at {target_path}")
            else:
                result['details']['message'] = 'Failed to create recovery media'
                self._log("Failed to create recovery media", 'error')
                
        except Exception as e:
            result['error'] = str(e)
            self._log(f"Error creating recovery media: {str(e)}", 'error')
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of WinRE integration.
        
        Returns:
            Dict containing status information
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'winre_initialized': self.winre_agent is not None,
            'temp_dir': self.temp_dir,
            'disk_space': self._get_disk_space()
        }
    
    def _get_disk_space(self) -> Dict[str, Any]:
        """Get disk space information for the temp directory."""
        try:
            total, used, free = shutil.disk_usage(os.path.dirname(self.temp_dir))
            return {
                'total_gb': round(total / (1024 ** 3), 2),
                'used_gb': round(used / (1024 ** 3), 2),
                'free_gb': round(free / (1024 ** 3), 2)
            }
        except Exception as e:
            self._log(f"Error getting disk space: {str(e)}", 'error')
            return {'error': str(e)}
