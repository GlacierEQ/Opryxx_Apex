# OPRYXX API Documentation

## Core Architecture

### RecoveryService
Main service for system recovery operations.

```python
from services.recovery_service import RecoveryService

service = RecoveryService()
results = service.execute_recovery()
```

#### Methods
- `execute_recovery()` - Execute complete recovery sequence
- `get_status()` - Get current recovery status
- `register_module(module)` - Register recovery module

### Memory Optimizer
Advanced memory management and optimization.

```python
from enhancements.memory_optimizer import AdvancedMemoryOptimizer

optimizer = AdvancedMemoryOptimizer()
stats = optimizer.get_memory_stats()
optimizations = optimizer.optimize_memory_aggressive()
```

#### Methods
- `get_memory_stats()` - Get detailed memory statistics
- `optimize_memory_aggressive()` - Perform aggressive optimization
- `auto_memory_management()` - Automatic memory management
- `monitor_memory_leaks()` - Monitor for memory leaks

### GPU Acceleration
Hardware acceleration for AI operations.

```python
from enhancements.gpu_acceleration import GPUAcceleration

gpu = GPUAcceleration()
status = gpu.get_gpu_status()
optimizations = gpu.optimize_gpu_memory()
```

#### Methods
- `get_gpu_status()` - Get GPU hardware status
- `optimize_gpu_memory()` - Optimize GPU memory usage
- `enable_ai_acceleration()` - Enable AI acceleration features

### System Validator
Comprehensive system validation and testing.

```python
from enhancements.system_validator import NexusSystemValidator

validator = NexusSystemValidator()
results = validator.run_full_validation()
```

#### Methods
- `test_memory_leak_detection()` - Test memory leak detection
- `test_memory_thresholds()` - Test memory threshold monitoring
- `benchmark_memory_operations()` - Benchmark memory operations
- `test_gpu_detection()` - Test GPU/NPU detection

## Configuration

### Security Configuration
```python
from security.security_config import SecurityConfig

security = SecurityConfig()
hashed = security.hash_password("password")
valid = security.verify_password("password", hashed)
```

### Performance Configuration
```python
# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'memory_operations_max_ms': 50,
    'gpu_acceleration_min_score': 50,
    'system_optimization_max_ms': 500,
    'leak_detection_max_ms': 2000,
    'overall_min_score': 60
}
```

## Error Handling

All methods return structured results:

```python
{
    'success': bool,
    'message': str,
    'data': dict,
    'timestamp': str
}
```

## Performance Monitoring

### Benchmarking
```python
from performance_benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark()
results = benchmark.run_full_benchmark()
```

### CI/CD Integration
```python
from ci_cd_integration import CICDIntegration

ci_cd = CICDIntegration()
exit_code = ci_cd.run_ci_tests()
```