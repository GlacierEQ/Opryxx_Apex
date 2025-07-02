# OPRYXX MEDIA HANDLER
# Part of OPRYXX Automated Recovery System
# Handles Windows 11 media download and preparation

# Configuration
$config = @{
    LogPath = "$env:ProgramData\OPRYXX\Recovery\Logs"
    MediaPath = "$env:ProgramData\OPRYXX\Recovery\Media"
    MediaCreationTool = "$env:TEMP\MediaCreationTool.exe"
    Win11DownloadURL = "https://go.microsoft.com/fwlink/?linkid=2156295"
    Win11ISO = "$env:ProgramData\OPRYXX\Recovery\Media\Win11_23H2_English_x64.iso"
}

# Create necessary directories
foreach ($dir in ($config.LogPath, $config.MediaPath)) {
    if (-not (Test-Path $dir)) { 
        New-Item -ItemType Directory -Path $dir -Force | Out-Null 
    }
}

# Logging function
function Write-OPRYXXLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    $logFile = Join-Path $config.LogPath "media_handler_$(Get-Date -Format 'yyyyMMdd').log"
    
    # Color coding for console
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN"  { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    
    Write-Host $logMessage -ForegroundColor $color
    Add-Content -Path $logFile -Value $logMessage
}

# Download Windows 11 Media Creation Tool
function Get-MediaCreationTool {
    Write-OPRYXXLog "Downloading Windows 11 Media Creation Tool..."
    try {
        $progressPreference = 'silentlyContinue'
        Invoke-WebRequest -Uri $config.Win11DownloadURL -OutFile $config.MediaCreationTool -UseBasicParsing -ErrorAction Stop
        
        if (Test-Path $config.MediaCreationTool) {
            Write-OPRYXXLog "Media Creation Tool downloaded successfully" -Level "SUCCESS"
            return $true
        } else {
            throw "Download completed but file not found"
        }
    } catch {
        Write-OPRYXXLog "Failed to download Media Creation Tool: $_" -Level "ERROR"
        return $false
    }
}

# Create Windows 11 ISO
function New-Windows11ISO {
    Write-OPRYXXLog "Creating Windows 11 ISO..."
    
    # Check if ISO already exists
    if (Test-Path $config.Win11ISO) {
        Write-OPRYXXLog "Windows 11 ISO already exists at: $($config.Win11ISO)" -Level "SUCCESS"
        return $true
    }
    
    # Ensure Media Creation Tool exists
    if (-not (Test-Path $config.MediaCreationTool)) {
        Write-OPRYXXLog "Media Creation Tool not found. Attempting to download..."
        if (-not (Get-MediaCreationTool)) {
            return $false
        }
    }
    
    # Run Media Creation Tool to create ISO
    try {
        $process = Start-Process -FilePath $config.MediaCreationTool -ArgumentList "/Auto Upgrade /Eula Accept /NoRestart /NoReboot /Quiet /ISO" -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            # Check if ISO was created in default location
            $defaultIsoPath = Join-Path ([Environment]::GetFolderPath('UserProfile')) "Downloads\Win11_23H2_English_x64.iso"
            if (Test-Path $defaultIsoPath) {
                Move-Item -Path $defaultIsoPath -Destination $config.Win11ISO -Force
                Write-OPRYXXLog "Windows 11 ISO created successfully at: $($config.Win11ISO)" -Level "SUCCESS"
                return $true
            } else {
                throw "ISO not found in default location"
            }
        } else {
            throw "Process exited with code $($process.ExitCode)"
        }
    } catch {
        Write-OPRYXXLog "Failed to create Windows 11 ISO: $_" -Level "ERROR"
        return $false
    }
}

