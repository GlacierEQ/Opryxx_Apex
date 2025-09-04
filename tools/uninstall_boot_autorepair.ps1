$ErrorActionPreference = 'Stop'
function Ensure-Elevation {
  if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Script must be run as Administrator. Relaunching with elevation..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
  }
}
Ensure-Elevation

try {
  Unregister-ScheduledTask -TaskName 'OpryxxAutoBootRepair' -Confirm:$false -ErrorAction Stop
  Write-Host 'OpryxxAutoBootRepair task removed.'
} catch {
  Write-Host "No task removed or error: $($_.Exception.Message)"
}

