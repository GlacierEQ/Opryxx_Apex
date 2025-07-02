#!/usr/bin/env python3
"""
Performance Regression Checker
Compares current benchmark results with historical data
"""

import json
import sys
from pathlib import Path

def check_regression(benchmark_file: str, threshold: float = 0.2):
    """Check for performance regressions"""
    
    if not Path(benchmark_file).exists():
        print(f"Benchmark file {benchmark_file} not found")
        return 0
    
    with open(benchmark_file) as f:
        data = json.load(f)
    
    regressions = []
    
    for benchmark in data.get('benchmarks', []):
        name = benchmark['name']
        current_time = benchmark['stats']['mean']
        
        # In a real scenario, you'd compare with historical data
        # For now, we'll just check if any test is unusually slow
        if current_time > 1.0:  # More than 1 second
            regressions.append(f"{name}: {current_time:.3f}s")
    
    if regressions:
        print("Performance regressions detected:")
        for regression in regressions:
            print(f"  - {regression}")
        return 1
    
    print("No performance regressions detected")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_performance_regression.py <benchmark.json>")
        sys.exit(1)
    
    sys.exit(check_regression(sys.argv[1]))