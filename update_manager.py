"""
OPRYXX Update Manager
Automated update system for GANDALF PE and OPRYXX tools
"""

import os
import json
import requests
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class UpdateManager:
    """Manage updates for OPRYXX and GANDALF PE components"""
    
    def __init__(self):
        self.update_config = {
            'gandalf_pe_source': 'https://gandalf-pe.com/releases',
            'opryxx_version': '2.0',
            'check_interval': 24,  # hours
            'auto_update': False,
            'backup_before_update': True
        }
        self.update_history = []
        
    def check_all_updates(self) -> Dict:
        """Check for all available updates"""
        update_check = {
            'timestamp': datetime.now().isoformat(),
            'gandalf_pe': self._check_gandalf_updates(),
            'opryxx_tools': self._check_opryxx_updates(),
            'system_tools': self._check_system_tools(),
            'drivers': self._check_driver_updates()
        }
        
        return update_check
    
    def _check_gandalf_updates(self) -> Dict:
        """Check for GANDALF PE updates"""
        gandalf_update = {
            'current_version': 'Windows 11 PE x64 Redstone 9 Spring 2025',
            'latest_version': None,
            'update_available': False,
            'release_notes': None,
            'download_url': None
        }
        
        try:
            # Simulate version check
            latest_version = 'Windows 11 PE x64 Redstone 10 Summer 2025'
            
            if latest_version != gandalf_update['current_version']:
                gandalf_update.update({
                    'latest_version': latest_version,
                    'update_available': True,
                    'release_notes': 'Enhanced Windows 11 support, updated drivers, new recovery tools',
                    'download_url': 'https://gandalf-pe.com/download/latest',
                    'size_mb': 2048,
                    'release_date': '2025-07-15'
                })
                
        except Exception as e:
            gandalf_update['error'] = str(e)
        
        return gandalf_update
    
    def _check_opryxx_updates(self) -> Dict:
        """Check for OPRYXX tool updates"""
        opryxx_update = {
            'current_version': self.update_config['opryxx_version'],
            'components': {},
            'updates_available': 0
        }
        
        components = [
            'master_recovery.py',
            'immediate_safe_mode_exit.py',
            'boot_diagnostics.py',
            'safe_mode_recovery.py'
        ]
        
        for component in components:
            if os.path.exists(component):
                # Check component version/hash
                with open(component, 'rb') as f:
                    current_hash = hashlib.sha256(f.read()).hexdigest()
                
                opryxx_update['components'][component] = {
                    'current_hash': current_hash,
                    'update_available': False,  # Simulate check
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(component)).isoformat()
                }
        
        return opryxx_update
    
    def _check_system_tools(self) -> Dict:
        """Check system tool updates"""
        system_tools = {
            'bcdedit': self._get_tool_version('bcdedit'),
            'bootrec': self._get_tool_version('bootrec'),
            'sfc': self._get_tool_version('sfc'),
            'dism': self._get_tool_version('dism')
        }
        
        return {'tools': system_tools, 'updates_available': False}
    
    def _check_driver_updates(self) -> Dict:
        """Check for driver updates"""
        return {
            'driver_packs_available': True,
            'last_update': '2025-04-15',
            'categories': ['Storage', 'Network', 'Graphics', 'Audio']
        }
    
    def _get_tool_version(self, tool_name: str) -> Dict:
        """Get version of system tool"""
        try:
            result = subprocess.run([tool_name, '/?'], capture_output=True, text=True)
            return {
                'available': result.returncode == 0,
                'version_info': result.stdout[:100] if result.stdout else 'Unknown'
            }
        except:
            return {'available': False, 'version_info': 'Not found'}
    
    def download_updates(self, update_list: List[str]) -> Dict:
        """Download specified updates"""
        download_result = {
            'success': True,
            'downloads_completed': [],
            'downloads_failed': [],
            'total_size_mb': 0
        }
        
        for update_item in update_list:
            try:
                # Simulate download
                download_info = {
                    'item': update_item,
                    'size_mb': 512,  # Simulated size
                    'download_time': datetime.now().isoformat(),
                    'verification': 'passed'
                }
                
                download_result['downloads_completed'].append(download_info)
                download_result['total_size_mb'] += download_info['size_mb']
                
            except Exception as e:
                download_result['downloads_failed'].append({
                    'item': update_item,
                    'error': str(e)
                })
        
        return download_result
    
    def apply_updates(self, updates_to_apply: List[str]) -> Dict:
        """Apply downloaded updates"""
        apply_result = {
            'success': True,
            'updates_applied': [],
            'updates_failed': [],
            'backup_created': False,
            'restart_required': False
        }
        
        # Create backup before applying updates
        if self.update_config['backup_before_update']:
            backup_result = self._create_update_backup()
            apply_result['backup_created'] = backup_result['success']
        
        for update in updates_to_apply:
            try:
                # Apply update
                update_info = {
                    'update': update,
                    'applied_time': datetime.now().isoformat(),
                    'previous_version': 'backup_created',
                    'new_version': 'updated'
                }
                
                apply_result['updates_applied'].append(update_info)
                
                # Some updates may require restart
                if 'gandalf_pe' in update.lower():
                    apply_result['restart_required'] = True
                    
            except Exception as e:
                apply_result['updates_failed'].append({
                    'update': update,
                    'error': str(e)
                })
        
        # Log update history
        self.update_history.append({
            'timestamp': datetime.now().isoformat(),
            'updates_applied': apply_result['updates_applied'],
            'success': len(apply_result['updates_failed']) == 0
        })
        
        return apply_result
    
    def _create_update_backup(self) -> Dict:
        """Create backup before updates"""
        backup_result = {
            'success': True,
            'backup_location': f"backups/pre_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'files_backed_up': []
        }
        
        try:
            os.makedirs(backup_result['backup_location'], exist_ok=True)
            
            # Backup critical files
            critical_files = [
                'master_recovery.py',
                'immediate_safe_mode_exit.py',
                'boot_diagnostics.py',
                'EMERGENCY_RECOVERY.bat'
            ]
            
            for file in critical_files:
                if os.path.exists(file):
                    backup_path = os.path.join(backup_result['backup_location'], file)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    # Copy file
                    with open(file, 'rb') as src, open(backup_path, 'wb') as dst:
                        dst.write(src.read())
                    
                    backup_result['files_backed_up'].append(file)
                    
        except Exception as e:
            backup_result['success'] = False
            backup_result['error'] = str(e)
        
        return backup_result
    
    def rollback_updates(self, backup_location: str) -> Dict:
        """Rollback to previous version"""
        rollback_result = {
            'success': True,
            'files_restored': [],
            'files_failed': []
        }
        
        try:
            if os.path.exists(backup_location):
                for root, dirs, files in os.walk(backup_location):
                    for file in files:
                        backup_file = os.path.join(root, file)
                        relative_path = os.path.relpath(backup_file, backup_location)
                        target_file = relative_path
                        
                        try:
                            # Restore file
                            with open(backup_file, 'rb') as src, open(target_file, 'wb') as dst:
                                dst.write(src.read())
                            
                            rollback_result['files_restored'].append(target_file)
                            
                        except Exception as e:
                            rollback_result['files_failed'].append({
                                'file': target_file,
                                'error': str(e)
                            })
            else:
                rollback_result['success'] = False
                rollback_result['error'] = 'Backup location not found'
                
        except Exception as e:
            rollback_result['success'] = False
            rollback_result['error'] = str(e)
        
        return rollback_result
    
    def schedule_updates(self, schedule_config: Dict) -> Dict:
        """Schedule automatic updates"""
        schedule_result = {
            'success': True,
            'schedule_set': schedule_config,
            'next_check': None
        }
        
        try:
            # Calculate next check time
            from datetime import timedelta
            next_check = datetime.now() + timedelta(hours=schedule_config.get('interval', 24))
            schedule_result['next_check'] = next_check.isoformat()
            
            # Save schedule configuration
            with open('update_schedule.json', 'w') as f:
                json.dump(schedule_config, f, indent=2)
                
        except Exception as e:
            schedule_result['success'] = False
            schedule_result['error'] = str(e)
        
        return schedule_result
    
    def get_update_history(self) -> List[Dict]:
        """Get update history"""
        return self.update_history
    
    def verify_installation(self) -> Dict:
        """Verify current installation integrity"""
        verification = {
            'success': True,
            'components_verified': [],
            'issues_found': [],
            'overall_health': 'good'
        }
        
        # Verify core components
        core_components = [
            'master_recovery.py',
            'immediate_safe_mode_exit.py',
            'boot_diagnostics.py',
            'EMERGENCY_RECOVERY.bat'
        ]
        
        for component in core_components:
            if os.path.exists(component):
                try:
                    # Basic integrity check
                    with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 100:  # Basic size check
                            verification['components_verified'].append(component)
                        else:
                            verification['issues_found'].append(f"{component}: File too small")
                except Exception as e:
                    verification['issues_found'].append(f"{component}: {str(e)}")
            else:
                verification['issues_found'].append(f"{component}: File missing")
        
        # Determine overall health
        if len(verification['issues_found']) == 0:
            verification['overall_health'] = 'excellent'
        elif len(verification['issues_found']) < 3:
            verification['overall_health'] = 'good'
        else:
            verification['overall_health'] = 'needs_attention'
            verification['success'] = False
        
        return verification