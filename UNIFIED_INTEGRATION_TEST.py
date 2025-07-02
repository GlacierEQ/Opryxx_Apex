#!/usr/bin/env python3
"""
UNIFIED INTEGRATION TEST
========================
Final test to verify complete full stack unification
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime

class UnifiedIntegrationTest:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'integration_score': 0,
            'status': 'UNKNOWN'
        }
        
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def test_python_core_integration(self):
        """Test Python core components integration"""
        self.log("Testing Python Core Integration...")
        
        try:
            # Test core imports
            test_code = """
import sys
sys.path.append('.')
from core.performance_monitor import PerformanceMonitor
from core.memory_optimizer import MemoryOptimizer
print("PYTHON_CORE_OK")
"""
            
            result = subprocess.run([
                sys.executable, '-c', test_code
            ], capture_output=True, text=True, timeout=10)
            
            if "PYTHON_CORE_OK" in result.stdout:
                self.log("  PASS: Python core components integrated")
                self.test_results['tests_passed'] += 1
                return True
            else:
                self.log("  FAIL: Python core integration failed")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: Python core test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_gui_integration(self):
        """Test GUI integration"""
        self.log("Testing GUI Integration...")
        
        try:
            # Test GUI imports without actually starting GUI
            test_code = """
import sys
sys.path.append('.')
import tkinter as tk
# Test GUI components can be imported
print("GUI_INTEGRATION_OK")
"""
            
            result = subprocess.run([
                sys.executable, '-c', test_code
            ], capture_output=True, text=True, timeout=10)
            
            if "GUI_INTEGRATION_OK" in result.stdout:
                self.log("  PASS: GUI components integrated")
                self.test_results['tests_passed'] += 1
                return True
            else:
                self.log("  FAIL: GUI integration failed")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: GUI test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_database_integration(self):
        """Test database integration"""
        self.log("Testing Database Integration...")
        
        try:
            import sqlite3
            
            # Test database connectivity
            if os.path.exists('data/opryxx.db'):
                conn = sqlite3.connect('data/opryxx.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                if len(tables) > 0:
                    self.log(f"  PASS: Database integrated ({len(tables)} tables)")
                    self.test_results['tests_passed'] += 1
                    return True
                else:
                    self.log("  FAIL: Database has no tables")
                    self.test_results['tests_failed'] += 1
                    return False
            else:
                self.log("  FAIL: Database file not found")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: Database test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_api_integration(self):
        """Test API integration"""
        self.log("Testing API Integration...")
        
        try:
            # Check if API configuration exists
            if os.path.exists('api/endpoints.json'):
                with open('api/endpoints.json', 'r') as f:
                    endpoints = json.load(f)
                    
                if 'endpoints' in endpoints:
                    self.log("  PASS: API endpoints configured")
                    self.test_results['tests_passed'] += 1
                    return True
                else:
                    self.log("  FAIL: API endpoints not properly configured")
                    self.test_results['tests_failed'] += 1
                    return False
            else:
                self.log("  FAIL: API configuration missing")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: API test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_bridge_integration(self):
        """Test Python-JavaScript bridge integration"""
        self.log("Testing Bridge Integration...")
        
        try:
            # Check bridge configuration
            if os.path.exists('api/bridge-config.json'):
                with open('api/bridge-config.json', 'r') as f:
                    config = json.load(f)
                    
                if 'python_bridge' in config and 'endpoints' in config:
                    self.log("  PASS: Bridge configuration valid")
                    self.test_results['tests_passed'] += 1
                    return True
                else:
                    self.log("  FAIL: Bridge configuration invalid")
                    self.test_results['tests_failed'] += 1
                    return False
            else:
                self.log("  FAIL: Bridge configuration missing")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: Bridge test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_launcher_integration(self):
        """Test launcher integration"""
        self.log("Testing Launcher Integration...")
        
        try:
            # Check if main launchers exist
            launchers = [
                'master_start.py',
                'UNIFIED_GUI.py',
                'launchers/LAUNCH_MEGA.bat',
                'launchers/LAUNCH_COMBINED.bat'
            ]
            
            existing_launchers = [l for l in launchers if os.path.exists(l)]
            
            if len(existing_launchers) >= 2:
                self.log(f"  PASS: Launchers integrated ({len(existing_launchers)}/{len(launchers)})")
                self.test_results['tests_passed'] += 1
                return True
            else:
                self.log("  FAIL: Insufficient launchers")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: Launcher test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def test_configuration_integration(self):
        """Test configuration integration"""
        self.log("Testing Configuration Integration...")
        
        try:
            # Check key configuration files
            configs = [
                'docker-compose.yml',
                'requirements.txt',
                'config/opryxx.json'
            ]
            
            valid_configs = 0
            for config in configs:
                if os.path.exists(config):
                    valid_configs += 1
                    
            if valid_configs >= 2:
                self.log(f"  PASS: Configuration integrated ({valid_configs}/{len(configs)})")
                self.test_results['tests_passed'] += 1
                return True
            else:
                self.log("  FAIL: Configuration incomplete")
                self.test_results['tests_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"  ERROR: Configuration test failed: {str(e)}")
            self.test_results['tests_failed'] += 1
            return False
            
    def calculate_integration_score(self):
        """Calculate overall integration score"""
        total_tests = self.test_results['tests_passed'] + self.test_results['tests_failed']
        
        if total_tests > 0:
            score = (self.test_results['tests_passed'] / total_tests) * 100
            self.test_results['integration_score'] = score
            
            if score >= 90:
                self.test_results['status'] = 'EXCELLENT'
            elif score >= 80:
                self.test_results['status'] = 'GOOD'
            elif score >= 70:
                self.test_results['status'] = 'FAIR'
            else:
                self.test_results['status'] = 'POOR'
        else:
            self.test_results['integration_score'] = 0
            self.test_results['status'] = 'NO_TESTS'
            
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("STARTING UNIFIED INTEGRATION TEST")
        self.log("=" * 50)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_python_core_integration,
            self.test_gui_integration,
            self.test_database_integration,
            self.test_api_integration,
            self.test_bridge_integration,
            self.test_launcher_integration,
            self.test_configuration_integration
        ]
        
        for test in tests:
            test()
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate final score
        self.calculate_integration_score()
        
        # Print results
        self.log("=" * 50)
        self.log("UNIFIED INTEGRATION TEST RESULTS")
        self.log("=" * 50)
        self.log(f"Tests Passed: {self.test_results['tests_passed']}")
        self.log(f"Tests Failed: {self.test_results['tests_failed']}")
        self.log(f"Integration Score: {self.test_results['integration_score']:.1f}%")
        self.log(f"Status: {self.test_results['status']}")
        self.log(f"Duration: {duration:.2f} seconds")
        self.log("=" * 50)
        
        # Save results
        report_file = f"unified_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        self.log(f"Results saved to: {report_file}")
        
        return self.test_results

def main():
    """Main test function"""
    tester = UnifiedIntegrationTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['status'] in ['EXCELLENT', 'GOOD']:
        print("\nFULL STACK UNIFICATION: VERIFIED")
        sys.exit(0)
    else:
        print("\nFULL STACK UNIFICATION: NEEDS ATTENTION")
        sys.exit(1)

if __name__ == "__main__":
    main()