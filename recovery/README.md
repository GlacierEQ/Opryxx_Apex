# OPRYXX Recovery Environment

This directory contains tools and scripts for creating a robust recovery environment for OPRYXX_LOGS, featuring Hiren's Boot integration, automated driver management, and system recovery options.

## Features

- **Hiren's Boot Integration** - Boot into a powerful recovery environment
- **Driver Management** - Backup and restore system drivers
- **System Restore** - Create and restore system restore points
- **Windows 11 Reinstallation** - Automated OS reinstallation with driver preservation
- **Recovery Tools** - Comprehensive set of diagnostic and repair tools

## Prerequisites

- Windows 10/11 with administrator privileges
- At least 8GB USB drive (for bootable media)
- Hiren's Boot CD ISO (automatically downloaded if not provided)
- Internet connection (for downloading components and drivers)

## Quick Start

### 1. Create Recovery Media

```powershell
# Run with administrator privileges
.\create_recovery_media.ps1 -UsbDrive "E:" -DownloadHirens
```

### 2. Boot from Recovery Media

1. Restart your computer
2. Enter boot menu (typically F12, F2, or DEL during startup)
3. Select your USB drive from the boot menu
4. Choose "OPRYXX Recovery Environment"

## Usage

### Driver Management

#### Backup Drivers
```powershell
# Backup all drivers with auto-naming
.\driver_manager.ps1 -Action Backup

# Backup with custom name
.\driver_manager.ps1 -Action Backup -BackupName "PreReinstall_$(Get-Date -Format 'yyyyMMdd')"
```

#### Restore Drivers
```powershell
# List available backups
.\driver_manager.ps1 -Action List

# Restore specific backup
.\driver_manager.ps1 -Action Restore -BackupName "PreReinstall_20230629"
```

### System Recovery

#### Create System Restore Point
```powershell
.\system_recovery.ps1 -Action Create -Description "Before software update"
```

#### Restore System
```powershell
# List available restore points
.\system_recovery.ps1 -Action List

# Restore to specific point
.\system_recovery.ps1 -Action Restore -SequenceNumber 5
```

### Windows Reinstallation

#### Automated Reinstall (Keeps files and apps)
```powershell
.\auto_reinstall.ps1 -InstallType Upgrade
```

#### Clean Install (Removes everything)
```powershell
.\auto_reinstall.ps1 -InstallType Clean -Confirm:$false
```

## Boot Menu Options

When booting into the recovery environment, you'll see these options:

1. **Launch Hiren's Boot CD** - Access advanced recovery tools
2. **Restore System from Backup** - Restore from a system image backup
3. **Automated Windows 11 Reinstall** - Reinstall Windows while preserving data
4. **Driver Backup/Restore** - Manage system drivers
5. **Command Prompt** - Advanced command line access
6. **Restart Computer** - Exit and restart

## Troubleshooting

### Boot Issues
- Ensure Secure Boot is disabled in BIOS/UEFI
- Verify USB drive is properly formatted as FAT32
- Try different USB ports (preferably USB 2.0)

### Driver Issues
- Run driver verification: `pnputil /scan-devices`
- Check Device Manager for missing drivers
- Use Hiren's Boot "Driver Backup" tool for problematic systems

### Recovery Environment Not Starting
- Run boot repair: `bcdedit /set {default} bootmenupolicy legacy`
- Rebuild BCD: `bootrec /rebuildbcd`
- Check disk for errors: `chkdsk C: /f /r`

## Security Considerations

- Always verify the integrity of downloaded ISOs
- Use secure boot when possible
- Keep recovery tools updated
- Store recovery media in a secure location

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the project repository or contact the development team.
