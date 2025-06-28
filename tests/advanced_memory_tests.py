"""
Advanced Memory Manager Tests
Comprehensive testing for memory management, GPU integration, and AI workloads
"""

import unittest
import time
import gc
import psutil
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from enhancements.memory_optimizer import AdvancedMemoryOptimizer
from enhancements.gpu_acceleration import GPUAcceleration
from enhancements.system_validator import NexusSystemValidator

class AdvancedMemoryTests(unittest.TestCase):
    
    def setUp(self):
        self.memory_optimizer = AdvancedMemoryOptimizer()
        self.gpu_accel = GPUAcceleration()
        self.validator = NexusSystemValidator()
    
    def test_memory_metrics_collection(self):
        """Test basic memory metrics collection"""
        print("Testing memory metrics collection...")
        
        stats = self.memory_optimizer.get_memory_stats()
        
        self.assertIn('total_ram', stats)
        self.assertIn('ram_usage', stats)
        
        print(f"Memory usage: {stats['ram_usage']}")
    
    def test_threshold_detection(self):
        """Test memory threshold detection"""
        print("Testing threshold detection...")
        
        thresholds = self.validator.test_memory_thresholds()
        
        self.assertIn('status', thresholds)
        self.assertIn(thresholds['status'], ['NORMAL', 'WARNING', 'CRITICAL'])
        
        print(f"Status: {thresholds['status']}")
    
    def test_garbage_collection_efficiency(self):
        """Test garbage collection efficiency"""
        print("Testing garbage collection...")
        
        test_objects = [{'data': f'test_{i}' * 100} for i in range(1000)]
        initial_memory = psutil.Process().memory_info().rss
        
        test_objects.clear()
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_freed = initial_memory - final_memory
        
        self.assertGreaterEqual(memory_freed, 0)
        print(f"Memory freed: {memory_freed / (1024*1024):.2f}MB")
    
    def test_memory_leak_detection(self):
        """Test memory leak detection"""
        print("Testing memory leak detection...")
        
        leak_test = self.validator.test_memory_leak_detection()
        
        self.assertIn('status', leak_test)
        self.assertIn('leak_detected', leak_test)
        
        print(f"Leak test: {leak_test['status']}")
    
    def test_gpu_detection(self):
        """Test GPU hardware detection"""
        print("Testing GPU detection...")
        
        gpu_info = self.gpu_accel.get_gpu_status()
        
        self.assertIn('gpu_available', gpu_info)
        self.assertIn('npu_available', gpu_info)
        
        print(f"GPU: {gpu_info['gpu_available']}, NPU: {gpu_info['npu_available']}")

def run_tests():
    """Run all tests"""
    print("ADVANCED MEMORY MANAGER TESTS")
    print("=" * 50)
    
    unittest.main(verbosity=2, exit=False)

if __name__ == "__main__":
    run_tests()