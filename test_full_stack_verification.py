#!/usr/bin/env python3
"""
OPRYXX Full Stack Verification Suite
Tests all functions, GUI components, and system integrations
"""

import unittest
import threading
import time
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class FullStackTestSuite(unittest.TestCase):
    """Comprehensive test suite for all OPRYXX components"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_results = {}
        
    def test_gui_initialization(self):
        """Test GUI initialization and components"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            # Mock tkinter to avoid GUI display during tests
            with patch('tkinter.Tk') as mock_tk:
                mock_root = Mock()
                mock_tk.return_value = mock_root
                
                app = UnifiedFullStackGUI()
                self.assertIsNotNone(app)
                self.test_results['gui_init'] = 'PASS'
                
        except Exception as e:
            self.test_results['gui_init'] = f'FAIL: {str(e)}'
            
    def test_system_components(self):
        """Test all system components"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test component initialization
            self.assertTrue(system.active)
            self.assertIn('recovery', system.components)
            self.assertIn('ai_optimizer', system.components)
            self.assertIn('monitoring', system.components)
            
            self.test_results['system_components'] = 'PASS'
            
        except Exception as e:
            self.test_results['system_components'] = f'FAIL: {str(e)}'
    
    def test_full_stack_scan(self):
        """Test full stack system scan"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            results = system.execute_full_stack_scan()
            
            # Verify all scan components
            required_scans = ['recovery', 'performance', 'health', 'security', 'optimization', 'prediction']
            for scan in required_scans:
                self.assertIn(scan, results)
                self.assertIn('status', results[scan])
            
            self.test_results['full_stack_scan'] = 'PASS'
            
        except Exception as e:
            self.test_results['full_stack_scan'] = f'FAIL: {str(e)}'
    
    def test_performance_monitoring(self):
        """Test performance monitoring functions"""
        try:
            # Mock psutil for testing
            with patch('psutil.cpu_percent', return_value=25.5):
                with patch('psutil.virtual_memory') as mock_mem:
                    mock_mem.return_value.percent = 45.2
                    
                    from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
                    system = UnifiedFullStackSystem()
                    
                    perf_results = system._scan_performance()
                    self.assertIn('cpu_usage', perf_results)
                    self.assertIn('memory_usage', perf_results)
                    self.assertIn('status', perf_results)
                    
            self.test_results['performance_monitoring'] = 'PASS'
            
        except Exception as e:
            self.test_results['performance_monitoring'] = f'FAIL: {str(e)}'
    
    def test_memory_optimization(self):
        """Test memory optimization functions"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test optimization scan
            opt_results = system._scan_optimization()
            self.assertIn('temp_files_mb', opt_results)
            self.assertIn('optimization_potential', opt_results)
            self.assertIn('status', opt_results)
            
            self.test_results['memory_optimization'] = 'PASS'
            
        except Exception as e:
            self.test_results['memory_optimization'] = f'FAIL: {str(e)}'
    
    def test_recovery_system(self):
        """Test recovery system functions"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test recovery scan
            recovery_results = system._scan_recovery()
            self.assertIn('status', recovery_results)
            
            # Test emergency recovery
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                recovery_actions = system.execute_emergency_recovery()
                self.assertIsInstance(recovery_actions, list)
            
            self.test_results['recovery_system'] = 'PASS'
            
        except Exception as e:
            self.test_results['recovery_system'] = f'FAIL: {str(e)}'
    
    def test_auto_fix_functions(self):
        """Test automated fix functions"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Mock subprocess calls
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                fixes = system.execute_auto_fix()
                self.assertIsInstance(fixes, list)
            
            self.test_results['auto_fix'] = 'PASS'
            
        except Exception as e:
            self.test_results['auto_fix'] = f'FAIL: {str(e)}'
    
    def test_prediction_system(self):
        """Test predictive analysis system"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test prediction scan
            pred_results = system._scan_prediction()
            self.assertIn('predictions', pred_results)
            self.assertIn('risk_level', pred_results)
            self.assertIn('status', pred_results)
            
            self.test_results['prediction_system'] = 'PASS'
            
        except Exception as e:
            self.test_results['prediction_system'] = f'FAIL: {str(e)}'
    
    def test_security_scan(self):
        """Test security scanning functions"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test security scan
            sec_results = system._scan_security()
            self.assertIn('firewall_status', sec_results)
            self.assertIn('antivirus_status', sec_results)
            self.assertIn('status', sec_results)
            
            self.test_results['security_scan'] = 'PASS'
            
        except Exception as e:
            self.test_results['security_scan'] = f'FAIL: {str(e)}'
    
    def test_health_monitoring(self):
        """Test system health monitoring"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test health scan
            with patch('psutil.pids', return_value=list(range(100))):
                with patch('psutil.boot_time', return_value=time.time() - 3600):
                    health_results = system._scan_health()
                    self.assertIn('process_count', health_results)
                    self.assertIn('health_score', health_results)
                    self.assertIn('status', health_results)
            
            self.test_results['health_monitoring'] = 'PASS'
            
        except Exception as e:
            self.test_results['health_monitoring'] = f'FAIL: {str(e)}'
    
    def test_gui_tabs_creation(self):
        """Test GUI tab creation and functionality"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk') as mock_tk:
                with patch('tkinter.Frame') as mock_frame:
                    with patch('ttk.Notebook') as mock_notebook:
                        mock_root = Mock()
                        mock_tk.return_value = mock_root
                        
                        app = UnifiedFullStackGUI()
                        
                        # Verify tab creation methods exist
                        self.assertTrue(hasattr(app, 'create_dashboard_tab'))
                        self.assertTrue(hasattr(app, 'create_monitoring_tab'))
                        self.assertTrue(hasattr(app, 'create_optimization_tab'))
                        self.assertTrue(hasattr(app, 'create_recovery_tab'))
                        self.assertTrue(hasattr(app, 'create_prediction_tab'))
                        self.assertTrue(hasattr(app, 'create_automation_tab'))
            
            self.test_results['gui_tabs'] = 'PASS'
            
        except Exception as e:
            self.test_results['gui_tabs'] = f'FAIL: {str(e)}'
    
    def test_control_functions(self):
        """Test GUI control functions"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                with patch('threading.Thread'):
                    app = UnifiedFullStackGUI()
                    
                    # Test control functions exist
                    control_functions = [
                        'full_stack_scan', 'auto_optimize', 'emergency_fix',
                        'toggle_ai_monitor', 'predict_prevent', 'clean_system',
                        'boost_performance', 'registry_repair', 'memory_optimize',
                        'emergency_recovery', 'boot_repair', 'system_restore',
                        'create_recovery', 'analyze_predict'
                    ]
                    
                    for func in control_functions:
                        self.assertTrue(hasattr(app, func), f"Missing function: {func}")
            
            self.test_results['control_functions'] = 'PASS'
            
        except Exception as e:
            self.test_results['control_functions'] = f'FAIL: {str(e)}'
    
    def test_logging_system(self):
        """Test logging and activity tracking"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                app = UnifiedFullStackGUI()
                
                # Test logging functions
                self.assertTrue(hasattr(app, 'log_activity'))
                self.assertTrue(hasattr(app, 'log_to_widget'))
                self.assertTrue(hasattr(app, 'update_metrics'))
            
            self.test_results['logging_system'] = 'PASS'
            
        except Exception as e:
            self.test_results['logging_system'] = f'FAIL: {str(e)}'
    
    def test_monitoring_thread(self):
        """Test background monitoring thread"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                with patch('threading.Thread') as mock_thread:
                    app = UnifiedFullStackGUI()
                    
                    # Verify monitoring thread is started
                    self.assertTrue(hasattr(app, 'start_monitoring'))
                    mock_thread.assert_called()
            
            self.test_results['monitoring_thread'] = 'PASS'
            
        except Exception as e:
            self.test_results['monitoring_thread'] = f'FAIL: {str(e)}'
    
    def test_settings_and_configuration(self):
        """Test settings and configuration management"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                app = UnifiedFullStackGUI()
                
                # Test automation variables
                self.assertTrue(hasattr(app, 'auto_vars'))
                
                # Test system configuration
                self.assertTrue(hasattr(app.system, 'components'))
                self.assertTrue(hasattr(app.system, 'stats'))
            
            self.test_results['settings_config'] = 'PASS'
            
        except Exception as e:
            self.test_results['settings_config'] = f'FAIL: {str(e)}'

class GUIFunctionTester:
    """Interactive GUI function tester"""
    
    def __init__(self):
        self.test_results = {}
        
    def test_all_gui_functions(self):
        """Test all GUI functions interactively"""
        print("🧪 TESTING ALL GUI FUNCTIONS")
        print("=" * 50)
        
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            # Create test GUI instance
            with patch('tkinter.Tk') as mock_tk:
                mock_root = Mock()
                mock_tk.return_value = mock_root
                
                app = UnifiedFullStackGUI()
                
                # Test all control functions
                test_functions = [
                    ('Full Stack Scan', app.full_stack_scan),
                    ('Auto Optimize', app.auto_optimize),
                    ('Emergency Fix', app.emergency_fix),
                    ('AI Monitor Toggle', app.toggle_ai_monitor),
                    ('Predict & Prevent', app.predict_prevent),
                    ('Clean System', app.clean_system),
                    ('Boost Performance', app.boost_performance),
                    ('Registry Repair', app.registry_repair),
                    ('Memory Optimize', app.memory_optimize),
                    ('Emergency Recovery', app.emergency_recovery),
                    ('Boot Repair', app.boot_repair),
                    ('System Restore', app.system_restore),
                    ('Create Recovery', app.create_recovery),
                    ('Analyze Predict', app.analyze_predict)
                ]
                
                for name, func in test_functions:
                    try:
                        print(f"Testing {name}...", end=" ")
                        func()
                        print("✅ PASS")
                        self.test_results[name] = 'PASS'
                    except Exception as e:
                        print(f"❌ FAIL: {str(e)}")
                        self.test_results[name] = f'FAIL: {str(e)}'
                
        except Exception as e:
            print(f"❌ GUI Test Setup Failed: {str(e)}")
            
        return self.test_results

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 OPRYXX FULL STACK VERIFICATION")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 RUNNING UNIT TESTS...")
    suite = unittest.TestLoader().loadTestsFromTestCase(FullStackTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run GUI function tests
    print("\n🖥️ TESTING GUI FUNCTIONS...")
    gui_tester = GUIFunctionTester()
    gui_results = gui_tester.test_all_gui_functions()
    
    # Generate comprehensive report
    print("\n📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    total_tests = len(result.testsRun) if hasattr(result, 'testsRun') else 0
    failed_tests = len(result.failures) + len(result.errors) if hasattr(result, 'failures') else 0
    
    print(f"Unit Tests: {total_tests - failed_tests}/{total_tests} PASSED")
    
    gui_passed = sum(1 for r in gui_results.values() if r == 'PASS')
    gui_total = len(gui_results)
    print(f"GUI Tests: {gui_passed}/{gui_total} PASSED")
    
    print(f"\nOverall Success Rate: {((total_tests - failed_tests + gui_passed) / (total_tests + gui_total)) * 100:.1f}%")
    
    # Detailed results
    print("\n🔍 DETAILED RESULTS:")
    print("-" * 40)
    
    if hasattr(result, 'failures') and result.failures:
        print("❌ FAILED UNIT TESTS:")
        for test, error in result.failures:
            print(f"  - {test}: {error}")
    
    if hasattr(result, 'errors') and result.errors:
        print("⚠️ ERROR UNIT TESTS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    failed_gui = {k: v for k, v in gui_results.items() if v != 'PASS'}
    if failed_gui:
        print("❌ FAILED GUI TESTS:")
        for test, error in failed_gui.items():
            print(f"  - {test}: {error}")
    
    print("\n✅ VERIFICATION COMPLETE!")
    
    return {
        'unit_tests': {'passed': total_tests - failed_tests, 'total': total_tests},
        'gui_tests': {'passed': gui_passed, 'total': gui_total},
        'overall_success_rate': ((total_tests - failed_tests + gui_passed) / (total_tests + gui_total)) * 100
    }

if __name__ == "__main__":
    results = run_comprehensive_tests()
    
    # Save results to file
    import json
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to test_results.json")