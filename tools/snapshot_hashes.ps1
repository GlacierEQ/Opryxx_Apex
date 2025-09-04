param(
  [string]$Out = (Join-Path (Split-Path $PSScriptRoot -Parent) 'code_hashes.json')
)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$includeExt = @('.ps1','.psm1','.psd1','.py','.js','.css','.json','.cmd','.bat','.html')
$exclude = @('run_','Backups','dist','build','vendor\\wheels','tools\\python-embed','node_modules')

function Should-Skip([string]$Path){
  foreach ($e in $exclude) { if ($Path -match [regex]::Escape($e)) { return $true } }
  return $false
}

$list = @()
$rootWithSep = if ($root.EndsWith('\')) { $root } else { $root + '\\' }
$rootUri = New-Object System.Uri($rootWithSep)
Get-ChildItem -Recurse -File -Path $root | Where-Object { $includeExt -contains $_.Extension } | ForEach-Object {
  $full = $_.FullName
  $rel = $full
  if (Should-Skip $rel) { return }
  $h = (Get-FileHash -Algorithm SHA256 -Path $full).Hash
  $list += [pscustomobject]@{ path=$rel; sha256=$h }
}
$list | ConvertTo-Json -Depth 4 | Set-Content $Out
Write-Host ("Hash snapshot written: {0} files -> {1}" -f ($list|Measure-Object).Count, $Out)
