param(
    [switch]$DryRun,
    [string]$LogRoot,
    [switch]$SafeRepairs,
    [string]$ResumePath
)

function Ensure-Elevation {
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "Script must be run as Administrator. Relaunching with elevation..."
        Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File '$PSCommandPath' $($MyInvocation.UnboundArguments)" -Verb RunAs
        exit
    }
}
if ($env:OPRYXX_SKIP_ELEVATION -ne '1') { Ensure-Elevation }

Write-Host "Opryxx Apex starting... (DryRun=$DryRun)"

# Import modules
$lib = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $lib 'Opryxx.Manifest.psm1') -Force
Import-Module (Join-Path $lib 'Opryxx.Logging.psm1') -Force
Import-Module (Join-Path $lib 'Opryxx.Executor.psm1') -Force

# Run context
$logBase = if ($LogRoot) { $LogRoot } else { Join-Path $env:ProgramData 'Opryxx\Logs' }
try { New-Item -ItemType Directory -Force -Path $logBase | Out-Null } catch { $logBase = $PSScriptRoot }
$ctx = $null
if ($ResumePath) {
    Write-Host ("Resuming run from {0}" -f $ResumePath)
    $ctx = Open-OpryxxRunContext -Path $ResumePath
} else {
    $ctx = New-OpryxxRunContext -Root $logBase
}

# Detect
$sysInfo = Get-CimInstance -ClassName Win32_ComputerSystem
$biosInfo = Get-CimInstance -ClassName Win32_BIOS
$boardInfo = Get-CimInstance -ClassName Win32_BaseBoard
Write-Host "Detected Manufacturer: $($sysInfo.Manufacturer)"
Write-Host "Detected Model: $($sysInfo.Model)"

if (-not $ResumePath) {
    # Manifest
    $manifestPath = Join-Path $PSScriptRoot 'manifest.json'
    $manifest = Get-OpryxxManifest -Path $manifestPath
    $model = Resolve-OpryxxModel -Manifest $manifest -ModelString (($sysInfo.Model | Out-String).Trim()) -Manufacturer (($sysInfo.Manufacturer | Out-String).Trim())
    if (-not $model) { throw 'Unable to resolve model' }
    Write-Host "Resolved model: $model"
    # Plan
    $plan = New-OpryxxPlan -Manifest $manifest -Model $model -RepoRoot $PSScriptRoot
    $plan | ConvertTo-Json -Depth 6 | Set-Content $ctx.PlanPath
    Add-OpryxxEvent -Ctx $ctx -Step 'plan' -Status 'ready' -Details @{model=$model; count=$plan.Count}
} else {
    Write-Host 'Loading existing plan for resume.'
}

if ($DryRun) {
    $plan = Get-Content $ctx.PlanPath -Raw | ConvertFrom-Json
    foreach ($s in $plan) { Write-Host ("[PLAN] {0}: {1}" -f $s.kind, $s.step) }
    Write-Host ("Plan written to {0}" -f $ctx.PlanPath)
    Write-Host ("Run folder: {0}" -f $ctx.Root)
    Write-Host "Opryxx Apex finished (dry-run)."
    exit 0
}

$planObj = Get-Content $ctx.PlanPath -Raw | ConvertFrom-Json
Invoke-OpryxxPlan -Plan $planObj -DryRun:$false -Ctx $ctx -RepoRoot $PSScriptRoot -AllowedRoots @('Y:\\CustomDrivers') -ApexPath (Join-Path $PSScriptRoot 'apex.ps1')
Write-OpryxxResult -Ctx $ctx -Result @{ status='completed' }
Write-Host ("Run folder: {0}" -f $ctx.Root)
Write-Host "Opryxx Apex finished."
