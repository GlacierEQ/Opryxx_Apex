param(
    [Parameter(Mandatory=$true)] [string]$Model,
    [string]$DriversRoot = (Join-Path $PSScriptRoot 'drivers'),
    [string]$OfflineImage,
    [switch]$DryRun
)

function Write-Log {
    param([string]$msg)
    $logFile = Join-Path $PSScriptRoot 'OPRYXX_InstallDrivers.log'
    Add-Content -Path $logFile -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg")
}

function Log-Json {
    param($step, $status, $details)
    $jsonLogFile = Join-Path $PSScriptRoot 'OPRYXX_Repair_Steps.json'
    $entry = @{timestamp=(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'); step=$step; status=$status; details=$details}
    $log = @()
    if (Test-Path $jsonLogFile) {
        $current = Get-Content $jsonLogFile -Raw | ConvertFrom-Json
        if ($null -ne $current) { $log = @($current) }
    }
    $log += $entry
    $log | ConvertTo-Json -Depth 6 | Set-Content $jsonLogFile
}

function Ensure-Elevation {
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "Script must be run as Administrator. Relaunching with elevation..."
        Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File '$PSCommandPath' $($MyInvocation.UnboundArguments)" -Verb RunAs
        exit
    }
}
Ensure-Elevation

$modelPath = Join-Path $DriversRoot $Model
if (-not (Test-Path $modelPath)) { throw "Model drivers not found: $modelPath" }

Write-Host "Installing drivers for model: $Model"
Write-Log   "Installing drivers for model: $Model"

$infFiles = Get-ChildItem -Recurse -File -Filter *.inf $modelPath
if (-not $infFiles) { Write-Host "No INF files found under $modelPath"; exit 0 }

foreach ($inf in $infFiles) {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would install: $($inf.FullName)"
        continue
    }
    if ($OfflineImage) {
        Write-Host "Adding driver to offline image: $($inf.FullName)"
        Write-Log   "DISM /image:$OfflineImage /add-driver /driver:'$($inf.FullName)'"
        $p = Start-Process -FilePath dism.exe -ArgumentList "/image:$OfflineImage","/add-driver","/driver:$($inf.FullName)" -PassThru -Wait -WindowStyle Hidden
        $status = if ($p.ExitCode -eq 0) { 'success' } else { "exit_$($p.ExitCode)" }
        Log-Json "install_driver_offline" $status $inf.FullName
    } else {
        Write-Host "Installing driver: $($inf.FullName)"
        Write-Log   "pnputil /add-driver '$($inf.FullName)' /install"
        $p = Start-Process -FilePath pnputil.exe -ArgumentList "/add-driver","$($inf.FullName)","/install" -PassThru -Wait -WindowStyle Hidden
        $status = if ($p.ExitCode -eq 0) { 'success' } else { "exit_$($p.ExitCode)" }
        Log-Json "install_driver" $status $inf.FullName
    }
}

Write-Host "Driver installation sequence complete."
Write-Log   "Driver installation sequence complete."
