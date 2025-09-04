param(
  [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  $py = $null
  $venvPy = Join-Path $PWD '.venv\Scripts\python.exe'
  if (Test-Path $venvPy) { $py = $venvPy }
  if (-not $py) {
    $embedPy = Join-Path $PWD 'tools\python-embed\python.exe'
    if (Test-Path $embedPy) { $py = $embedPy }
  }
  if (-not $py) {
    $py = (Get-Command py -ErrorAction SilentlyContinue)?.Source
    if (-not $py) { $py = (Get-Command python -ErrorAction SilentlyContinue)?.Source }
  }
  if (-not $py) { throw 'Python not found. Install Python or fetch python-embed (tools/fetch_python_embed.ps1).' }

  if (-not $SkipInstall) {
    $pip = "`"$py`" -m pip"
    try { iex "$pip install --upgrade pip" } catch {}
    $wheels = Join-Path $PWD 'vendor\wheels'
    if (Test-Path $wheels) {
      iex "$pip install --no-index --find-links `"$wheels`" -r requirements.txt"
    } else {
      iex "$pip install -r requirements.txt"
    }
  }
  & $py 'backend_api_scaffold.py'
}
finally { Pop-Location }

