"""
GPU/Accelerated Computing Module
Provides hardware-accelerated computation capabilities
"""

import numpy as np
from typing import Any, Optional, Union, List, Dict, Tuple
import time
import logging
from enum import Enum, auto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComputeDevice(Enum):
    """Available compute devices"""
    CPU = auto()
    CUDA_GPU = auto()
    NPU = auto()

class AcceleratedCompute:
    """
    Handles GPU/NPU accelerated computations with automatic fallback to CPU
    Implements memory management and performance optimization
    """
    
    def __init__(self, preferred_device: ComputeDevice = None):
        self.available_devices = self._detect_available_devices()
        self.active_device = preferred_device if preferred_device in self.available_devices else ComputeDevice.CPU
        self._init_device()
        self.memory_usage = 0
        self.operations_count = 0
        self.start_time = time.time()
        
    def _detect_available_devices(self) -> List[ComputeDevice]:
        """Detect available compute devices"""
        devices = [ComputeDevice.CPU]  # CPU is always available
        
        # Enhanced GPU detection
        from core.gpu_detector import gpu_detector
        gpus = gpu_detector.detect_all_gpus()
        
        if gpus:
            devices.append(ComputeDevice.CUDA_GPU)
            best_gpu = gpu_detector.get_best_gpu()
            logger.info(f"Detected GPU: {best_gpu.name} ({best_gpu.memory_mb}MB) via {best_gpu.backend}")
        
        # Check PyTorch CUDA as fallback
        try:
            import torch
            if torch.cuda.is_available() and ComputeDevice.CUDA_GPU not in devices:
                devices.append(ComputeDevice.CUDA_GPU)
                logger.info(f"PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
        except ImportError:
            pass
            
        return devices
    
    def _init_device(self):
        """Initialize the selected compute device"""
        if self.active_device == ComputeDevice.CUDA_GPU and ComputeDevice.CUDA_GPU in self.available_devices:
            import torch
            self.device = torch.device("cuda:0")
            torch.backends.cudnn.benchmark = True  # Enable cuDNN auto-tuner
            logger.info(f"Initialized CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            self.device = None  # Use CPU with NumPy
            logger.info("Using CPU for computation")
    
    def to_device(self, data: Any) -> Any:
        """Move data to the active compute device"""
        if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
            import torch
            if isinstance(data, (list, tuple)):
                return [self.to_device(x) for x in data]
            elif isinstance(data, dict):
                return {k: self.to_device(v) for k, v in data.items()}
            elif isinstance(data, np.ndarray):
                return torch.from_numpy(data).to(self.device)
            elif torch.is_tensor(data):
                return data.to(self.device)
        return data
    
    def to_numpy(self, data: Any) -> np.ndarray:
        """Convert data to NumPy array, moving from device if needed"""
        import torch
        if torch.is_tensor(data):
            if data.is_cuda:
                data = data.cpu()
            return data.numpy()
        elif isinstance(data, np.ndarray):
            return data
        else:
            return np.array(data)
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Perform matrix multiplication using the active device
        
        Args:
            a: First matrix (m x n)
            b: Second matrix (n x p)
            
        Returns:
            Resulting matrix (m x p)
        """
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                a_tensor = self.to_device(a)
                b_tensor = self.to_device(b)
                result = torch.mm(a_tensor, b_tensor)
                return self.to_numpy(result)
            else:
                # Fall back to NumPy on CPU
                return np.matmul(a, b)
                
        except Exception as e:
            logger.error(f"Matrix multiplication failed: {e}")
            # Fall back to CPU if GPU operation fails
            if self.active_device != ComputeDevice.CPU:
                logger.warning("Falling back to CPU")
                self.active_device = ComputeDevice.CPU
                return np.matmul(a, b)
            raise
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            logger.debug(f"Matrix multiply completed in {(time.time() - start_time) * 1000:.2f}ms")
    
    def elementwise_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Perform element-wise multiplication (Hadamard product)
        
        Args:
            a: First array
            b: Second array (must be broadcastable to a's shape)
            
        Returns:
            Resulting array with element-wise product
        """
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                a_tensor = self.to_device(a)
                b_tensor = self.to_device(b)
                result = torch.mul(a_tensor, b_tensor)
                return self.to_numpy(result)
        except Exception as e:
            logger.warning(f"GPU elementwise multiply failed, falling back to CPU: {e}")
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            
        return np.multiply(a, b)
        
    def matrix_inverse(self, a: np.ndarray) -> np.ndarray:
        """
        Compute the inverse of a square matrix
        
        Args:
            a: Square matrix to invert
            
        Returns:
            Inverse of the input matrix
        """
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                a_tensor = self.to_device(a)
                result = torch.inverse(a_tensor)
                return self.to_numpy(result)
        except Exception as e:
            logger.warning(f"GPU matrix inverse failed, falling back to CPU: {e}")
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            
        return np.linalg.inv(a)
        
    def matrix_transpose(self, a: np.ndarray) -> np.ndarray:
        """
        Transpose a matrix
        
        Args:
            a: Input matrix
            
        Returns:
            Transposed matrix
        """
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                a_tensor = self.to_device(a)
                result = a_tensor.t() if a_tensor.dim() == 2 else a_tensor.transpose(-2, -1)
                return self.to_numpy(result)
        except Exception as e:
            logger.warning(f"GPU matrix transpose failed, falling back to CPU: {e}")
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            
        return np.transpose(a)
        
    def vector_norm(self, a: np.ndarray, ord: int = 2) -> float:
        """
        Compute vector or matrix norm
        
        Args:
            a: Input array
            ord: Order of the norm (e.g., 2 for L2 norm, 1 for L1 norm)
            
        Returns:
            Norm of the input array
        """
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                a_tensor = self.to_device(a)
                result = torch.norm(a_tensor, p=ord)
                return float(self.to_numpy(result))
        except Exception as e:
            logger.warning(f"GPU norm calculation failed, falling back to CPU: {e}")
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            
        return float(np.linalg.norm(a, ord=ord))
        
    def batch_operations(self, operation: str, *args, **kwargs) -> np.ndarray:
        """
        Perform batch operations on multiple inputs
        
        Args:
            operation: Name of the operation to perform ('matmul', 'add', 'mul', etc.)
            *args: Arguments for the operation
            **kwargs: Additional arguments for the operation
            
        Returns:
            Result of the batch operation
        """
        if operation not in ['matmul', 'add', 'mul', 'div']:
            raise ValueError(f"Unsupported batch operation: {operation}")
            
        start_time = time.time()
        
        try:
            if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
                import torch
                torch_args = [self.to_device(arg) for arg in args]
                
                if operation == 'matmul':
                    result = torch.bmm(*torch_args)
                elif operation == 'add':
                    result = torch.add(*torch_args, **kwargs)
                elif operation == 'mul':
                    result = torch.mul(*torch_args, **kwargs)
                elif operation == 'div':
                    result = torch.div(*torch_args, **kwargs)
                    
                return self.to_numpy(result)
        except Exception as e:
            logger.warning(f"GPU batch {operation} failed, falling back to CPU: {e}")
        finally:
            self.operations_count += 1
            self._update_memory_usage()
            
        # Fallback to CPU
        if operation == 'matmul':
            return np.matmul(*args, **kwargs)
        elif operation == 'add':
            return np.add(*args, **kwargs)
        elif operation == 'mul':
            return np.multiply(*args, **kwargs)
        elif operation == 'div':
            return np.divide(*args, **kwargs)
    
    def _update_memory_usage(self):
        """Update memory usage statistics"""
        if self.active_device == ComputeDevice.CUDA_GPU and self.device is not None:
            import torch
            self.memory_usage = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for the compute operations"""
        elapsed = time.time() - self.start_time
        return {
            "operations_count": self.operations_count,
            "operations_per_second": self.operations_count / elapsed if elapsed > 0 else 0,
            "memory_usage_mb": self.memory_usage,
            "active_device": self.active_device.name
        }
    
    def clear_cache(self):
        """Clear device cache to free memory"""
        if self.active_device == ComputeDevice.CUDA_GPU:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self.memory_usage = 0

# Global instance for easy access
accelerator = AcceleratedCompute()

def enable_gpu_acceleration(enable: bool = True):
    """Enable or disable GPU acceleration"""
    global accelerator
    if enable and ComputeDevice.CUDA_GPU in accelerator.available_devices:
        accelerator.active_device = ComputeDevice.CUDA_GPU
        accelerator._init_device()
    else:
        accelerator.active_device = ComputeDevice.CPU
        accelerator._init_device()

def is_gpu_available() -> bool:
    """Check if GPU acceleration is available"""
    return ComputeDevice.CUDA_GPU in accelerator.available_devices

def get_compute_device() -> ComputeDevice:
    """Get the currently active compute device"""
    return accelerator.active_device
