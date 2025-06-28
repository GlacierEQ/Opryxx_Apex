"""
CI/CD Integration for NEXUS AI Performance Testing
"""

import json
import sys
from datetime import datetime
from performance_benchmark import PerformanceBenchmark

class CICDIntegration:
    def __init__(self):
        self.benchmark = PerformanceBenchmark()
        self.performance_thresholds = {
            'memory_operations_max_ms': 50,
            'gpu_acceleration_min_score': 50,
            'system_optimization_max_ms': 500,
            'leak_detection_max_ms': 2000,
            'overall_min_score': 60
        }
    
    def run_ci_tests(self):
        """Run CI/CD performance tests"""
        print("🚀 NEXUS AI CI/CD Performance Tests")
        print("=" * 50)
        
        # Run benchmark
        results = self.benchmark.run_full_benchmark()
        
        # Validate against thresholds
        validation_results = self._validate_performance(results)
        
        # Generate reports
        self._generate_ci_report(results, validation_results)
        
        # Return exit code
        return 0 if validation_results['passed'] else 1
    
    def _validate_performance(self, results):
        """Validate performance against thresholds"""
        validation = {
            'passed': True,
            'failures': [],
            'warnings': []
        }
        
        # Memory operations validation
        memory_ops = results['memory_operations']
        avg_memory_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
        
        if avg_memory_time > self.performance_thresholds['memory_operations_max_ms']:
            validation['failures'].append(f"Memory operations too slow: {avg_memory_time:.2f}ms > {self.performance_thresholds['memory_operations_max_ms']}ms")
            validation['passed'] = False
        
        # GPU performance validation
        gpu_perf = results['gpu_performance']
        if gpu_perf['gpu_available']:
            gpu_score = gpu_perf['acceleration_score']
            if gpu_score < self.performance_thresholds['gpu_acceleration_min_score']:
                validation['warnings'].append(f"GPU acceleration below target: {gpu_score:.1f} < {self.performance_thresholds['gpu_acceleration_min_score']}")
        
        # System optimization validation
        sys_opt = results['system_optimization']
        opt_time = sys_opt['optimization_time_ms']
        if opt_time > self.performance_thresholds['system_optimization_max_ms']:
            validation['failures'].append(f"System optimization too slow: {opt_time:.2f}ms > {self.performance_thresholds['system_optimization_max_ms']}ms")
            validation['passed'] = False
        
        # Leak detection validation
        leak_det = results['leak_detection']
        leak_time = leak_det['detection_time_ms']
        if leak_time > self.performance_thresholds['leak_detection_max_ms']:
            validation['failures'].append(f"Leak detection too slow: {leak_time:.2f}ms > {self.performance_thresholds['leak_detection_max_ms']}ms")
            validation['passed'] = False
        
        # Overall score validation
        overall_score = self._calculate_overall_score(results)
        if overall_score < self.performance_thresholds['overall_min_score']:
            validation['failures'].append(f"Overall score below minimum: {overall_score} < {self.performance_thresholds['overall_min_score']}")
            validation['passed'] = False
        
        return validation
    
    def _calculate_overall_score(self, results):
        """Calculate overall performance score"""
        score = 0
        
        # Memory operations (40%)
        memory_ops = results['memory_operations']
        avg_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
        if avg_time < 10:
            score += 40
        elif avg_time < 30:
            score += 25
        else:
            score += 10
        
        # GPU performance (30%)
        gpu_perf = results['gpu_performance']
        if gpu_perf['gpu_available']:
            gpu_score = min(30, gpu_perf['acceleration_score'] / 100 * 30)
            score += gpu_score
        
        # System optimization (20%)
        sys_opt = results['system_optimization']
        if sys_opt['optimization_time_ms'] < 100:
            score += 20
        elif sys_opt['optimization_time_ms'] < 300:
            score += 10
        
        # Leak detection (10%)
        leak_det = results['leak_detection']
        if leak_det['detection_time_ms'] < 1000:
            score += 10
        
        return int(score)
    
    def _generate_ci_report(self, results, validation):
        """Generate CI/CD report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': results,
            'validation': validation,
            'performance_score': self._calculate_overall_score(results),
            'status': 'PASSED' if validation['passed'] else 'FAILED'
        }
        
        # Save JSON report
        with open('nexus_ci_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n📊 CI/CD TEST RESULTS")
        print(f"Status: {report['status']}")
        print(f"Performance Score: {report['performance_score']}/100")
        
        if validation['failures']:
            print(f"\n❌ FAILURES:")
            for failure in validation['failures']:
                print(f"  • {failure}")
        
        if validation['warnings']:
            print(f"\n⚠️ WARNINGS:")
            for warning in validation['warnings']:
                print(f"  • {warning}")
        
        if validation['passed']:
            print(f"\n✅ All performance tests passed!")
        else:
            print(f"\n❌ Performance tests failed!")
        
        print(f"\n📄 Detailed report saved: nexus_ci_report.json")

def main():
    """Main CI/CD entry point"""
    ci_cd = CICDIntegration()
    exit_code = ci_cd.run_ci_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()