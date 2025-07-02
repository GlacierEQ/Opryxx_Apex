"""
Performance Optimization Tests
Tests for GPU acceleration and performance monitoring
"""

import unittest
import numpy as np
import time
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.performance_monitor import PerformanceMonitor, start_performance_monitoring, stop_performance_monitoring
from core.gpu_acceleration import AcceleratedCompute, enable_gpu_acceleration, is_gpu_available

class TestPerformanceOptimization(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.monitor = PerformanceMonitor(update_interval=0.1)
        cls.accelerator = AcceleratedCompute()
        cls.test_matrix_size = 1000  # Size of test matrices
        
        # Create test data
        cls.matrix_a = np.random.randn(cls.test_matrix_size, cls.test_matrix_size).astype(np.float32)
        cls.matrix_b = np.random.randn(cls.test_matrix_size, cls.test_matrix_size).astype(np.float32)
    
    def setUp(self):
        """Run before each test"""
        self.monitor.start()
        
    def tearDown(self):
        """Run after each test"""
        self.monitor.stop()
    
    def test_performance_monitor_initialization(self):
        """Test that performance monitor initializes correctly"""
        self.assertTrue(hasattr(self.monitor, 'metrics_history'))
        self.assertGreaterEqual(len(self.monitor.metrics_history), 0)
    
    def test_performance_metrics_collection(self):
        """Test that performance metrics are collected correctly"""
        # Give the monitor time to collect some data
        time.sleep(0.5)
        
        metrics = self.monitor.get_metrics()
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.timestamp, 0)
        self.assertGreaterEqual(metrics.cpu_usage, 0)
        self.assertLessEqual(metrics.cpu_usage, 100)
        self.assertGreaterEqual(metrics.memory_usage, 0)
        self.assertLessEqual(metrics.memory_usage, 100)
        self.assertGreaterEqual(metrics.score, 0)
        self.assertLessEqual(metrics.score, 100)
    
    def test_gpu_acceleration_available(self):
        """Test GPU acceleration availability detection"""
        # This test just checks if the GPU detection logic works
        # It doesn't require a GPU to be present
        _ = is_gpu_available()
        
    def test_matrix_multiplication(self):
        """Test matrix multiplication with and without GPU acceleration"""
        # Test CPU implementation
        enable_gpu_acceleration(False)
        start_time = time.time()
        result_cpu = self.accelerator.matrix_multiply(self.matrix_a, self.matrix_b)
        cpu_time = time.time() - start_time
        
        # Test GPU implementation if available
        gpu_time = float('inf')
        if is_gpu_available():
            enable_gpu_acceleration(True)
            start_time = time.time()
            result_gpu = self.accelerator.matrix_multiply(self.matrix_a, self.matrix_b)
            gpu_time = time.time() - start_time
            
            # Verify results are the same (within floating point tolerance)
            np.testing.assert_allclose(result_cpu, result_gpu, rtol=1e-5, atol=1e-5)
        
        # Log performance comparison
        print(f"\nPerformance Comparison (matrix {self.test_matrix_size}x{self.test_matrix_size}):")
        print(f"CPU time: {cpu_time:.4f}s")
        if is_gpu_available():
            print(f"GPU time: {gpu_time:.4f}s")
            print(f"Speedup: {cpu_time / gpu_time:.2f}x")
    
    def test_performance_score(self):
        """Test that performance score is calculated correctly"""
        # Simulate different load scenarios and verify score calculation
        test_cases = [
            (0, 0, 100),     # No load
            (50, 50, 50),    # Medium load
            (100, 100, 0),   # Full load
            (25, 75, 65),    # Mixed load
        ]
        
        for cpu, mem, expected_score in test_cases:
            with self.subTest(cpu=cpu, mem=mem, expected=expected_score):
                score = self.monitor._calculate_score(cpu, mem)
                self.assertAlmostEqual(score, expected_score, delta=1.0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
