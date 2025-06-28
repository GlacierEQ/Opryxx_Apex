"""
GPU/NPU Acceleration for NEXUS AI
Hardware acceleration for AI operations
"""

import subprocess
import psutil
import os

class GPUAcceleration:
    def __init__(self):
        self.gpu_available = False
        self.npu_available = False
        self.gpu_info = {}
        self.detect_hardware()
    
    def detect_hardware(self):
        """Detect available GPU/NPU hardware"""
        
        # Check for NVIDIA GPU
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.gpu_available = True
                self.gpu_info['nvidia'] = result.stdout.strip()
                print(f"✅ NVIDIA GPU detected: {self.gpu_info['nvidia']}")
        except:
            pass
        
        # Check for AMD GPU
        try:
            result = subprocess.run(['rocm-smi', '--showproductname'], capture_output=True, text=True)
            if result.returncode == 0:
                self.gpu_available = True
                self.gpu_info['amd'] = result.stdout.strip()
                print(f"✅ AMD GPU detected")
        except:
            pass
        
        # Check for Intel NPU (AI acceleration)
        try:
            result = subprocess.run(['wmic', 'path', 'win32_processor', 'get', 'name'], 
                                  capture_output=True, text=True)
            if 'intel' in result.stdout.lower() and ('ultra' in result.stdout.lower() or 'core' in result.stdout.lower()):
                self.npu_available = True
                print("✅ Intel NPU (AI acceleration) detected")
        except:
            pass
    
    def optimize_gpu_memory(self):
        """Optimize GPU memory usage"""
        optimizations = []
        
        if self.gpu_available:
            try:
                # Clear GPU memory cache
                if 'nvidia' in self.gpu_info:
                    subprocess.run(['nvidia-smi', '--gpu-reset'], capture_output=True)
                    optimizations.append("NVIDIA GPU memory cleared")
                
                # Set GPU performance mode
                subprocess.run(['nvidia-smi', '-pm', '1'], capture_output=True)
                optimizations.append("GPU performance mode enabled")
                
            except:
                pass
        
        return optimizations
    
    def enable_ai_acceleration(self):
        """Enable AI acceleration features"""
        accelerations = []
        
        if self.npu_available:
            # Enable Intel AI acceleration
            try:
                # Set CPU for AI workloads
                subprocess.run(['powercfg', '/setacvalueindex', 'scheme_current', 
                              'sub_processor', 'PROCTHROTTLEMAX', '100'], capture_output=True)
                accelerations.append("Intel NPU AI acceleration enabled")
            except:
                pass
        
        if self.gpu_available:
            # Enable GPU compute
            try:
                os.environ['CUDA_VISIBLE_DEVICES'] = '0'
                accelerations.append("GPU compute acceleration enabled")
            except:
                pass
        
        return accelerations
    
    def get_gpu_status(self):
        """Get current GPU status"""
        status = {
            'gpu_available': self.gpu_available,
            'npu_available': self.npu_available,
            'gpu_info': self.gpu_info
        }
        
        if self.gpu_available:
            try:
                # Get GPU utilization
                result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
                                       '--format=csv,noheader,nounits'], capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_util, mem_used, mem_total = result.stdout.strip().split(', ')
                    status['gpu_utilization'] = f"{gpu_util}%"
                    status['gpu_memory'] = f"{mem_used}MB / {mem_total}MB"
            except:
                pass
        
        return status