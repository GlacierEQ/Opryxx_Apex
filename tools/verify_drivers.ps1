param(
  [string]$Manifest = (Join-Path (Split-Path $PSScriptRoot -Parent) 'manifest.json')
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Manifest)) { throw "Manifest not found: $Manifest" }
$m = Get-Content $Manifest -Raw | ConvertFrom-Json

function Get-ModelDriverPaths {
  param($Manifest)
  $paths = @()
  if ($Manifest.models) {
    foreach ($mo in $Manifest.models) {
      foreach ($st in $mo.steps) {
        if ($st.kind -eq 'drivers.inf' -and $st.path) { $paths += $st.path }
      }
    }
  }
  if ($Manifest.resources) {
    foreach ($r in $Manifest.resources) {
      if ($r.type -eq 'driver-folder' -and $r.path) { $paths += $r.path }
    }
  }
  return ($paths | Sort-Object -Unique)
}

$repo = Split-Path $PSScriptRoot -Parent
$targets = Get-ModelDriverPaths -Manifest $m | ForEach-Object {
  if ([System.IO.Path]::IsPathRooted($_)) { $_ } else { Join-Path $repo $_ }
} | Where-Object { Test-Path $_ }

$sum = @()
foreach ($p in $targets) {
  $files = Get-ChildItem -Recurse -File -Path $p -ErrorAction SilentlyContinue | Where-Object { $_.Extension -in '.cat','.sys','.exe' }
  foreach ($f in $files) {
    $sig = $null
    try { $sig = Get-AuthenticodeSignature -FilePath $f.FullName } catch {}
    $status = 'Unknown'
    $signer = $null
    $thumb = $null
    if ($sig) {
      try { if ($sig.Status) { $status = [string]$sig.Status } } catch {}
      try { if ($sig.SignerCertificate -and $sig.SignerCertificate.Subject) { $signer = [string]$sig.SignerCertificate.Subject } } catch {}
      try { if ($sig.SignerCertificate -and $sig.SignerCertificate.Thumbprint) { $thumb = [string]$sig.SignerCertificate.Thumbprint } } catch {}
    }
    $sum += [pscustomobject]@{
      path = $f.FullName
      status = $status
      signer = $signer
      thumbprint = $thumb
    }
  }
}

$out = [pscustomobject]@{
  scanned = ($sum | Measure-Object).Count
  valid = ($sum | Where-Object { $_.status -eq 'Valid' } | Measure-Object).Count
  notSigned = ($sum | Where-Object { $_.status -eq 'NotSigned' } | Measure-Object).Count
  unknown = ($sum | Where-Object { $_.status -notin @('Valid','NotSigned') } | Measure-Object).Count
  details = $sum
}

$dest = Join-Path $repo 'driver_integrity.json'
$out | ConvertTo-Json -Depth 6 | Set-Content $dest
Write-Host ("Scanned: {0}, Valid: {1}, NotSigned: {2}, Other: {3}" -f $out.scanned,$out.valid,$out.notSigned,$out.unknown)
Write-Host ("Report written: {0}" -f $dest)
