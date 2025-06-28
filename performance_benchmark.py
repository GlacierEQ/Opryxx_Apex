"""
Performance Benchmarking Script
Comprehensive performance testing for NEXUS AI system
"""

import time
import psutil
import gc
from enhancements.system_validator import NexusSystemValidator
from enhancements.memory_optimizer import AdvancedMemoryOptimizer
from enhancements.gpu_acceleration import GPUAcceleration

class PerformanceBenchmark:
    def __init__(self):
        self.validator = NexusSystemValidator()
        self.memory_optimizer = AdvancedMemoryOptimizer()
        self.gpu_accel = GPUAcceleration()
        
    def run_full_benchmark(self):
        """Run complete performance benchmark"""
        print("NEXUS AI PERFORMANCE BENCHMARK")
        print("=" * 50)
        
        results = {
            'memory_operations': self._benchmark_memory_operations(),
            'gpu_performance': self._benchmark_gpu_performance(),
            'system_optimization': self._benchmark_system_optimization(),
            'leak_detection': self._benchmark_leak_detection()
        }
        
        self._generate_report(results)
        return results
    
    def _benchmark_memory_operations(self):
        """Benchmark memory operations"""
        print("\nBenchmarking memory operations...")
        
        operations = {
            'array_allocation': lambda: [bytearray(1024) for _ in range(1000)],
            'object_creation': lambda: [{'id': i} for i in range(1000)],
            'string_operations': lambda: ''.join([f'str_{i}' for i in range(1000)])
        }
        
        results = {}
        for name, operation in operations.items():
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss
            
            data = operation()
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss
            
            results[name] = {
                'time_ms': (end_time - start_time) * 1000,
                'memory_mb': (end_memory - start_memory) / (1024 * 1024)
            }
            
            del data
            gc.collect()
            
            print(f"  {name}: {results[name]['time_ms']:.2f}ms, {results[name]['memory_mb']:.2f}MB")
        
        return results
    
    def _benchmark_gpu_performance(self):
        """Benchmark GPU performance"""
        print("\nBenchmarking GPU performance...")
        
        gpu_status = self.gpu_accel.get_gpu_status()
        
        if gpu_status['gpu_available']:
            # Run GPU acceleration test
            accel_test = self.validator.test_gpu_acceleration()
            
            result = {
                'gpu_available': True,
                'memory_bandwidth': accel_test.get('memory_bandwidth', 0),
                'acceleration_score': accel_test.get('acceleration_score', 0)
            }
            
            print(f"  GPU bandwidth: {result['memory_bandwidth']:.1f} MB/s")
            print(f"  Acceleration score: {result['acceleration_score']:.1f}")
        else:
            result = {'gpu_available': False}
            print("  No GPU available")
        
        return result
    
    def _benchmark_system_optimization(self):
        """Benchmark system optimization"""
        print("\nBenchmarking system optimization...")
        
        start_time = time.perf_counter()
        
        # Run optimization
        optimizations = self.memory_optimizer.optimize_memory_aggressive()
        
        end_time = time.perf_counter()
        
        result = {
            'optimization_time_ms': (end_time - start_time) * 1000,
            'optimizations_count': len(optimizations)
        }
        
        print(f"  Optimization time: {result['optimization_time_ms']:.2f}ms")
        print(f"  Optimizations applied: {result['optimizations_count']}")
        
        return result
    
    def _benchmark_leak_detection(self):
        """Benchmark leak detection"""
        print("\nBenchmarking leak detection...")
        
        start_time = time.perf_counter()
        
        # Run leak detection
        leak_test = self.validator.test_memory_leak_detection()
        
        end_time = time.perf_counter()
        
        result = {
            'detection_time_ms': (end_time - start_time) * 1000,
            'leak_detected': leak_test.get('leak_detected', False),
            'memory_diff_mb': leak_test.get('memory_diff_mb', 0)
        }
        
        print(f"  Detection time: {result['detection_time_ms']:.2f}ms")
        print(f"  Leak status: {'DETECTED' if result['leak_detected'] else 'NONE'}")
        
        return result
    
    def _generate_report(self, results):
        """Generate performance report"""
        print("\n" + "=" * 50)
        print("PERFORMANCE BENCHMARK REPORT")
        print("=" * 50)
        
        # Memory operations summary
        memory_ops = results['memory_operations']
        avg_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
        avg_memory = sum(op['memory_mb'] for op in memory_ops.values()) / len(memory_ops)
        
        print(f"Memory Operations Average: {avg_time:.2f}ms, {avg_memory:.2f}MB")
        
        # GPU performance
        gpu_perf = results['gpu_performance']
        if gpu_perf['gpu_available']:
            print(f"GPU Performance Score: {gpu_perf['acceleration_score']:.1f}/100")
        else:
            print("GPU Performance: Not Available")
        
        # System optimization
        sys_opt = results['system_optimization']
        print(f"System Optimization: {sys_opt['optimization_time_ms']:.2f}ms")
        
        # Leak detection
        leak_det = results['leak_detection']
        print(f"Leak Detection: {leak_det['detection_time_ms']:.2f}ms")
        
        # Overall score
        score = self._calculate_overall_score(results)
        print(f"\nOVERALL PERFORMANCE SCORE: {score}/100")
        
        if score >= 80:
            print("STATUS: EXCELLENT PERFORMANCE")
        elif score >= 60:
            print("STATUS: GOOD PERFORMANCE")
        else:
            print("STATUS: NEEDS OPTIMIZATION")
    
    def _calculate_overall_score(self, results):
        """Calculate overall performance score"""
        score = 0
        
        # Memory operations (30 points)
        memory_ops = results['memory_operations']
        avg_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
        if avg_time < 10:
            score += 30
        elif avg_time < 50:
            score += 20
        else:
            score += 10
        
        # GPU performance (25 points)
        gpu_perf = results['gpu_performance']
        if gpu_perf['gpu_available']:
            gpu_score = min(25, gpu_perf['acceleration_score'] / 4)
            score += gpu_score
        
        # System optimization (25 points)
        sys_opt = results['system_optimization']
        if sys_opt['optimization_time_ms'] < 100:
            score += 25
        elif sys_opt['optimization_time_ms'] < 500:
            score += 15
        else:
            score += 5
        
        # Leak detection (20 points)
        leak_det = results['leak_detection']
        if leak_det['detection_time_ms'] < 1000:
            score += 20
        elif leak_det['detection_time_ms'] < 5000:
            score += 10
        else:
            score += 5
        
        return int(score)

def main():
    """Run performance benchmark"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark()
    
    return results

if __name__ == "__main__":
    main()