<#
.SYNOPSIS
    Creates bootable recovery media with Hiren's Boot and OPRYXX recovery tools.
.DESCRIPTION
    This script automates the process of creating a bootable USB drive with Hiren's Boot CD
    and OPRYXX recovery tools for system recovery and maintenance.
.PARAMETER UsbDrive
    The drive letter of the USB drive to use (e.g., 'F:').
.PARAMETER HirensIsoPath
    Path to Hiren's Boot CD ISO file. If not provided, it will be downloaded automatically.
.PARAMETER DownloadHirens
    Switch to automatically download the latest Hiren's Boot CD if not found.
.PARAMETER Force
    Skip all confirmation prompts.
.EXAMPLE
    .\create_recovery_media.ps1 -UsbDrive "F:" -DownloadHirens
    Creates recovery media on drive F: and downloads Hiren's Boot CD if needed.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Za-z]:$')]
    [string]$UsbDrive,
    
    [string]$HirensIsoPath,
    [switch]$DownloadHirens,
    [switch]$Force
)

# Ensure running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

# Set error action preference
$ErrorActionPreference = 'Stop'

# Script variables
$script:tempDir = Join-Path $env:TEMP "OPRYXX_Recovery_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$script:hirensUrl = "https://www.hirensbootcd.org/files/HBCD_PE_x64.iso"
$script:rufusUrl = "https://github.com/pbatard/rufus/releases/download/v4.3/rufus-4.3p.exe"
$script:sevenZipUrl = "https://www.7-zip.org/a/7z2301-x64.exe"

function Write-Header {
    param([string]$Message)
    $separator = '=' * $Message.Length
    Write-Host "`n$separator" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "$separator`n" -ForegroundColor Cyan
}

function Test-CommandExists {
    param([string]$Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

function Get-WebFile {
    param(
        [string]$Url,
        [string]$OutputPath,
        [string]$Description
    )
    
    Write-Host "Downloading $Description..." -ForegroundColor Cyan
    try {
        $progressPreference = 'silentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing
        Write-Host "Downloaded $Description to $OutputPath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to download $Description from $Url`n$($_.Exception.Message)"
        return $false
    }
    finally {
        $progressPreference = 'Continue'
    }
}

function Confirm-DriveIsUsb {
    param([string]$DriveLetter)
    
    try {
        $drive = Get-Volume -DriveLetter $DriveLetter[0] -ErrorAction Stop
        if ($drive.DriveType -ne 'Removable') {
            Write-Error "Drive $DriveLetter is not a removable USB drive."
            return $false
        }
        return $true
    }
    catch {
        Write-Error "Could not verify drive $DriveLetter : $_"
        return $false
    }
}

function Get-HirensIso {
    param([string]$OutputPath)
    
    if (-not [string]::IsNullOrEmpty($HirensIsoPath) -and (Test-Path $HirensIsoPath)) {
        Write-Host "Using provided Hiren's Boot ISO: $HirensIsoPath" -ForegroundColor Green
        Copy-Item -Path $HirensIsoPath -Destination $OutputPath -Force
        return $true
    }
    
    if ($DownloadHirens) {
        Write-Host "Downloading Hiren's Boot CD..." -ForegroundColor Cyan
        return Get-WebFile -Url $script:hirensUrl -OutputPath $OutputPath -Description "Hiren's Boot CD"
    }
    
    Write-Error "Hiren's Boot ISO not found. Please provide the path or use -DownloadHirens to download it."
    return $false
}

function Install-7Zip {
    if (Test-CommandExists '7z') {
        return $true
    }
    
    $installerPath = Join-Path $script:tempDir '7z_installer.exe'
    
    if (-not (Get-WebFile -Url $script:sevenZipUrl -OutputPath $installerPath -Description "7-Zip Installer")) {
        return $false
    }
    
    Write-Host "Installing 7-Zip..." -ForegroundColor Cyan
    try {
        $process = Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -ne 0) {
            throw "7-Zip installation failed with exit code $($process.ExitCode)"
        }
        
        # Refresh PATH to include 7-Zip
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (-not (Test-CommandExists '7z')) {
            throw "7-Zip installation completed but '7z' command is not available."
        }
        
        Write-Host "7-Zip installed successfully." -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to install 7-Zip: $_"
        return $false
    }
}

function Create-RecoveryMedia {
    param(
        [string]$UsbDrive,
        [string]$HirensIsoPath
    )
    
    # Create temp directory
    New-Item -ItemType Directory -Path $script:tempDir -Force | Out-Null
    
    # Get Hiren's Boot ISO
    $hirensIso = Join-Path $script:tempDir "HBCD_PE_x64.iso"
    if (-not (Get-HirensIso -OutputPath $hirensIso)) {
        return $false
    }
    
    # Install 7-Zip if needed
    if (-not (Install-7Zip)) {
        return $false
    }
    
    # Extract Hiren's Boot ISO
    Write-Host "Extracting Hiren's Boot CD..." -ForegroundColor Cyan
    $extractDir = Join-Path $script:tempDir "HBCD_Extracted"
    New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
    
    try {
        & 7z x "$hirensIso" -o"$extractDir" -y | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to extract Hiren's Boot ISO"
        }
    }
    catch {
        Write-Error "Error extracting Hiren's Boot ISO: $_"
        return $false
    }
    
    # Copy OPRYXX recovery tools
    Write-Host "Copying OPRYXX recovery tools..." -ForegroundColor Cyan
    $recoveryToolsDir = Join-Path $extractDir "OPRYXX"
    New-Item -ItemType Directory -Path $recoveryToolsDir -Force | Out-Null
    
    # Copy all files from the recovery directory
    $recoverySource = Join-Path $PSScriptRoot "*"
    Copy-Item -Path $recoverySource -Destination $recoveryToolsDir -Recurse -Force
    
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
start /wait HBCD\HBCD_Menu.cmd
goto start

:restore
start /wait OPRYXX\tools\restore_system.cmd
goto start

:reinstall
start /wait OPRYXX\tools\auto_reinstall.cmd
goto start

:drivers
start /wait OPRYXX\tools\driver_manager.cmd
goto start

:cmd
cmd.exe
goto start

:restart
shutdown /r /t 0
"@
    
    $autorunScript | Out-File -FilePath (Join-Path $extractDir "autorun.cmd") -Encoding ASCII
    
    # Copy files to USB drive
    Write-Host "Copying files to USB drive $UsbDrive ..." -ForegroundColor Cyan
    try {
        Get-ChildItem -Path $extractDir | ForEach-Object {
            $destPath = Join-Path $UsbDrive $_.Name
            if ($_.PSIsContainer) {
                Copy-Item -Path $_.FullName -Destination $destPath -Recurse -Force
            } else {
                Copy-Item -Path $_.FullName -Destination $destPath -Force
            }
        }
    }
    catch {
        Write-Error "Failed to copy files to USB drive: $_"
        return $false
    }
    
    # Make USB bootable using bootsect
    Write-Host "Making USB drive bootable..." -ForegroundColor Cyan
    try {
        $bootsectPath = Join-Path $env:SystemRoot "System32\bootsect.exe"
        if (Test-Path $bootsectPath) {
            & $bootsectPath "/nt60" $UsbDrive "/mbr" "/force"
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Bootsect completed with warnings. The drive might still be bootable."
            }
        }
        else {
            Write-Warning "bootsect.exe not found. The drive might not be bootable."
            Write-Host "Please run the following command as Administrator to make the drive bootable:"
            Write-Host "bootsect /nt60 $UsbDrive /mbr /force" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Warning "Error making USB drive bootable: $_"
    }
    
    return $true
}

