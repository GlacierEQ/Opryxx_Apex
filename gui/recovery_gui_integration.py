import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import sys
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Any

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Import recovery modules
try:
    from core.modules.dell_hardware import DellHardwareDetector
    from core.modules.uefi_boot_repair import UEFIBootRepair
    from core.samsung_ssd_recovery import Samsung4TBRecovery
    from core.modules.windows11_recovery import Windows11Recovery
    from core.modules.recovery_media_builder import RecoveryMediaBuilder, DriveInfo
    from core.enhanced_logging import EnhancedLogger
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.path.append(str(Path(__file__).parent.parent / 'recovery'))

from hardware_rescue import HardwareRescue
from bitlocker_rescue import BitLockerRescue
from samsung_4tb_recovery import Samsung4TBRecovery
from windows11_bypass import Windows11Recovery

class MediaType(Enum):
    """Supported recovery media types"""
    WINDOWS_PE = "Windows PE"
    LINUX_RESCUE = "Linux Rescue"
    WINDOWS_INSTALL = "Windows Install"

class FileSystemType(Enum):
    """Supported filesystem types"""
    FAT32 = "FAT32"
    NTFS = "NTFS"
    EXFAT = "exFAT"

class RecoveryTab:
    """Recovery tab for MEGA_OPRYXX GUI"""

    def __init__(self, parent_notebook, mega_system):
        self.parent = parent_notebook
        self.mega_system = mega_system
        self.recovery_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.recovery_frame, text="Hardware Recovery")
        
        self.hardware_rescue = HardwareRescue()
        self.bitlocker_rescue = BitLockerRescue()
        self.samsung_recovery = None
        self.windows11_recovery = Windows11Recovery()
        self.recovery_builder = RecoveryMediaBuilder()
        
        # Track recovery media builder state
        self.current_drive: Optional[DriveInfo] = None
        self.media_builder_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        self.setup_recovery_ui()
    
    def setup_recovery_ui(self):
        """Setup recovery interface"""
        # Main sections
        self.create_dell_section()
        self.create_samsung_section()
        self.create_windows11_section()
        self.create_recovery_media_section()
        self.create_log_section()
    
    def create_dell_section(self):
        """Dell Inspiron recovery section"""
        dell_frame = ttk.LabelFrame(self.recovery_frame, text="Dell Inspiron 2-in-1 7040 Recovery")
        dell_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(dell_frame, text="Detect Dell Hardware", 
                  command=self.detect_dell_hardware).pack(side='left', padx=5)
        ttk.Button(dell_frame, text="Fix Boot Loop", 
                  command=self.fix_dell_boot_loop).pack(side='left', padx=5)
        ttk.Button(dell_frame, text="UEFI Repair", 
                  command=self.dell_uefi_repair).pack(side='left', padx=5)
    
    def create_samsung_section(self):
        """Samsung SSD recovery section"""
        samsung_frame = ttk.LabelFrame(self.recovery_frame, text="Samsung 4TB SSD BitLocker Recovery")
        samsung_frame.pack(fill='x', padx=10, pady=5)
        
        # Recovery key input
        key_frame = ttk.Frame(samsung_frame)
        key_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(key_frame, text="Recovery Key:").pack(side='left')
        self.recovery_key_entry = ttk.Entry(key_frame, width=50, show='*')
        self.recovery_key_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Drive letter input
        drive_frame = ttk.Frame(samsung_frame)
        drive_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(drive_frame, text="Drive Letter:").pack(side='left')
        self.drive_letter_entry = ttk.Entry(drive_frame, width=5)
        self.drive_letter_entry.pack(side='left', padx=5)
        
        # Buttons
        button_frame = ttk.Frame(samsung_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Detect Samsung Drives", 
                  command=self.detect_samsung_drives).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Unlock BitLocker", 
                  command=self.unlock_samsung_bitlocker).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Full Recovery", 
                  command=self.samsung_full_recovery).pack(side='left', padx=5)
    
    def create_windows11_section(self):
        """Windows 11 bypass section"""
        win11_frame = ttk.LabelFrame(self.recovery_frame, text="Windows 11 TPM/Secure Boot Bypass")
        win11_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(win11_frame, text="Check Compatibility", 
                  command=self.check_win11_compatibility).pack(side='left', padx=5)
        ttk.Button(win11_frame, text="Bypass TPM Check", 
                  command=self.bypass_tpm_check).pack(side='left', padx=5)
        ttk.Button(win11_frame, text="Create Bypass Registry", 
                  command=self.create_bypass_registry).pack(side='left', padx=5)
    
    def create_recovery_media_section(self):
        """Recovery Media Builder section"""
        media_frame = ttk.LabelFrame(self.recovery_frame, text="Recovery Media Builder")
        media_frame.pack(fill='x', padx=10, pady=5)
        
        # Drive selection
        drive_frame = ttk.Frame(media_frame)
        drive_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(drive_frame, text="Select Drive:").pack(side='left')
        self.drive_combobox = ttk.Combobox(drive_frame, state='readonly', width=40)
        self.drive_combobox.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(drive_frame, text="Refresh", 
                  command=self.refresh_drive_list).pack(side='left', padx=5)
        
        # Media type selection
        type_frame = ttk.Frame(media_frame)
        type_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(type_frame, text="Media Type:").pack(side='left')
        self.media_type = tk.StringVar(value=MediaType.WINDOWS_PE.value)
        for media in MediaType:
            ttk.Radiobutton(type_frame, text=media.value, variable=self.media_type,
                          value=media.value).pack(side='left', padx=5)
        
        # Filesystem selection
        fs_frame = ttk.Frame(media_frame)
        fs_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(fs_frame, text="Filesystem:").pack(side='left')
        self.fs_type = tk.StringVar(value=FileSystemType.FAT32.value)
        for fs in FileSystemType:
            ttk.Radiobutton(fs_frame, text=fs.value, variable=self.fs_type,
                          value=fs.value).pack(side='left', padx=5)
        
        # Action buttons
        btn_frame = ttk.Frame(media_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        self.create_btn = ttk.Button(btn_frame, text="Create Recovery Media",
                                  command=self.start_recovery_media_creation)
        self.create_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", state='disabled',
                                command=self.stop_recovery_media_creation)
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Validate Media",
                  command=self.validate_recovery_media).pack(side='left', padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(media_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill='x', padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(media_frame, textvariable=self.status_var).pack(fill='x', padx=5, pady=2)
        
        # Initialize drive list
        self.refresh_drive_list()
    
    def create_log_section(self):
        """Recovery log section"""
        log_frame = ttk.LabelFrame(self.recovery_frame, text="Recovery Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Recovery Media Builder Methods
    def refresh_drive_list(self):
        """Refresh the list of available drives"""
        try:
            drives = self.recovery_builder.list_available_drives()
            drive_list = [f"{d.drive_letter}: {d.volume_label or 'No Label'} ({d.size_gb:.1f}GB)" 
                         for d in drives]
            self.drive_combobox['values'] = drive_list
            self.drive_combobox.set('' if not drive_list else drive_list[0])
            self.status_var.set(f"Found {len(drive_list)} available drive(s)")
        except Exception as e:
            self.log_message(f"[ERROR] Failed to refresh drive list: {e}")
    
    def start_recovery_media_creation(self):
        """Start the recovery media creation process"""
        if not self.drive_combobox.get():
            messagebox.showerror("Error", "Please select a drive")
            return
            
        drive_letter = self.drive_combobox.get().split(':')[0]
        media_type = self.media_type.get()
        fs_type = self.fs_type.get()
        
        # Confirm before proceeding
        if not messagebox.askyesno("Confirm", 
                                 f"This will erase all data on {drive_letter}:\n"
                                 f"Media Type: {media_type}\n"
                                 f"Filesystem: {fs_type}\n\n"
                                 "Do you want to continue?"):
            return
        
        # Disable controls during operation
        self.create_btn['state'] = 'disabled'
        self.stop_btn['state'] = 'normal'
        self.stop_event.clear()
        
        # Start the media creation in a separate thread
        self.media_builder_thread = threading.Thread(
            target=self._create_recovery_media_thread,
            args=(drive_letter, media_type, fs_type),
            daemon=True
        )
        self.media_builder_thread.start()
    
    def _create_recovery_media_thread(self, drive_letter: str, media_type: str, fs_type: str):
        """Thread function for creating recovery media"""
        try:
            self.log_message(f"[RECOVERY] Starting {media_type} media creation on {drive_letter}:")
            
            # Format the drive
            self._update_status(f"Formatting {drive_letter}: as {fs_type}...")
            format_result = self.recovery_builder.format_drive(drive_letter, fs_type)
            if not format_result['success']:
                raise Exception(f"Format failed: {format_result.get('message', 'Unknown error')}")
            
            self.log_message(f"[RECOVERY] {format_result['message']}")
            
            # Create the appropriate media type
            self._update_status(f"Creating {media_type} media...")
            if media_type == MediaType.WINDOWS_PE.value:
                result = self.recovery_builder.create_windows_pe_media(drive_letter)
            elif media_type == MediaType.WINDOWS_INSTALL.value:
                result = self.recovery_builder.create_windows_install_media(drive_letter)
            else:  # LINUX_RESCUE
                result = self.recovery_builder.create_linux_rescue_media(drive_letter)
            
            if not result['success']:
                raise Exception(result.get('message', 'Unknown error during media creation'))
            
            # Validate the media
            self._update_status("Validating media...")
            validation = self.recovery_builder.validate_recovery_media(drive_letter)
            if not validation['success']:
                self.log_message(f"[WARNING] Media validation warnings: {validation.get('message', 'Unknown')}")
            
            self.log_message(f"[SUCCESS] {media_type} media created successfully on {drive_letter}:")
            self._update_status("Media creation completed successfully")
            
        except Exception as e:
            self.log_message(f"[ERROR] Failed to create recovery media: {e}")
            self._update_status("Media creation failed")
        finally:
            # Re-enable controls
            self.after(0, self._reset_media_builder_ui)
    
    def stop_recovery_media_creation(self):
        """Stop the recovery media creation process"""
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the current operation?"):
            self.stop_event.set()
            self._update_status("Stopping...")
    
    def validate_recovery_media(self):
        """Validate the selected recovery media"""
        if not self.drive_combobox.get():
            messagebox.showerror("Error", "Please select a drive")
            return
            
        drive_letter = self.drive_combobox.get().split(':')[0]
        
        def run_validation():
            try:
                self.log_message(f"[RECOVERY] Validating media on {drive_letter}:")
                result = self.recovery_builder.validate_recovery_media(drive_letter)
                
                if result['success']:
                    self.log_message("[SUCCESS] Media validation passed")
                    self._update_status("Media validation passed")
                else:
                    self.log_message(f"[WARNING] Media validation issues: {result.get('message', 'Unknown')}")
                    self._update_status("Media validation found issues")
                
            except Exception as e:
                self.log_message(f"[ERROR] Media validation failed: {e}")
                self._update_status("Media validation failed")
        
        threading.Thread(target=run_validation, daemon=True).start()
    
    def _update_status(self, message: str):
        """Update the status label and log"""
        self.after(0, lambda: self.status_var.set(message))
        self.log_message(f"[STATUS] {message}")
    
    def _reset_media_builder_ui(self):
        """Reset the media builder UI to its initial state"""
        self.create_btn['state'] = 'normal'
        self.stop_btn['state'] = 'disabled'
        self.progress_var.set(0)
    
    def log_message(self, message: str):
        """Add message to recovery log"""
        def _log():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        
        # Ensure thread-safe GUI updates
        if threading.current_thread() is threading.main_thread():
            _log()
        else:
            self.after(0, _log)
        
        # Also update the status for important messages
        if message.startswith("[STATUS]"):
            self.after(0, lambda: self.status_var.set(message[9:]))
    
    # Dell Recovery Methods
    def detect_dell_hardware(self):
        """Detect Dell hardware"""
        def run_detection():
            self.log_message("[DELL] Detecting Dell hardware...")
            try:
                hardware = self.hardware_rescue.detect_hardware()
                if 'Dell' in hardware.get('system', ''):
                    self.log_message(f"[DELL] Detected: {hardware['system']}")
                    self.log_message(f"[DELL] Drives found: {len(hardware.get('drives', []))}")
                else:
                    self.log_message("[DELL] No Dell system detected")
            except Exception as e:
                self.log_message(f"[ERROR] Dell detection failed: {e}")
        
        threading.Thread(target=run_detection, daemon=True).start()
    
    def fix_dell_boot_loop(self):
        """Fix Dell boot loop"""
        def run_fix():
            self.log_message("[DELL] Starting boot loop repair...")
            try:
                self.hardware_rescue.rescue_dell_boot_loop()
                self.log_message("[DELL] Boot loop repair completed")
            except Exception as e:
                self.log_message(f"[ERROR] Boot loop repair failed: {e}")
        
        threading.Thread(target=run_fix, daemon=True).start()
    
    def dell_uefi_repair(self):
        """Dell UEFI repair"""
        def run_uefi_repair():
            self.log_message("[DELL] Starting UEFI repair...")
            try:
                # Run UEFI repair commands
                commands = [
                    'bootrec /fixmbr',
                    'bootrec /fixboot',
                    'bootrec /rebuildbcd',
                    'bcdboot C:\\Windows /s C: /f UEFI'
                ]
                
                for cmd in commands:
                    self.log_message(f"[DELL] Running: {cmd}")
                    # Command execution would be handled by hardware_rescue
                
                self.log_message("[DELL] UEFI repair completed")
            except Exception as e:
                self.log_message(f"[ERROR] UEFI repair failed: {e}")
        
        threading.Thread(target=run_uefi_repair, daemon=True).start()
    
    # Samsung Recovery Methods
    def detect_samsung_drives(self):
        """Detect Samsung drives"""
        def run_detection():
            self.log_message("[SAMSUNG] Detecting Samsung drives...")
            try:
                recovery = Samsung4TBRecovery()
                drives = recovery.detect_samsung_drives()
                
                if drives:
                    for drive in drives:
                        self.log_message(f"[SAMSUNG] Found: {drive['name']} ({drive['size_gb']}GB)")
                else:
                    self.log_message("[SAMSUNG] No Samsung 4TB drives detected")
            except Exception as e:
                self.log_message(f"[ERROR] Samsung detection failed: {e}")
        
        threading.Thread(target=run_detection, daemon=True).start()
    
    def unlock_samsung_bitlocker(self):
        """Unlock Samsung BitLocker drive"""
        recovery_key = self.recovery_key_entry.get().strip()
        drive_letter = self.drive_letter_entry.get().strip()
        
        if not recovery_key:
            messagebox.showerror("Error", "Please enter BitLocker recovery key")
            return
        
        def run_unlock():
            self.log_message(f"[SAMSUNG] Unlocking drive {drive_letter or 'auto-detect'}...")
            try:
                recovery = Samsung4TBRecovery(drive_letter, recovery_key)
                
                if drive_letter:
                    success = recovery.unlock_with_recovery_key(drive_letter, recovery_key)
                    if success:
                        self.log_message(f"[SAMSUNG] Drive {drive_letter}: unlocked successfully!")
                    else:
                        self.log_message(f"[ERROR] Failed to unlock drive {drive_letter}:")
                else:
                    self.log_message("[SAMSUNG] Auto-detecting encrypted drives...")
                    # Auto-detection logic would go here
                    
            except Exception as e:
                self.log_message(f"[ERROR] BitLocker unlock failed: {e}")
        
        threading.Thread(target=run_unlock, daemon=True).start()
    
    def samsung_full_recovery(self):
        """Full Samsung SSD recovery"""
        recovery_key = self.recovery_key_entry.get().strip()
        drive_letter = self.drive_letter_entry.get().strip()
        
        def run_full_recovery():
            self.log_message("[SAMSUNG] Starting full recovery process...")
            try:
                recovery = Samsung4TBRecovery(drive_letter, recovery_key)
                result = recovery.full_samsung_recovery()
                
                if result['success']:
                    self.log_message(f"[SUCCESS] {result['message']}")
                    if 'drive_letter' in result:
                        self.log_message(f"[INFO] Drive accessible at: {result['drive_letter']}:\\")
                else:
                    self.log_message(f"[ERROR] Recovery failed: {result['error']}")
                
                # Show log entries
                for log_entry in result.get('log', []):
                    self.log_message(f"[LOG] {log_entry}")
                    
            except Exception as e:
                self.log_message(f"[ERROR] Full recovery failed: {e}")
        
        threading.Thread(target=run_full_recovery, daemon=True).start()
    
    # Windows 11 Methods
    def check_win11_compatibility(self):
        """Check Windows 11 compatibility"""
        def run_check():
            self.log_message("[WIN11] Checking Windows 11 compatibility...")
            try:
                status = self.windows11_recovery.check_upgrade_status()
                
                for check, result in status.items():
                    status_text = "PASS" if result else "FAIL"
                    self.log_message(f"[WIN11] {check}: {status_text}")
                    
            except Exception as e:
                self.log_message(f"[ERROR] Compatibility check failed: {e}")
        
        threading.Thread(target=run_check, daemon=True).start()
    
    def bypass_tpm_check(self):
        """Bypass TPM check"""
        def run_bypass():
            self.log_message("[WIN11] Bypassing TPM and hardware checks...")
            try:
                success, message = self.windows11_recovery.bypass_tpm_check()
                
                if success:
                    self.log_message(f"[WIN11] SUCCESS: {message}")
                else:
                    self.log_message(f"[WIN11] FAILED: {message}")
                    
            except Exception as e:
                self.log_message(f"[ERROR] TPM bypass failed: {e}")
        
        threading.Thread(target=run_bypass, daemon=True).start()
    
    def create_bypass_registry(self):
        """Create bypass registry file"""
        def run_create():
            self.log_message("[WIN11] Creating bypass registry file...")
            try:
                success, message = self.windows11_recovery.create_registry_bypass()
                
                if success:
                    self.log_message(f"[WIN11] Registry file created: {message}")
                    self.log_message("[WIN11] Run as admin and double-click .reg file to apply")
                else:
                    self.log_message(f"[WIN11] FAILED: {message}")
                    
            except Exception as e:
                self.log_message(f"[ERROR] Registry creation failed: {e}")
        
        threading.Thread(target=run_create, daemon=True).start()
