param(
  [string]$Snapshot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'code_hashes.json')
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Snapshot)) { throw "Snapshot not found: $Snapshot (run snapshot_hashes.ps1 first)" }
$root = Split-Path $PSScriptRoot -Parent
$data = Get-Content $Snapshot -Raw | ConvertFrom-Json

$missing = @()
$mismatch = @()
$ok = 0
foreach ($e in $data) {
  $p = if ([System.IO.Path]::IsPathRooted([string]$e.path)) { [string]$e.path } else { (Join-Path $root ([string]$e.path)) }
  if (-not (Test-Path $p)) { $missing += $e.path; continue }
  $cur = (Get-FileHash -Algorithm SHA256 -Path $p).Hash
  if ($cur -ne $e.sha256) { $mismatch += [pscustomobject]@{ path=$e.path; expected=$e.sha256; actual=$cur } } else { $ok++ }
}

$report = [pscustomobject]@{ ok=$ok; missing=$missing; mismatch=$mismatch }
$out = Join-Path $root 'code_hashes_report.json'
$report | ConvertTo-Json -Depth 6 | Set-Content $out
Write-Host ("Verified OK: {0}, Missing: {1}, Mismatch: {2}" -f $ok, $missing.Count, $mismatch.Count)
Write-Host ("Report: {0}" -f $out)
