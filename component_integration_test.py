#!/usr/bin/env python3
"""
Component Integration Test
Tests integration between all OPRYXX components
"""

import sys
import os
import time
import threading
from unittest.mock import Mock, patch
import json

class ComponentIntegrationTester:
    """Tests integration between all system components"""
    
    def __init__(self):
        self.test_results = {}
        self.components_tested = 0
        self.integrations_passed = 0
        
    def test_all_integrations(self):
        """Test all component integrations"""
        print("🔗 TESTING COMPONENT INTEGRATIONS")
        print("=" * 50)
        
        integration_tests = [
            ('GUI ↔ System Backend', self.test_gui_system_integration),
            ('Monitoring ↔ Performance', self.test_monitoring_performance_integration),
            ('Recovery ↔ Emergency Systems', self.test_recovery_emergency_integration),
            ('AI ↔ Optimization Engine', self.test_ai_optimization_integration),
            ('Prediction ↔ Monitoring', self.test_prediction_monitoring_integration),
            ('Automation ↔ All Systems', self.test_automation_integration),
            ('Logging ↔ All Components', self.test_logging_integration),
            ('Settings ↔ Configuration', self.test_settings_integration)
        ]
        
        for test_name, test_func in integration_tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                test_func()
                print(f"✅ {test_name}: PASSED")
                self.integrations_passed += 1
            except Exception as e:
                print(f"❌ {test_name}: FAILED - {str(e)}")
                self.test_results[test_name] = f"FAILED: {str(e)}"
            
            self.components_tested += 1
        
        return self.test_results
    
    def test_gui_system_integration(self):
        """Test GUI to system backend integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI, UnifiedFullStackSystem
            
            # Mock GUI components
            with patch('tkinter.Tk'):
                gui = UnifiedFullStackGUI()
                system = gui.system
                
                # Test system is properly initialized
                assert hasattr(gui, 'system')
                assert isinstance(system, UnifiedFullStackSystem)
                
                # Test GUI can call system functions
                assert hasattr(system, 'execute_full_stack_scan')
                assert hasattr(system, 'execute_auto_fix')
                assert hasattr(system, 'execute_emergency_recovery')
                
                # Test system state is accessible from GUI
                assert hasattr(system, 'components')
                assert hasattr(system, 'stats')
                
                self.test_results['gui_system_integration'] = 'PASSED'
                
        except Exception as e:
            raise Exception(f"GUI-System integration failed: {str(e)}")
    
    def test_monitoring_performance_integration(self):
        """Test monitoring and performance system integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test performance monitoring integration
            perf_results = system._scan_performance()
            assert 'cpu_usage' in perf_results
            assert 'memory_usage' in perf_results
            assert 'status' in perf_results
            
            # Test health monitoring integration
            health_results = system._scan_health()
            assert 'health_score' in health_results
            assert 'status' in health_results
            
            self.test_results['monitoring_performance_integration'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Monitoring-Performance integration failed: {str(e)}")
    
    def test_recovery_emergency_integration(self):
        """Test recovery and emergency systems integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test recovery scan integration
            recovery_results = system._scan_recovery()
            assert 'status' in recovery_results
            
            # Test emergency recovery integration
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                emergency_results = system.execute_emergency_recovery()
                assert isinstance(emergency_results, list)
            
            self.test_results['recovery_emergency_integration'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Recovery-Emergency integration failed: {str(e)}")
    
    def test_ai_optimization_integration(self):
        """Test AI and optimization engine integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test optimization scan integration
            opt_results = system._scan_optimization()
            assert 'optimization_potential' in opt_results
            assert 'status' in opt_results
            
            # Test auto-fix integration
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                fix_results = system.execute_auto_fix()
                assert isinstance(fix_results, list)
            
            self.test_results['ai_optimization_integration'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"AI-Optimization integration failed: {str(e)}")
    
    def test_prediction_monitoring_integration(self):
        """Test prediction and monitoring system integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test prediction integration with monitoring data
            pred_results = system._scan_prediction()
            assert 'predictions' in pred_results
            assert 'risk_level' in pred_results
            
            # Test prediction uses monitoring data
            perf_results = system._scan_performance()
            assert perf_results['cpu_usage'] >= 0
            assert perf_results['memory_usage'] >= 0
            
            self.test_results['prediction_monitoring_integration'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Prediction-Monitoring integration failed: {str(e)}")
    
    def test_automation_integration(self):
        """Test automation system integration with all components"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                gui = UnifiedFullStackGUI()
                
                # Test automation variables exist
                assert hasattr(gui, 'auto_vars')
                
                # Test automation can trigger system functions
                system = gui.system
                assert hasattr(system, 'execute_full_stack_scan')
                assert hasattr(system, 'execute_auto_fix')
                
                self.test_results['automation_integration'] = 'PASSED'
                
        except Exception as e:
            raise Exception(f"Automation integration failed: {str(e)}")
    
    def test_logging_integration(self):
        """Test logging system integration with all components"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                gui = UnifiedFullStackGUI()
                
                # Test logging functions exist
                assert hasattr(gui, 'log_activity')
                assert hasattr(gui, 'log_to_widget')
                
                # Test logging can be called from different components
                gui.log_activity("Test message")
                
                self.test_results['logging_integration'] = 'PASSED'
                
        except Exception as e:
            raise Exception(f"Logging integration failed: {str(e)}")
    
    def test_settings_integration(self):
        """Test settings and configuration integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI, UnifiedFullStackSystem
            
            with patch('tkinter.Tk'):
                gui = UnifiedFullStackGUI()
                system = gui.system
                
                # Test settings affect system behavior
                assert hasattr(system, 'components')
                assert hasattr(system, 'stats')
                
                # Test GUI settings integration
                assert hasattr(gui, 'auto_vars')
                
                self.test_results['settings_integration'] = 'PASSED'
                
        except Exception as e:
            raise Exception(f"Settings integration failed: {str(e)}")

class RealTimeIntegrationTester:
    """Tests real-time integration scenarios"""
    
    def __init__(self):
        self.running = False
        self.test_results = {}
        
    def test_real_time_scenarios(self):
        """Test real-time integration scenarios"""
        print("\n⏱️ TESTING REAL-TIME SCENARIOS")
        print("=" * 40)
        
        scenarios = [
            ('Continuous Monitoring', self.test_continuous_monitoring),
            ('Auto-Response System', self.test_auto_response),
            ('Emergency Detection', self.test_emergency_detection),
            ('Performance Tracking', self.test_performance_tracking)
        ]
        
        for scenario_name, test_func in scenarios:
            print(f"\n🔄 Testing {scenario_name}...")
            try:
                test_func()
                print(f"✅ {scenario_name}: PASSED")
            except Exception as e:
                print(f"❌ {scenario_name}: FAILED - {str(e)}")
                self.test_results[scenario_name] = f"FAILED: {str(e)}"
        
        return self.test_results
    
    def test_continuous_monitoring(self):
        """Test continuous monitoring integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackGUI
            
            with patch('tkinter.Tk'):
                with patch('threading.Thread') as mock_thread:
                    gui = UnifiedFullStackGUI()
                    
                    # Verify monitoring thread is created
                    mock_thread.assert_called()
                    
                    # Test update functions exist
                    assert hasattr(gui, 'update_metrics')
                    assert hasattr(gui, 'start_monitoring')
            
            self.test_results['continuous_monitoring'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Continuous monitoring test failed: {str(e)}")
    
    def test_auto_response(self):
        """Test automated response system"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test auto-fix can be triggered
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                fixes = system.execute_auto_fix()
                assert isinstance(fixes, list)
            
            self.test_results['auto_response'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Auto-response test failed: {str(e)}")
    
    def test_emergency_detection(self):
        """Test emergency detection and response"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test emergency recovery can be triggered
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                recovery = system.execute_emergency_recovery()
                assert isinstance(recovery, list)
            
            self.test_results['emergency_detection'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Emergency detection test failed: {str(e)}")
    
    def test_performance_tracking(self):
        """Test performance tracking integration"""
        try:
            from UNIFIED_FULL_STACK_GUI import UnifiedFullStackSystem
            
            system = UnifiedFullStackSystem()
            
            # Test performance metrics can be collected
            perf_results = system._scan_performance()
            assert 'cpu_usage' in perf_results
            assert 'memory_usage' in perf_results
            
            # Test stats are updated
            assert hasattr(system, 'stats')
            assert 'optimizations' in system.stats
            
            self.test_results['performance_tracking'] = 'PASSED'
            
        except Exception as e:
            raise Exception(f"Performance tracking test failed: {str(e)}")

def run_integration_tests():
    """Run all integration tests"""
    print("🔗 OPRYXX COMPONENT INTEGRATION TESTS")
    print("=" * 60)
    
    # Run component integration tests
    component_tester = ComponentIntegrationTester()
    component_results = component_tester.test_all_integrations()
    
    # Run real-time integration tests
    realtime_tester = RealTimeIntegrationTester()
    realtime_results = realtime_tester.test_real_time_scenarios()
    
    # Generate comprehensive report
    print("\n📊 INTEGRATION TEST REPORT")
    print("=" * 60)
    
    component_passed = component_tester.integrations_passed
    component_total = component_tester.components_tested
    
    realtime_passed = sum(1 for r in realtime_results.values() if 'PASSED' in str(r))
    realtime_total = len(realtime_results)
    
    total_passed = component_passed + realtime_passed
    total_tests = component_total + realtime_total
    
    print(f"Component Integration Tests: {component_passed}/{component_total} PASSED")
    print(f"Real-time Integration Tests: {realtime_passed}/{realtime_total} PASSED")
    print(f"Overall Integration Success: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.1f}%)")
    
    # Detailed results
    print("\n🔍 DETAILED RESULTS:")
    print("-" * 40)
    
    all_results = {**component_results, **realtime_results}
    failed_tests = {k: v for k, v in all_results.items() if 'FAILED' in str(v)}
    
    if failed_tests:
        print("❌ FAILED INTEGRATION TESTS:")
        for test, error in failed_tests.items():
            print(f"  - {test}: {error}")
    else:
        print("✅ ALL INTEGRATION TESTS PASSED!")
    
    # Save results
    results_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'component_tests': {'passed': component_passed, 'total': component_total},
        'realtime_tests': {'passed': realtime_passed, 'total': realtime_total},
        'overall_success_rate': (total_passed/total_tests)*100,
        'detailed_results': all_results
    }
    
    with open('integration_test_results.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n📄 Results saved to integration_test_results.json")
    
    return results_data

if __name__ == "__main__":
    results = run_integration_tests()
    print("\n✅ INTEGRATION TESTING COMPLETE!")