# Create bootable USB
function New-BootableUSB {
    param(
        [string]$ISOPath = $config.Win11ISO,
        [string]$DriveLetter = (Get-Volume | Where-Object { $_.DriveType -eq 'Removable' -and $_.DriveLetter } | Select-Object -First 1).DriveLetter
    )
    
    if (-not $DriveLetter) {
        Write-OPRYXXLog "No USB drive found. Please insert a USB drive and try again." -Level "ERROR"
        return $false
    }
    
    $usbPath = "${DriveLetter}:\"
    
    try {
        Write-OPRYXXLog "Creating bootable USB on $usbPath..."
        
        # Format USB drive
        Write-OPRYXXLog "Formatting USB drive..."
        Format-Volume -DriveLetter $DriveLetter -FileSystem FAT32 -Confirm:$false -Force
        
        # Mount ISO and copy files
        Write-OPRYXXLog "Mounting ISO..."
        $isoMount = Mount-DiskImage -ImagePath $ISOPath -PassThru -ErrorAction Stop
        $isoDrive = ($isoMount | Get-Volume).DriveLetter
        $sourcePath = "${isoDrive}:\\*"
        
        # Copy files with progress
        Write-OPRYXXLog "Copying files to USB (this may take a while)..."
        $sourceItems = Get-ChildItem -Path $sourcePath
        $totalItems = $sourceItems.Count
        $currentItem = 0
        
        foreach ($item in $sourceItems) {
            $currentItem++
            $progress = [math]::Round(($currentItem / $totalItems) * 100)
            Write-Progress -Activity "Copying files to USB" -Status "$progress% Complete" -PercentComplete $progress
            
            $destination = Join-Path $usbPath $item.Name
            if ($item.PSIsContainer) {
                if (-not (Test-Path $destination)) {
                    New-Item -Path $destination -ItemType Directory | Out-Null
                }
                Copy-Item -Path $item.FullName -Destination $destination -Recurse -Force
            } else {
                Copy-Item -Path $item.FullName -Destination $destination -Force
            }
        }
        
        Write-Progress -Activity "Copying files to USB" -Completed
        Dismount-DiskImage -InputObject $isoMount
        
        Write-OPRYXXLog "Bootable USB created successfully on $usbPath" -Level "SUCCESS"
        return $true
    } catch {
        Write-OPRYXXLog "Error creating bootable USB: $_" -Level "ERROR"
        if ($isoMount) { Dismount-DiskImage -InputObject $isoMount -ErrorAction SilentlyContinue }
        return $false
    }
}

# Main execution
function Start-OPRYXXMediaHandler {
    [CmdletBinding()]
    param(
        [switch]$CreateISO,
        [switch]$CreateUSB,
        [string]$ISOPath = $config.Win11ISO,
        [string]$USBDrive
    )
    
    Write-OPRYXXLog "=== OPRYXX MEDIA HANDLER STARTED ==="
    
    try {
        # Create ISO if requested or if needed for USB creation
        if ($CreateISO -or ($CreateUSB -and -not (Test-Path $ISOPath))) {
            if (-not (New-Windows11ISO)) {
                throw "Failed to create Windows 11 ISO"
            }
        }
        
        # Create bootable USB if requested
        if ($CreateUSB) {
            if (-not (Test-Path $ISOPath)) {
                throw "ISO file not found at: $ISOPath"
            }
            
            $driveLetter = if ($USBDrive) { $USBDrive.TrimEnd('\') } else { $null }
            if (-not (New-BootableUSB -ISOPath $ISOPath -DriveLetter $driveLetter)) {
                throw "Failed to create bootable USB"
            }
        }
        
        Write-OPRYXXLog "=== MEDIA HANDLER COMPLETED SUCCESSFULLY ===" -Level "SUCCESS"
        return 0
    } catch {
        Write-OPRYXXLog "MEDIA HANDLER FAILED: $_" -Level "ERROR"
        return 1
    }
}

# Execute if run directly
if ($MyInvocation.InvocationName -ne '.') {
    # Parse command line arguments
    param(
        [switch]$CreateISO,
        [switch]$CreateUSB,
        [string]$ISOPath,
        [string]$USBDrive
    )
    
    if (-not ($CreateISO -or $CreateUSB)) {
        Write-Host "Usage:"
        Write-Host "  .\OPRYXX_Media_Handler.ps1 -CreateISO"
        Write-Host "  .\OPRYXX_Media_Handler.ps1 -CreateUSB [-USBDrive X]"
        Write-Host "  .\OPRYXX_Media_Handler.ps1 -CreateISO -CreateUSB [-USBDrive X] [-ISOPath path\to\windows.iso]"
        exit 1
    }
    
    $params = @{}
    if ($CreateISO) { $params.CreateISO = $true }
    if ($CreateUSB) { $params.CreateUSB = $true }
    if ($ISOPath) { $params.ISOPath = $ISOPath }
    if ($USBDrive) { $params.USBDrive = $USBDrive }
    
    exit (Start-OPRYXXMediaHandler @params)
}
