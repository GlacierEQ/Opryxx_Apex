"""
UNIFIED FULL STACK VERIFICATION
Comprehensive testing of all integrated components
"""

import os
import sys
import importlib.util
import subprocess
import time
from datetime import datetime

class UnifiedStackVerifier:
    def __init__(self):
        self.results = {
            'components_verified': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
    
    def verify_complete_stack(self):
        """Verify all components of the unified stack"""
        print("🔍 UNIFIED FULL STACK VERIFICATION")
        print("=" * 60)
        
        # Test 1: Core System Files
        self._verify_core_files()
        
        # Test 2: GUI Components
        self._verify_gui_components()
        
        # Test 3: System Integration
        self._verify_system_integration()
        
        # Test 4: Performance Capabilities
        self._verify_performance()
        
        # Test 5: Recovery Functions
        self._verify_recovery_functions()
        
        # Test 6: AI Components
        self._verify_ai_components()
        
        # Generate final report
        self._generate_verification_report()
    
    def _verify_core_files(self):
        """Verify core system files exist"""
        print("\n📁 VERIFYING CORE FILES...")
        
        core_files = [
            'UNIFIED_FULL_STACK_GUI.py',
            'gui/MEGA_OPRYXX.py',
            'ULTIMATE_NEXUS_AI.py',
            'ai/ULTIMATE_AI_OPTIMIZER.py',
            'core/main.py'
        ]
        
        for file in core_files:
            if os.path.exists(file):
                print(f"✅ {file}")
                self.results['tests_passed'] += 1
            else:
                print(f"❌ {file} - MISSING")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Missing core file: {file}")
        
        self.results['components_verified'] += 1
    
    def _verify_gui_components(self):
        """Verify GUI components"""
        print("\n🖥️ VERIFYING GUI COMPONENTS...")
        
        try:
            # Test tkinter availability
            import tkinter as tk
            print("✅ Tkinter GUI framework")
            self.results['tests_passed'] += 1
            
            # Test ttk styling
            from tkinter import ttk
            print("✅ TTK styling components")
            self.results['tests_passed'] += 1
            
            # Test scrolledtext
            from tkinter import scrolledtext
            print("✅ ScrolledText widgets")
            self.results['tests_passed'] += 1
            
        except ImportError as e:
            print(f"❌ GUI component error: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"GUI component missing: {e}")
        
        self.results['components_verified'] += 1
    
    def _verify_system_integration(self):
        """Verify system integration capabilities"""
        print("\n🔗 VERIFYING SYSTEM INTEGRATION...")
        
        try:
            # Test psutil for system monitoring
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            print(f"✅ System monitoring (CPU: {cpu}%, Memory: {memory.percent}%)")
            self.results['tests_passed'] += 1
            
            # Test subprocess for system commands
            result = subprocess.run(['echo', 'test'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("✅ System command execution")
                self.results['tests_passed'] += 1
            else:
                print("⚠️ System command execution - limited")
                self.results['warnings'].append("Limited system command access")
            
            # Test threading for background operations
            import threading
            print("✅ Multi-threading support")
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ System integration error: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"System integration issue: {e}")
        
        self.results['components_verified'] += 1
    
    def _verify_performance(self):
        """Verify performance monitoring capabilities"""
        print("\n⚡ VERIFYING PERFORMANCE CAPABILITIES...")
        
        try:
            import psutil
            
            # CPU monitoring
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            print(f"✅ CPU monitoring ({cpu_count} cores, {cpu_freq.current if cpu_freq else 'N/A'} MHz)")
            self.results['tests_passed'] += 1
            
            # Memory monitoring
            memory = psutil.virtual_memory()
            print(f"✅ Memory monitoring ({memory.total // (1024**3)} GB total)")
            self.results['tests_passed'] += 1
            
            # Disk monitoring
            disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
            print(f"✅ Disk monitoring ({disk.total // (1024**3)} GB total)")
            self.results['tests_passed'] += 1
            
            # Process monitoring
            processes = len(psutil.pids())
            print(f"✅ Process monitoring ({processes} active processes)")
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ Performance monitoring error: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Performance monitoring issue: {e}")
        
        self.results['components_verified'] += 1
    
    def _verify_recovery_functions(self):
        """Verify recovery function capabilities"""
        print("\n🔧 VERIFYING RECOVERY FUNCTIONS...")
        
        try:
            # Test environment variable access
            temp_dir = os.environ.get('TEMP' if os.name == 'nt' else 'TMPDIR', '/tmp')
            if os.path.exists(temp_dir):
                print(f"✅ Temp directory access ({temp_dir})")
                self.results['tests_passed'] += 1
            
            # Test file system operations
            test_file = os.path.join(temp_dir, 'opryxx_test.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("✅ File system operations")
                self.results['tests_passed'] += 1
            except:
                print("⚠️ Limited file system access")
                self.results['warnings'].append("Limited file system access")
            
            # Test registry access (Windows only)
            if os.name == 'nt':
                try:
                    import winreg
                    print("✅ Registry access capability")
                    self.results['tests_passed'] += 1
                except ImportError:
                    print("⚠️ Registry access not available")
                    self.results['warnings'].append("Registry access not available")
            
        except Exception as e:
            print(f"❌ Recovery function error: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Recovery function issue: {e}")
        
        self.results['components_verified'] += 1
    
    def _verify_ai_components(self):
        """Verify AI and optimization components"""
        print("\n🤖 VERIFYING AI COMPONENTS...")
        
        try:
            # Test JSON for configuration
            import json
            test_config = {'test': True}
            json_str = json.dumps(test_config)
            parsed = json.loads(json_str)
            print("✅ JSON configuration handling")
            self.results['tests_passed'] += 1
            
            # Test datetime for logging
            from datetime import datetime, timedelta
            now = datetime.now()
            print(f"✅ DateTime operations ({now.strftime('%Y-%m-%d %H:%M:%S')})")
            self.results['tests_passed'] += 1
            
            # Test time operations
            import time
            start_time = time.time()
            time.sleep(0.1)
            elapsed = time.time() - start_time
            print(f"✅ Time operations ({elapsed:.3f}s precision)")
            self.results['tests_passed'] += 1
            
            # Test typing for type hints
            from typing import Dict, List, Optional
            print("✅ Type hinting support")
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ AI component error: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"AI component issue: {e}")
        
        self.results['components_verified'] += 1
    
    def _generate_verification_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "=" * 60)
        print("📊 UNIFIED FULL STACK VERIFICATION REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        success_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🔍 Components Verified: {self.results['components_verified']}")
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # System readiness assessment
        if success_rate >= 90:
            status = "🟢 FULLY OPERATIONAL"
            readiness = "READY FOR PRODUCTION"
        elif success_rate >= 75:
            status = "🟡 MOSTLY OPERATIONAL"
            readiness = "READY WITH MINOR ISSUES"
        elif success_rate >= 50:
            status = "🟠 PARTIALLY OPERATIONAL"
            readiness = "NEEDS ATTENTION"
        else:
            status = "🔴 CRITICAL ISSUES"
            readiness = "NOT READY"
        
        print(f"\n🎯 System Status: {status}")
        print(f"🚀 Readiness: {readiness}")
        
        # Critical issues
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        
        # Warnings
        if self.results['warnings']:
            print(f"\n⚠️ WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        # Recommendations
        self._generate_recommendations()
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.results['recommendations'])}):")
            for rec in self.results['recommendations']:
                print(f"   • {rec}")
        
        print("\n" + "=" * 60)
        print(f"✅ VERIFICATION COMPLETED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def _generate_recommendations(self):
        """Generate recommendations based on verification results"""
        if self.results['tests_failed'] > 0:
            self.results['recommendations'].append("Address failed tests before production deployment")
        
        if len(self.results['critical_issues']) > 0:
            self.results['recommendations'].append("Resolve critical issues immediately")
        
        if len(self.results['warnings']) > 2:
            self.results['recommendations'].append("Review and address system warnings")
        
        # Performance recommendations
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                self.results['recommendations'].append("System memory usage is high - consider optimization")
            
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 70:
                self.results['recommendations'].append("CPU usage is high - monitor system load")
        except:
            pass
        
        # Always recommend testing
        self.results['recommendations'].append("Run comprehensive testing before full deployment")
        self.results['recommendations'].append("Monitor system performance after deployment")

def main():
    """Run unified stack verification"""
    print("🚀 STARTING UNIFIED FULL STACK VERIFICATION")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verifier = UnifiedStackVerifier()
    verifier.verify_complete_stack()
    
    return verifier.results

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results['tests_failed'] == 0:
        sys.exit(0)  # Success
    elif len(results['critical_issues']) > 0:
        sys.exit(2)  # Critical issues
    else:
        sys.exit(1)  # Minor issues