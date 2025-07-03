#!/usr/bin/env python3
"""
OPRYXX AI OPTIMIZATION ENGINE
Advanced AI-powered system optimization with GPU/NPU acceleration
"""

import os
import sys
import time
import json
import threading
import subprocess
import psutil
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_usage: float
    temperature: float
    power_usage: float
    network_io: Tuple[int, int]
    timestamp: datetime

@dataclass
class OptimizationAction:
    action_type: str
    priority: int
    description: str
    estimated_impact: float
    execution_time: float

class HardwareDetector:
    """Advanced hardware detection and management"""
    
    def __init__(self):
        self.gpu_info = {}
        self.npu_info = {}
        self.cpu_info = {}
        self.detect_hardware()
    
    def detect_hardware(self):
        """Detect all available hardware acceleration"""
        self.detect_gpu()
        self.detect_npu()
        self.detect_cpu_features()
    
    def detect_gpu(self):
        """Detect GPU capabilities"""
        try:
            # NVIDIA GPU detection
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,utilization.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for i, line in enumerate(result.stdout.strip().split('\n')):
                    if line.strip():
                        parts = line.split(', ')
                        self.gpu_info[f'nvidia_{i}'] = {
                            'name': parts[0],
                            'memory_total': int(parts[1]),
                            'type': 'NVIDIA',
                            'compute_capability': self.get_nvidia_compute_capability(i)
                        }
        except:
            pass
        
        try:
            # AMD GPU detection
            result = subprocess.run(['rocm-smi', '--showproductname', '--showmeminfo'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.gpu_info['amd_0'] = {
                    'name': 'AMD GPU',
                    'type': 'AMD',
                    'rocm_support': True
                }
        except:
            pass
        
        try:
            # Intel GPU detection
            result = subprocess.run(['intel_gpu_top', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                self.gpu_info['intel_0'] = {
                    'name': 'Intel GPU',
                    'type': 'Intel',
                    'opencl_support': True
                }
        except:
            pass
    
    def detect_npu(self):
        """Detect NPU/AI accelerators"""
        try:
            # Intel NPU detection
            if os.path.exists('/sys/class/intel_npu'):
                self.npu_info['intel_npu'] = {
                    'name': 'Intel NPU',
                    'type': 'Intel',
                    'ai_acceleration': True
                }
        except:
            pass
        
        try:
            # Qualcomm NPU detection
            result = subprocess.run(['qnn-platform-validator'], capture_output=True, text=True)
            if result.returncode == 0:
                self.npu_info['qualcomm_npu'] = {
                    'name': 'Qualcomm NPU',
                    'type': 'Qualcomm',
                    'ai_acceleration': True
                }
        except:
            pass
    
    def detect_cpu_features(self):
        """Detect CPU AI/ML features"""
        try:
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            self.cpu_info = {
                'name': info.get('brand_raw', 'Unknown'),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'avx2': 'avx2' in info.get('flags', []),
                'avx512': 'avx512f' in info.get('flags', []),
                'ai_extensions': self.detect_ai_extensions(info)
            }
        except:
            self.cpu_info = {
                'name': 'Unknown CPU',
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'avx2': False,
                'avx512': False,
                'ai_extensions': []
            }
    
    def detect_ai_extensions(self, cpu_info):
        """Detect AI-specific CPU extensions"""
        ai_extensions = []
        flags = cpu_info.get('flags', [])
        
        if 'avx512_vnni' in flags:
            ai_extensions.append('AVX512-VNNI')
        if 'avx512_bf16' in flags:
            ai_extensions.append('AVX512-BF16')
        if 'amx_tile' in flags:
            ai_extensions.append('AMX')
        
        return ai_extensions
    
    def get_nvidia_compute_capability(self, gpu_id):
        """Get NVIDIA GPU compute capability"""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=compute_cap', 
                                   '--format=csv,noheader,nounits', f'--id={gpu_id}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "Unknown"
    
    def get_best_compute_device(self):
        """Select best available compute device"""
        if self.npu_info:
            return ('NPU', list(self.npu_info.keys())[0])
        elif self.gpu_info:
            # Prefer NVIDIA for compute
            nvidia_gpus = [k for k in self.gpu_info.keys() if 'nvidia' in k]
            if nvidia_gpus:
                return ('GPU', nvidia_gpus[0])
            else:
                return ('GPU', list(self.gpu_info.keys())[0])
        else:
            return ('CPU', 'cpu_0')

class AIOptimizationEngine:
    """AI-powered system optimization engine"""
    
    def __init__(self):
        self.hardware = HardwareDetector()
        self.metrics_history = []
        self.optimization_models = {}
        self.running = False
        self.performance_baseline = None
        self.load_models()
    
    def load_models(self):
        """Load or initialize AI models"""
        # Simple ML models for optimization
        self.optimization_models = {
            'performance_predictor': self.create_performance_model(),
            'anomaly_detector': self.create_anomaly_model(),
            'resource_optimizer': self.create_resource_model()
        }
    
    def create_performance_model(self):
        """Create performance prediction model"""
        return {
            'type': 'linear_regression',
            'weights': np.random.randn(10),
            'bias': 0.0,
            'trained': False
        }
    
    def create_anomaly_model(self):
        """Create anomaly detection model"""
        return {
            'type': 'isolation_forest',
            'threshold': 0.1,
            'baseline_metrics': None,
            'trained': False
        }
    
    def create_resource_model(self):
        """Create resource optimization model"""
        return {
            'type': 'reinforcement_learning',
            'q_table': {},
            'learning_rate': 0.1,
            'epsilon': 0.1,
            'trained': False
        }
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        try:
            # Basic system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = (net_io.bytes_sent, net_io.bytes_recv)
            
            # GPU usage (if available)
            gpu_usage = self.get_gpu_usage()
            
            # Temperature (if available)
            temperature = self.get_system_temperature()
            
            # Power usage estimation
            power_usage = self.estimate_power_usage(cpu_usage, gpu_usage)
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                gpu_usage=gpu_usage,
                temperature=temperature,
                power_usage=power_usage,
                network_io=network_io,
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return None
    
    def get_gpu_usage(self) -> float:
        """Get GPU utilization"""
        try:
            if 'nvidia_0' in self.hardware.gpu_info:
                result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', 
                                       '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return float(result.stdout.strip())
        except:
            pass
        return 0.0
    
    def get_system_temperature(self) -> float:
        """Get system temperature"""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get CPU temperature
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            return entries[0].current if entries else 0.0
        except:
            pass
        return 0.0
    
    def estimate_power_usage(self, cpu_usage: float, gpu_usage: float) -> float:
        """Estimate system power usage"""
        # Simple power estimation model
        base_power = 50  # Base system power in watts
        cpu_power = (cpu_usage / 100) * 65  # CPU power scaling
        gpu_power = (gpu_usage / 100) * 150  # GPU power scaling
        
        return base_power + cpu_power + gpu_power
    
    def predict_performance(self, metrics: SystemMetrics) -> float:
        """Predict system performance score"""
        model = self.optimization_models['performance_predictor']
        
        # Feature vector
        features = np.array([
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.disk_usage,
            metrics.gpu_usage,
            metrics.temperature,
            metrics.power_usage,
            metrics.network_io[0] / 1e6,  # Normalize network I/O
            metrics.network_io[1] / 1e6,
            len(psutil.pids()),  # Process count
            psutil.boot_time()   # Uptime factor
        ])
        
        if model['trained']:
            # Simple linear model prediction
            score = np.dot(features, model['weights']) + model['bias']
            return max(0, min(100, score))
        else:
            # Heuristic scoring
            score = 100 - (metrics.cpu_usage * 0.3 + 
                          metrics.memory_usage * 0.3 + 
                          metrics.disk_usage * 0.2 + 
                          metrics.temperature * 0.2)
            return max(0, score)
    
    def detect_anomalies(self, metrics: SystemMetrics) -> List[str]:
        """Detect system anomalies"""
        anomalies = []
        
        # Simple threshold-based anomaly detection
        if metrics.cpu_usage > 90:
            anomalies.append("High CPU usage detected")
        
        if metrics.memory_usage > 85:
            anomalies.append("High memory usage detected")
        
        if metrics.temperature > 80:
            anomalies.append("High system temperature detected")
        
        if metrics.disk_usage > 90:
            anomalies.append("Low disk space detected")
        
        # Pattern-based anomalies
        if len(self.metrics_history) > 10:
            recent_cpu = [m.cpu_usage for m in self.metrics_history[-10:]]
            if np.std(recent_cpu) > 30:  # High CPU variance
                anomalies.append("Unstable CPU performance detected")
        
        return anomalies
    
    def generate_optimizations(self, metrics: SystemMetrics) -> List[OptimizationAction]:
        """Generate AI-powered optimization recommendations"""
        actions = []
        
        # CPU optimizations
        if metrics.cpu_usage > 80:
            actions.append(OptimizationAction(
                action_type="cpu_optimization",
                priority=1,
                description="Optimize CPU-intensive processes",
                estimated_impact=15.0,
                execution_time=30.0
            ))
        
        # Memory optimizations
        if metrics.memory_usage > 75:
            actions.append(OptimizationAction(
                action_type="memory_cleanup",
                priority=2,
                description="Clear memory caches and optimize RAM usage",
                estimated_impact=20.0,
                execution_time=15.0
            ))
        
        # Disk optimizations
        if metrics.disk_usage > 85:
            actions.append(OptimizationAction(
                action_type="disk_cleanup",
                priority=2,
                description="Clean temporary files and optimize disk space",
                estimated_impact=10.0,
                execution_time=60.0
            ))
        
        # GPU optimizations
        if metrics.gpu_usage > 90 and self.hardware.gpu_info:
            actions.append(OptimizationAction(
                action_type="gpu_optimization",
                priority=1,
                description="Optimize GPU workload distribution",
                estimated_impact=25.0,
                execution_time=20.0
            ))
        
        # Power optimizations
        if metrics.power_usage > 200:
            actions.append(OptimizationAction(
                action_type="power_optimization",
                priority=3,
                description="Optimize power consumption settings",
                estimated_impact=12.0,
                execution_time=10.0
            ))
        
        # Sort by priority and impact
        actions.sort(key=lambda x: (x.priority, -x.estimated_impact))
        return actions
    
    def execute_optimization(self, action: OptimizationAction) -> bool:
        """Execute optimization action"""
        try:
            if action.action_type == "cpu_optimization":
                return self.optimize_cpu()
            elif action.action_type == "memory_cleanup":
                return self.cleanup_memory()
            elif action.action_type == "disk_cleanup":
                return self.cleanup_disk()
            elif action.action_type == "gpu_optimization":
                return self.optimize_gpu()
            elif action.action_type == "power_optimization":
                return self.optimize_power()
            else:
                return False
        except Exception as e:
            print(f"Error executing optimization {action.action_type}: {e}")
            return False
    
    def optimize_cpu(self) -> bool:
        """Optimize CPU performance"""
        try:
            # Set high performance power plan
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], 
                         check=True, capture_output=True)
            
            # Optimize process priorities
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:
                        # Lower priority for high CPU processes
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except:
                    continue
            
            return True
        except:
            return False
    
    def cleanup_memory(self) -> bool:
        """Clean up memory"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear system caches
            subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                         capture_output=True)
            
            # Clear DNS cache
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            
            return True
        except:
            return False
    
    def cleanup_disk(self) -> bool:
        """Clean up disk space"""
        try:
            # Clear temp files
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                'C:\\Windows\\Temp'
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    subprocess.run(['del', '/q', '/s', f'{temp_dir}\\*'], 
                                 shell=True, capture_output=True)
            
            # Run disk cleanup
            subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
            
            return True
        except:
            return False
    
    def optimize_gpu(self) -> bool:
        """Optimize GPU performance"""
        try:
            if 'nvidia_0' in self.hardware.gpu_info:
                # Set GPU performance mode
                subprocess.run(['nvidia-smi', '-pm', '1'], capture_output=True)
                subprocess.run(['nvidia-smi', '-ac', '4004,1911'], capture_output=True)
            
            return True
        except:
            return False
    
    def optimize_power(self) -> bool:
        """Optimize power settings"""
        try:
            # Set balanced power plan for efficiency
            subprocess.run(['powercfg', '/setactive', '381b4222-f694-41f0-9685-ff5bb260df2e'], 
                         capture_output=True)
            
            # Optimize USB power settings
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 
                          'SUB_USB', 'USBSELECTIVESUSPEND', '1'], capture_output=True)
            
            return True
        except:
            return False
    
    def start_monitoring(self):
        """Start continuous monitoring and optimization"""
        self.running = True
        
        def monitoring_loop():
            while self.running:
                try:
                    # Collect metrics
                    metrics = self.collect_metrics()
                    if metrics:
                        self.metrics_history.append(metrics)
                        
                        # Keep only last 1000 metrics
                        if len(self.metrics_history) > 1000:
                            self.metrics_history = self.metrics_history[-1000:]
                        
                        # Predict performance
                        performance_score = self.predict_performance(metrics)
                        
                        # Detect anomalies
                        anomalies = self.detect_anomalies(metrics)
                        
                        # Generate optimizations if needed
                        if performance_score < 70 or anomalies:
                            optimizations = self.generate_optimizations(metrics)
                            
                            # Execute high-priority optimizations
                            for action in optimizations[:3]:  # Limit to top 3
                                if action.priority <= 2:
                                    success = self.execute_optimization(action)
                                    print(f"Executed {action.description}: {'Success' if success else 'Failed'}")
                        
                        # Log status
                        print(f"Performance Score: {performance_score:.1f}% | "
                              f"CPU: {metrics.cpu_usage:.1f}% | "
                              f"Memory: {metrics.memory_usage:.1f}% | "
                              f"GPU: {metrics.gpu_usage:.1f}%")
                        
                        if anomalies:
                            print(f"Anomalies: {', '.join(anomalies)}")
                    
                    time.sleep(30)  # Monitor every 30 seconds
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(60)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        print("AI Optimization Engine started")
        print(f"Hardware detected: {len(self.hardware.gpu_info)} GPUs, {len(self.hardware.npu_info)} NPUs")
        print(f"Best compute device: {self.hardware.get_best_compute_device()}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        print("AI Optimization Engine stopped")
    
    def get_status(self) -> Dict:
        """Get current system status"""
        if not self.metrics_history:
            return {"status": "No data available"}
        
        latest_metrics = self.metrics_history[-1]
        performance_score = self.predict_performance(latest_metrics)
        anomalies = self.detect_anomalies(latest_metrics)
        
        return {
            "performance_score": performance_score,
            "cpu_usage": latest_metrics.cpu_usage,
            "memory_usage": latest_metrics.memory_usage,
            "gpu_usage": latest_metrics.gpu_usage,
            "temperature": latest_metrics.temperature,
            "power_usage": latest_metrics.power_usage,
            "anomalies": anomalies,
            "hardware": {
                "gpus": len(self.hardware.gpu_info),
                "npus": len(self.hardware.npu_info),
                "best_device": self.hardware.get_best_compute_device()
            }
        }

def main():
    """Main function to run AI Optimization Engine"""
    print("OPRYXX AI OPTIMIZATION ENGINE")
    print("=" * 50)
    
    # Initialize engine
    engine = AIOptimizationEngine()
    
    # Start monitoring
    engine.start_monitoring()
    
    try:
        # Keep running and show status
        while True:
            time.sleep(60)
            status = engine.get_status()
            print(f"\nSystem Status: Performance {status.get('performance_score', 0):.1f}%")
            
    except KeyboardInterrupt:
        print("\nShutting down AI Optimization Engine...")
        engine.stop_monitoring()

if __name__ == "__main__":
    main()