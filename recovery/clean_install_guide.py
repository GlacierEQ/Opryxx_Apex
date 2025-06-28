"""
Clean Windows 11 Install Guide
Complete OS wipe and reinstall process
"""

import subprocess
import os

class CleanInstallGuide:
    def __init__(self):
        self.steps = []
    
    def show_clean_install_process(self):
        """Show the complete clean install process"""
        
        print("CLEAN WINDOWS 11 INSTALL PROCESS")
        print("=" * 50)
        
        print("\n🔥 PHASE 1: PREPARATION")
        print("1. Backup important data to external drive")
        print("2. Download Windows 11 ISO from Microsoft")
        print("3. Create bootable USB with Rufus or Media Creation Tool")
        print("4. Note your Windows 11 product key")
        
        print("\n🚀 PHASE 2: BOOT FROM USB")
        print("1. Insert bootable USB")
        print("2. Restart PC and press F12/F2/DEL (depends on motherboard)")
        print("3. Select USB drive from boot menu")
        print("4. Boot into Windows 11 installer")
        
        print("\n💥 PHASE 3: COMPLETE WIPE")
        print("1. Select 'Custom: Install Windows only (advanced)'")
        print("2. DELETE ALL PARTITIONS (this wipes everything)")
        print("3. Select unallocated space")
        print("4. Click 'New' to create fresh partition")
        print("5. Click 'Next' to start clean install")
        
        print("\n⚡ PHASE 4: FRESH INSTALL")
        print("1. Windows installs automatically (15-30 minutes)")
        print("2. PC restarts several times (normal)")
        print("3. Complete initial Windows setup")
        print("4. Install drivers and updates")
        
        print("\n🎯 PHASE 5: RESTORE NEXUS AI")
        print("1. Download NEXUS AI installer")
        print("2. Run NEXUS_AI_Installer.exe")
        print("3. Your PC is now CLEAN + OPTIMIZED!")
    
    def create_emergency_boot_usb(self):
        """Instructions for creating emergency boot USB"""
        
        print("\n🛠️ CREATING EMERGENCY BOOT USB")
        print("=" * 40)
        
        print("OPTION 1: Windows Media Creation Tool")
        print("1. Download from: https://www.microsoft.com/software-download/windows11")
        print("2. Run MediaCreationTool11.exe")
        print("3. Select 'Create installation media'")
        print("4. Choose USB flash drive (8GB+)")
        print("5. Tool creates bootable USB automatically")
        
        print("\nOPTION 2: Manual ISO + Rufus")
        print("1. Download Windows 11 ISO")
        print("2. Download Rufus from: https://rufus.ie/")
        print("3. Insert USB drive (8GB+)")
        print("4. Run Rufus, select ISO and USB")
        print("5. Click 'START' to create bootable USB")
    
    def show_bios_boot_keys(self):
        """Show common BIOS boot keys"""
        
        print("\n🔑 BIOS BOOT KEYS BY MANUFACTURER")
        print("=" * 40)
        
        boot_keys = {
            "ASUS": "F8 or DEL",
            "MSI": "F11 or DEL", 
            "Gigabyte": "F12 or DEL",
            "ASRock": "F11 or F2",
            "Dell": "F12",
            "HP": "F9 or ESC",
            "Lenovo": "F12 or F1",
            "Acer": "F12 or F2"
        }
        
        for brand, key in boot_keys.items():
            print(f"{brand:10} - Press {key} during startup")
        
        print("\n💡 TIP: Press the key repeatedly while PC starts up!")

def main():
    """Show complete clean install guide"""
    guide = CleanInstallGuide()
    
    guide.show_clean_install_process()
    guide.create_emergency_boot_usb()
    guide.show_bios_boot_keys()
    
    print("\n🚨 WARNING: This COMPLETELY WIPES your PC!")
    print("🔒 Make sure to backup important data first!")
    print("🎉 Result: Brand new Windows 11 + NEXUS AI!")

if __name__ == "__main__":
    main()