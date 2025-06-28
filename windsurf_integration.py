"""
Windsurf Extensions Integration for OPRYXX
"""

import json
import os
from typing import Dict, List

class WindsurfIntegration:
    def __init__(self):
        self.config = self._load_windsurf_config()
        self.extensions = self._discover_extensions()
        
    def _load_windsurf_config(self) -> Dict:
        """Load Windsurf configuration"""
        config_files = [
            '.windsurfrules',
            'windsurf_ai_rules.md',
            '.bevel/shareable/config.json'
        ]
        
        config = {}
        for file_path in config_files:
            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.json'):
                        with open(file_path, 'r') as f:
                            config.update(json.load(f))
                    else:
                        with open(file_path, 'r') as f:
                            config[file_path] = f.read()
                except Exception as e:
                    print(f"Warning: Could not load {file_path}: {e}")
        
        return config
    
    def _discover_extensions(self) -> List[str]:
        """Discover available Windsurf extensions"""
        extensions = []
        
        # Check for Bevel integration
        if os.path.exists('.bevel'):
            extensions.append('bevel')
        
        # Check for Continue integration
        if os.path.exists('.continue'):
            extensions.append('continue')
        
        # Check for Cursor integration
        if os.path.exists('.cursor'):
            extensions.append('cursor')
        
        # Check for Qodo integration
        if os.path.exists('.qodo'):
            extensions.append('qodo')
        
        return extensions
    
    def validate_integration(self) -> Dict:
        """Validate Windsurf extensions integration"""
        validation = {
            'status': 'OK',
            'extensions_found': self.extensions,
            'config_loaded': bool(self.config),
            'issues': []
        }
        
        # Check OPRYXX-specific requirements
        required_features = [
            'ai/',
            'recovery/',
            'enhancements/',
            'performance_benchmark.py',
            'MASTER_LAUNCHER.bat'
        ]
        
        for feature in required_features:
            if not os.path.exists(feature):
                validation['issues'].append(f"Missing required feature: {feature}")
        
        # Check Windsurf rules compliance
        if '.windsurfrules' not in self.config:
            validation['issues'].append("Windsurf rules not properly configured")
        
        if validation['issues']:
            validation['status'] = 'ISSUES_FOUND'
        
        return validation
    
    def optimize_for_windsurf(self):
        """Optimize OPRYXX for Windsurf integration"""
        optimizations = []
        
        # Create Windsurf-compatible API endpoints
        if not os.path.exists('api/windsurf_endpoints.json'):
            self._create_windsurf_api()
            optimizations.append("Created Windsurf API endpoints")
        
        # Update configuration for Windsurf compatibility
        self._update_windsurf_config()
        optimizations.append("Updated Windsurf configuration")
        
        # Create extension hooks
        self._create_extension_hooks()
        optimizations.append("Created extension hooks")
        
        return optimizations
    
    def _create_windsurf_api(self):
        """Create Windsurf-compatible API endpoints"""
        api_config = {
            "endpoints": {
                "/api/v1/health": {
                    "method": "GET",
                    "description": "System health check",
                    "handler": "get_system_health"
                },
                "/api/v1/optimize": {
                    "method": "POST",
                    "description": "Trigger system optimization",
                    "handler": "run_optimization"
                },
                "/api/v1/recovery": {
                    "method": "POST",
                    "description": "Execute recovery operation",
                    "handler": "run_recovery"
                },
                "/api/v1/performance": {
                    "method": "GET",
                    "description": "Get performance metrics",
                    "handler": "get_performance_metrics"
                }
            }
        }
        
        os.makedirs('api', exist_ok=True)
        with open('api/windsurf_endpoints.json', 'w') as f:
            json.dump(api_config, f, indent=2)
    
    def _update_windsurf_config(self):
        """Update Windsurf configuration"""
        windsurf_config = {
            "opryxx_integration": {
                "version": "2.0",
                "features": {
                    "ai_optimization": True,
                    "recovery_operations": True,
                    "performance_monitoring": True,
                    "gpu_acceleration": True
                },
                "endpoints": {
                    "health": "/api/v1/health",
                    "optimize": "/api/v1/optimize",
                    "recovery": "/api/v1/recovery",
                    "performance": "/api/v1/performance"
                }
            }
        }
        
        # Update .bevel config if exists
        if os.path.exists('.bevel/shareable/config.json'):
            try:
                with open('.bevel/shareable/config.json', 'r') as f:
                    existing_config = json.load(f)
                
                existing_config.update(windsurf_config)
                
                with open('.bevel/shareable/config.json', 'w') as f:
                    json.dump(existing_config, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not update Bevel config: {e}")
    
    def _create_extension_hooks(self):
        """Create hooks for Windsurf extensions"""
        hooks = {
            "pre_optimization": [],
            "post_optimization": [],
            "pre_recovery": [],
            "post_recovery": [],
            "performance_update": []
        }
        
        os.makedirs('api', exist_ok=True)
        with open('api/extension_hooks.json', 'w') as f:
            json.dump(hooks, f, indent=2)
    
    def get_integration_status(self) -> Dict:
        """Get current integration status"""
        return {
            'windsurf_extensions': self.extensions,
            'config_files': list(self.config.keys()),
            'api_available': os.path.exists('api/windsurf_endpoints.json'),
            'hooks_available': os.path.exists('api/extension_hooks.json'),
            'opryxx_features': {
                'ai_systems': len([f for f in os.listdir('ai') if f.endswith('.py')]),
                'recovery_modules': len([f for f in os.listdir('recovery') if f.endswith('.py')]),
                'enhancements': len([f for f in os.listdir('enhancements') if f.endswith('.py')])
            }
        }

def main():
    """Test Windsurf integration"""
    print("🌊 OPRYXX Windsurf Integration Check")
    print("=" * 50)
    
    integration = WindsurfIntegration()
    
    # Validate integration
    validation = integration.validate_integration()
    print(f"Status: {validation['status']}")
    print(f"Extensions: {', '.join(validation['extensions_found'])}")
    
    if validation['issues']:
        print("Issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    # Optimize for Windsurf
    optimizations = integration.optimize_for_windsurf()
    print(f"\nOptimizations applied:")
    for opt in optimizations:
        print(f"  ✅ {opt}")
    
    # Show status
    status = integration.get_integration_status()
    print(f"\nIntegration Status:")
    print(f"  Extensions: {', '.join(status['windsurf_extensions'])}")
    print(f"  API Available: {status['api_available']}")
    print(f"  OPRYXX Features: {status['opryxx_features']}")

if __name__ == "__main__":
    main()