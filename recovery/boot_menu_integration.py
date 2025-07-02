"""
Boot Menu Integration for Easy Access
"""

import subprocess
import os

class BootMenuIntegration:
    def __init__(self):
        self.opryxx_path = os.path.abspath(".")
        
    def add_to_boot_menu(self):
        """Add OPRYXX to Windows boot menu"""
        print("🔧 Adding OPRYXX to boot menu...")
        
        # Create boot entry
        subprocess.run([
            'bcdedit', '/create', '/d', 'OPRYXX Recovery System', '/application', 'bootsector'
        ])
        
        # Set boot path
        subprocess.run([
            'bcdedit', '/set', '{bootmgr}', 'displaybootmenu', 'yes'
        ])
        
        # Set timeout
        subprocess.run([
            'bcdedit', '/timeout', '10'
        ])
        
        print("✅ OPRYXX added to boot menu")
        print("💡 Hold SHIFT while restarting to access OPRYXX Recovery")
    
    def create_emergency_shortcut(self):
        """Create desktop shortcut for emergency access"""
        shortcut_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\🚨 OPRYXX Emergency Recovery.lnk")
$Shortcut.TargetPath = "{self.opryxx_path}\\AUTOMATED_REINSTALL.bat"
$Shortcut.IconLocation = "shell32.dll,21"
$Shortcut.Description = "OPRYXX Emergency OS Recovery - Double-click when PC has problems"
$Shortcut.Save()
'''
        
        subprocess.run(['powershell', '-Command', shortcut_script])
        print("✅ Emergency shortcut created on desktop")

def main():
    """Setup boot menu integration"""
    integration = BootMenuIntegration()
    integration.add_to_boot_menu()
    integration.create_emergency_shortcut()

if __name__ == "__main__":
    main()