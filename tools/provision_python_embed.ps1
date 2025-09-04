param(
  [string]$EmbedRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\python-embed'),
  [string]$Requirements = (Join-Path (Split-Path $PSScriptRoot -Parent) 'requirements.txt')
)

$ErrorActionPreference = 'Stop'
$py = Join-Path $EmbedRoot 'python.exe'
if (-not (Test-Path $py)) { throw "Embed Python not found at $py. Run tools/fetch_python_embed.ps1 first." }

# Ensure import site is enabled in ._pth
$pth = Get-ChildItem -Path $EmbedRoot -Filter "python*.pth" | Select-Object -First 1
if ($pth) {
  $content = Get-Content $pth -Raw
  if ($content -match '(?m)^[#]*import site') {
    $new = ($content -replace '(?m)^[#]*import site','import site')
    Set-Content -Path $pth.FullName -Value $new -NoNewline
  } else {
    Add-Content -Path $pth.FullName -Value "`nimport site`n"
  }
}

# Download get-pip.py
$gp = Join-Path $env:TEMP 'get-pip.py'
Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile $gp
& $py $gp

# Install requirements into embed
$pipExe = Join-Path $EmbedRoot 'Scripts\pip.exe'
if (Test-Path $pipExe) {
  & $pipExe install --upgrade pip
  & $pipExe install -r $Requirements
} else {
  & $py -m pip install --upgrade pip
  & $py -m pip install -r $Requirements
}
Write-Host "Embed Python provisioned with packages."
