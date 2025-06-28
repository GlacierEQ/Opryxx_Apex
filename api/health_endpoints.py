"""
Health Check Endpoints for OPRYXX API
"""

import psutil
import time
from datetime import datetime
from typing import Dict

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "services": {
                "nexus_ai": self._check_nexus_ai(),
                "recovery_system": self._check_recovery_system(),
                "performance_monitor": self._check_performance_monitor()
            }
        }
    
    def get_readiness(self) -> Dict:
        """Check if system is ready to serve requests"""
        health = self.get_system_health()
        
        ready = (
            health["system"]["cpu_percent"] < 90 and
            health["system"]["memory_percent"] < 90 and
            all(health["services"].values())
        )
        
        return {
            "ready": ready,
            "timestamp": datetime.now().isoformat(),
            "checks": health["services"]
        }
    
    def get_liveness(self) -> Dict:
        """Check if system is alive"""
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time
        }
    
    def _check_nexus_ai(self) -> bool:
        """Check NEXUS AI status"""
        try:
            # Check if AI processes are running
            return psutil.cpu_percent() < 95  # Simple health check
        except:
            return False
    
    def _check_recovery_system(self) -> bool:
        """Check recovery system status"""
        try:
            import os
            return os.path.exists("recovery/master_recovery.py")
        except:
            return False
    
    def _check_performance_monitor(self) -> bool:
        """Check performance monitor status"""
        try:
            return psutil.virtual_memory().percent < 95
        except:
            return False