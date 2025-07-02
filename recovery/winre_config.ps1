<#
.SYNOPSIS
    Configures Windows Recovery Environment (WinRE) with OPRYXX_LOGS recovery tools.
.DESCRIPTION
    This script sets up WinRE with custom recovery options including Hiren's Boot integration,
    automated driver backup/restore, and system recovery tools.
#>

#Requires -RunAsAdministrator

param (
    [string]$HirensIsoPath = "D:\Hirens_Boot_PE_x64.iso",
    [string]$RecoveryToolsPath = "X:\sources\recovery\OPRYXX",
    [switch]$SkipIsoCopy,
    [switch]$SkipBootMenu
)

$ErrorActionPreference = "Stop"

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

function Test-IsWinPE {
    return Test-Path "HKLM:\SYSTEM\CurrentControlSet\Control\MiniNT"
}

function Copy-HirensToRecovery {
    param (
        [string]$IsoPath,
        [string]$TargetPath
    )
    
    Write-Host "Mounting Hiren's Boot ISO..." -ForegroundColor Cyan
    $iso = Mount-DiskImage -ImagePath $IsoPath -PassThru
    $driveLetter = ($iso | Get-Volume).DriveLetter
    $sourcePath = "${driveLetter}:\"
    
    try {
        if (-not (Test-Path $TargetPath)) {
            New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
        }
        
        Write-Host "Copying Hiren's Boot files to recovery partition..." -ForegroundColor Cyan
        robocopy "$sourcePath" $TargetPath /E /R:1 /W:1 /NP /NFL /NDL /NJH /NJS /nc /ns /nfl
        
        # Create autorun script
        $autorunScript = @"
@echo off
title OPRYXX Recovery Environment
:start
cls
echo ==============================================
echo     OPRYXX Recovery Environment - v1.0
echo ==============================================
echo.
echo [1] Launch Hiren's Boot CD
echo [2] Restore System from Backup
echo [3] Automated Windows 11 Reinstall
echo [4] Driver Backup/Restore
echo [5] Command Prompt
echo [6] Restart Computer
echo.
set /p choice="Select an option (1-6): "

if "%choice%"=="1" goto hiren
if "%choice%"=="2" goto restore
if "%choice%"=="3" goto reinstall
if "%choice%"=="4" goto drivers
if "%choice%"=="5" goto cmd
if "%choice%"=="6" goto restart
goto start

:hiren
start /wait %~dp0\HBCD\HBCD\HBCD_Menu.cmd
goto start

:restore
start /wait %~dp0\tools\restore_system.cmd
goto start

:reinstall
start /wait %~dp0\tools\auto_reinstall.cmd
goto start

:drivers
start /wait %~dp0\tools\driver_manager.cmd
goto start

:cmd
cmd.exe

goto start

:restart
shutdown /r /t 0
"@
        
        $autorunScript | Out-File -FilePath "$TargetPath\autorun.cmd" -Encoding ASCII
        
        Write-Host "Hiren's Boot files copied successfully." -ForegroundColor Green
    }
    finally {
        Dismount-DiskImage -InputObject $iso
    }
}

