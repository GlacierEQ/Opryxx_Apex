"""
GPU Activation Script
Forces GPU acceleration activation
"""

from core.gpu_acceleration import enable_gpu_acceleration, is_gpu_available, get_compute_device
from core.enhanced_gpu_ops import enhanced_gpu_ops
import numpy as np
import time

def activate_gpu():
    print("GPU Activation and Testing")
    print("=" * 30)
    
    # Check GPU availability
    gpu_available = is_gpu_available()
    print(f"GPU Available: {gpu_available}")
    
    if gpu_available:
        # Force enable GPU acceleration
        enable_gpu_acceleration(True)
        print(f"Active Device: {get_compute_device().name}")
        
        # Test GPU operations
        print("\nTesting GPU operations...")
        
        # Matrix multiplication test
        a = np.random.randn(1000, 1000).astype(np.float32)
        b = np.random.randn(1000, 1000).astype(np.float32)
        
        start_time = time.time()
        result = enhanced_gpu_ops.accelerator.matrix_multiply(a, b)
        gpu_time = time.time() - start_time
        
        print(f"GPU Matrix Multiplication: {gpu_time:.4f}s")
        print(f"Result shape: {result.shape}")
        
        # Benchmark all operations
        benchmarks = enhanced_gpu_ops.benchmark_operations(size=500)
        print(f"\nGPU Benchmarks:")
        for op, time_ms in benchmarks.items():
            if op != 'device':
                print(f"  {op}: {time_ms:.2f}ms")
        print(f"  Device: {benchmarks['device']}")
        
        print("\n[SUCCESS] GPU acceleration is ACTIVE and ELEVATED!")
        return True
    else:
        print("[ERROR] No GPU detected - check drivers and installation")
        return False

if __name__ == "__main__":
    activate_gpu()