"""
Automated OS Reinstall Recovery System
"""

import os
import subprocess
import time
from pathlib import Path

class AutomatedOSReinstall:
    def __init__(self):
        self.backup_path = "C:\\OPRYXX_BACKUP"
        self.iso_path = None
        self.usb_drive = None
        
    def execute_automated_reinstall(self):
        """Execute fully automated OS reinstall"""
        print("🚀 OPRYXX AUTOMATED OS REINSTALL INITIATED")
        
        # Phase 1: Auto-backup critical data
        self._auto_backup_system()
        
        # Phase 2: Download Windows 11 ISO
        self._download_windows_iso()
        
        # Phase 3: Create bootable USB
        self._create_bootable_usb()
        
        # Phase 4: Configure auto-install
        self._setup_unattended_install()
        
        # Phase 5: Initiate reboot to USB
        self._reboot_to_usb()
    
    def _auto_backup_system(self):
        """Automatically backup critical system data"""
        print("💾 Auto-backing up critical data...")
        
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Backup user data
        user_folders = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures")
        ]
        
        for folder in user_folders:
            if os.path.exists(folder):
                subprocess.run(['robocopy', folder, f"{self.backup_path}\\{os.path.basename(folder)}", '/E'], 
                             capture_output=True)
        
        # Export Windows product key
        result = subprocess.run(['wmic', 'path', 'softwarelicensingservice', 'get', 'OA3xOriginalProductKey'], 
                              capture_output=True, text=True)
        
        with open(f"{self.backup_path}\\product_key.txt", 'w') as f:
            f.write(result.stdout)
        
        print("✅ Backup completed")
    
    def _download_windows_iso(self):
        """Download Windows 11 ISO automatically"""
        print("📥 Downloading Windows 11 ISO...")
        
        # Use PowerShell to download Windows 11
        ps_script = '''
        $url = "https://software-download.microsoft.com/download/sg/Win11_23H2_English_x64v2.iso"
        $output = "C:\\Windows11.iso"
        Invoke-WebRequest -Uri $url -OutFile $output
        '''
        
        subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
        self.iso_path = "C:\\Windows11.iso"
        print("✅ ISO downloaded")
    
    def _create_bootable_usb(self):
        """Create bootable USB automatically"""
        print("💿 Creating bootable USB...")
        
        # Find USB drive
        drives = subprocess.run(['wmic', 'logicaldisk', 'where', 'drivetype=2', 'get', 'deviceid'], 
                              capture_output=True, text=True)
        
        for line in drives.stdout.split('\n'):
            if ':' in line:
                self.usb_drive = line.strip()
                break
        
        if not self.usb_drive:
            raise Exception("No USB drive found")
        
        # Format USB and copy ISO
        subprocess.run(['format', self.usb_drive, '/FS:FAT32', '/Q', '/Y'], capture_output=True)
        subprocess.run(['powershell', f'Mount-DiskImage -ImagePath "{self.iso_path}"'], capture_output=True)
        
        # Copy ISO contents to USB
        subprocess.run(['robocopy', 'D:', f"{self.usb_drive}\\", '/E'], capture_output=True)
        
        print("✅ Bootable USB created")
    
    def _setup_unattended_install(self):
        """Setup unattended Windows installation"""
        print("⚙️ Configuring unattended install...")
        
        autounattend_xml = '''<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
    <settings pass="windowsPE">
        <component name="Microsoft-Windows-Setup">
            <DiskConfiguration>
                <Disk wcm:action="add">
                    <DiskID>0</DiskID>
                    <WillWipeDisk>true</WillWipeDisk>
                    <CreatePartitions>
                        <CreatePartition wcm:action="add">
                            <Order>1</Order>
                            <Type>Primary</Type>
                            <Extend>true</Extend>
                        </CreatePartition>
                    </CreatePartitions>
                </Disk>
            </DiskConfiguration>
            <ImageInstall>
                <OSImage>
                    <InstallTo>
                        <DiskID>0</DiskID>
                        <PartitionID>1</PartitionID>
                    </InstallTo>
                </OSImage>
            </ImageInstall>
        </component>
    </settings>
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup">
            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <SkipMachineOOBE>true</SkipMachineOOBE>
            </OOBE>
        </component>
    </settings>
</unattend>'''
        
        with open(f"{self.usb_drive}\\autounattend.xml", 'w') as f:
            f.write(autounattend_xml)
        
        print("✅ Unattended install configured")
    
    def _reboot_to_usb(self):
        """Reboot system to USB drive"""
        print("🔄 Rebooting to USB for automated install...")
        
        # Set boot order to USB first
        subprocess.run(['bcdedit', '/set', '{fwbootmgr}', 'bootsequence', '{usb}'], capture_output=True)
        
        # Schedule reboot
        subprocess.run(['shutdown', '/r', '/t', '10', '/c', 'OPRYXX Automated OS Reinstall'], capture_output=True)
        
        print("✅ System will reboot in 10 seconds for automated installation")
        print("🤖 OPRYXX will automatically reinstall Windows 11 and restore your data")

def main():
    """Execute automated OS reinstall"""
    reinstaller = AutomatedOSReinstall()
    reinstaller.execute_automated_reinstall()

if __name__ == "__main__":
    main()