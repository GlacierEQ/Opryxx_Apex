"""
Enhanced GPU Operations Module
Extends GPU acceleration with additional compute operations
"""

import numpy as np
import time
from typing import Dict, List, Optional, Union
from core.gpu_acceleration import accelerator, ComputeDevice

class EnhancedGPUOperations:
    """Extended GPU operations beyond basic matrix multiplication"""
    
    def __init__(self):
        self.accelerator = accelerator
        self.benchmark_cache = {}
    
    def vector_operations(self, operation: str, *arrays) -> np.ndarray:
        """Perform vectorized operations (add, subtract, multiply, divide)"""
        try:
            if self.accelerator.active_device == ComputeDevice.CUDA_GPU:
                import torch
                tensors = [self.accelerator.to_device(arr) for arr in arrays]
                
                if operation == 'add':
                    result = torch.add(tensors[0], tensors[1])
                elif operation == 'subtract':
                    result = torch.sub(tensors[0], tensors[1])
                elif operation == 'multiply':
                    result = torch.mul(tensors[0], tensors[1])
                elif operation == 'divide':
                    result = torch.div(tensors[0], tensors[1])
                else:
                    raise ValueError(f"Unsupported operation: {operation}")
                    
                return self.accelerator.to_numpy(result)
            else:
                # CPU fallback
                if operation == 'add':
                    return np.add(arrays[0], arrays[1])
                elif operation == 'subtract':
                    return np.subtract(arrays[0], arrays[1])
                elif operation == 'multiply':
                    return np.multiply(arrays[0], arrays[1])
                elif operation == 'divide':
                    return np.divide(arrays[0], arrays[1])
                    
        except Exception as e:
            print(f"Vector operation {operation} failed: {e}")
            if self.accelerator.active_device != ComputeDevice.CPU:
                self.accelerator.active_device = ComputeDevice.CPU
                return self.vector_operations(operation, *arrays)
            raise
    
    def fft_transform(self, data: np.ndarray) -> np.ndarray:
        """Perform Fast Fourier Transform"""
        try:
            if self.accelerator.active_device == ComputeDevice.CUDA_GPU:
                import torch
                tensor = self.accelerator.to_device(data)
                result = torch.fft.fft(tensor)
                return self.accelerator.to_numpy(result)
            else:
                return np.fft.fft(data)
        except Exception as e:
            print(f"FFT failed: {e}")
            if self.accelerator.active_device != ComputeDevice.CPU:
                self.accelerator.active_device = ComputeDevice.CPU
                return np.fft.fft(data)
            raise
    
    def convolution(self, signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Perform 1D convolution"""
        try:
            if self.accelerator.active_device == ComputeDevice.CUDA_GPU:
                import torch
                import torch.nn.functional as F
                
                signal_tensor = self.accelerator.to_device(signal).unsqueeze(0).unsqueeze(0)
                kernel_tensor = self.accelerator.to_device(kernel).unsqueeze(0).unsqueeze(0)
                
                result = F.conv1d(signal_tensor, kernel_tensor, padding='same')
                return self.accelerator.to_numpy(result.squeeze())
            else:
                return np.convolve(signal, kernel, mode='same')
        except Exception as e:
            print(f"Convolution failed: {e}")
            if self.accelerator.active_device != ComputeDevice.CPU:
                self.accelerator.active_device = ComputeDevice.CPU
                return np.convolve(signal, kernel, mode='same')
            raise
    
    def benchmark_operations(self, size: int = 1000) -> Dict[str, float]:
        """Benchmark different operations on current device"""
        if size in self.benchmark_cache:
            return self.benchmark_cache[size]
        
        test_matrix = np.random.randn(size, size).astype(np.float32)
        test_vector = np.random.randn(size).astype(np.float32)
        test_kernel = np.random.randn(min(size//10, 100)).astype(np.float32)
        
        results = {}
        
        # Matrix multiplication benchmark
        start = time.time()
        _ = self.accelerator.matrix_multiply(test_matrix, test_matrix)
        results['matrix_multiply_ms'] = (time.time() - start) * 1000
        
        # Vector operations benchmark
        start = time.time()
        _ = self.vector_operations('add', test_vector, test_vector)
        results['vector_add_ms'] = (time.time() - start) * 1000
        
        # FFT benchmark
        start = time.time()
        _ = self.fft_transform(test_vector)
        results['fft_ms'] = (time.time() - start) * 1000
        
        # Convolution benchmark
        start = time.time()
        _ = self.convolution(test_vector, test_kernel)
        results['convolution_ms'] = (time.time() - start) * 1000
        
        results['device'] = self.accelerator.active_device.name
        self.benchmark_cache[size] = results
        return results

# Global instance
enhanced_gpu_ops = EnhancedGPUOperations()