# Main execution
try {
    Write-Header "OPRYXX Recovery Media Creator"
    
    # Check if drive exists and is USB
    if (-not (Test-Path $UsbDrive)) {
        throw "Drive $UsbDrive does not exist."
    }
    
    if (-not (Confirm-DriveIsUsb -DriveLetter $UsbDrive)) {
        throw "$UsbDrive is not a valid USB drive."
    }
    
    # Confirm before proceeding
    if (-not $Force) {
        Write-Warning "ALL DATA ON $UsbDrive WILL BE LOST!"
        $confirmation = Read-Host "Are you sure you want to continue? (y/n)"
        if ($confirmation -ne 'y') {
            Write-Host "Operation cancelled by user." -ForegroundColor Yellow
            exit 0
        }
    }
    
    # Format USB drive
    Write-Host "Formatting USB drive $UsbDrive as FAT32..." -ForegroundColor Cyan
    $format = @{
        FileSystem = 'FAT32'
        Confirm = $false
        Force = $true
    }
    
    try {
        Format-Volume -DriveLetter $UsbDrive[0] @format
    }
    catch {
        Write-Warning "Failed to format drive: $_"
        Write-Host "Trying alternative format method..." -ForegroundColor Yellow
        try {
            $vol = Get-Volume -DriveLetter $UsbDrive[0]
            $vol | Format-Volume -FileSystem FAT32 -NewFileSystemLabel "OPRYXX_RECOVERY" -Confirm:$false -Force
        }
        catch {
            throw "Failed to format drive using alternative method: $_"
        }
    }
    
    # Create recovery media
    if (Create-RecoveryMedia -UsbDrive $UsbDrive -HirensIsoPath $HirensIsoPath) {
        Write-Host "`nRecovery media created successfully on $UsbDrive" -ForegroundColor Green
        Write-Host "You can now boot from this USB drive to access the recovery environment." -ForegroundColor Green
    }
    else {
        throw "Failed to create recovery media."
    }
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
finally {
    # Clean up
    if (Test-Path $script:tempDir) {
        Remove-Item -Path $script:tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
