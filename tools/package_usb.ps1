param(
  [Parameter(Mandatory=$true)][string]$TargetRoot,
  [switch]$IncludePython,
  [string]$PythonVersion = '3.11.9',
  [switch]$InstallAutoRepair
)

$ErrorActionPreference = 'Stop'

function Resolve-Abs([string]$p) { return [System.IO.Path]::GetFullPath($p) }

function Copy-OpryxxTree {
  param([string]$Src,[string]$Dst)
  $exclude = @(
    '^\.git($|\\)',
    '^dist($|\\)',
    '^build($|\\)',
    '^vendor\\wheels\\tmp($|\\)',
    '^run_\\d{8}_\\d{6}($|\\)',
    '^Backups($|\\)',
    '^\.venv($|\\)',
    'OPRYXX_Repair\.log$',
    'OPRYXX_InstallDrivers\.log$',
    'OPRYXX_Repair_Steps\.json$',
    'step_state\.json$',
    'plan\.json$',
    'health_report\.json$'
  )
  $rx = $exclude | ForEach-Object { New-Object regex $_ }
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  Get-ChildItem -Recurse -File -Force -Path $Src | ForEach-Object {
    $rel = [System.IO.Path]::GetRelativePath($Src, $_.FullName)
    $relNorm = $rel -replace '/', '\\'
    foreach ($r in $rx) { if ($r.IsMatch($relNorm)) { return } }
    $to = Join-Path $Dst $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $to -Parent) | Out-Null
    Copy-Item -Path $_.FullName -Destination $to -Force
  }
}

function Ensure-PythonEmbed {
  param([string]$DstRoot,[string]$Ver)
  $tools = Join-Path $DstRoot 'tools'
  $dst = Join-Path $tools 'python-embed'
  if (Test-Path (Join-Path $dst "python.exe")) { return $dst }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  $zip = Join-Path $env:TEMP ("python-" + $Ver + "-embed-amd64.zip")
  $uri = "https://www.python.org/ftp/python/$Ver/python-$Ver-embed-amd64.zip"
  Write-Host ("Downloading Python embed {0}..." -f $Ver)
  Invoke-WebRequest -Uri $uri -OutFile $zip
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dst)
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
  # Enable site imports
  $pth = Get-ChildItem -Path $dst -Filter "python*.pth" | Select-Object -First 1
  if ($pth) {
    $content = Get-Content $pth -Raw
    if ($content -notmatch 'import site') {
      Add-Content -Path $pth.FullName -Value "`nimport site`n"
    }
  }
  return $dst
}

$target = Resolve-Abs $TargetRoot
if (-not (Test-Path $target)) { New-Item -ItemType Directory -Force -Path $target | Out-Null }

$repo = Resolve-Abs (Join-Path $PSScriptRoot '..')
$dstRepo = Join-Path $target 'OPRYXX'
Write-Host ("Copying OPRYXX to {0}" -f $dstRepo)
Copy-OpryxxTree -Src $repo -Dst $dstRepo

# Helper launchers
$launch = @"
@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0OPRYXX\apex.ps1"
endlocal
"@
Set-Content -Path (Join-Path $target 'Launch_Opryxx.cmd') -Value $launch -Encoding ASCII

$launchDry = @"
@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0OPRYXX\apex.ps1" -DryRun
endlocal
"@
Set-Content -Path (Join-Path $target 'Launch_Opryxx_DryRun.cmd') -Value $launchDry -Encoding ASCII

if ($IncludePython) {
  $pyPath = Ensure-PythonEmbed -DstRoot $dstRepo -Ver $PythonVersion
  $api = @"
@echo off
setlocal
set PY=%~dp0OPRYXX\tools\python-embed\python.exe
if not exist "%PY%" (
  echo Python embed not found. Use system Python or run tools\bootstrap_python.ps1.
  exit /b 1
)
""%PY%"" "%~dp0OPRYXX\backend_api_scaffold.py"
endlocal
"@
  Set-Content -Path (Join-Path $target 'Start_Opryxx_API.cmd') -Value $api -Encoding ASCII
}

$readme = @"
OPRYXX USB Toolkit
===================

Contents:
- OPRYXX\ ... (PowerShell modules, scripts, UI, drivers)
- Launch_Opryxx.cmd             -> Run full repair
- Launch_Opryxx_DryRun.cmd      -> Plan only (no changes)
- Start_Opryxx_API.cmd          -> (optional) Start Python API if python embed included

Optional boot auto-repair installer (run on target Windows):
  powershell -ExecutionPolicy Bypass -File OPRYXX\tools\install_boot_autorepair.ps1

WinPE/RE usage:
- If building a WinPE USB, set startnet.cmd to run:
    wpeinit && powershell -ExecutionPolicy Bypass -File X:\OPRYXX\apex.ps1

Notes:
- Administrator privileges recommended for repair actions.
- Offline Python UI requires system Python or the included python-embed.
"@
Set-Content -Path (Join-Path $target 'README-USB.txt') -Value $readme -Encoding UTF8

if ($InstallAutoRepair) {
  Write-Host 'Installing boot auto-repair task on this system...'
  powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $dstRepo 'tools\install_boot_autorepair.ps1') | Out-Host
}

Write-Host "USB package ready at $target"

