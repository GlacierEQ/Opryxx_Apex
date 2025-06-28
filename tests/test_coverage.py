"""
Comprehensive Test Coverage for OPRYXX System
"""

import unittest
import coverage
import sys
import os

class TestCoverage:
    def __init__(self):
        self.cov = coverage.Coverage()
        
    def run_with_coverage(self):
        """Run all tests with coverage reporting"""
        print("🔍 Running comprehensive test coverage...")
        
        # Start coverage
        self.cov.start()
        
        # Import and run all test modules
        test_modules = [
            'tests.advanced_memory_tests',
            'tests.test_safe_mode',
            'tests.test_workbench'
        ]
        
        suite = unittest.TestSuite()
        
        for module_name in test_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(module))
            except ImportError:
                print(f"⚠️ Could not import {module_name}")
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage and generate report
        self.cov.stop()
        self.cov.save()
        
        # Generate reports
        print("\n📊 COVERAGE REPORT:")
        self.cov.report()
        
        # Generate HTML report
        self.cov.html_report(directory='coverage_html')
        print("📄 HTML coverage report: coverage_html/index.html")
        
        return result.wasSuccessful()

def main():
    """Run coverage analysis"""
    coverage_runner = TestCoverage()
    success = coverage_runner.run_with_coverage()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())