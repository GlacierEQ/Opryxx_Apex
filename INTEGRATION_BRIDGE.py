"""
INTEGRATION BRIDGE - Seamless Component Integration
Connects all OPRYXX components into the Ultimate Master GUI
"""

import os
import sys
import importlib
import traceback
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ComponentIntegration:
    """Integrates all OPRYXX components"""
    
    def __init__(self):
        self.components = {}
        self.integration_status = {}
    
    def integrate_component(self, name: str, module_path: str, class_name: str = None):
        """Integrate a component with error handling"""
        try:
            # Try to import the module
            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location(name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get the class if specified
                if class_name and hasattr(module, class_name):
                    component_class = getattr(module, class_name)
                    self.components[name] = component_class
                else:
                    self.components[name] = module
                
                self.integration_status[name] = {'status': 'SUCCESS', 'error': None}
                logger.info(f"Successfully integrated component: {name}")
                return True
            else:
                error_msg = f"Module file not found: {module_path}"
                self.integration_status[name] = {'status': 'FAILED', 'error': error_msg}
                logger.warning(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Failed to integrate {name}: {str(e)}"
            self.integration_status[name] = {'status': 'FAILED', 'error': error_msg}
            logger.error(error_msg)
            return False
    
    def get_component(self, name: str):
        """Get an integrated component"""
        return self.components.get(name)
    
    def get_integration_status(self):
        """Get integration status for all components"""
        return self.integration_status.copy()

def setup_opryxx_integration():
    """Setup integration for all OPRYXX components"""
    try:
        integration = ComponentIntegration()
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Core components
        components_to_integrate = [
            ('mega_opryxx', os.path.join(base_path, 'gui', 'MEGA_OPRYXX.py'), 'MegaOPRYXX'),
            ('ai_workbench', os.path.join(base_path, 'ai', 'AI_WORKBENCH.py'), 'AIWorkbench'),
            ('ultimate_ai', os.path.join(base_path, 'ai', 'ULTIMATE_AI_OPTIMIZER.py'), 'UltimateAIOptimizer'),
            ('unified_gui', os.path.join(base_path, 'UNIFIED_FULL_STACK_GUI.py'), 'UnifiedFullStackSystem'),
            ('master_start', os.path.join(base_path, 'master_start.py'), 'MasterStartApp'),
            ('pipelines', os.path.join(base_path, 'pipelines.py'), None)
        ]
        
        # Integrate each component
        for name, path, class_name in components_to_integrate:
            integration.integrate_component(name, path, class_name)
        
        return integration
        
    except Exception as e:
        logger.error(f"Failed to setup OPRYXX integration: {e}")
        return None

class SafeComponentWrapper:
    """Safe wrapper for components with error handling"""
    
    def __init__(self, component, name: str):
        self.component = component
        self.name = name
        self.active = True
    
    def safe_call(self, method_name: str, *args, **kwargs):
        """Safely call a component method"""
        try:
            if not self.active:
                return None
            
            if hasattr(self.component, method_name):
                method = getattr(self.component, method_name)
                return method(*args, **kwargs)
            else:
                logger.warning(f"Method {method_name} not found in {self.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling {method_name} on {self.name}: {e}")
            return None
    
    def safe_get_attr(self, attr_name: str, default=None):
        """Safely get a component attribute"""
        try:
            if not self.active:
                return default
            
            return getattr(self.component, attr_name, default)
        except Exception as e:
            logger.error(f"Error getting {attr_name} from {self.name}: {e}")
            return default
    
    def deactivate(self):
        """Deactivate the component"""
        self.active = False

def create_safe_components(integration: ComponentIntegration):
    """Create safe wrappers for all integrated components"""
    safe_components = {}
    
    for name, component in integration.components.items():
        try:
            safe_components[name] = SafeComponentWrapper(component, name)
        except Exception as e:
            logger.error(f"Failed to create safe wrapper for {name}: {e}")
    
    return safe_components

# Export integration functions
__all__ = ['ComponentIntegration', 'SafeComponentWrapper', 'setup_opryxx_integration', 'create_safe_components']