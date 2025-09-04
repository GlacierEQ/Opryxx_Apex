param(
  [string]$Python = 'py',
  [switch]$InstallDeps
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
  if ($InstallDeps) {
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -r requirements.txt
    & $Python -m pip install pyinstaller
  }

  $web = Join-Path $PSScriptRoot 'web'
  if (-not (Test-Path $web)) { throw "Web assets not found: $web" }

  # Build single-file EXE, include web assets
  $addData = "web;web"
  & $Python -m PyInstaller --noconfirm --clean --onefile `
    --name OpryxxControlCenter `
    --add-data $addData `
    --hidden-import flask_socketio `
    --hidden-import gevent `
    --hidden-import geventwebsocket `
    backend_api_scaffold.py

  Write-Host "Build complete. See dist/OpryxxControlCenter.exe"
}
finally { Pop-Location }
