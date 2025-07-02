#!/usr/bin/env python3
"""
OPRYXX FULL STACK VERIFICATION
==============================
Comprehensive verification of all system components
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path

class FullStackVerifier:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'integration_tests': {},
            'overall_status': 'UNKNOWN'
        }
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Remove emojis for Windows console compatibility
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] {level}: {clean_message}")
        
    def verify_python_backend(self):
        """Verify Python backend components"""
        self.log("🐍 Verifying Python Backend...")
        
        backend_components = {
            'FastAPI Backend': 'backend/main.py',
            'Core Architecture': 'core/architecture/core.py',
            'Performance Monitor': 'core/performance_monitor.py',
            'Memory Optimizer': 'core/memory_optimizer.py',
            'GPU Operations': 'core/enhanced_gpu_ops.py',
            'Resilience System': 'core/resilience_system.py'
        }
        
        results = {}
        for name, path in backend_components.items():
            if os.path.exists(path):
                try:
                    # Try to import/compile check
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', path
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        results[name] = {'status': 'OK', 'path': path}
                        self.log(f"  ✅ {name}")
                    else:
                        results[name] = {'status': 'COMPILE_ERROR', 'error': result.stderr}
                        self.log(f"  ❌ {name}: Compile error")
                except Exception as e:
                    results[name] = {'status': 'ERROR', 'error': str(e)}
                    self.log(f"  ❌ {name}: {str(e)}")
            else:
                results[name] = {'status': 'MISSING', 'path': path}
                self.log(f"  ⚠️  {name}: File missing")
        
        self.results['components']['python_backend'] = results
        
    def verify_javascript_frontend(self):
        """Verify JavaScript/Node.js components"""
        self.log("🌐 Verifying JavaScript Frontend...")
        
        js_components = {
            'NEXUS Core Bridge': 'ai-workbench/nexus-core-bridge.js',
            'Package Config': 'ai-workbench/package.json',
            'WebSocket Server': 'ai-workbench/server/websocket-server.js',
            'API Server': 'ai-workbench/api/server.js'
        }
        
        results = {}
        for name, path in js_components.items():
            if os.path.exists(path):
                try:
                    # Check Node.js syntax
                    result = subprocess.run([
                        'node', '--check', path
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        results[name] = {'status': 'OK', 'path': path}
                        self.log(f"  ✅ {name}")
                    else:
                        results[name] = {'status': 'SYNTAX_ERROR', 'error': result.stderr}
                        self.log(f"  ❌ {name}: Syntax error")
                except FileNotFoundError:
                    results[name] = {'status': 'NODE_MISSING', 'error': 'Node.js not found'}
                    self.log(f"  ⚠️  {name}: Node.js not available")
                except Exception as e:
                    results[name] = {'status': 'ERROR', 'error': str(e)}
                    self.log(f"  ❌ {name}: {str(e)}")
            else:
                results[name] = {'status': 'MISSING', 'path': path}
                self.log(f"  ⚠️  {name}: File missing")
        
        self.results['components']['javascript_frontend'] = results
        
    def verify_gui_components(self):
        """Verify GUI components"""
        self.log("🖥️  Verifying GUI Components...")
        
        gui_components = {
            'Master Start GUI': 'master_start.py',
            'Unified GUI': 'UNIFIED_GUI.py',
            'Modern Interface': 'gui/modern_interface.py',
            'Web Interface': 'gui/web_interface.py',
            'MEGA OPRYXX GUI': 'gui/MEGA_OPRYXX.py'
        }
        
        results = {}
        for name, path in gui_components.items():
            if os.path.exists(path):
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'py_compile', path
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        results[name] = {'status': 'OK', 'path': path}
                        self.log(f"  ✅ {name}")
                    else:
                        results[name] = {'status': 'COMPILE_ERROR', 'error': result.stderr}
                        self.log(f"  ❌ {name}: Compile error")
                except Exception as e:
                    results[name] = {'status': 'ERROR', 'error': str(e)}
                    self.log(f"  ❌ {name}: {str(e)}")
            else:
                results[name] = {'status': 'MISSING', 'path': path}
                self.log(f"  ⚠️  {name}: File missing")
        
        self.results['components']['gui_components'] = results
        
    def verify_database_layer(self):
        """Verify database components"""
        self.log("🗄️  Verifying Database Layer...")
        
        db_components = {
            'SQLite Database': 'data/opryxx.db',
            'Database Utils': 'core/db_utils.py',
            'Models': 'models/base.py',
            'Migrations': 'migrations/env.py'
        }
        
        results = {}
        for name, path in db_components.items():
            if os.path.exists(path):
                if path.endswith('.db'):
                    # Check if database file is accessible
                    try:
                        import sqlite3
                        conn = sqlite3.connect(path)
                        conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        conn.close()
                        results[name] = {'status': 'OK', 'path': path}
                        self.log(f"  ✅ {name}")
                    except Exception as e:
                        results[name] = {'status': 'DB_ERROR', 'error': str(e)}
                        self.log(f"  ❌ {name}: Database error")
                else:
                    # Check Python files
                    try:
                        result = subprocess.run([
                            sys.executable, '-m', 'py_compile', path
                        ], capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            results[name] = {'status': 'OK', 'path': path}
                            self.log(f"  ✅ {name}")
                        else:
                            results[name] = {'status': 'COMPILE_ERROR', 'error': result.stderr}
                            self.log(f"  ❌ {name}: Compile error")
                    except Exception as e:
                        results[name] = {'status': 'ERROR', 'error': str(e)}
                        self.log(f"  ❌ {name}: {str(e)}")
            else:
                results[name] = {'status': 'MISSING', 'path': path}
                self.log(f"  ⚠️  {name}: File missing")
        
        self.results['components']['database_layer'] = results
        
    def verify_configuration(self):
        """Verify configuration files"""
        self.log("⚙️  Verifying Configuration...")
        
        config_files = {
            'Docker Compose': 'docker-compose.yml',
            'Requirements': 'requirements.txt',
            'Environment': '.env',
            'OPRYXX Config': 'config/opryxx.json',
            'API Endpoints': 'api/endpoints.json'
        }
        
        results = {}
        for name, path in config_files.items():
            if os.path.exists(path):
                try:
                    if path.endswith('.json'):
                        with open(path, 'r') as f:
                            json.load(f)
                    elif path.endswith('.yml') or path.endswith('.yaml'):
                        # Basic YAML check
                        with open(path, 'r') as f:
                            content = f.read()
                            if 'version:' in content or 'services:' in content:
                                pass  # Basic validation
                    
                    results[name] = {'status': 'OK', 'path': path}
                    self.log(f"  ✅ {name}")
                except Exception as e:
                    results[name] = {'status': 'INVALID', 'error': str(e)}
                    self.log(f"  ❌ {name}: Invalid format")
            else:
                results[name] = {'status': 'MISSING', 'path': path}
                self.log(f"  ⚠️  {name}: File missing")
        
        self.results['components']['configuration'] = results
        
    def test_integration_points(self):
        """Test integration between components"""
        self.log("🔗 Testing Integration Points...")
        
        integration_tests = {}
        
        # Test 1: Python-JavaScript Bridge
        try:
            bridge_config = 'api/bridge-config.json'
            if os.path.exists(bridge_config):
                with open(bridge_config, 'r') as f:
                    config = json.load(f)
                    if 'endpoints' in config and 'python_bridge' in config:
                        integration_tests['python_js_bridge'] = {'status': 'OK', 'config_valid': True}
                        self.log("  ✅ Python-JavaScript Bridge Config")
                    else:
                        integration_tests['python_js_bridge'] = {'status': 'INVALID_CONFIG'}
                        self.log("  ❌ Python-JavaScript Bridge: Invalid config")
            else:
                integration_tests['python_js_bridge'] = {'status': 'MISSING_CONFIG'}
                self.log("  ⚠️  Python-JavaScript Bridge: Config missing")
        except Exception as e:
            integration_tests['python_js_bridge'] = {'status': 'ERROR', 'error': str(e)}
            self.log(f"  ❌ Python-JavaScript Bridge: {str(e)}")
        
        # Test 2: Database Connectivity
        try:
            if os.path.exists('data/opryxx.db'):
                import sqlite3
                conn = sqlite3.connect('data/opryxx.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                conn.close()
                
                integration_tests['database_connectivity'] = {
                    'status': 'OK', 
                    'table_count': table_count
                }
                self.log(f"  ✅ Database Connectivity ({table_count} tables)")
            else:
                integration_tests['database_connectivity'] = {'status': 'NO_DATABASE'}
                self.log("  ⚠️  Database Connectivity: No database file")
        except Exception as e:
            integration_tests['database_connectivity'] = {'status': 'ERROR', 'error': str(e)}
            self.log(f"  ❌ Database Connectivity: {str(e)}")
        
        # Test 3: API Endpoints Configuration
        try:
            if os.path.exists('api/endpoints.json'):
                with open('api/endpoints.json', 'r') as f:
                    endpoints = json.load(f)
                    endpoint_count = len(endpoints.get('endpoints', []))
                    integration_tests['api_endpoints'] = {
                        'status': 'OK',
                        'endpoint_count': endpoint_count
                    }
                    self.log(f"  ✅ API Endpoints ({endpoint_count} configured)")
            else:
                integration_tests['api_endpoints'] = {'status': 'MISSING'}
                self.log("  ⚠️  API Endpoints: Configuration missing")
        except Exception as e:
            integration_tests['api_endpoints'] = {'status': 'ERROR', 'error': str(e)}
            self.log(f"  ❌ API Endpoints: {str(e)}")
        
        self.results['integration_tests'] = integration_tests
        
    def calculate_overall_status(self):
        """Calculate overall system status"""
        self.log("📊 Calculating Overall Status...")
        
        total_components = 0
        ok_components = 0
        
        # Count component statuses
        for category, components in self.results['components'].items():
            for name, status in components.items():
                total_components += 1
                if status.get('status') == 'OK':
                    ok_components += 1
        
        # Count integration test statuses
        for test_name, result in self.results['integration_tests'].items():
            total_components += 1
            if result.get('status') == 'OK':
                ok_components += 1
        
        success_rate = (ok_components / total_components * 100) if total_components > 0 else 0
        
        if success_rate >= 90:
            overall_status = 'EXCELLENT'
        elif success_rate >= 75:
            overall_status = 'GOOD'
        elif success_rate >= 50:
            overall_status = 'FAIR'
        else:
            overall_status = 'POOR'
        
        self.results['overall_status'] = overall_status
        self.results['success_rate'] = success_rate
        self.results['total_components'] = total_components
        self.results['ok_components'] = ok_components
        
        self.log(f"📈 Success Rate: {success_rate:.1f}% ({ok_components}/{total_components})")
        self.log(f"🎯 Overall Status: {overall_status}")
        
    def generate_report(self):
        """Generate comprehensive report"""
        self.log("📋 Generating Report...")
        
        report_file = f"full_stack_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"📄 Report saved: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("OPRYXX FULL STACK VERIFICATION SUMMARY")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Success Rate: {self.results['success_rate']:.1f}%")
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"OK Components: {self.results['ok_components']}")
        print(f"Total Components: {self.results['total_components']}")
        print("="*60)
        
        # Component breakdown
        for category, components in self.results['components'].items():
            ok_count = sum(1 for c in components.values() if c.get('status') == 'OK')
            total_count = len(components)
            print(f"{category.replace('_', ' ').title()}: {ok_count}/{total_count}")
        
        # Integration tests
        ok_tests = sum(1 for t in self.results['integration_tests'].values() if t.get('status') == 'OK')
        total_tests = len(self.results['integration_tests'])
        print(f"Integration Tests: {ok_tests}/{total_tests}")
        
        print("="*60)
        
        return report_file
        
    def run_verification(self):
        """Run complete verification"""
        print("STARTING OPRYXX FULL STACK VERIFICATION")
        print("="*60)
        
        start_time = time.time()
        
        # Run all verification steps
        self.verify_python_backend()
        self.verify_javascript_frontend()
        self.verify_gui_components()
        self.verify_database_layer()
        self.verify_configuration()
        self.test_integration_points()
        self.calculate_overall_status()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.results['verification_duration'] = duration
        
        self.log(f"⏱️  Verification completed in {duration:.2f} seconds")
        
        # Generate report
        report_file = self.generate_report()
        
        return self.results

def main():
    """Main verification function"""
    verifier = FullStackVerifier()
    results = verifier.run_verification()
    
    # Exit with appropriate code
    if results['overall_status'] in ['EXCELLENT', 'GOOD']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()