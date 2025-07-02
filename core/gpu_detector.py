"""
Enhanced GPU Detection and Elevation
Comprehensive GPU detection with multiple backends
"""

import subprocess
import platform
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GPUInfo:
    name: str
    memory_mb: int
    driver_version: str
    compute_capability: Optional[str] = None
    backend: str = "unknown"

class GPUDetector:
    def __init__(self):
        self.detected_gpus: List[GPUInfo] = []
        self.detection_methods = [
            self._detect_nvidia_smi,
            self._detect_wmi,
            self._detect_torch,
            self._detect_opencl,
            self._detect_directml
        ]
    
    def detect_all_gpus(self) -> List[GPUInfo]:
        """Detect GPUs using all available methods"""
        self.detected_gpus.clear()
        
        for method in self.detection_methods:
            try:
                gpus = method()
                if gpus:
                    self.detected_gpus.extend(gpus)
                    logger.info(f"Found {len(gpus)} GPU(s) via {method.__name__}")
            except Exception as e:
                logger.debug(f"{method.__name__} failed: {e}")
        
        # Remove duplicates
        unique_gpus = []
        seen_names = set()
        for gpu in self.detected_gpus:
            if gpu.name not in seen_names:
                unique_gpus.append(gpu)
                seen_names.add(gpu.name)
        
        self.detected_gpus = unique_gpus
        return self.detected_gpus
    
    def _detect_nvidia_smi(self) -> List[GPUInfo]:
        """Detect NVIDIA GPUs using nvidia-smi"""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        gpus.append(GPUInfo(
                            name=parts[0],
                            memory_mb=int(parts[1]),
                            driver_version=parts[2],
                            backend="nvidia-smi"
                        ))
            return gpus
        except:
            return []
    
    def _detect_wmi(self) -> List[GPUInfo]:
        """Detect GPUs using Windows WMI"""
        if platform.system() != "Windows":
            return []
        
        try:
            import wmi
            c = wmi.WMI()
            gpus = []
            
            for gpu in c.Win32_VideoController():
                if gpu.Name and "Microsoft" not in gpu.Name:
                    memory_mb = 0
                    if gpu.AdapterRAM:
                        memory_mb = gpu.AdapterRAM // (1024 * 1024)
                    
                    gpus.append(GPUInfo(
                        name=gpu.Name,
                        memory_mb=memory_mb,
                        driver_version=gpu.DriverVersion or "Unknown",
                        backend="wmi"
                    ))
            return gpus
        except:
            return []
    
    def _detect_torch(self) -> List[GPUInfo]:
        """Detect GPUs using PyTorch"""
        try:
            import torch
            gpus = []
            
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    gpus.append(GPUInfo(
                        name=props.name,
                        memory_mb=props.total_memory // (1024 * 1024),
                        driver_version="Unknown",
                        compute_capability=f"{props.major}.{props.minor}",
                        backend="torch"
                    ))
            return gpus
        except:
            return []
    
    def _detect_opencl(self) -> List[GPUInfo]:
        """Detect GPUs using OpenCL"""
        try:
            import pyopencl as cl
            gpus = []
            
            for platform in cl.get_platforms():
                for device in platform.get_devices(device_type=cl.device_type.GPU):
                    memory_mb = device.global_mem_size // (1024 * 1024)
                    gpus.append(GPUInfo(
                        name=device.name.strip(),
                        memory_mb=memory_mb,
                        driver_version=device.driver_version.strip(),
                        backend="opencl"
                    ))
            return gpus
        except:
            return []
    
    def _detect_directml(self) -> List[GPUInfo]:
        """Detect GPUs using DirectML (Windows)"""
        if platform.system() != "Windows":
            return []
        
        try:
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 
                                   'name,AdapterRAM,DriverVersion', '/format:csv'], 
                                  capture_output=True, text=True, timeout=10)
            
            gpus = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 4 and parts[2]:  # Has name
                        name = parts[2].strip()
                        if name and "Microsoft" not in name:
                            memory_mb = 0
                            if parts[1] and parts[1].strip():
                                try:
                                    memory_mb = int(parts[1]) // (1024 * 1024)
                                except:
                                    pass
                            
                            gpus.append(GPUInfo(
                                name=name,
                                memory_mb=memory_mb,
                                driver_version=parts[3].strip() if parts[3] else "Unknown",
                                backend="directml"
                            ))
            return gpus
        except:
            return []
    
    def get_best_gpu(self) -> Optional[GPUInfo]:
        """Get the best available GPU"""
        if not self.detected_gpus:
            self.detect_all_gpus()
        
        if not self.detected_gpus:
            return None
        
        # Prioritize by memory size and backend preference
        backend_priority = {"torch": 4, "nvidia-smi": 3, "opencl": 2, "wmi": 1, "directml": 1}
        
        best_gpu = max(self.detected_gpus, 
                      key=lambda gpu: (backend_priority.get(gpu.backend, 0), gpu.memory_mb))
        return best_gpu

# Global detector instance
gpu_detector = GPUDetector()