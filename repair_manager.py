import os
import subprocess
import shutil
import psutil
from datetime import datetime
import threading # Added threading for future async operations
import json

class RepairManager:
    def __init__(self, status_callback=None, log_callback=None, progress_callback=None):
        self.status_callback = status_callback or (lambda x: None)
        self.log_callback = log_callback or (lambda x: None)
        self.progress_callback = progress_callback or (lambda x: None)
        self.stop_flag = False
        
        self.base_dir = os.path.dirname(__file__) # Base directory of OPRYXX scripts
        self.modules_dir = os.path.join(self.base_dir, 'modules')
        os.makedirs(self.modules_dir, exist_ok=True)
        
        self.manifest_path = os.path.join(self.modules_dir, 'modules_manifest.json')
        self.modules_metadata = {}
        
        self.load_manifest()
        self.create_and_register_default_modules()
    
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] [RepairManager] [{level}] {message}'
        if self.log_callback:
            self.log_callback(log_message)
    
    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)
    
    def update_progress(self, progress):
        if self.progress_callback:
            self.progress_callback(progress)

    def load_manifest(self):
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r', encoding='utf-8') as f:
                    self.modules_metadata = json.load(f)
                self.log("Module manifest loaded.")
            else:
                self.modules_metadata = {}
                self.save_manifest() # Create an empty manifest if none exists
                self.log("Module manifest not found, created a new one.")
        except Exception as e:
            self.log(f"Error loading module manifest: {e}", 'ERROR')
            self.modules_metadata = {} # Reset to empty if loading fails

    def save_manifest(self):
        try:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.modules_metadata, f, indent=4)
            self.log("Module manifest saved.")
        except Exception as e:
            self.log(f"Error saving module manifest: {e}", 'ERROR')

    def create_and_register_default_modules(self):
        """Create default .bat repair modules and ensure they are in the manifest."""
        default_module_definitions = {
            'temp_clean': {
                'name': 'Temporary File Cleanup',
                'description': 'Cleans various temporary file locations and prefetch.',
                'category': 'Maintenance',
                'language': 'Batch',
                'script_content': '''
@echo off
echo [STATUS] OPRYXX: Cleaning temporary files...
del /f /s /q %TEMP%\\*.* > nul 2>&1
del /f /s /q %SystemRoot%\\Temp\\*.* > nul 2>&1
del /f /s /q %SystemRoot%\\Prefetch\\*.* > nul 2>&1
echo [STATUS] OPRYXX: Temporary files cleaned.
exit /b 0
                '''
            },
            'sys_scan': {
                'name': 'System File Scan & Repair',
                'description': 'Runs SFC (System File Checker) and DISM to repair system image.',
                'category': 'Repair',
                'language': 'Batch',
                'script_content': '''
@echo off
echo [STATUS] OPRYXX: Running System File Checker (SFC)...
sfc /scannow
echo [STATUS] OPRYXX: Running DISM RestoreHealth...
DISM /Online /Cleanup-Image /RestoreHealth
echo [STATUS] OPRYXX: System file scan and repair complete.
exit /b 0
                '''
            },
            'disk_repair': {
                'name': 'Disk Check (C:)',
                'description': 'Schedules CHKDSK for drive C: on the next restart.',
                'category': 'Repair',
                'language': 'Batch',
                'script_content': '''
@echo off
echo [STATUS] OPRYXX: Scheduling disk check for C: (requires reboot)...
echo Y | chkdsk C: /f /r
echo [STATUS] OPRYXX: Disk check for C: scheduled.
exit /b 0
                '''
            },
            'net_reset': {
                'name': 'Network Stack Reset',
                'description': 'Resets Winsock, IP stack, and flushes DNS cache.',
                'category': 'Repair',
                'language': 'Batch',
                'script_content': '''
@echo off
echo [STATUS] OPRYXX: Resetting network stack...
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /renew
ipconfig /flushdns
echo [STATUS] OPRYXX: Network stack reset complete.
exit /b 0
                '''
            }
            # Add more default modules as needed
        }

        manifest_updated = False
        for module_id, details in default_module_definitions.items():
            script_filename = f"{module_id}.bat" # Default modules are batch files
            script_path = os.path.join(self.modules_dir, script_filename)
            
            # Create script file if it doesn't exist
            if not os.path.exists(script_path):
                try:
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(details['script_content'].strip())
                    self.log(f"Created default module script: {script_filename}")
                except Exception as e:
                    self.log(f"Failed to create default script {script_filename}: {e}", "ERROR")
                    continue # Skip registration if script creation fails

            # Register or update in manifest if it's a known default module
            if module_id not in self.modules_metadata or self.modules_metadata[module_id].get('is_default', False):
                self.modules_metadata[module_id] = {
                    'id': module_id,
                    'name': details['name'],
                    'description': details['description'],
                    'category': details['category'],
                    'language': details['language'],
                    'script_file': script_filename,
                    'enabled': True, # Defaults are enabled by default
                    'is_default': True,
                    'version': "1.0" # Basic versioning
                }
                manifest_updated = True
                self.log(f"Registered/Updated default module in manifest: {module_id}")

        if manifest_updated:
            self.save_manifest()

    def get_all_modules_metadata(self):
        """Returns a copy of all module metadata."""
        return self.modules_metadata.copy() # Return a copy to prevent direct modification

    def get_module_script_content(self, module_id):
        metadata = self.modules_metadata.get(module_id)
        if not metadata:
            self.log(f"Metadata not found for module {module_id}", 'ERROR')
            return None
        
        script_path = os.path.join(self.modules_dir, metadata['script_file'])
        try:
            if os.path.exists(script_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.log(f"Script file not found for module {module_id}: {script_path}", 'ERROR')
                return f"# SCRIPT FILE MISSING: {metadata['script_file']}"
        except Exception as e:
            self.log(f"Error reading script for {module_id}: {e}", 'ERROR')
            return f"# ERROR LOADING SCRIPT: {e}"

    def save_module(self, module_data, script_content, is_new_module, original_module_id=None):
        module_id = module_data['id']
        script_filename = module_data['script_file']
        script_path = os.path.join(self.modules_dir, script_filename)

        if is_new_module and module_id in self.modules_metadata:
            self.log(f"Module ID '{module_id}' already exists. Cannot create new module.", 'ERROR')
            return False
        
        if not is_new_module and original_module_id and original_module_id != module_id:
            # Handle ID change: remove old, add new (effectively a rename of the script file and manifest key)
            if module_id in self.modules_metadata:
                self.log(f"New module ID '{module_id}' already exists. Cannot rename.", 'ERROR')
                return False
            old_metadata = self.modules_metadata.pop(original_module_id, None)
            old_script_path = os.path.join(self.modules_dir, old_metadata['script_file'] if old_metadata else '')
            if old_metadata and os.path.exists(old_script_path):
                try:
                    os.remove(old_script_path)
                    self.log(f"Removed old script file during rename: {old_script_path}")
                except Exception as e:
                    self.log(f"Error removing old script file {old_script_path} during rename: {e}", "WARNING")       
        elif not is_new_module and original_module_id is None:
            self.log("Original module ID missing for an existing module save operation.", 'ERROR')
            return False

        try:
            # Write the script file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            self.log(f"Script file saved: {script_path}")

            # Update metadata (ensure 'is_default' is False for custom/edited modules)
            module_data['is_default'] = False 
            module_data['version'] = self.modules_metadata.get(module_id, {}).get('version', "1.0") # Preserve or set version
            # Increment version if content changed (simple check)
            # More robust versioning would involve hashing or more complex diffing
            # For now, let's assume any save to a custom module might be a new version
            if not is_new_module and self.modules_metadata.get(module_id, {}).get('script_content_hash') != hash(script_content): # Conceptual hash
                 current_version = self.modules_metadata.get(module_id, {}).get('version', "1.0")
                 # simple version increment: 1.0 -> 1.1, 1.9 -> 2.0
                 parts = current_version.split('.')
                 if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                     major, minor = int(parts[0]), int(parts[1])
                     minor += 1
                     if minor >= 10: # simple roll-over
                         major += 1
                         minor = 0
                     module_data['version'] = f"{major}.{minor}"
                 else: # fallback if version format is unexpected
                     module_data['version'] = "1.1" if current_version == "1.0" else current_version + "_updated"
            
            # module_data['script_content_hash'] = hash(script_content) # Store hash for future version check

            self.modules_metadata[module_id] = module_data
            self.save_manifest()
            return True
        except Exception as e:
            self.log(f"Error saving module {module_id}: {e}", 'ERROR')
            # Attempt to rollback manifest changes if script saving failed mid-operation
            if is_new_module and module_id in self.modules_metadata:
                del self.modules_metadata[module_id]
            elif not is_new_module and original_module_id and original_module_id != module_id:
                # Attempt to restore old metadata if rename failed
                if old_metadata: self.modules_metadata[original_module_id] = old_metadata
            self.save_manifest() # Try to save the potentially rolled-back manifest
            return False

    def delete_module(self, module_id):
        metadata = self.modules_metadata.get(module_id)
        if not metadata:
            self.log(f"Module {module_id} not found in manifest for deletion.", 'ERROR')
            return False
        
        if metadata.get('is_default', False):
            self.log(f"Cannot delete default module: {module_id}", 'WARNING')
            return False
        
        script_path = os.path.join(self.modules_dir, metadata['script_file'])
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
                self.log(f"Script file deleted: {script_path}")
            else:
                self.log(f"Script file not found for deletion (manifest inconsistency?): {script_path}", 'WARNING')
            
            del self.modules_metadata[module_id]
            self.save_manifest()
            return True
        except Exception as e:
            self.log(f"Error deleting module {module_id}: {e}", 'ERROR')
            return False

    def run_module(self, module_id):
        metadata = self.modules_metadata.get(module_id)
        if not metadata:
            self.log(f"Module '{module_id}' not found for execution.", 'ERROR')
            self.update_status(f"Error: Module {module_id} not found.")
            return False

        if not metadata.get('enabled', True):
            self.log(f"Module '{module_id}' is disabled. Skipping.", 'WARNING')
            self.update_status(f"Module {module_id} disabled.")
            return True # Considered success as it's intentionally skipped

        script_path = os.path.join(self.modules_dir, metadata['script_file'])
        if not os.path.exists(script_path):
            self.log(f"Script file not found for module '{module_id}': {script_path}", 'ERROR')
            self.update_status(f"Error: Script for {module_id} missing.")
            return False
        
        self.log(f"Executing module: {metadata.get('name', module_id)} ({metadata['script_file']}) Lng: {metadata.get('language')}")
        self.update_status(f"Running: {metadata.get('name', module_id)}")
        
        try:
            # Determine how to run based on language
            command = []
            script_language = metadata.get('language', 'Batch').lower()
            if script_language == 'batch':
                command = [script_path]
            elif script_language == 'powershell':
                command = ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_path]
            elif script_language == 'python':
                command = ['python.exe', script_path] # Assumes python is in PATH
            else:
                self.log(f"Unsupported script language '{script_language}' for module {module_id}", 'ERROR')
                return False

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True, 
                shell=False, # Important for security, especially with PowerShell/Python
                cwd=self.modules_dir # Run script from modules directory
            )
            
            # Stream stdout and stderr
            for line in iter(process.stdout.readline, ''):
                if self.stop_flag: process.terminate(); break
                if line.strip(): self.log(f"[M:{module_id}] {line.strip()}")
                if "[STATUS]" in line: self.update_status(line.split("[STATUS]")[-1].strip())
            
            for line in iter(process.stderr.readline, ''):
                if self.stop_flag: process.terminate(); break
                if line.strip(): self.log(f"[M:{module_id}|ERR] {line.strip()}", 'ERROR')

            process.wait()
            
            if self.stop_flag:
                self.log(f"Module '{module_id}' execution stopped by user.", 'WARNING')
                self.update_status("Execution stopped.")
                return False

            if process.returncode == 0:
                self.log(f"Module '{metadata.get('name', module_id)}' completed successfully.")
                self.update_status(f"Completed: {metadata.get('name', module_id)}")
                return True
            else:
                self.log(f"Module '{metadata.get('name', module_id)}' failed with code {process.returncode}.", 'ERROR')
                self.update_status(f"Failed: {metadata.get('name', module_id)}")
                return False
        except Exception as e:
            self.log(f"Critical error running module '{module_id}': {e}", 'ERROR')
            self.update_status(f"Error with module: {module_id}")
            return False

    def run_repair_chain(self, selected_module_ids):
        self.stop_flag = False
        total_selected = len(selected_module_ids)
        if total_selected == 0:
            self.log("No modules selected for repair chain.", "WARNING")
            self.update_status("No modules selected.")
            return

        self.log(f"Starting repair chain with {total_selected} module(s). Selected: {', '.join(selected_module_ids)}")
        self.update_status(f"Starting repair chain ({total_selected} modules)...")
        self.update_progress(0)

        # Automatic backup if configured (assuming config is passed or handled elsewhere)
        # For now, let's say it's always attempted or controlled by a GUI setting directly passed.
        if self.config.get('auto_backup', True): # GUI should pass this setting via OPRYXXEnhanced config
             self.create_backup() 

        modules_completed = 0
        for i, module_id in enumerate(selected_module_ids):
            if self.stop_flag:
                self.log("Repair chain stopped by user.", 'WARNING')
                self.update_status("Repair chain stopped.")
                break
            
            self.update_progress((modules_completed / total_selected) * 100)
            success = self.run_module(module_id)
            
            if success:
                modules_completed += 1
            elif not self.stop_flag: # If module failed and not stopped by user
                # Decide whether to continue (e.g., based on a config or user prompt via GUI)
                self.log(f"Module {module_id} failed. Continuing chain (default behavior).", 'WARNING')
                # For now, we continue. A more robust system would allow user choice.
        
        final_progress = (modules_completed / total_selected) * 100 if total_selected > 0 else 100
        self.update_progress(final_progress)
        
        if not self.stop_flag:
            self.log(f"Repair chain finished. {modules_completed}/{total_selected} modules ran successfully.")
            self.update_status(f"Repair complete. {modules_completed}/{total_selected} successful.")
        else:
            self.log(f"Repair chain aborted. {modules_completed}/{total_selected} modules ran before stop.")
            self.update_status(f"Repair aborted. {modules_completed}/{total_selected} ran.")

    def create_backup(self): # Placeholder for backup logic
        self.log("Backup process initiated (placeholder).", 'INFO')
        # Actual backup logic here, e.g., system restore point, file backup
        # For now, just simulate time and success
        # time.sleep(2) # Simulate backup time
        self.update_status("Creating system backup...")
        self.log("System backup completed (simulated).", 'INFO')
        self.update_status("System backup complete.")
        return True

    def stop(self):
        self.stop_flag = True
        self.log("Stop signal received for current operations.", 'WARNING')
        self.update_status("Stopping current operations...")

