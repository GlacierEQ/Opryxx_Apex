"""
OPRYXX Unified System - Optimized Architecture
"""

import sys
import os
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.base import ModuleRegistry, ModuleResult
from core.config import get_config
from core.logger import get_logger
from modules.recovery.samsung_recovery import SamsungRecoveryModule
from modules.recovery.dell_recovery import DellRecoveryModule
from modules.ai.optimization_engine import AIOptimizationModule

class UnifiedOPRYXXSystem:
    """Unified OPRYXX system with optimized architecture"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("unified_system")
        self.registry = ModuleRegistry()
        self.running = False
        self._setup_modules()
    
    def _setup_modules(self):
        """Setup and register all modules"""
        modules = [
            SamsungRecoveryModule(),
            DellRecoveryModule(),
            AIOptimizationModule()
        ]
        
        for module in modules:
            if self.registry.register(module):
                self.logger.info(f"Registered module: {module.name}")
            else:
                self.logger.error(f"Failed to register module: {module.name}")
    
    def initialize(self) -> Dict[str, ModuleResult]:
        """Initialize all modules"""
        self.logger.info("Initializing OPRYXX unified system")
        results = self.registry.initialize_all()
        
        success_count = sum(1 for r in results.values() if r.success)
        total_count = len(results)
        
        self.logger.info(f"Initialized {success_count}/{total_count} modules")
        return results
    
    def execute_recovery(self, module_name: str, **kwargs) -> ModuleResult:
        """Execute recovery operation"""
        module = self.registry.get_module(module_name)
        if not module:
            return ModuleResult(False, f"Module {module_name} not found")
        
        if not module.is_ready():
            return ModuleResult(False, f"Module {module_name} not ready")
        
        self.logger.info(f"Executing recovery: {module_name}")
        return module.execute(**kwargs)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        modules = self.registry.get_all_modules()
        status = {
            'system_ready': True,
            'modules': {},
            'timestamp': time.time()
        }
        
        for name, module in modules.items():
            module_status = {
                'status': module.get_status().value,
                'ready': module.is_ready()
            }
            status['modules'][name] = module_status
            
            if not module.is_ready():
                status['system_ready'] = False
        
        return status
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self.running:
            return
        
        self.running = True
        
        def monitor_loop():
            ai_module = self.registry.get_module("ai_optimization")
            
            while self.running:
                try:
                    if ai_module and ai_module.is_ready():
                        result = ai_module.execute()
                        if result.success:
                            self.logger.info(f"AI optimization: {result.message}")
                        else:
                            self.logger.error(f"AI optimization failed: {result.message}")
                    
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.running = False
        self.logger.info("System monitoring stopped")
    
    def shutdown(self):
        """Shutdown the system"""
        self.logger.info("Shutting down OPRYXX unified system")
        self.stop_monitoring()
        
        cleanup_results = self.registry.cleanup_all()
        success_count = sum(1 for r in cleanup_results.values() if r.success)
        total_count = len(cleanup_results)
        
        self.logger.info(f"Cleaned up {success_count}/{total_count} modules")

def main():
    """Main entry point"""
    print("OPRYXX UNIFIED SYSTEM")
    print("=" * 50)
    
    # Initialize system
    system = UnifiedOPRYXXSystem()
    init_results = system.initialize()
    
    # Check initialization results
    failed_modules = [name for name, result in init_results.items() if not result.success]
    if failed_modules:
        print(f"Warning: Failed to initialize modules: {failed_modules}")
    
    # Start monitoring
    system.start_monitoring()
    
    try:
        # Interactive mode
        while True:
            print("\nOPRYXX Commands:")
            print("1. Samsung SSD Recovery")
            print("2. Dell Boot Recovery")
            print("3. AI Optimization")
            print("4. System Status")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                recovery_key = input("Enter BitLocker recovery key (or press Enter to skip): ").strip()
                result = system.execute_recovery("samsung_recovery", recovery_key=recovery_key)
                print(f"Samsung Recovery: {result.message}")
                
            elif choice == "2":
                result = system.execute_recovery("dell_recovery")
                print(f"Dell Recovery: {result.message}")
                
            elif choice == "3":
                result = system.execute_recovery("ai_optimization")
                print(f"AI Optimization: {result.message}")
                
            elif choice == "4":
                status = system.get_system_status()
                print(f"System Ready: {status['system_ready']}")
                for name, module_status in status['modules'].items():
                    print(f"  {name}: {module_status['status']}")
                    
            elif choice == "5":
                break
            else:
                print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    
    finally:
        system.shutdown()
        print("OPRYXX system shutdown complete")

if __name__ == "__main__":
    main()