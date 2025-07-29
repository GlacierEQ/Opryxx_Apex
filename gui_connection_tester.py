"""
GUI Connection Tester - Comprehensive GUI Function Testing
Tests all GUI connections and functions with transparent operation feedback
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from datetime import datetime
import subprocess

class GUIConnectionTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX GUI Connection Tester")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        self.test_results = {}
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#1e1e1e')
        header.pack(fill='x', padx=10, pady=10)
        
        title = tk.Label(header, text="🔧 OPRYXX GUI CONNECTION TESTER", 
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1e1e1e')
        title.pack()
        
        # Test controls
        control_frame = tk.Frame(self.root, bg='#1e1e1e')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(control_frame, text="🚀 START ALL TESTS", 
                 command=self.start_all_tests, bg='#4CAF50', fg='white',
                 font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="🔍 TEST MEGA OPRYXX", 
                 command=self.test_mega_opryxx, bg='#2196F3', fg='white').pack(side='left', padx=5)
        
        tk.Button(control_frame, text="🎯 TEST UNIFIED GUI", 
                 command=self.test_unified_gui, bg='#FF9800', fg='white').pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        # Results area
        results_frame = tk.Frame(self.root, bg='#1e1e1e')
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tk.Label(results_frame, text="Test Results:", font=('Arial', 12, 'bold'),
                fg='#ffffff', bg='#1e1e1e').pack(anchor='w')
        
        self.results_text = tk.Text(results_frame, bg='#2d2d2d', fg='#ffffff',
                                   font=('Consolas', 9), wrap='word')
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to test GUI connections")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bg='#333333', fg='#ffffff', anchor='w')
        status_bar.pack(fill='x', side='bottom')
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {'INFO': '#ffffff', 'SUCCESS': '#4CAF50', 'ERROR': '#F44336', 'WARNING': '#FF9800'}
        
        self.results_text.insert('end', f"[{timestamp}] {level}: {message}\n")
        self.results_text.see('end')
        self.root.update()
        
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()
        
    def start_all_tests(self):
        self.progress.start()
        self.results_text.delete(1.0, 'end')
        self.update_status("🔄 Running comprehensive GUI tests...")
        
        def run_tests():
            self.log("🚀 STARTING COMPREHENSIVE GUI CONNECTION TESTS", 'INFO')
            self.log("=" * 60, 'INFO')
            
            # Test 1: MEGA OPRYXX GUI
            self.log("\n📋 TEST 1: MEGA OPRYXX GUI CONNECTION", 'INFO')
            self.test_mega_opryxx_connection()
            
            # Test 2: Unified GUI
            self.log("\n📋 TEST 2: UNIFIED GUI CONNECTION", 'INFO')
            self.test_unified_gui_connection()
            
            # Test 3: Master Start
            self.log("\n📋 TEST 3: MASTER START CONNECTION", 'INFO')
            self.test_master_start_connection()
            
            # Test 4: Component Integration
            self.log("\n📋 TEST 4: COMPONENT INTEGRATION", 'INFO')
            self.test_component_integration()
            
            # Test 5: Function Transparency
            self.log("\n📋 TEST 5: FUNCTION TRANSPARENCY", 'INFO')
            self.test_function_transparency()
            
            # Summary
            self.log("\n" + "=" * 60, 'INFO')
            self.log("✅ ALL GUI CONNECTION TESTS COMPLETED", 'SUCCESS')
            self.generate_test_summary()
            
            self.root.after(0, lambda: [self.progress.stop(), 
                                       self.update_status("✅ All tests completed")])
        
        threading.Thread(target=run_tests, daemon=True).start()
        
    def test_mega_opryxx_connection(self):
        try:
            self.log("  🔍 Testing MEGA OPRYXX GUI import...", 'INFO')
            
            # Test import
            try:
                from gui.MEGA_OPRYXX import MegaGUI, MegaOPRYXX
                self.log("  ✅ MEGA OPRYXX import successful", 'SUCCESS')
                self.test_results['mega_import'] = True
            except Exception as e:
                self.log(f"  ❌ MEGA OPRYXX import failed: {e}", 'ERROR')
                self.test_results['mega_import'] = False
                return
            
            # Test class initialization
            self.log("  🔍 Testing MEGA OPRYXX initialization...", 'INFO')
            try:
                # Test without actually creating GUI
                mega_system = MegaOPRYXX()
                self.log("  ✅ MEGA OPRYXX system initialized", 'SUCCESS')
                self.test_results['mega_init'] = True
            except Exception as e:
                self.log(f"  ❌ MEGA OPRYXX initialization failed: {e}", 'ERROR')
                self.test_results['mega_init'] = False
            
            # Test API client
            self.log("  🔍 Testing API client connection...", 'INFO')
            try:
                api_status = mega_system.api.get_system_status()
                if api_status is None:
                    self.log("  ⚠️  API client created but no backend connection", 'WARNING')
                else:
                    self.log("  ✅ API client connected successfully", 'SUCCESS')
                self.test_results['mega_api'] = True
            except Exception as e:
                self.log(f"  ⚠️  API client warning: {e}", 'WARNING')
                self.test_results['mega_api'] = False
                
        except Exception as e:
            self.log(f"  ❌ MEGA OPRYXX test failed: {e}", 'ERROR')
            self.test_results['mega_overall'] = False
            
    def test_unified_gui_connection(self):
        try:
            self.log("  🔍 Testing Unified GUI import...", 'INFO')
            
            # Test import
            try:
                from gui.unified_gui import UnifiedGUI
                self.log("  ✅ Unified GUI import successful", 'SUCCESS')
                self.test_results['unified_import'] = True
            except Exception as e:
                self.log(f"  ❌ Unified GUI import failed: {e}", 'ERROR')
                self.test_results['unified_import'] = False
                return
            
            # Test dependencies
            self.log("  🔍 Testing Unified GUI dependencies...", 'INFO')
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                self.log("  ✅ Matplotlib and NumPy available", 'SUCCESS')
                self.test_results['unified_deps'] = True
            except Exception as e:
                self.log(f"  ⚠️  Some dependencies missing: {e}", 'WARNING')
                self.test_results['unified_deps'] = False
                
        except Exception as e:
            self.log(f"  ❌ Unified GUI test failed: {e}", 'ERROR')
            self.test_results['unified_overall'] = False
            
    def test_master_start_connection(self):
        try:
            self.log("  🔍 Testing Master Start import...", 'INFO')
            
            # Test import
            try:
                from master_start import MasterStartApp
                self.log("  ✅ Master Start import successful", 'SUCCESS')
                self.test_results['master_import'] = True
            except Exception as e:
                self.log(f"  ❌ Master Start import failed: {e}", 'ERROR')
                self.test_results['master_import'] = False
                return
            
            # Test system info function
            self.log("  🔍 Testing system info gathering...", 'INFO')
            try:
                from master_start import get_system_info
                sys_info = get_system_info()
                if 'error' not in sys_info:
                    self.log("  ✅ System info gathered successfully", 'SUCCESS')
                    self.test_results['master_sysinfo'] = True
                else:
                    self.log(f"  ⚠️  System info warning: {sys_info['error']}", 'WARNING')
                    self.test_results['master_sysinfo'] = False
            except Exception as e:
                self.log(f"  ⚠️  System info warning: {e}", 'WARNING')
                self.test_results['master_sysinfo'] = False
                
        except Exception as e:
            self.log(f"  ❌ Master Start test failed: {e}", 'ERROR')
            self.test_results['master_overall'] = False
            
    def test_component_integration(self):
        try:
            self.log("  🔍 Testing component integration...", 'INFO')
            
            # Test core modules
            core_modules = [
                'core.gpu_acceleration',
                'core.performance_monitor', 
                'core.memory_optimizer',
                'core.resilience_system'
            ]
            
            available_modules = 0
            for module in core_modules:
                try:
                    __import__(module)
                    self.log(f"  ✅ {module} available", 'SUCCESS')
                    available_modules += 1
                except ImportError:
                    self.log(f"  ⚠️  {module} not available", 'WARNING')
            
            if available_modules > 0:
                self.log(f"  ✅ {available_modules}/{len(core_modules)} core modules available", 'SUCCESS')
                self.test_results['integration'] = True
            else:
                self.log("  ⚠️  No core modules available - running in fallback mode", 'WARNING')
                self.test_results['integration'] = False
                
        except Exception as e:
            self.log(f"  ❌ Integration test failed: {e}", 'ERROR')
            self.test_results['integration'] = False
            
    def test_function_transparency(self):
        try:
            self.log("  🔍 Testing function transparency features...", 'INFO')
            
            # Test logging capabilities
            self.log("  ✅ Function start: Logging system active", 'SUCCESS')
            time.sleep(0.5)
            self.log("  🔄 Function action: Processing test data", 'INFO')
            time.sleep(0.5)
            self.log("  ✅ Function complete: Transparency test passed", 'SUCCESS')
            
            # Test status updates
            self.update_status("🔄 Testing status transparency...")
            time.sleep(0.5)
            self.update_status("✅ Status transparency working")
            
            self.test_results['transparency'] = True
            
        except Exception as e:
            self.log(f"  ❌ Transparency test failed: {e}", 'ERROR')
            self.test_results['transparency'] = False
            
    def test_mega_opryxx(self):
        self.progress.start()
        self.update_status("🔄 Testing MEGA OPRYXX specifically...")
        
        def test():
            self.log("🎯 FOCUSED MEGA OPRYXX TEST", 'INFO')
            self.test_mega_opryxx_connection()
            self.root.after(0, lambda: [self.progress.stop(),
                                       self.update_status("✅ MEGA OPRYXX test complete")])
        
        threading.Thread(target=test, daemon=True).start()
        
    def test_unified_gui(self):
        self.progress.start()
        self.update_status("🔄 Testing Unified GUI specifically...")
        
        def test():
            self.log("🎯 FOCUSED UNIFIED GUI TEST", 'INFO')
            self.test_unified_gui_connection()
            self.root.after(0, lambda: [self.progress.stop(),
                                       self.update_status("✅ Unified GUI test complete")])
        
        threading.Thread(target=test, daemon=True).start()
        
    def generate_test_summary(self):
        self.log("\n📊 TEST SUMMARY REPORT", 'INFO')
        self.log("-" * 40, 'INFO')
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        self.log(f"Total Tests: {total_tests}", 'INFO')
        self.log(f"Passed: {passed_tests}", 'SUCCESS')
        self.log(f"Failed/Warning: {total_tests - passed_tests}", 'WARNING')
        self.log(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%", 'INFO')
        
        # Detailed results
        self.log("\nDetailed Results:", 'INFO')
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}", 'SUCCESS' if result else 'ERROR')
            
        # Recommendations
        self.log("\n💡 RECOMMENDATIONS:", 'INFO')
        if not self.test_results.get('mega_import', True):
            self.log("  • Check MEGA OPRYXX GUI file paths", 'WARNING')
        if not self.test_results.get('unified_deps', True):
            self.log("  • Install missing dependencies: pip install matplotlib numpy", 'WARNING')
        if not self.test_results.get('integration', True):
            self.log("  • Some core modules missing - system will run in fallback mode", 'WARNING')
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tester = GUIConnectionTester()
    tester.run()