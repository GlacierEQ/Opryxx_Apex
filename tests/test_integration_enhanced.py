"""
Enhanced Integration Tests
Tests for memory optimization, enhanced GPU operations, and resilience systems
"""

import unittest
import time
import numpy as np
from unittest.mock import patch, MagicMock

from core.memory_optimizer import MemoryOptimizer, OptimizationLevel
from core.enhanced_gpu_ops import EnhancedGPUOperations
from core.resilience_system import CircuitBreaker, RetryPolicy, HealthChecker, circuit_breaker, retry

class TestMemoryOptimization(unittest.TestCase):
    
    def setUp(self):
        self.optimizer = MemoryOptimizer(OptimizationLevel.MODERATE)
    
    def tearDown(self):
        self.optimizer.stop_monitoring()
    
    def test_memory_metrics_collection(self):
        """Test memory metrics collection"""
        metrics = self.optimizer.get_memory_metrics()
        
        self.assertGreater(metrics.total_mb, 0)
        self.assertGreaterEqual(metrics.available_mb, 0)
        self.assertGreaterEqual(metrics.used_mb, 0)
        self.assertGreaterEqual(metrics.usage_percent, 0)
        self.assertLessEqual(metrics.usage_percent, 100)
    
    def test_optimization_trigger(self):
        """Test optimization triggering logic"""
        # Mock high memory usage
        with patch.object(self.optimizer, 'get_memory_metrics') as mock_metrics:
            mock_metrics.return_value.usage_percent = 80.0
            
            should_optimize = self.optimizer._should_optimize(mock_metrics.return_value)
            self.assertTrue(should_optimize)
    
    def test_memory_optimization(self):
        """Test memory optimization execution"""
        result = self.optimizer.optimize_memory()
        
        self.assertIn('timestamp', result)
        self.assertIn('before_usage_percent', result)
        self.assertIn('after_usage_percent', result)
        self.assertIn('freed_mb', result)
        self.assertIn('optimizations', result)
    
    def test_cleanup_callback_registration(self):
        """Test cleanup callback registration and execution"""
        callback_executed = False
        
        def test_callback():
            nonlocal callback_executed
            callback_executed = True
            return "Test cleanup executed"
        
        self.optimizer.register_cleanup_callback(test_callback)
        self.optimizer.optimize_memory()
        
        self.assertTrue(callback_executed)

class TestEnhancedGPUOperations(unittest.TestCase):
    
    def setUp(self):
        self.gpu_ops = EnhancedGPUOperations()
        self.test_size = 100  # Smaller size for faster tests
        self.test_vector = np.random.randn(self.test_size).astype(np.float32)
        self.test_matrix = np.random.randn(self.test_size, self.test_size).astype(np.float32)
    
    def test_vector_operations(self):
        """Test vector operations"""
        a = np.array([1, 2, 3, 4], dtype=np.float32)
        b = np.array([5, 6, 7, 8], dtype=np.float32)
        
        # Test addition
        result = self.gpu_ops.vector_operations('add', a, b)
        expected = np.array([6, 8, 10, 12], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
        
        # Test subtraction
        result = self.gpu_ops.vector_operations('subtract', a, b)
        expected = np.array([-4, -4, -4, -4], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_fft_transform(self):
        """Test FFT transform"""
        # Simple test signal
        signal = np.array([1, 0, 1, 0], dtype=np.float32)
        result = self.gpu_ops.fft_transform(signal)
        
        # FFT should return complex numbers
        self.assertEqual(len(result), len(signal))
        self.assertTrue(np.iscomplexobj(result))
    
    def test_convolution(self):
        """Test convolution operation"""
        signal = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        kernel = np.array([1, 0, -1], dtype=np.float32)
        
        result = self.gpu_ops.convolution(signal, kernel)
        self.assertEqual(len(result), len(signal))
    
    def test_benchmark_operations(self):
        """Test operation benchmarking"""
        benchmarks = self.gpu_ops.benchmark_operations(size=50)  # Small size for speed
        
        required_keys = ['matrix_multiply_ms', 'vector_add_ms', 'fft_ms', 'convolution_ms', 'device']
        for key in required_keys:
            self.assertIn(key, benchmarks)
            if key != 'device':
                self.assertGreater(benchmarks[key], 0)

class TestResilienceSystem(unittest.TestCase):
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        breaker = CircuitBreaker(failure_threshold=3)
        
        @breaker
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(breaker.state.name, "CLOSED")
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker
        def failing_function():
            raise ValueError("Test error")
        
        # First failure
        with self.assertRaises(ValueError):
            failing_function()
        
        # Second failure - should open circuit
        with self.assertRaises(ValueError):
            failing_function()
        
        self.assertEqual(breaker.state.name, "OPEN")
        
        # Third call should fail due to open circuit
        with self.assertRaises(Exception) as context:
            failing_function()
        
        self.assertIn("Circuit breaker is OPEN", str(context.exception))
    
    def test_retry_policy_success_after_failure(self):
        """Test retry policy succeeds after initial failures"""
        call_count = 0
        
        @retry(max_attempts=3, base_delay=0.01)  # Fast retry for testing
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_retry_policy_exhausts_attempts(self):
        """Test retry policy exhausts all attempts"""
        call_count = 0
        
        @retry(max_attempts=2, base_delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError):
            always_failing_function()
        
        self.assertEqual(call_count, 2)
    
    def test_health_checker(self):
        """Test health checker functionality"""
        checker = HealthChecker()
        health_status = True
        recovery_called = False
        
        def health_check():
            return health_status
        
        def recovery_action():
            nonlocal recovery_called
            recovery_called = True
        
        checker.register_health_check("test_service", health_check, recovery_action)
        
        # Start monitoring briefly
        checker.start_monitoring(interval=0.1)
        time.sleep(0.2)
        
        # Simulate health failure
        health_status = False
        time.sleep(0.2)
        
        checker.stop_monitoring()
        
        # Check that recovery was attempted
        self.assertTrue(recovery_called)
        status = checker.get_health_status()
        self.assertFalse(status["test_service"])

class TestIntegratedSystem(unittest.TestCase):
    """Test integration between all enhanced systems"""
    
    def test_resilient_gpu_operations(self):
        """Test GPU operations with resilience patterns"""
        
        @circuit_breaker("gpu_matrix_mult", failure_threshold=2)
        @retry(max_attempts=2, base_delay=0.01)
        def resilient_matrix_multiply(a, b):
            from core.enhanced_gpu_ops import enhanced_gpu_ops
            return enhanced_gpu_ops.accelerator.matrix_multiply(a, b)
        
        # Test with valid matrices
        a = np.random.randn(10, 10).astype(np.float32)
        b = np.random.randn(10, 10).astype(np.float32)
        
        result = resilient_matrix_multiply(a, b)
        self.assertEqual(result.shape, (10, 10))
    
    def test_memory_optimization_with_monitoring(self):
        """Test memory optimization integrated with performance monitoring"""
        optimizer = MemoryOptimizer(OptimizationLevel.AGGRESSIVE)
        
        # Register a test cleanup callback
        cleanup_executed = False
        
        def test_cleanup():
            nonlocal cleanup_executed
            cleanup_executed = True
            return "Test cleanup"
        
        optimizer.register_cleanup_callback(test_cleanup)
        
        # Force optimization
        result = optimizer.optimize_memory()
        
        self.assertTrue(cleanup_executed)
        self.assertIn('optimizations', result)
        
        # Check optimization stats
        stats = optimizer.get_optimization_stats()
        self.assertGreater(stats['total_optimizations'], 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)