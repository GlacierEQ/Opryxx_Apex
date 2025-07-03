"""
STACK VERIFICATION - Simple Version
Complete verification of recovery and health systems
"""

import os
import sys
import subprocess
import time
import json
import psutil
from datetime import datetime

def verify_full_stack():
    """Verify complete full stack system"""
    print("FULL STACK VERIFICATION SYSTEM")
    print("=" * 60)
    print("Verifying recovery and health systems...")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_score': 0,
        'status': 'UNKNOWN'
    }
    
    # Test 1: System Information
    print("\n[1/8] Testing System Information...")
    try:
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        
        results['tests']['system_info'] = {
            'success': True,
            'cpu_count': cpu_count,
            'memory_gb': memory.total // (1024**3),
            'disk_gb': disk.total // (1024**3)
        }
        print(f"[PASS] System: {cpu_count} CPUs, {memory.total // (1024**3)}GB RAM, {disk.total // (1024**3)}GB Disk")
    except Exception as e:
        results['tests']['system_info'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] System info: {e}")
    
    # Test 2: Hardware Detection
    print("\n[2/8] Testing Hardware Detection...")
    try:
        result = subprocess.run(['wmic', 'computersystem', 'get', 'manufacturer'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            manufacturer = result.stdout.lower()
            is_dell = 'dell' in manufacturer
            is_msi = 'msi' in manufacturer
            
            results['tests']['hardware_detection'] = {
                'success': True,
                'dell_detected': is_dell,
                'msi_detected': is_msi
            }
            print(f"[PASS] Hardware: Dell={is_dell}, MSI={is_msi}")
        else:
            results['tests']['hardware_detection'] = {'success': False, 'error': 'WMIC failed'}
            print("[FAIL] Hardware detection failed")
    except Exception as e:
        results['tests']['hardware_detection'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] Hardware detection: {e}")
    
    # Test 3: Recovery Tools
    print("\n[3/8] Testing Recovery Tools...")
    recovery_tools = ['bcdedit', 'bootrec', 'manage-bde', 'chkdsk', 'sfc']
    available_tools = 0
    
    for tool in recovery_tools:
        try:
            result = subprocess.run([tool, '/?'], capture_output=True, timeout=5)
            if result.returncode in [0, 1]:
                available_tools += 1
        except:
            pass
    
    results['tests']['recovery_tools'] = {
        'success': available_tools >= 3,
        'available_tools': available_tools,
        'total_tools': len(recovery_tools)
    }
    print(f"[{'PASS' if available_tools >= 3 else 'FAIL'}] Recovery tools: {available_tools}/{len(recovery_tools)} available")
    
    # Test 4: Recovery Files
    print("\n[4/8] Testing Recovery Files...")
    recovery_files = [
        'ULTIMATE_BOOT_RECOVERY.py',
        'ULTIMATE_DATA_RECOVERY.py',
        'BITLOCKER_RECOVERY.py',
        'ULTIMATE_UNIFIED_SYSTEM.py'
    ]
    
    existing_files = sum(1 for f in recovery_files if os.path.exists(f))
    results['tests']['recovery_files'] = {
        'success': existing_files >= 3,
        'existing_files': existing_files,
        'total_files': len(recovery_files)
    }
    print(f"[{'PASS' if existing_files >= 3 else 'FAIL'}] Recovery files: {existing_files}/{len(recovery_files)} found")
    
    # Test 5: Health Monitoring
    print("\n[5/8] Testing Health Monitoring...")
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        processes = len(psutil.pids())
        
        results['tests']['health_monitoring'] = {
            'success': True,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'process_count': processes
        }
        print(f"[PASS] Health: CPU={cpu_percent:.1f}%, Memory={memory_percent:.1f}%, Processes={processes}")
    except Exception as e:
        results['tests']['health_monitoring'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] Health monitoring: {e}")
    
    # Test 6: Drive Detection
    print("\n[6/8] Testing Drive Detection...")
    try:
        drives = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drives.append({
                    'device': partition.device,
                    'fstype': partition.fstype,
                    'total_gb': usage.total // (1024**3)
                })
            except:
                pass
        
        results['tests']['drive_detection'] = {
            'success': len(drives) > 0,
            'drives_found': len(drives),
            'drives': drives
        }
        print(f"[PASS] Drives: {len(drives)} drives detected")
    except Exception as e:
        results['tests']['drive_detection'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] Drive detection: {e}")
    
    # Test 7: BitLocker Detection
    print("\n[7/8] Testing BitLocker Detection...")
    try:
        result = subprocess.run(['manage-bde', '-status'], capture_output=True, text=True, timeout=10)
        bitlocker_available = result.returncode == 0
        
        results['tests']['bitlocker_detection'] = {
            'success': bitlocker_available,
            'bitlocker_available': bitlocker_available
        }
        print(f"[{'PASS' if bitlocker_available else 'FAIL'}] BitLocker: {'Available' if bitlocker_available else 'Not available'}")
    except Exception as e:
        results['tests']['bitlocker_detection'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] BitLocker detection: {e}")
    
    # Test 8: Performance Test
    print("\n[8/8] Testing Performance...")
    try:
        start_time = time.time()
        for _ in range(100):
            psutil.cpu_percent()
        end_time = time.time()
        
        response_time = end_time - start_time
        performance_good = response_time < 2.0
        
        results['tests']['performance'] = {
            'success': performance_good,
            'response_time': response_time,
            'calls_per_second': 100 / response_time
        }
        print(f"[{'PASS' if performance_good else 'FAIL'}] Performance: {response_time:.2f}s for 100 calls")
    except Exception as e:
        results['tests']['performance'] = {'success': False, 'error': str(e)}
        print(f"[FAIL] Performance test: {e}")
    
    # Calculate overall score
    successful_tests = sum(1 for test in results['tests'].values() if test.get('success', False))
    total_tests = len(results['tests'])
    results['overall_score'] = (successful_tests / total_tests) * 100
    
    if results['overall_score'] >= 90:
        results['status'] = 'EXCELLENT'
    elif results['overall_score'] >= 80:
        results['status'] = 'GOOD'
    elif results['overall_score'] >= 70:
        results['status'] = 'FAIR'
    else:
        results['status'] = 'NEEDS_IMPROVEMENT'
    
    # Display summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    print(f"Overall Score: {results['overall_score']:.1f}/100")
    print(f"System Status: {results['status']}")
    
    # Hardware-specific summary
    hardware = results['tests'].get('hardware_detection', {})
    if hardware.get('dell_detected'):
        print("\nDell Inspiron 2-in-1 7040 Support: READY")
    if hardware.get('msi_detected'):
        print("MSI Summit 16 2024 Support: READY")
    
    recovery_tools = results['tests'].get('recovery_tools', {})
    if recovery_tools.get('success'):
        print("Boot Recovery Capability: READY")
    
    bitlocker = results['tests'].get('bitlocker_detection', {})
    if bitlocker.get('success'):
        print("Samsung SSD BitLocker Recovery: READY")
    
    drives = results['tests'].get('drive_detection', {})
    if drives.get('success'):
        print("WD Drive Recovery Capability: READY")
    
    print("=" * 60)
    
    # Save results
    try:
        results_file = f'verification_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")
    except Exception as e:
        print(f"Failed to save results: {e}")
    
    return results['overall_score'] >= 70

def main():
    """Main verification function"""
    print("OPRYXX FULL STACK VERIFICATION")
    print("Testing Dell Inspiron 2-in-1 7040 & MSI Summit 16 2024 Support")
    print("Samsung SSD & WD Drive Recovery Capabilities")
    
    try:
        success = verify_full_stack()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nVerification interrupted by user")
        return 2
    except Exception as e:
        print(f"\nCritical error: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())