"""
OPRYXX Main Entry Point
Clean architecture implementation
"""

import sys
from services.recovery_service import RecoveryService
from architecture.core import RecoveryStatus

def main():
    print("OPRYXX Recovery System v2.0")
    print("=" * 40)
    
    try:
        service = RecoveryService()
        
        # Show system status
        status = service.get_system_status()
        print(f"Modules: {status['modules_registered']}")
        print(f"Version: {status['version']}")
        print()
        
        # Execute recovery
        print("Executing recovery sequence...")
        results = service.execute_recovery()
        
        # Display results
        success_count = sum(1 for r in results if r.status == RecoveryStatus.SUCCESS)
        print(f"\nResults: {success_count}/{len(results)} successful")
        
        for result in results:
            print(f"- {result.message} [{result.status.value}]")
        
        return 0 if success_count == len(results) else 1
        
    except Exception as e:
        print(f"Critical error: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())