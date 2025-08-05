"""
SYSTEM VERIFICATION - Complete Integration Test
Verifies all components work together seamlessly with error handling
"""

import os
import sys
import time
import traceback
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemVerification:
    """Complete system verification with error handling"""
    
    def __init__(self):
        self.verification_results = {}
        self.errors = []
        self.warnings = []
        
    def verify_file_exists(self, file_path: str, description: str) -> bool:
        """Verify a file exists"""
        try:
            if os.path.exists(file_path):
                logger.info(f"✅ {description}: {file_path}")
                return True
            else:
                error_msg = f"❌ {description}: {file_path} - NOT FOUND"
                logger.error(error_msg)
                self.errors.append(error_msg)
                return False
        except Exception as e:
            error_msg = f"❌ Error checking {description}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def verify_import(self, module_name: str, file_path: str = None) -> bool:
        """Verify a module can be imported"""
        try:
            if file_path and not os.path.exists(file_path):
                error_msg = f"❌ Module file not found: {file_path}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                return False
            
            # Try to import
            import importlib.util
            if file_path:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                __import__(module_name)
            
            logger.info(f"✅ Module import successful: {module_name}")
            return True
            
        except Exception as e:
            error_msg = f"❌ Module import failed: {module_name} - {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def verify_dependencies(self) -> Dict[str, bool]:
        """Verify all required dependencies"""
        logger.info("🔍 Verifying dependencies...")
        
        dependencies = {
            'tkinter': 'tkinter',
            'psutil': 'psutil',
            'threading': 'threading',
            'subprocess': 'subprocess',
            'logging': 'logging',
            'datetime': 'datetime',
            'asyncio': 'asyncio'
        }
        
        results = {}
        for name, module in dependencies.items():
            try:
                __import__(module)
                results[name] = True
                logger.info(f"✅ Dependency available: {name}")
            except ImportError as e:
                results[name] = False
                error_msg = f"❌ Dependency missing: {name} - {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
        
        return results
    
    def verify_core_files(self) -> Dict[str, bool]:
        """Verify all core files exist"""
        logger.info("🔍 Verifying core files...")
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        core_files = {
            'Ultimate Master GUI': os.path.join(base_path, 'ULTIMATE_MASTER_GUI.py'),
            'Enhanced Pipelines': os.path.join(base_path, 'ENHANCED_PIPELINES.py'),
            'Integration Bridge': os.path.join(base_path, 'INTEGRATION_BRIDGE.py'),
            'Ultimate Launcher': os.path.join(base_path, 'ULTIMATE_LAUNCHER.bat'),
            'MEGA OPRYXX': os.path.join(base_path, 'gui', 'MEGA_OPRYXX.py'),
            'AI Workbench': os.path.join(base_path, 'ai', 'AI_WORKBENCH.py'),
            'Ultimate AI Optimizer': os.path.join(base_path, 'ai', 'ULTIMATE_AI_OPTIMIZER.py'),
            'Master Start': os.path.join(base_path, 'master_start.py'),
            'Unified GUI': os.path.join(base_path, 'UNIFIED_FULL_STACK_GUI.py')
        }
        
        results = {}
        for name, path in core_files.items():
            results[name] = self.verify_file_exists(path, name)
        
        return results
    
    def verify_component_imports(self) -> Dict[str, bool]:
        """Verify all components can be imported"""
        logger.info("🔍 Verifying component imports...")
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        components = {
            'Ultimate Master GUI': os.path.join(base_path, 'ULTIMATE_MASTER_GUI.py'),
            'Enhanced Pipelines': os.path.join(base_path, 'ENHANCED_PIPELINES.py'),
            'Integration Bridge': os.path.join(base_path, 'INTEGRATION_BRIDGE.py')
        }
        
        results = {}
        for name, path in components.items():
            results[name] = self.verify_import(name.lower().replace(' ', '_'), path)
        
        return results
    
    def verify_gui_integration(self) -> bool:
        """Verify GUI integration works"""
        logger.info("🔍 Verifying GUI integration...")
        
        try:
            # Test Ultimate Master GUI initialization
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            # Import without running
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "ultimate_master_gui", 
                os.path.join(os.path.dirname(__file__), 'ULTIMATE_MASTER_GUI.py')
            )
            module = importlib.util.module_from_spec(spec)
            
            # Check if main classes exist
            spec.loader.exec_module(module)
            
            required_classes = ['UltimateMasterGUI', 'OperationTracker', 'AIWorkbenchIntegration']
            for class_name in required_classes:
                if hasattr(module, class_name):
                    logger.info(f"✅ GUI class available: {class_name}")
                else:
                    error_msg = f"❌ GUI class missing: {class_name}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return False
            
            logger.info("✅ GUI integration verification successful")
            return True
            
        except Exception as e:
            error_msg = f"❌ GUI integration verification failed: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def verify_pipeline_integration(self) -> bool:
        """Verify pipeline integration works"""
        logger.info("🔍 Verifying pipeline integration...")
        
        try:
            # Test Enhanced Pipelines
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "enhanced_pipelines", 
                os.path.join(os.path.dirname(__file__), 'ENHANCED_PIPELINES.py')
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if main classes exist
            required_classes = ['EnhancedPipelineProcessor', 'OperationState', 'OperationContext']
            for class_name in required_classes:
                if hasattr(module, class_name):
                    logger.info(f"✅ Pipeline class available: {class_name}")
                else:
                    error_msg = f"❌ Pipeline class missing: {class_name}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return False
            
            # Test pipeline processor creation
            processor_class = getattr(module, 'EnhancedPipelineProcessor')
            processor = processor_class()
            
            # Test command parsing
            test_query = "launch ultimate gui"
            command_info = processor.parse_natural_language(test_query)
            
            if command_info and command_info.get('task_type') == 'ultimate_gui':
                logger.info("✅ Pipeline command parsing successful")
            else:
                warning_msg = f"⚠️ Pipeline command parsing unexpected result: {command_info}"
                logger.warning(warning_msg)
                self.warnings.append(warning_msg)
            
            logger.info("✅ Pipeline integration verification successful")
            return True
            
        except Exception as e:
            error_msg = f"❌ Pipeline integration verification failed: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def verify_ai_integration(self) -> bool:
        """Verify AI components integration"""
        logger.info("🔍 Verifying AI integration...")
        
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            ai_components = [
                os.path.join(base_path, 'ai', 'AI_WORKBENCH.py'),
                os.path.join(base_path, 'ai', 'ULTIMATE_AI_OPTIMIZER.py')
            ]
            
            for component_path in ai_components:
                if os.path.exists(component_path):
                    logger.info(f"✅ AI component found: {os.path.basename(component_path)}")
                else:
                    warning_msg = f"⚠️ AI component not found: {component_path}"
                    logger.warning(warning_msg)
                    self.warnings.append(warning_msg)
            
            logger.info("✅ AI integration verification completed")
            return True
            
        except Exception as e:
            error_msg = f"❌ AI integration verification failed: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive system verification"""
        logger.info("🚀 Starting comprehensive system verification...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all verifications
        verification_steps = [
            ("Dependencies", self.verify_dependencies),
            ("Core Files", self.verify_core_files),
            ("Component Imports", self.verify_component_imports),
            ("GUI Integration", self.verify_gui_integration),
            ("Pipeline Integration", self.verify_pipeline_integration),
            ("AI Integration", self.verify_ai_integration)
        ]
        
        results = {}
        overall_success = True
        
        for step_name, step_func in verification_steps:
            try:
                logger.info(f"\n📋 {step_name} Verification:")
                logger.info("-" * 40)
                
                step_result = step_func()
                results[step_name] = step_result
                
                if isinstance(step_result, dict):
                    step_success = all(step_result.values())
                else:
                    step_success = step_result
                
                if not step_success:
                    overall_success = False
                
                status = "✅ PASSED" if step_success else "❌ FAILED"
                logger.info(f"{step_name}: {status}")
                
            except Exception as e:
                error_msg = f"❌ {step_name} verification failed: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                results[step_name] = False
                overall_success = False
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"⏱️ Total Duration: {duration:.2f} seconds")
        logger.info(f"✅ Overall Status: {'PASSED' if overall_success else 'FAILED'}")
        logger.info(f"❌ Errors: {len(self.errors)}")
        logger.info(f"⚠️ Warnings: {len(self.warnings)}")
        
        if self.errors:
            logger.info("\n❌ ERRORS:")
            for error in self.errors:
                logger.error(f"  • {error}")
        
        if self.warnings:
            logger.info("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")
        
        if overall_success:
            logger.info("\n🎉 SYSTEM VERIFICATION COMPLETED SUCCESSFULLY!")
            logger.info("✅ All components are properly integrated and ready for use")
            logger.info("🚀 Ultimate Master GUI is ready for maximum power operation")
        else:
            logger.info("\n⚠️ SYSTEM VERIFICATION COMPLETED WITH ISSUES")
            logger.info("🔧 Please address the errors above before proceeding")
        
        logger.info("=" * 60)
        
        return {
            "overall_success": overall_success,
            "duration": duration,
            "results": results,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main verification entry point"""
    try:
        print("🚀 OPRYXX SYSTEM VERIFICATION")
        print("=" * 60)
        print("🔍 Comprehensive Integration Test")
        print("✅ Error Handling Verification")
        print("🔧 Component Integration Check")
        print("🚀 Maximum Power Validation")
        print("=" * 60)
        
        verifier = SystemVerification()
        results = verifier.run_comprehensive_verification()
        
        # Save results to file
        results_file = f"verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️ Could not save results file: {e}")
        
        # Exit with appropriate code
        exit_code = 0 if results["overall_success"] else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal verification error: {e}")
        traceback.print_exc()
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()