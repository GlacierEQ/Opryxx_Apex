"""
OPRYXX OS Reinstallation Workflow
This script provides an interactive interface for the OS reinstallation process.
"""
import sys
import os
import time
from utils.os_reinstall import OSReinstallQODO

def print_status(message):
    """Print status message with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[STATUS][{timestamp}] {message}")

def print_log(message):
    """Print log message with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG][{timestamp}] {message}")

def prompt_continue():
    """Prompt user to continue with default action"""
    try:
        input("Press Enter to continue or Ctrl+C to cancel...")
        return True
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        return False

def run_os_reinstall():
    print("\n" + "=" * 60)
    print("OPRYXX OS REINSTALLATION WORKFLOW")
    print("=" * 60)
    print("This will guide you through the Windows 11 reinstallation process.")
    print("Please ensure you have backed up all important data before proceeding.")
    print("=" * 60 + "\n")
    
    # Initialize the reinstaller early to check for any immediate issues
    try:
        reinstaller = OSReinstallQODO(
            update_status_callback=print_status,
            update_log_callback=print_log
        )
        print("[INIT] OS Reinstallation components initialized successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize OS reinstallation components: {str(e)}")
        return
    
    # Step 1: Backup data
    print("\n[STEP 1/7] BACKUP CRITICAL DATA")
    print("-" * 40)
    print("Before proceeding, you MUST back up all important data.")
    print("This includes documents, photos, downloads, and any other personal files.")
    print("\nRecommended backup locations:")
    print("- External hard drive")
    print("- Cloud storage (OneDrive, Google Drive, etc.)")
    print("- Network storage\n")
    
    if not prompt_continue():
        return
        
    reinstaller.backup_data()
    
    print("\n[ACTION REQUIRED] Please verify your backup is complete.")
    print("Check that all important files are safely copied to your backup location.")
    if not prompt_continue():
        return
    
    # Step 2: Gather installation media
    print("\n[STEP 2/7] GATHER INSTALLATION MEDIA")
    print("-" * 40)
    print("You will need a Windows 11 installation media (USB or ISO).")
    print("This can be created using the Media Creation Tool from Microsoft.")
    
    if not prompt_continue():
        return
        
    reinstaller.gather_media()
    
    print("\n[ACTION REQUIRED] Please ensure you have the Windows 11 installation media ready.")
    print("You can download it from: https://www.microsoft.com/software-download/windows11")
    if not prompt_continue():
        return
    
    # Step 3: Prepare USB
    print("\n[STEP 3/7] PREPARE BOOTABLE USB")
    print("-" * 40)
    print("You'll need a USB drive (8GB or larger) to create bootable media.")
    print("The USB will be erased during this process.")
    
    if not prompt_continue():
        return
        
    reinstaller.prepare_usb()
    
    print("\n[ACTION REQUIRED] Please create a bootable USB using one of these tools:")
    print("- Rufus (recommended): https://rufus.ie/")
    print("- Windows Media Creation Tool")
    print("- Ventoy: https://www.ventoy.net/\n")
    print("Make sure to select the Windows 11 ISO when prompted.")
    if not prompt_continue():
        return
    
    # Step 4: Export keys and drivers
    print("\n[STEP 4/7] EXPORT KEYS AND DRIVERS")
    print("-" * 40)
    print("It's important to export your Windows product key and device drivers")
    print("before reinstalling the operating system.\n")
    
    if not prompt_continue():
        return
        
    reinstaller.export_keys_and_drivers()
    
    print("\n[ACTION REQUIRED] Please ensure you have:")
    print("1. Your Windows product key (if not digital license)")
    print("2. Downloaded the latest drivers for your hardware")
    print("3. Backed up any custom driver configurations\n")
    if not prompt_continue():
        return
    
    # Step 5: Q-SECURE Checkpoint
    print("\n[STEP 5/7] FINAL VERIFICATION")
    print("-" * 40 + "\n")
    print("IMPORTANT: This is your last chance to verify everything is backed up!")
    print("\nPlease confirm you have:")
    print("✅ Backed up all personal files")
    print("✅ Saved important passwords and licenses")
    print("✅ Created bootable Windows 11 USB")
    print("✅ Exported product keys and drivers")
    print("✅ Have your Windows login credentials ready")
    
    reinstaller.qsecure_checkpoint()
    
    print("\nWARNING: The next steps will modify your system.")
    print("Make sure your computer is connected to power and won't be interrupted.\n")
    if not prompt_continue():
        return
    
    # Step 6: Installation options
    print("\n[STEP 6/7] SELECT INSTALLATION TYPE")
    print("-" * 40)
    print("Choose the type of installation you want to perform:\n")
    print("1. In-place repair (recommended first try)")
    print("   - Keeps all your files, apps, and settings")
    print("   - Repairs Windows system files")
    print("   - Fastest option with minimal changes\n")
    
    print("2. Advanced repair (keep files only)")
    print("   - Keeps your personal files only")
    print("   - Removes all apps and settings")
    print("   - Good for fixing system issues while keeping files\n")
    
    print("3. Clean install (most thorough)")
    print("   - Erases everything on the system drive")
    print("   - Fresh Windows installation")
    print("   - Recommended for maximum performance and stability\n")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3, or 'q' to quit): ").strip().lower()
            if choice == 'q':
                print("\nOperation cancelled by user.")
                return
                
            if choice not in ['1', '2', '3']:
                print("Invalid choice. Please enter 1, 2, or 3.")
                continue
                
            print("\n[CONFIRMATION]")
            if choice == "3":
                print("WARNING: This will ERASE ALL DATA on your system drive!")
                confirm = input("Type 'ERASE' to confirm: ").strip()
                if confirm != 'ERASE':
                    print("Confirmation failed. Please try again.")
                    continue
            else:
                if not prompt_continue():
                    return
            
            if choice == "1":
                reinstaller.attempt_inplace_repair()
            elif choice == "2":
                reinstaller.advanced_repair()
            else:  # choice == "3"
                reinstaller.clean_install()
            break
            
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            return
    
    # Step 7: Post-installation
    print("\n[STEP 7/7] POST-INSTALLATION")
    print("-" * 40)
    print("\nThe main installation is complete! Here's what to do next:\n")
    
    reinstaller.post_install()
    reinstaller.validate_and_finalize()
    
    # Generate report
    report_file = reinstaller.export_report()
    
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    print(f"\n✅ Report saved to: {report_file}")
    
    print("\nNEXT STEPS:")
    print("1. Restart your computer")
    print("2. Complete Windows setup")
    print("3. Install updates")
    print("4. Restore your files from backup")
    print("5. Reinstall your applications")
    print("\nThank you for using OPRYXX OS Reinstallation Workflow!")

if __name__ == "__main__":
    try:
        run_os_reinstall()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
