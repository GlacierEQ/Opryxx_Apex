"""
ULTIMATE NEXUS AI
Complete system with memory leak detection, GPU/NPU acceleration, and validation
"""

from ENHANCED_PERFORMANCE_AI import EnhancedPerformanceAI
from enhancements.system_validator import NexusSystemValidator
import threading
import time

class UltimateNexusAI(EnhancedPerformanceAI):
    def __init__(self):
        super().__init__()
        self.validator = NexusSystemValidator()
        self.validation_interval = 300  # 5 minutes
        self.leak_detection_active = True
        
    def start_ultimate_nexus(self):
        """Start Ultimate NEXUS AI with full validation"""
        print("ULTIMATE NEXUS AI STARTING...")
        print("=" * 50)
        
        # Run initial system validation
        self._run_initial_validation()
        
        # Start enhanced performance AI
        self.start_enhanced_performance()
        
        # Start continuous validation
        self._start_continuous_validation()
        
        print("🚀 ULTIMATE NEXUS AI FULLY ACTIVE!")
        
    def _run_initial_validation(self):
        """Run initial system validation"""
        print("🔍 Running initial system validation...")
        
        validation_results = self.validator.run_full_validation()
        
        # Store validation results
        self.validation_results = validation_results
        
        # Adjust performance based on validation
        if validation_results['overall_score'] >= 80:
            self.set_performance_mode('ULTRA')
        elif validation_results['overall_score'] >= 60:
            self.set_performance_mode('PERFORMANCE')
        else:
            self.set_performance_mode('BALANCED')
        
        print(f"✅ Initial validation complete: {validation_results['status']}")
        
    def _start_continuous_validation(self):
        """Start continuous system validation"""
        def validation_loop():
            while self.active:
                try:
                    time.sleep(self.validation_interval)
                    
                    if self.leak_detection_active:
                        # Run memory leak detection
                        leak_test = self.validator.test_memory_leak_detection()
                        if leak_test.get('leak_detected'):
                            self.log_action(f"🚨 MEMORY LEAK DETECTED: {leak_test['memory_diff_mb']:.1f}MB")
                            self._handle_memory_leak()
                        
                        # Check memory thresholds
                        memory_status = self.validator.test_memory_thresholds()
                        if memory_status['status'] in ['WARNING', 'CRITICAL']:
                            self.log_action(f"⚠️ Memory {memory_status['status']}: {memory_status['usage_percent']:.1f}%")
                            self._handle_memory_pressure(memory_status)
                    
                except Exception as e:
                    self.log_action(f"Validation error: {e}")
        
        threading.Thread(target=validation_loop, daemon=True).start()
        print("🔄 Continuous validation started")
    
    def _handle_memory_leak(self):
        """Handle detected memory leak"""
        self.log_action("🔧 Handling memory leak...")
        
        # Force aggressive memory cleanup
        memory_actions = self.memory_optimizer.auto_memory_management()
        for action in memory_actions:
            self.log_action(f"Leak fix: {action}")
        
        # Run garbage collection
        import gc
        gc.collect()
        
        # Notify user
        if hasattr(self, 'notifications'):
            self.notifications.notify("Memory Leak", "Detected and fixed memory leak")
        
        self.problems_solved += 1
    
    def _handle_memory_pressure(self, memory_status):
        """Handle memory pressure situations"""
        if memory_status['status'] == 'CRITICAL':
            self.log_action("🚨 CRITICAL memory pressure - emergency cleanup")
            
            # Emergency memory cleanup
            self.memory_optimizer.optimize_memory_aggressive()
            
            # Kill memory hogs
            leaky_processes = self.memory_optimizer.monitor_memory_leaks()
            for proc in leaky_processes[:3]:  # Kill top 3
                try:
                    import psutil
                    p = psutil.Process(proc['pid'])
                    p.terminate()
                    self.log_action(f"Emergency kill: {proc['name']}")
                except:
                    pass
            
            # Switch to extreme performance mode temporarily
            old_mode = self.performance_mode
            self.set_performance_mode('EXTREME')
            
            # Revert after 5 minutes
            def revert_mode():
                time.sleep(300)
                self.set_performance_mode(old_mode)
            
            threading.Thread(target=revert_mode, daemon=True).start()
    
    def get_ultimate_status(self):
        """Get ultimate system status"""
        base_status = super().get_enhanced_status()
        
        # Add validation info
        if hasattr(self, 'validation_results'):
            base_status['validation'] = {
                'overall_score': self.validation_results['overall_score'],
                'status': self.validation_results['status'],
                'gpu_capabilities': self.validation_results['gpu_detection']['capabilities'],
                'memory_status': self.validation_results['memory_thresholds']['status']
            }
        
        base_status['leak_detection_active'] = self.leak_detection_active
        
        return base_status
    
    def run_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n🔍 ULTIMATE NEXUS AI DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # Current status
        status = self.get_ultimate_status()
        
        print(f"🤖 AI Status: {status['ai_name']} - {'ACTIVE' if status['active'] else 'INACTIVE'}")
        print(f"⚡ Performance Mode: {status['performance_mode']}")
        print(f"🔧 Problems Solved: {status['problems_solved']}")
        print(f"⚙️ Optimizations: {status['optimizations_performed']}")
        
        # Memory status
        memory = status['memory_stats']
        print(f"\n💾 Memory Status:")
        print(f"   Total RAM: {memory['total_ram']}")
        print(f"   Available: {memory['available_ram']}")
        print(f"   Usage: {memory['ram_usage']}")
        
        # GPU status
        gpu = status['gpu_status']
        print(f"\n🎮 Hardware Acceleration:")
        print(f"   GPU Available: {gpu['gpu_available']}")
        print(f"   NPU Available: {gpu['npu_available']}")
        
        # Validation status
        if 'validation' in status:
            val = status['validation']
            print(f"\n📊 System Validation:")
            print(f"   Overall Score: {val['overall_score']}/100")
            print(f"   Status: {val['status']}")
            print(f"   GPU Capabilities: {', '.join(val['gpu_capabilities']) or 'None'}")
        
        print(f"\n🔄 Leak Detection: {'ACTIVE' if status['leak_detection_active'] else 'INACTIVE'}")

def main():
    """Launch Ultimate NEXUS AI"""
    print("🚀 ULTIMATE NEXUS AI - Complete System")
    print("Memory Leak Detection + GPU/NPU Acceleration + Advanced Optimization")
    print("=" * 80)
    
    ultimate_ai = UltimateNexusAI()
    ultimate_ai.start_ultimate_nexus()
    
    # Show diagnostic report every 60 seconds
    def diagnostic_reporter():
        while ultimate_ai.active:
            time.sleep(60)
            ultimate_ai.run_diagnostic_report()
    
    threading.Thread(target=diagnostic_reporter, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Ultimate NEXUS AI shutting down...")

if __name__ == "__main__":
    main()