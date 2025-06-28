"""
Performance benchmarking for critical components.
"""
import time
import random
import statistics
from typing import Callable, Dict, List, Tuple, TypeVar, Any
from functools import wraps

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.db_utils import DatabaseManager, with_retry
from core.caching import CacheManager, cached
from core.performance import PerformanceMonitor, monitor_performance

# Type variables
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Initialize performance monitor
perf_monitor = PerformanceMonitor()

# Initialize cache
cache = CacheManager()

# Database setup
Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'benchmark_test'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    value = Column(Integer)
    category = Column(String(50))


def setup_database(db_url: str = 'sqlite:///:memory:') -> DatabaseManager:
    """Set up test database and return a DatabaseManager instance."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return DatabaseManager(engine)

def benchmark(func: F) -> F:
    """Decorator to benchmark a function's execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Record the benchmark result
        if not hasattr(benchmark, 'results'):
            benchmark.results = {}
        
        if func_name not in benchmark.results:
            benchmark.results[func_name] = []
            
        benchmark.results[func_name].append(duration)
        
        return result
    return cast(F, wrapper)

def print_benchmark_results():
    """Print benchmark results in a formatted table."""
    if not hasattr(benchmark, 'results') or not benchmark.results:
        print("No benchmark results to display.")
        return
    
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("=" * 80)
    
    # Calculate statistics for each benchmark
    results = []
    for func_name, durations in benchmark.results.items():
        if not durations:
            continue
            
        stats = {
            'function': func_name,
            'runs': len(durations),
            'avg_ms': statistics.mean(durations),
            'min_ms': min(durations),
            'max_ms': max(durations),
            'median_ms': statistics.median(durations),
            'stdev_ms': statistics.stdev(durations) if len(durations) > 1 else 0,
        }
        results.append(stats)
    
    # Sort by average time (descending)
    results.sort(key=lambda x: x['avg_ms'], reverse=True)
    
    # Print table header
    print(f"{'Function':<50} {'Runs':>6} {'Avg (ms)':>12} {'Min (ms)':>12} {'Max (ms)':>12} {'Median (ms)':>12} {'StDev':>12}")
    print("-" * 120)
    
    # Print each row
    for stats in results:
        print(
            f"{stats['function']:<50} "
            f"{stats['runs']:>6} "
            f"{stats['avg_ms']:>12.4f} "
            f"{stats['min_ms']:>12.4f} "
            f"{stats['max_ms']:>12.4f} "
            f"{stats['median_ms']:>12.4f} "
            f"{stats['stdev_ms']:>12.4f}"
        )
    
    print("=" * 80 + "\n")

# Benchmark functions

@benchmark
def benchmark_database_inserts(db_manager: DatabaseManager, count: int = 1000) -> None:
    """Benchmark database insert performance."""
    data = [
        {
            'name': f'test_{i}',
            'description': 'A test description ' * 10,
            'value': i,
            'category': 'test'
        }
        for i in range(count)
    ]
    
    with db_manager.session_scope() as session:
        session.bulk_insert_mappings(TestModel, data)

@benchmark
def benchmark_database_selects(db_manager: DatabaseManager, count: int = 1000) -> List[Dict]:
    """Benchmark database select performance."""
    results = []
    for i in range(count):
        with db_manager.session_scope() as session:
            result = session.query(TestModel).filter(
                TestModel.value == i % 100
            ).all()
            results.extend([r.__dict__ for r in result])
    return results

@benchmark
def benchmark_cached_operations(cache: CacheManager, count: int = 10000) -> None:
    """Benchmark cache operations."""
    for i in range(count):
        key = f'test_{i % 100}'
        value = {'id': i, 'data': 'x' * 100}
        cache.set(key, value, ttl=60)
        
        # Read back half the time
        if i % 2 == 0:
            _ = cache.get(key)

@benchmark
def benchmark_performance_monitor(monitor: PerformanceMonitor, count: int = 10000) -> None:
    """Benchmark performance monitoring overhead."""
    for i in range(count):
        with monitor.measure('test_operation'):
            # Simulate some work
            _ = [x * 2 for x in range(1000)]

@benchmark
def benchmark_complex_query(db_manager: DatabaseManager, count: int = 100) -> List[Dict]:
    """Benchmark complex query performance."""
    results = []
    for _ in range(count):
        with db_manager.session_scope() as session:
            result = session.query(
                TestModel.category,
                TestModel.value
            ).filter(
                TestModel.value > 0,
                TestModel.name.like('test_%')
            ).order_by(
                TestModel.value.desc()
            ).limit(100).all()
            
            results.extend([r._asdict() for r in result])
    
    return results

def run_benchmarks():
    """Run all benchmarks."""
    print("Setting up benchmark environment...")
    
    # Initialize components
    db_manager = setup_database()
    cache = CacheManager()
    monitor = PerformanceMonitor()
    
    # Warm-up phase
    print("Warming up...")
    benchmark_database_inserts(db_manager, 100)
    benchmark_database_selects(db_manager, 100)
    benchmark_cached_operations(cache, 1000)
    benchmark_performance_monitor(monitor, 1000)
    benchmark_complex_query(db_manager, 10)
    
    # Clear benchmark results after warm-up
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Run benchmarks
    print("\nRunning benchmarks...")
    
    # Database benchmarks
    print("\nBenchmarking database operations...")
    benchmark_database_inserts(db_manager, 1000)
    benchmark_database_selects(db_manager, 1000)
    benchmark_complex_query(db_manager, 100)
    
    # Cache benchmarks
    print("\nBenchmarking cache operations...")
    benchmark_cached_operations(cache, 10000)
    
    # Performance monitoring benchmarks
    print("\nBenchmarking performance monitoring...")
    benchmark_performance_monitor(monitor, 10000)
    
    # Print results
    print_benchmark_results()

if __name__ == "__main__":
    run_benchmarks()
