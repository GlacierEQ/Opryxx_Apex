param(
  [string]$Version = '3.11.9',
  [string]$Dest = (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\python-embed')
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$zip = Join-Path $env:TEMP ("python-" + $Version + "-embed-amd64.zip")
$uri = "https://www.python.org/ftp/python/$Version/python-$Version-embed-amd64.zip"
Write-Host ("Downloading Python embed {0}..." -f $Version)
Invoke-WebRequest -Uri $uri -OutFile $zip
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $Dest)
Remove-Item $zip -Force -ErrorAction SilentlyContinue
$pth = Get-ChildItem -Path $Dest -Filter "python*.pth" | Select-Object -First 1
if ($pth) {
  $content = Get-Content $pth -Raw
  if ($content -match '(?m)^[#]*import site') {
    $new = ($content -replace '(?m)^[#]*import site','import site')
    Set-Content -Path $pth.FullName -Value $new -NoNewline
  } else {
    Add-Content -Path $pth.FullName -Value "`nimport site`n"
  }
}
Write-Host "Python embed ready at: $Dest"
