# OPRYXX Recovery System - Quick Start Guide

## Prerequisites
- Windows 10/11
- Python 3.8+
- Administrator privileges
- 8GB+ USB drive (for bootable media)

## Quick Start

### 1. Install Dependencies
```powershell
# Install required Python packages
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### 2. Create Recovery Media

#### Using PowerShell (Admin):
```powershell
# Navigate to recovery directory
cd recovery

# Create recovery media (replace E: with your USB drive letter)
.\create_recovery_media.ps1 -UsbDrive "E:" -DownloadHirens
```

#### Command-line Options:
```
-UsbDrive          Drive letter (e.g., "E:")
-DownloadHirens    Automatically download Hiren's Boot
-Force             Skip confirmation prompts
-SkipIsoCopy       Skip copying Hiren's Boot ISO
-SkipBootMenu      Skip updating boot menu
```

### 3. Boot from Recovery Media
1. Insert USB drive
2. Restart computer
3. Press boot menu key (F12, F2, or DEL)
4. Select USB drive
5. Follow on-screen instructions

## Common Tasks

### Backup Drivers
```powershell
# Create a driver backup
.\recovery\driver_manager.py backup "pre_update_backup"

# List available backups
.\recovery\driver_manager.py list
```

### Restore System
1. Boot from recovery media
2. Select "Restore System from Backup"
3. Choose a restore point
4. Follow prompts

### Reinstall Windows
1. Boot from recovery media
2. Select "Automated Windows 11 Reinstall"
3. Choose installation type:
   - Keep files and apps
   - Keep files only
   - Clean install
4. Follow on-screen instructions

## Troubleshooting

### Common Issues
- **Can't boot from USB**: 
  - Enable USB boot in BIOS/UEFI
  - Disable Secure Boot
  - Try different USB port (preferably USB 2.0)

- **Driver issues**:
  ```powershell
  # Scan for hardware changes
  pnputil /scan-devices
  
  # Check device manager
  devmgmt.msc
  ```

- **Recovery environment not starting**:
  ```powershell
  # Rebuild BCD
  bootrec /rebuildbcd
  
  # Check disk
  chkdsk C: /f /r
  ```

## Getting Help

### View Logs
```
%TEMP%\opryxx_recovery.log
```

### Command Reference
```
driver_manager.py backup [name]    Create driver backup
driver_manager.py list            List backups
driver_manager.py restore [name]  Restore drivers
```

## Next Steps
- [Full Documentation](CI_CD_SETUP.md)
- [Advanced Configuration](ADVANCED.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---
*For support, open an issue in the repository or contact the development team.*
