function Test-FileHash {
    param([string]$Path,[string]$Sha256)
    if ([string]::IsNullOrWhiteSpace($Sha256)) { return $true }
    if (-not (Test-Path $Path)) { return $false }
    $actual = (Get-FileHash -Algorithm SHA256 -Path $Path).Hash
    return ($actual -ieq $Sha256)
}

function Resolve-CanonicalPath {
    param([string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-PathWithin {
    param([string]$Path,[string]$Root)
    $full = Resolve-CanonicalPath -Path $Path
    $root = Resolve-CanonicalPath -Path $Root
    return $full.StartsWith($root,[System.StringComparison]::OrdinalIgnoreCase)
}

Export-ModuleMember -Function Test-FileHash, Resolve-CanonicalPath, Test-PathWithin

