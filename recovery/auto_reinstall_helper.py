"""
Auto Reinstall Helper
Prepares system for clean Windows 11 reinstall
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# Set console to use UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class AutoReinstallHelper:
    def __init__(self):
        self.backup_info = {}
    
    def prepare_for_reinstall(self):
        """Prepare system for clean reinstall"""
        
        print("PREPARING FOR CLEAN WINDOWS 11 REINSTALL")
        print("=" * 50)
        
        # Gather system info
        self._gather_system_info()
        
        # Create reinstall checklist
        self._create_reinstall_checklist()
        
        # Show next steps
        self._show_next_steps()
    
    def _gather_system_info(self):
        """Gather important system information"""
        
        print("[INFO] Gathering system information...")
        
        try:
            # Get Windows product key
            result = subprocess.run([
                'wmic', 'path', 'softwarelicensingservice', 
                'get', 'OA3xOriginalProductKey'
            ], capture_output=True, text=True)
            
            product_key = "Not found"
            for line in result.stdout.split('\n'):
                if line.strip() and 'OA3x' not in line:
                    product_key = line.strip()
                    break
            
            self.backup_info['product_key'] = product_key
            
            # Get system specs
            self.backup_info['computer_name'] = os.environ.get('COMPUTERNAME', 'Unknown')
            self.backup_info['username'] = os.environ.get('USERNAME', 'Unknown')
            
            # Get installed programs list
            result = subprocess.run([
                'wmic', 'product', 'get', 'name,version'
            ], capture_output=True, text=True)
            
            self.backup_info['installed_programs'] = result.stdout
            
            print("✅ System information gathered")
            
        except Exception as e:
            print(f"⚠️ Error gathering system info: {e}")
    
    def _create_reinstall_checklist(self):
        """Create checklist for reinstall process"""
        
        checklist = f"""
WINDOWS 11 CLEAN REINSTALL CHECKLIST
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔑 SYSTEM INFORMATION:
Computer Name: {self.backup_info.get('computer_name', 'Unknown')}
Username: {self.backup_info.get('username', 'Unknown')}
Windows Product Key: {self.backup_info.get('product_key', 'Not found')}

PRE-INSTALL CHECKLIST:
[ ] Backup all important files to external drive
[ ] Export browser bookmarks and passwords
[ ] Note down WiFi passwords
[ ] Save software license keys
[ ] Create Windows 11 bootable USB
[ ] Back up personal files
[ ] Save product keys
[ ] Download Windows 11 ISO
[ ] Create bootable USB

PREP PRE-INSTALL:
[ ] Disable Secure Boot
[ ] Enable TPM 2.0
[ ] Backup drivers
[ ] Save network settings

INSTALL INSTALLATION:
[ ] Boot from USB
[ ] Delete all partitions
[ ] Install Windows 11
[ ] Install NEXUS AI system
[ ] Restore backed up files

POST POST-INSTALL:
[ ] Run Windows Updates
[ ] Install NEXUS AI Ultimate
[ ] Activate 24/7 optimization
[ ] Restore personal files
[ ] Reinstall essential programs

COMPLETE RESULT: Brand new PC with NEXUS AI!
"""
        
        with open('REINSTALL_CHECKLIST.txt', 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print("Reinstall checklist created: REINSTALL_CHECKLIST.txt")
    
    def _show_next_steps(self):
        """Show next steps for user"""
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review REINSTALL_CHECKLIST.txt")
        print("2. Backup ALL important data")
        print("3. Create Windows 11 bootable USB")
        print("4. Run recovery/NUCLEAR_RESET.bat for complete guide")
        print("5. Follow step-by-step process")
        
        print(f"\n[KEY] Your Windows Product Key: {self.backup_info.get('product_key', 'Not found')}")
        print("[SAVE] Save this key - you'll need it!")

def main():
    """Run auto reinstall helper"""
    helper = AutoReinstallHelper()
    helper.prepare_for_reinstall()

if __name__ == "__main__":
    main()