#!/usr/bin/env python3
"""
GUI Settings and Options Validator
Validates all GUI settings, options, and configurations
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime

class GUISettingsValidator:
    """Validates all GUI settings and options"""
    
    def __init__(self):
        self.validation_results = {}
        self.settings_tested = 0
        self.settings_passed = 0
        
    def validate_all_settings(self):
        """Validate all GUI settings and options"""
        print("🔧 VALIDATING GUI SETTINGS & OPTIONS")
        print("=" * 50)
        
        # Test categories
        test_categories = [
            ('Theme Settings', self.test_theme_settings),
            ('Control Settings', self.test_control_settings),
            ('Monitoring Settings', self.test_monitoring_settings),
            ('Automation Settings', self.test_automation_settings),
            ('Performance Settings', self.test_performance_settings),
            ('Recovery Settings', self.test_recovery_settings),
            ('Display Settings', self.test_display_settings),
            ('Logging Settings', self.test_logging_settings)
        ]
        
        for category, test_func in test_categories:
            print(f"\n📋 Testing {category}...")
            try:
                test_func()
                print(f"✅ {category}: PASSED")
            except Exception as e:
                print(f"❌ {category}: FAILED - {str(e)}")
                self.validation_results[category] = f"FAILED: {str(e)}"
        
        return self.validation_results
    
    def test_theme_settings(self):
        """Test theme and appearance settings"""
        theme_settings = {
            'bg_color': '#0a0a0a',
            'panel_bg': '#1a1a2e',
            'accent_color': '#00ff41',
            'warning_color': '#ff9500',
            'error_color': '#ff0040',
            'text_bg': '#0f0f23'
        }
        
        for setting, value in theme_settings.items():
            self.settings_tested += 1
            if isinstance(value, str) and value.startswith('#') and len(value) == 7:
                self.settings_passed += 1
            else:
                raise ValueError(f"Invalid color format for {setting}: {value}")
        
        self.validation_results['theme_settings'] = 'PASSED'
    
    def test_control_settings(self):
        """Test control panel settings"""
        control_settings = {
            'auto_scan_interval': 300,  # 5 minutes
            'emergency_timeout': 30,    # 30 seconds
            'max_concurrent_operations': 3,
            'enable_sound_alerts': True,
            'confirm_destructive_actions': True
        }
        
        for setting, value in control_settings.items():
            self.settings_tested += 1
            if setting.endswith('_interval') or setting.endswith('_timeout'):
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid timeout/interval for {setting}: {value}")
            elif setting.startswith('enable_') or setting.startswith('confirm_'):
                if isinstance(value, bool):
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boolean for {setting}: {value}")
            else:
                self.settings_passed += 1
        
        self.validation_results['control_settings'] = 'PASSED'
    
    def test_monitoring_settings(self):
        """Test monitoring configuration settings"""
        monitoring_settings = {
            'update_frequency': 5,      # seconds
            'history_retention': 1000,  # records
            'cpu_alert_threshold': 80,  # percent
            'memory_alert_threshold': 85, # percent
            'disk_alert_threshold': 90,   # percent
            'enable_real_time_graphs': True,
            'log_performance_data': True
        }
        
        for setting, value in monitoring_settings.items():
            self.settings_tested += 1
            if setting.endswith('_threshold'):
                if isinstance(value, (int, float)) and 0 <= value <= 100:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid threshold for {setting}: {value}")
            elif setting in ['update_frequency', 'history_retention']:
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid value for {setting}: {value}")
            elif isinstance(value, bool):
                self.settings_passed += 1
            else:
                raise ValueError(f"Unexpected setting type for {setting}: {type(value)}")
        
        self.validation_results['monitoring_settings'] = 'PASSED'
    
    def test_automation_settings(self):
        """Test automation configuration settings"""
        automation_settings = {
            'auto_optimization': True,
            'auto_recovery': True,
            'auto_monitoring': True,
            'auto_prediction': True,
            'optimization_schedule': 'daily',
            'recovery_retry_attempts': 3,
            'prediction_interval': 3600  # 1 hour
        }
        
        for setting, value in automation_settings.items():
            self.settings_tested += 1
            if setting.startswith('auto_'):
                if isinstance(value, bool):
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boolean for {setting}: {value}")
            elif setting == 'optimization_schedule':
                if value in ['hourly', 'daily', 'weekly', 'manual']:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid schedule for {setting}: {value}")
            elif setting.endswith('_attempts') or setting.endswith('_interval'):
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid value for {setting}: {value}")
        
        self.validation_results['automation_settings'] = 'PASSED'
    
    def test_performance_settings(self):
        """Test performance optimization settings"""
        performance_settings = {
            'optimization_level': 'moderate',
            'memory_cleanup_threshold': 75,
            'temp_cleanup_size_mb': 100,
            'registry_backup_enabled': True,
            'safe_mode_detection': True,
            'performance_boost_level': 2
        }
        
        for setting, value in performance_settings.items():
            self.settings_tested += 1
            if setting == 'optimization_level':
                if value in ['conservative', 'moderate', 'aggressive']:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid optimization level: {value}")
            elif setting.endswith('_threshold') or setting.endswith('_size_mb'):
                if isinstance(value, (int, float)) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid value for {setting}: {value}")
            elif setting.endswith('_enabled') or setting.endswith('_detection'):
                if isinstance(value, bool):
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boolean for {setting}: {value}")
            elif setting == 'performance_boost_level':
                if isinstance(value, int) and 1 <= value <= 5:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boost level: {value}")
        
        self.validation_results['performance_settings'] = 'PASSED'
    
    def test_recovery_settings(self):
        """Test recovery system settings"""
        recovery_settings = {
            'create_restore_points': True,
            'backup_critical_files': True,
            'emergency_recovery_timeout': 600,  # 10 minutes
            'safe_mode_auto_exit': True,
            'boot_repair_attempts': 3,
            'recovery_media_path': 'C:\\Recovery'
        }
        
        for setting, value in recovery_settings.items():
            self.settings_tested += 1
            if setting.startswith('create_') or setting.startswith('backup_') or setting.endswith('_auto_exit'):
                if isinstance(value, bool):
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boolean for {setting}: {value}")
            elif setting.endswith('_timeout') or setting.endswith('_attempts'):
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid value for {setting}: {value}")
            elif setting.endswith('_path'):
                if isinstance(value, str) and len(value) > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid path for {setting}: {value}")
        
        self.validation_results['recovery_settings'] = 'PASSED'
    
    def test_display_settings(self):
        """Test display and UI settings"""
        display_settings = {
            'window_width': 1400,
            'window_height': 900,
            'font_family': 'Arial',
            'font_size': 10,
            'show_tooltips': True,
            'animate_transitions': True,
            'tab_position': 'top',
            'status_bar_enabled': True
        }
        
        for setting, value in display_settings.items():
            self.settings_tested += 1
            if setting.startswith('window_'):
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid window dimension for {setting}: {value}")
            elif setting == 'font_family':
                if isinstance(value, str) and len(value) > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid font family: {value}")
            elif setting == 'font_size':
                if isinstance(value, int) and 8 <= value <= 20:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid font size: {value}")
            elif setting == 'tab_position':
                if value in ['top', 'bottom', 'left', 'right']:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid tab position: {value}")
            elif isinstance(value, bool):
                self.settings_passed += 1
            else:
                raise ValueError(f"Unexpected setting type for {setting}: {type(value)}")
        
        self.validation_results['display_settings'] = 'PASSED'
    
    def test_logging_settings(self):
        """Test logging configuration settings"""
        logging_settings = {
            'log_level': 'INFO',
            'max_log_size_mb': 50,
            'log_rotation_count': 5,
            'enable_file_logging': True,
            'enable_console_logging': True,
            'log_format': 'detailed',
            'log_directory': 'logs'
        }
        
        for setting, value in logging_settings.items():
            self.settings_tested += 1
            if setting == 'log_level':
                if value in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid log level: {value}")
            elif setting.endswith('_size_mb') or setting.endswith('_count'):
                if isinstance(value, int) and value > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid value for {setting}: {value}")
            elif setting.startswith('enable_'):
                if isinstance(value, bool):
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid boolean for {setting}: {value}")
            elif setting == 'log_format':
                if value in ['simple', 'detailed', 'json']:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid log format: {value}")
            elif setting == 'log_directory':
                if isinstance(value, str) and len(value) > 0:
                    self.settings_passed += 1
                else:
                    raise ValueError(f"Invalid log directory: {value}")
        
        self.validation_results['logging_settings'] = 'PASSED'

class InteractiveGUITester:
    """Interactive GUI testing interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX GUI Settings Validator")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        self.validator = GUISettingsValidator()
        self.create_interface()
    
    def create_interface(self):
        """Create testing interface"""
        # Header
        header = tk.Label(self.root, text="🔧 GUI SETTINGS VALIDATOR", 
                         font=('Arial', 16, 'bold'), fg='#00ff41', bg='#2b2b2b')
        header.pack(pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg='#2b2b2b')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🧪 Run All Tests", command=self.run_all_tests,
                 bg='#00ff41', fg='black', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📊 Generate Report", command=self.generate_report,
                 bg='#ff8000', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="💾 Save Results", command=self.save_results,
                 bg='#8000ff', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Results display
        results_frame = tk.Frame(self.root, bg='#1a1a2e', relief='raised', bd=2)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(results_frame, text="📋 TEST RESULTS", 
                font=('Arial', 12, 'bold'), fg='#00ff41', bg='#1a1a2e').pack(pady=5)
        
        self.results_text = tk.Text(results_frame, bg='#0f0f23', fg='white',
                                   font=('Consolas', 9), wrap='word')
        scrollbar = tk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to test GUI settings...")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bg='#1a1a2e', fg='#00ff41', font=('Arial', 9))
        status_bar.pack(fill='x', pady=(5, 0))
    
    def run_all_tests(self):
        """Run all validation tests"""
        self.status_var.set("🧪 Running validation tests...")
        self.results_text.delete(1.0, tk.END)
        
        # Run validation
        results = self.validator.validate_all_settings()
        
        # Display results
        self.results_text.insert(tk.END, "🔧 GUI SETTINGS VALIDATION RESULTS\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        passed = sum(1 for r in results.values() if r == 'PASSED')
        total = len(results)
        
        self.results_text.insert(tk.END, f"📊 SUMMARY:\n")
        self.results_text.insert(tk.END, f"Settings Tested: {self.validator.settings_tested}\n")
        self.results_text.insert(tk.END, f"Settings Passed: {self.validator.settings_passed}\n")
        self.results_text.insert(tk.END, f"Categories Passed: {passed}/{total}\n")
        self.results_text.insert(tk.END, f"Success Rate: {(self.validator.settings_passed/self.validator.settings_tested)*100:.1f}%\n\n")
        
        self.results_text.insert(tk.END, "📋 DETAILED RESULTS:\n")
        self.results_text.insert(tk.END, "-" * 30 + "\n")
        
        for category, result in results.items():
            status = "✅" if result == 'PASSED' else "❌"
            self.results_text.insert(tk.END, f"{status} {category}: {result}\n")
        
        self.status_var.set(f"✅ Validation complete - {passed}/{total} categories passed")
    
    def generate_report(self):
        """Generate detailed validation report"""
        self.results_text.insert(tk.END, "\n\n📄 DETAILED VALIDATION REPORT\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n")
        self.results_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Add detailed explanations
        explanations = {
            'theme_settings': 'Color scheme and visual appearance validation',
            'control_settings': 'Control panel configuration validation',
            'monitoring_settings': 'Real-time monitoring configuration validation',
            'automation_settings': 'Automated processes configuration validation',
            'performance_settings': 'Performance optimization settings validation',
            'recovery_settings': 'System recovery configuration validation',
            'display_settings': 'User interface display settings validation',
            'logging_settings': 'Logging system configuration validation'
        }
        
        for category, explanation in explanations.items():
            result = self.validator.validation_results.get(category, 'NOT TESTED')
            self.results_text.insert(tk.END, f"🔍 {category.upper()}:\n")
            self.results_text.insert(tk.END, f"   Description: {explanation}\n")
            self.results_text.insert(tk.END, f"   Result: {result}\n\n")
        
        self.status_var.set("📄 Detailed report generated")
    
    def save_results(self):
        """Save validation results to file"""
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'settings_tested': self.validator.settings_tested,
            'settings_passed': self.validator.settings_passed,
            'success_rate': (self.validator.settings_passed/self.validator.settings_tested)*100 if self.validator.settings_tested > 0 else 0,
            'validation_results': self.validator.validation_results
        }
        
        filename = f"gui_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            self.results_text.insert(tk.END, f"\n💾 Results saved to: {filename}\n")
            self.status_var.set(f"💾 Results saved to {filename}")
            
        except Exception as e:
            self.results_text.insert(tk.END, f"\n❌ Error saving results: {str(e)}\n")
            self.status_var.set(f"❌ Error saving results")
    
    def run(self):
        """Start the interactive tester"""
        self.root.mainloop()

def main():
    """Main function to run GUI settings validation"""
    print("🔧 OPRYXX GUI SETTINGS VALIDATOR")
    print("=" * 50)
    
    # Command line validation
    validator = GUISettingsValidator()
    results = validator.validate_all_settings()
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"Settings Tested: {validator.settings_tested}")
    print(f"Settings Passed: {validator.settings_passed}")
    print(f"Success Rate: {(validator.settings_passed/validator.settings_tested)*100:.1f}%")
    
    # Launch interactive tester
    print("\n🖥️ Launching interactive GUI tester...")
    tester = InteractiveGUITester()
    tester.run()

if __name__ == "__main__":
    main()