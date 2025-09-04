param(
  [string]$OutDir = (Join-Path (Split-Path $PSScriptRoot -Parent) 'vendor\wheels'),
  [string]$Python
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Find-Python {
  param([string]$Hint)
  if ($Hint -and (Test-Path $Hint)) { return $Hint }
  $c = (Get-Command py -ErrorAction SilentlyContinue)?.Source
  if ($c) { return $c }
  $c = (Get-Command python -ErrorAction SilentlyContinue)?.Source
  if ($c) { return $c }
  throw 'Python not found on PATH. Install Python to download wheels.'
}

$py = Find-Python -Hint $Python
& $py -m pip install --upgrade pip
& $py -m pip download -r (Join-Path (Split-Path $PSScriptRoot -Parent) 'requirements.txt') -d $OutDir --only-binary=:all:
Write-Host ("Wheels downloaded to {0}" -f $OutDir)

