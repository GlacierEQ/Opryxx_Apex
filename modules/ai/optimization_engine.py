"""
Optimized AI Engine Module
"""

import psutil
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.base import BaseModule, ModuleResult
from core.logger import get_logger

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_usage: float = 0.0
    timestamp: float = 0.0

@dataclass
class OptimizationAction:
    action_type: str
    priority: int
    description: str
    estimated_impact: float

class AIOptimizationModule(BaseModule):
    """AI-powered system optimization"""
    
    def __init__(self):
        super().__init__("ai_optimization")
        self.logger = get_logger("ai_optimization")
        self.metrics_history = []
        self.baseline_performance = None
        
    def initialize(self) -> ModuleResult:
        """Initialize AI optimization module"""
        try:
            self.logger.info("Initializing AI optimization module")
            self.baseline_performance = self._collect_metrics()
            return ModuleResult(True, "AI optimization module initialized")
        except Exception as e:
            return ModuleResult(False, f"Initialization failed: {e}", error=e)
    
    def execute(self, **kwargs) -> ModuleResult:
        """Execute AI optimization"""
        try:
            # Collect current metrics
            current_metrics = self._collect_metrics()
            self.metrics_history.append(current_metrics)
            
            # Keep only last 100 metrics
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            # Predict performance
            performance_score = self._predict_performance(current_metrics)
            
            # Generate optimizations if needed
            optimizations = []
            if performance_score < 70:
                optimizations = self._generate_optimizations(current_metrics)
                
                # Execute high-priority optimizations
                executed = []
                for opt in optimizations[:3]:  # Top 3 optimizations
                    if opt.priority <= 2 and self._execute_optimization(opt):
                        executed.append(opt.description)
                
                return ModuleResult(
                    success=len(executed) > 0,
                    message=f"Executed {len(executed)} optimizations",
                    data={
                        'performance_score': performance_score,
                        'executed': executed,
                        'metrics': current_metrics.__dict__
                    }
                )
            
            return ModuleResult(
                success=True,
                message=f"System performing well (score: {performance_score:.1f})",
                data={'performance_score': performance_score, 'metrics': current_metrics.__dict__}
            )
            
        except Exception as e:
            return ModuleResult(False, f"Optimization failed: {e}", error=e)
    
    def cleanup(self) -> ModuleResult:
        """Cleanup resources"""
        self.metrics_history.clear()
        return ModuleResult(True, "Cleanup completed")
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            return SystemMetrics(
                cpu_usage=cpu,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                timestamp=psutil.time.time()
            )
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return SystemMetrics(0, 0, 0)
    
    def _predict_performance(self, metrics: SystemMetrics) -> float:
        """Predict system performance score"""
        # Simple heuristic model
        score = 100 - (
            metrics.cpu_usage * 0.3 +
            metrics.memory_usage * 0.3 +
            metrics.disk_usage * 0.2 +
            (100 - metrics.gpu_usage) * 0.2
        )
        return max(0, min(100, score))
    
    def _generate_optimizations(self, metrics: SystemMetrics) -> List[OptimizationAction]:
        """Generate optimization recommendations"""
        actions = []
        
        if metrics.cpu_usage > 80:
            actions.append(OptimizationAction(
                action_type="cpu_optimization",
                priority=1,
                description="Optimize CPU-intensive processes",
                estimated_impact=15.0
            ))
        
        if metrics.memory_usage > 75:
            actions.append(OptimizationAction(
                action_type="memory_cleanup",
                priority=2,
                description="Clear memory caches",
                estimated_impact=20.0
            ))
        
        if metrics.disk_usage > 85:
            actions.append(OptimizationAction(
                action_type="disk_cleanup",
                priority=2,
                description="Clean temporary files",
                estimated_impact=10.0
            ))
        
        # Sort by priority and impact
        actions.sort(key=lambda x: (x.priority, -x.estimated_impact))
        return actions
    
    def _execute_optimization(self, action: OptimizationAction) -> bool:
        """Execute optimization action"""
        try:
            if action.action_type == "cpu_optimization":
                return self._optimize_cpu()
            elif action.action_type == "memory_cleanup":
                return self._cleanup_memory()
            elif action.action_type == "disk_cleanup":
                return self._cleanup_disk()
            return False
        except Exception as e:
            self.logger.error(f"Optimization execution failed: {e}")
            return False
    
    def _optimize_cpu(self) -> bool:
        """Optimize CPU performance"""
        try:
            import subprocess
            # Set high performance power plan
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], 
                         check=True, capture_output=True)
            return True
        except:
            return False
    
    def _cleanup_memory(self) -> bool:
        """Clean up memory"""
        try:
            import gc
            import subprocess
            gc.collect()
            subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                         capture_output=True)
            return True
        except:
            return False
    
    def _cleanup_disk(self) -> bool:
        """Clean up disk space"""
        try:
            import subprocess
            import os
            
            # Clear temp files
            temp_dirs = [os.environ.get('TEMP', ''), 'C:\\Windows\\Temp']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    subprocess.run(['del', '/q', '/s', f'{temp_dir}\\*'], 
                                 shell=True, capture_output=True)
            return True
        except:
            return False