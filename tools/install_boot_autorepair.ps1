param(
  [string]$RepoRoot = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = 'Stop'

function Ensure-Elevation {
  if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Script must be run as Administrator. Relaunching with elevation..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RepoRoot `"$RepoRoot`"" -Verb RunAs
    exit
  }
}
Ensure-Elevation

$lib = Join-Path $RepoRoot 'lib'
$repair = Join-Path $lib 'Opryxx.Repair.psm1'
if (-not (Test-Path $repair)) { throw "Repair module not found: $repair" }

Import-Module $repair -Force
$res = Register-OpryxxBootAutoRepair -RepoRoot $RepoRoot
$state = Get-OpryxxBootAutoRepair

$out = [pscustomobject]@{ ok=$true; install=$res; state=$state }
$out | ConvertTo-Json -Depth 6 | Write-Output

