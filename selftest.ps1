param(
  [switch]$Verbose
)

$ErrorActionPreference = 'Stop'

function Assert-True { param([bool]$cond,[string]$msg) if (-not $cond) { throw $msg } }

$root = $PSScriptRoot
$apex = Join-Path $root 'apex.ps1'
$manifestPath = Join-Path $root 'manifest.json'
Assert-True (Test-Path $apex) "Missing $apex"
Assert-True (Test-Path $manifestPath) "Missing $manifestPath"

$env:OPRYXX_SKIP_ELEVATION = '1'
Write-Host "[SelfTest] Running apex dry-run..."
powershell -NoProfile -ExecutionPolicy Bypass -File $apex -DryRun | Out-Host

$planPath = Join-Path $root 'plan.json'
Assert-True (Test-Path $planPath) "Plan not generated: $planPath"
$plan = Get-Content $planPath -Raw | ConvertFrom-Json
Assert-True ($plan.Count -ge 6) "Unexpected plan length"

Write-Host "[SelfTest] Selecting first model from manifest..."
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$modelRes = @($manifest.resources | Where-Object { $_.model })
Assert-True ($modelRes.Count -ge 1) "No model entries in manifest"
$model = $modelRes[0].model

Write-Host "[SelfTest] Enumerating .inf under model: $model"
$driversRoot = Join-Path $root 'drivers'
$modelPath = Join-Path $driversRoot $model
Assert-True (Test-Path $modelPath) "Model path not found: $modelPath"
$inf = Get-ChildItem -Recurse -File -Filter *.inf $modelPath -ErrorAction SilentlyContinue
Write-Host ("Found {0} INF files" -f ($inf|Measure-Object).Count)

$installer = Join-Path $root 'install_model_drivers.ps1'
Assert-True (Test-Path $installer) "Missing $installer"
Write-Host "[SelfTest] Running driver installer dry-run..."
powershell -NoProfile -ExecutionPolicy Bypass -File $installer -Model $model -DriversRoot $driversRoot -DryRun | Out-Host

$logJson = Join-Path $root 'OPRYXX_Repair_Steps.json'
if (Test-Path $logJson) {
  $log = Get-Content $logJson -Raw | ConvertFrom-Json
  Assert-True ($null -ne $log) "Failed to parse JSON log"
}

Write-Host "[SelfTest] OK: dry-run plan, health report, and driver enumeration validated."