function Add-RecoveryTools {
    param (
        [string]$ToolsPath
    )
    
    $toolsDir = "$ToolsPath\tools"
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    
    # Create driver backup/restore script
    @"
@echo off
setlocal enabledelayedexpansion

:start
cls
echo ==============================================
echo     OPRYXX Driver Management
echo ==============================================
echo.
echo [1] Backup All Drivers
echo [2] Restore Drivers
echo [3] List Available Backups
echo [4] Return to Main Menu
echo.
set /p choice="Select an option (1-4): "

if "%choice%"=="1" goto backup
if "%choice%"=="2" goto restore
if "%choice%"=="3" goto list
if "%choice%"=="4" exit /b
goto start

:backup
set /p backup_name=Enter a name for this backup (or press Enter for auto-name): 
if "%backup_name%"=="" (
    python %~dp0\driver_manager.py backup
) else (
    python %~dp0\driver_manager.py backup "%backup_name%"
)
pause
goto start

:restore
python %~dp0\driver_manager.py list
set /p backup_name=Enter the name of the backup to restore: 
python %~dp0\driver_manager.py restore "%backup_name%"
pause
goto start

:list
python %~dp0\driver_manager.py list
pause
goto start
"@ | Out-File -FilePath "$toolsDir\driver_manager.cmd" -Encoding ASCII

    # Create system restore script
    @"
@echo off
setlocal enabledelayedexpansion

:start
cls
echo ==============================================
echo     OPRYXX System Restore
echo ==============================================
echo.
echo [1] Create System Restore Point
echo [2] Restore from System Restore Point
echo [3] List Available Restore Points
echo [4] Return to Main Menu
echo.
set /p choice="Select an option (1-4): "

if "%choice%"=="1" goto create
if "%choice%"=="2" goto restore
if "%choice%"=="3" goto list
if "%choice%"=="4" exit /b
goto start

:create
powershell -Command "Checkpoint-Computer -Description 'OPRYXX Recovery Point' -RestorePointType MODIFY_SETTINGS"
echo Restore point created.
pause
goto start

:restore
powershell -Command "Get-ComputerRestorePoint | Format-Table -AutoSize"
set /p sequence=Enter the Sequence Number of the restore point: 
powershell -Command "Restore-Computer -RestorePoint %sequence% -Confirm:$false"
pause
goto start

:list
powershell -Command "Get-ComputerRestorePoint | Format-Table -AutoSize"
pause
goto start
"@ | Out-File -FilePath "$toolsDir\restore_system.cmd" -Encoding ASCII

    # Create auto reinstall script
    @"
@echo off
setlocal enabledelayedexpansion

:start
cls
echo ==============================================
echo     OPRYXX Windows 11 Automated Reinstall
echo ==============================================
echo.
echo WARNING: This will reinstall Windows 11 and may result in data loss.
echo Make sure to back up all important data before proceeding.
echo.
set /p confirm=Are you sure you want to continue? (y/n): 

if /i "%confirm%" neq "y" (
    exit /b
)

echo.
echo [1] Keep personal files and apps
echo [2] Keep personal files only
echo [3] Clean install (remove everything)
echo.
set /p install_type=Select installation type (1-3): 

if "%install_type%"=="1" set INSTALL_OPTIONS=/auto upgrade /microsoft /dynamicupdate enable /showoobe none /quiet
if "%install_type%"=="2" set INSTALL_OPTIONS=/auto clean /microsoft /showoobe none /quiet
if "%install_type%"=="3" set INSTALL_OPTIONS=/auto clean /microsoft /showoobe none /quiet /noreboot

if not defined INSTALL_OPTIONS (
    echo Invalid selection.
    pause
    goto start
)

echo.
echo Starting Windows 11 reinstallation...

echo Backing up drivers...
python %~dp0\driver_manager.py backup "PreReinstall_%DATE:/=-%_%TIME::=-%"

echo Starting Windows Setup...
start /wait setup.exe %INSTALL_OPTIONS%

echo Installation complete. The system will restart in 30 seconds...
timeout /t 30
shutdown /r /t 0
"@ | Out-File -FilePath "$toolsDir\auto_reinstall.cmd" -Encoding ASCII
}

