"""
Tests for GPU-accelerated operations
"""
import unittest
import numpy as np
from core.gpu_acceleration import AcceleratedCompute, ComputeDevice

class TestGPUOperations(unittest.TestCase):
    """Test suite for GPU-accelerated operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.accelerator = AcceleratedCompute(preferred_device=ComputeDevice.CUDA_GPU)
        cls.test_matrix_size = 1000
        
        # Generate test data
        np.random.seed(42)
        cls.matrix_a = np.random.randn(cls.test_matrix_size, cls.test_matrix_size).astype(np.float32)
        cls.matrix_b = np.random.randn(cls.test_matrix_size, cls.test_matrix_size).astype(np.float32)
        cls.vector = np.random.randn(cls.test_matrix_size).astype(np.float32)
        
    def test_elementwise_multiply(self):
        """Test element-wise multiplication"""
        result = self.accelerator.elementwise_multiply(self.matrix_a, self.matrix_b)
        expected = np.multiply(self.matrix_a, self.matrix_b)
        np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-5)
        
    def test_matrix_inverse(self):
        """Test matrix inversion"""
        # Create a positive definite matrix to ensure invertibility
        matrix = self.matrix_a @ self.matrix_a.T + np.eye(self.test_matrix_size)
        result = self.accelerator.matrix_inverse(matrix)
        identity_approx = matrix @ result
        np.testing.assert_allclose(identity_approx, np.eye(self.test_matrix_size), rtol=1e-4, atol=1e-4)
        
    def test_matrix_transpose(self):
        """Test matrix transposition"""
        result = self.accelerator.matrix_transpose(self.matrix_a)
        expected = np.transpose(self.matrix_a)
        np.testing.assert_array_equal(result, expected)
        
    def test_vector_norm(self):
        """Test vector norm calculation"""
        # Test L2 norm (default)
        result_l2 = self.accelerator.vector_norm(self.vector)
        expected_l2 = np.linalg.norm(self.vector)
        self.assertAlmostEqual(result_l2, expected_l2, places=5)
        
        # Test L1 norm
        result_l1 = self.accelerator.vector_norm(self.vector, ord=1)
        expected_l1 = np.linalg.norm(self.vector, ord=1)
        self.assertAlmostEqual(result_l1, expected_l1, places=5)
        
    def test_batch_operations(self):
        """Test batch operations"""
        batch_size = 10
        batch_a = np.random.randn(batch_size, self.test_matrix_size, self.test_matrix_size).astype(np.float32)
        batch_b = np.random.randn(batch_size, self.test_matrix_size, self.test_matrix_size).astype(np.float32)
        
        # Test batch matrix multiplication
        result_matmul = self.accelerator.batch_operations('matmul', batch_a, batch_b)
        expected_matmul = np.matmul(batch_a, batch_b)
        np.testing.assert_allclose(result_matmul, expected_matmul, rtol=1e-5, atol=1e-5)
        
        # Test batch addition
        result_add = self.accelerator.batch_operations('add', batch_a, batch_b)
        expected_add = batch_a + batch_b
        np.testing.assert_allclose(result_add, expected_add, rtol=1e-5, atol=1e-5)
        
    def test_performance_benchmark(self):
        """Benchmark performance of GPU operations"""
        import time
        
        # Warm up
        _ = self.accelerator.matrix_multiply(self.matrix_a, self.matrix_b)
        
        # Time matrix multiplication
        start = time.time()
        _ = self.accelerator.matrix_multiply(self.matrix_a, self.matrix_b)
        gpu_time = time.time() - start
        
        # Time CPU matrix multiplication for comparison
        start = time.time()
        _ = np.matmul(self.matrix_a, self.matrix_b)
        cpu_time = time.time() - start
        
        print(f"\nPerformance Benchmark ({self.test_matrix_size}x{self.test_matrix_size} matrices):")
        print(f"GPU time: {gpu_time*1000:.2f}ms")
        print(f"CPU time: {cpu_time*1000:.2f}ms")
        print(f"Speedup: {cpu_time/max(gpu_time, 1e-10):.2f}x")
        
        # Verify GPU is being used if available
        if self.accelerator.active_device == ComputeDevice.CUDA_GPU:
            self.assertLess(gpu_time, cpu_time, "GPU should be faster than CPU for matrix multiplication")

if __name__ == "__main__":
    unittest.main(verbosity=2)
