"""
Integration tests for performance benchmarks.
"""
import os
import sys
import pytest
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import benchmark module
from benchmarks.performance_benchmark import (
    benchmark,
    setup_database,
    benchmark_database_inserts,
    benchmark_database_selects,
    benchmark_cached_operations,
    benchmark_performance_monitor,
    benchmark_complex_query
)

# Test configuration
TEST_DB_URL = 'sqlite:///:memory:'
SAMPLE_SIZE = 10

@pytest.fixture(scope="module")
def db_manager():
    """Set up test database and return a DatabaseManager instance."""
    return setup_database(TEST_DB_URL)

@pytest.mark.integration
@pytest.mark.performance
def test_benchmark_database_inserts(db_manager):
    """Test database insert performance benchmark."""
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Run benchmark with small sample size for testing
    benchmark_database_inserts(db_manager, SAMPLE_SIZE)
    
    # Verify results were recorded
    assert hasattr(benchmark, 'results')
    assert 'benchmarks.performance_benchmark.benchmark_database_inserts' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['benchmarks.performance_benchmark.benchmark_database_inserts']
    assert len(timings) == 1
    assert timings[0] > 0

@pytest.mark.integration
@pytest.mark.performance
def test_benchmark_database_selects(db_manager):
    """Test database select performance benchmark."""
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Run benchmark with small sample size for testing
    results = benchmark_database_selects(db_manager, SAMPLE_SIZE)
    
    # Verify results were recorded
    assert hasattr(benchmark, 'results')
    assert 'benchmarks.performance_benchmark.benchmark_database_selects' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['benchmarks.performance_benchmark.benchmark_database_selects']
    assert len(timings) == 1
    assert timings[0] > 0
    
    # Verify query results
    assert isinstance(results, list)

@pytest.mark.integration
@pytest.mark.performance
def test_benchmark_cached_operations():
    """Test cache operations performance benchmark."""
    from core.caching import CacheManager
    
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Run benchmark with small sample size for testing
    cache = CacheManager()
    benchmark_cached_operations(cache, SAMPLE_SIZE)
    
    # Verify results were recorded
    assert hasattr(benchmark, 'results')
    assert 'benchmarks.performance_benchmark.benchmark_cached_operations' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['benchmarks.performance_benchmark.benchmark_cached_operations']
    assert len(timings) == 1
    assert timings[0] > 0

@pytest.mark.integration
@pytest.mark.performance
def test_benchmark_performance_monitor():
    """Test performance monitoring benchmark."""
    from core.performance import PerformanceMonitor
    
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Run benchmark with small sample size for testing
    monitor = PerformanceMonitor()
    benchmark_performance_monitor(monitor, SAMPLE_SIZE)
    
    # Verify results were recorded
    assert hasattr(benchmark, 'results')
    assert 'benchmarks.performance_benchmark.benchmark_performance_monitor' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['benchmarks.performance_benchmark.benchmark_performance_monitor']
    assert len(timings) == 1
    assert timings[0] > 0

@pytest.mark.integration
@pytest.mark.performance
def test_benchmark_complex_query(db_manager):
    """Test complex query performance benchmark."""
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Add some test data
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    
    # Run benchmark with small sample size for testing
    results = benchmark_complex_query(db_manager, 2)  # Reduced sample size for testing
    
    # Verify results were recorded
    assert hasattr(benchmark, 'results')
    assert 'benchmarks.performance_benchmark.benchmark_complex_query' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['benchmarks.performance_benchmark.benchmark_complex_query']
    assert len(timings) == 1
    assert timings[0] > 0
    
    # Verify query results
    assert isinstance(results, list)

def test_benchmark_decorator():
    """Test the benchmark decorator functionality."""
    # Clear any previous benchmark results
    if hasattr(benchmark, 'results'):
        benchmark.results.clear()
    
    # Define a test function
    @benchmark
    def test_function():
        time.sleep(0.01)  # Simulate work
        return "test_result"
    
    # Call the function
    result = test_function()
    
    # Verify the function worked
    assert result == "test_result"
    
    # Verify benchmark recorded the result
    assert hasattr(benchmark, 'results')
    assert 'test_benchmarks.test_function' in benchmark.results
    
    # Verify timing data was recorded
    timings = benchmark.results['test_benchmarks.test_function']
    assert len(timings) == 1
    assert timings[0] >= 10  # Should be at least 10ms (sleep time)
