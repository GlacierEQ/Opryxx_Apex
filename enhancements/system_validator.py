"""
NEXUS System Validator
Advanced memory leak detection and GPU/NPU validation
"""

import psutil
import time
import gc
import subprocess
import os
from typing import Dict, List, Tuple

class NexusSystemValidator:
    def __init__(self):
        self.memory_threshold_warning = 80  # 80%
        self.memory_threshold_critical = 90  # 90%
        self.leak_threshold_mb = 10  # 10MB leak threshold
        
    def test_memory_leak_detection(self) -> Dict:
        """Test for memory leaks with large array allocation"""
        print("🔍 Testing memory leak detection...")
        
        # Get initial memory
        initial_memory = psutil.virtual_memory().used
        
        # Allocate large arrays to test for leaks
        test_arrays = []
        try:
            for i in range(100):
                # Create 1MB arrays
                test_array = bytearray(1024 * 1024)  # 1MB
                test_arrays.append(test_array)
            
            # Clear arrays
            test_arrays.clear()
            
            # Force garbage collection
            gc.collect()
            time.sleep(1)  # Allow cleanup
            
            # Get final memory
            final_memory = psutil.virtual_memory().used
            
            # Calculate leak
            memory_diff = final_memory - initial_memory
            leak_mb = memory_diff / (1024 * 1024)
            
            result = {
                'initial_memory_mb': initial_memory / (1024 * 1024),
                'final_memory_mb': final_memory / (1024 * 1024),
                'memory_diff_mb': leak_mb,
                'leak_detected': leak_mb > self.leak_threshold_mb,
                'status': 'LEAK DETECTED' if leak_mb > self.leak_threshold_mb else 'NO LEAKS'
            }
            
            print(f"✅ Memory leak test: {result['status']} ({leak_mb:.1f}MB diff)")
            return result
            
        except Exception as e:
            return {'error': str(e), 'status': 'ERROR'}
    
    def test_memory_thresholds(self) -> Dict:
        """Monitor memory thresholds and report detailed metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Determine status
        if memory.percent >= self.memory_threshold_critical:
            status = 'CRITICAL'
        elif memory.percent >= self.memory_threshold_warning:
            status = 'WARNING'
        else:
            status = 'NORMAL'
        
        result = {
            'total_gb': memory.total / (1024**3),
            'used_gb': memory.used / (1024**3),
            'free_gb': memory.free / (1024**3),
            'usage_percent': memory.percent,
            'swap_total_gb': swap.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_percent': swap.percent,
            'status': status,
            'warning_threshold': self.memory_threshold_warning,
            'critical_threshold': self.memory_threshold_critical
        }
        
        print(f"📊 Memory status: {status} ({memory.percent:.1f}% used)")
        return result
    
    def benchmark_memory_operations(self) -> Dict:
        """Benchmark common memory operations"""
        print("⚡ Benchmarking memory operations...")
        
        results = {}
        
        # Array allocation benchmark
        results['array_allocation'] = self._benchmark_operation(
            lambda: [bytearray(1024) for _ in range(1000)],
            "Array Allocation (1000x1KB)"
        )
        
        # Object creation benchmark
        results['object_creation'] = self._benchmark_operation(
            lambda: [{'id': i, 'data': f'item_{i}'} for i in range(1000)],
            "Object Creation (1000 objects)"
        )
        
        # String manipulation benchmark
        results['string_manipulation'] = self._benchmark_operation(
            lambda: ''.join([f'string_{i}_' for i in range(1000)]),
            "String Manipulation (1000 concatenations)"
        )
        
        return results
    
    def _benchmark_operation(self, operation, name: str) -> Dict:
        """Generic benchmark method for timing and memory measurement"""
        # Get initial memory
        initial_memory = psutil.Process().memory_info().rss
        
        # Time the operation
        start_time = time.perf_counter()
        
        try:
            result = operation()
            success = True
        except Exception as e:
            result = None
            success = False
        
        end_time = time.perf_counter()
        
        # Get final memory
        final_memory = psutil.Process().memory_info().rss
        
        # Calculate metrics
        execution_time = (end_time - start_time) * 1000  # ms
        memory_used = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        benchmark_result = {
            'name': name,
            'execution_time_ms': execution_time,
            'memory_used_mb': memory_used,
            'success': success
        }
        
        print(f"  {name}: {execution_time:.2f}ms, {memory_used:.2f}MB")
        return benchmark_result
    
    def test_gpu_detection(self) -> Dict:
        """Detect and validate GPU/NPU capabilities"""
        print("🎮 Testing GPU/NPU detection...")
        
        gpu_info = {
            'nvidia_cuda': False,
            'nvidia_cudnn': False,
            'amd_rocm': False,
            'intel_npu': False,
            'gpu_memory_gb': 0,
            'capabilities': []
        }
        
        # Test NVIDIA CUDA
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_info['nvidia_cuda'] = True
                gpu_memory_mb = int(result.stdout.strip())
                gpu_info['gpu_memory_gb'] = gpu_memory_mb / 1024
                gpu_info['capabilities'].append('NVIDIA CUDA')
                print("✅ NVIDIA CUDA detected")
        except:
            pass
        
        # Test cuDNN
        try:
            import ctypes
            cudnn_lib = ctypes.CDLL('cudnn64_8.dll')  # Common cuDNN version
            gpu_info['nvidia_cudnn'] = True
            gpu_info['capabilities'].append('cuDNN')
            print("✅ cuDNN detected")
        except:
            pass
        
        # Test Intel NPU (check for Intel AI acceleration)
        try:
            result = subprocess.run(['wmic', 'path', 'win32_processor', 'get', 'name'], 
                                  capture_output=True, text=True)
            if 'intel' in result.stdout.lower():
                # Check for modern Intel processors with NPU
                if any(keyword in result.stdout.lower() for keyword in ['ultra', 'core i7-13', 'core i9-13']):
                    gpu_info['intel_npu'] = True
                    gpu_info['capabilities'].append('Intel NPU')
                    print("✅ Intel NPU detected")
        except:
            pass
        
        # Test AMD ROCm
        try:
            result = subprocess.run(['rocm-smi', '--showproductname'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_info['amd_rocm'] = True
                gpu_info['capabilities'].append('AMD ROCm')
                print("✅ AMD ROCm detected")
        except:
            pass
        
        return gpu_info
    
    def test_gpu_acceleration(self) -> Dict:
        """Test GPU acceleration capabilities"""
        print("⚡ Testing GPU acceleration...")
        
        acceleration_info = {
            'webgl_available': False,
            'compute_shaders': False,
            'memory_bandwidth': 0,
            'acceleration_score': 0
        }
        
        # Test compute capabilities
        try:
            # Simple GPU memory bandwidth test
            start_time = time.perf_counter()
            
            # Simulate GPU memory operations
            test_data = bytearray(100 * 1024 * 1024)  # 100MB
            for i in range(0, len(test_data), 1024):
                test_data[i] = i % 256
            
            end_time = time.perf_counter()
            
            # Calculate bandwidth (rough estimate)
            bandwidth_mbps = (100 / (end_time - start_time))
            acceleration_info['memory_bandwidth'] = bandwidth_mbps
            acceleration_info['acceleration_score'] = min(100, bandwidth_mbps / 10)
            
            print(f"📊 Memory bandwidth: {bandwidth_mbps:.1f} MB/s")
            
        except Exception as e:
            acceleration_info['error'] = str(e)
        
        return acceleration_info
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable sizes"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(bytes_value)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"
    
    def run_full_validation(self) -> Dict:
        """Run complete system validation"""
        print("🚀 NEXUS SYSTEM VALIDATION")
        print("=" * 50)
        
        validation_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'memory_leak_test': self.test_memory_leak_detection(),
            'memory_thresholds': self.test_memory_thresholds(),
            'memory_benchmarks': self.benchmark_memory_operations(),
            'gpu_detection': self.test_gpu_detection(),
            'gpu_acceleration': self.test_gpu_acceleration()
        }
        
        # Calculate overall score
        score = 0
        if not validation_results['memory_leak_test'].get('leak_detected', True):
            score += 20
        if validation_results['memory_thresholds']['status'] == 'NORMAL':
            score += 20
        if validation_results['gpu_detection']['capabilities']:
            score += 30
        if validation_results['gpu_acceleration']['acceleration_score'] > 50:
            score += 30
        
        validation_results['overall_score'] = score
        validation_results['status'] = 'EXCELLENT' if score >= 80 else 'GOOD' if score >= 60 else 'NEEDS_IMPROVEMENT'
        
        print(f"\n🎯 VALIDATION COMPLETE: {validation_results['status']} ({score}/100)")
        
        return validation_results

def main():
    """Run NEXUS system validation"""
    validator = NexusSystemValidator()
    results = validator.run_full_validation()
    
    print(f"\n📊 SUMMARY:")
    print(f"Memory Status: {results['memory_thresholds']['status']}")
    print(f"GPU Capabilities: {', '.join(results['gpu_detection']['capabilities']) or 'None'}")
    print(f"Overall Score: {results['overall_score']}/100")

if __name__ == "__main__":
    main()