function Update-BootMenu {
    param (
        [string]$RecoveryPath
    )
    
    if ($SkipBootMenu) {
        Write-Host "Skipping boot menu update as requested." -ForegroundColor Yellow
        return
    }
    
    Write-Host "Updating boot menu configuration..." -ForegroundColor Cyan
    
    # Backup current BCD
    $bcdBackup = "$env:TEMP\bcd_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    bcdedit /export $bcdBackup
    Write-Host "Current BCD configuration backed up to $bcdBackup" -ForegroundColor Green
    
    # Add custom recovery entry
    $recoveryGuid = [guid]::NewGuid().ToString()
    $recoveryTitle = "OPRYXX Recovery Environment"
    $recoveryPath = "$RecoveryPath\autorun.cmd"
    
    try {
        # Create new boot entry
        bcdedit /create /d "$recoveryTitle" /application osloader | Out-Null
        $recoveryGuid = (bcdedit /enum | Select-String -Pattern "$recoveryTitle" -Context 0,2 | 
                        Select-Object -First 1 | ForEach-Object { $_.ToString().Split()[1] })
        
        # Configure boot entry
        bcdedit /set "{$recoveryGuid}" device "ramdisk=[$($RecoveryPath.Replace('\', '\\'))]boot.sdi,{ramdiskoptions}"
        bcdedit /set "{$recoveryGuid}" osdevice "ramdisk=[$($RecoveryPath.Replace('\', '\\'))]boot.sdi,{ramdiskoptions}"
        bcdedit /set "{$recoveryGuid}" systemroot "\Windows"
        bcdedit /set "{$recoveryGuid}" winpe "Yes"
        bcdedit /set "{$recoveryGuid}" detecthal "Yes"
        bcdedit /set "{$recoveryGuid}" winpe "Yes"
        bcdedit /set "{$recoveryGuid}" ems "No"
        bcdedit /set "{$recoveryGuid}" bootmenupolicy "Legacy"
        bcdedit /set "{$recoveryGuid}" nointegritychecks "Yes"
        bcdedit /set "{$recoveryGuid}" testsigning "Yes"
        bcdedit /set "{$recoveryGuid}" path "\Windows\System32\boot\winload.exe"
        bcdedit /set "{$recoveryGuid}" description "$recoveryTitle"
        bcdedit /displayorder "{$recoveryGuid}" /addlast
        
        # Set timeout
        bcdedit /timeout 10
        
        Write-Host "Boot menu updated successfully." -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to update boot menu: $_"
        Write-Host "Restoring BCD from backup..." -ForegroundColor Yellow
        bcdedit /import $bcdBackup
        throw
    }
}

# Main execution
try {
    # Check if running in WinPE
    if (Test-IsWinPE) {
        $recoveryPath = $env:SystemDrive
    }
    else {
        # Get recovery partition
        $recoveryPartition = Get-Partition | Where-Object { $_.Type -eq 'Recovery' } | Select-Object -First 1
        if (-not $recoveryPartition) {
            throw "No recovery partition found."
        }
        
        # Assign drive letter if needed
        $recoveryDrive = Get-Volume -Partition $recoveryPartition | Select-Object -ExpandProperty DriveLetter
        if (-not $recoveryDrive) {
            $recoveryDrive = (Get-Volume | Where-Object { $_.DriveType -eq 'CD-ROM' }).DriveLetter
            if (-not $recoveryDrive) {
                $recoveryDrive = 'Z:'
            }
            else {
                $recoveryDrive = "${recoveryDrive}:"
            }
            
            $recoveryPartition | Set-Partition -NewDriveLetter $recoveryDrive[0]
            $recoveryDrive = $recoveryDrive[0] + ":"
        }
        else {
            $recoveryDrive = "${recoveryDrive}:"
        }
        
        $recoveryPath = "${recoveryDrive}Recovery\OPRYXX"
    }
    
    # Create recovery directory
    if (-not (Test-Path $recoveryPath)) {
        New-Item -ItemType Directory -Path $recoveryPath -Force | Out-Null
    }
    
    # Copy Hiren's Boot files if not skipped
    if (-not $SkipIsoCopy -and (Test-Path $HirensIsoPath)) {
        Copy-HirensToRecovery -IsoPath $HirensIsoPath -TargetPath "$recoveryPath\HBCD"
    }
    
    # Add recovery tools
    Add-RecoveryTools -ToolsPath $recoveryPath
    
    # Copy driver manager script
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    Copy-Item "$scriptPath\driver_manager.py" "$recoveryPath\tools\" -Force
    
    # Update boot menu
    Update-BootMenu -RecoveryPath $recoveryPath
    
    Write-Host "`nOPRYXX Recovery Environment has been configured successfully!" -ForegroundColor Green
    Write-Host "Recovery tools location: $recoveryPath" -ForegroundColor Cyan
    Write-Host "You can now access the recovery environment from the boot menu." -ForegroundColor Cyan
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
finally {
    # Clean up
    if ($recoveryDrive) {
        Remove-PartitionAccessPath -DiskNumber $recoveryPartition.DiskNumber -PartitionNumber $recoveryPartition.PartitionNumber -AccessPath $recoveryDrive -ErrorAction SilentlyContinue
    }
}
