"""
Test script for WinRE integration with Opryxx

This script demonstrates how to use the WinREIntegration class with Opryxx.
"""

import os
import sys
import logging
from winre_integration import WinREIntegration

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('winre_test.log')
    ]
)

class MockOrchestrator:
    """Mock orchestrator for testing purposes."""
    
    def __init__(self):
        self.logs = []
    
    def log_callback(self, message):
        """Log callback for the orchestrator."""
        self.logs.append(message)
        print(f"[ORCHESTRATOR] {message}")

def print_banner(title):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, '='))
    print("=" * 80)

def test_winre_integration():
    """Test the WinRE integration."""
    # Create mock orchestrator
    orchestrator = MockOrchestrator()
    
    # Configuration
    config = {
        'temp_dir': 'E:\\Temp\\WinRE_Recovery',
        'recovery_media_path': 'E:\\RecoveryMedia'
    }
    
    try:
        # Initialize WinRE integration
        print_banner("Initializing WinRE Integration")
        winre = WinREIntegration(orchestrator, config)
        
        # Get status
        print_banner("Getting Status")
        status = winre.get_status()
        print("WinRE Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Check health
        print_banner("Checking WinRE Health")
        health = winre.check_winre_health()
        print("Health Check Results:")
        print(f"  Status: {health['status']}")
        print("  Details:")
        for key, value in health['details'].items():
            print(f"    {key}: {value}")
        
        # Repair if needed
        if health['status'] != 'healthy':
            print_banner("Repairing WinRE")
            repair_result = winre.repair_winre()
            print("Repair Results:")
            print(f"  Success: {repair_result['success']}")
            if not repair_result['success']:
                print(f"  Error: {repair_result.get('error', 'Unknown error')}")
        
        # Create recovery media
        print_banner("Creating Recovery Media")
        recovery_result = winre.create_recovery_media()
        print("Recovery Media Results:")
        print(f"  Success: {recovery_result['success']}")
        print(f"  Target Path: {recovery_result['target_path']}")
        if not recovery_result['success']:
            print(f"  Error: {recovery_result.get('error', 'Unknown error')}")
        
        print_banner("Test Completed Successfully")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("WinRE Integration Test Script\n" + "=" * 50 + "\n")
    
    # Check if running as administrator
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        print("WARNING: This script should be run as Administrator for full functionality.")
        print("Some operations may fail without elevated privileges.\n")
    
    # Run the test
    success = test_winre_integration()
    
    # Print final result
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] WinRE integration test completed successfully!")
    else:
        print("[ERROR] WinRE integration test failed. Check the logs for details.")
    print("=" * 50)
