function Get-OpryxxManifest {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "Manifest not found: $Path" }
    $raw = Get-Content $Path -Raw | ConvertFrom-Json
    return $raw
}

function Resolve-OpryxxModel {
    param(
        $Manifest,
        [string]$ModelString,
        [string]$Manufacturer
    )
    $candidates = @()
    # v2 models
    if ($Manifest.models) {
        foreach ($m in $Manifest.models) {
            $aliases = @($m.name) + @($m.aliases)
            foreach ($a in $aliases) {
                if (-not [string]::IsNullOrWhiteSpace($a)) {
                    if ($ModelString -like "*${a}*") { $candidates += @{ model=$m.name } }
                }
            }
        }
    }
    # v1 resources
    if ($Manifest.resources) {
        foreach ($res in $Manifest.resources) {
            if ($res.model) {
                $aliases = @($res.model) + @($res.aliases)
                foreach ($a in $aliases) {
                    if (-not [string]::IsNullOrWhiteSpace($a)) {
                        if ($ModelString -like "*${a}*") { $candidates += $res }
                    }
                }
            }
        }
    }
    if ($candidates.Count -gt 0) { return ($candidates | Select-Object -First 1).model }
    if ($Manufacturer -match 'MSI') { return 'MSI_Summit_E16_AI_Studio_A1VFTG' }
    if ($Manufacturer -match 'Dell') { return 'Inspiron_2in1_7550' }
    return $null
}

function New-OpryxxPlan {
    param(
        $Manifest,
        [string]$Model,
        [string]$RepoRoot
    )
    $plan = @()
    $plan += @{ order=1; step='Detect hardware and OS'; kind='detect' }
    $plan += @{ order=2; step='Create restore point'; kind='repair.restore_point' }
    # Baseline repairs applicable to all models
    $plan += @{ order=3; step='Windows Update reset'; kind='repair.wu.reset' }
    $plan += @{ order=4; step='Network stack reset'; kind='repair.net.reset' }
    $plan += @{ order=5; step='Repair: SFC'; kind='repair.sfc' }
    $plan += @{ order=6; step='Repair: DISM'; kind='repair.dism' }
    # Gather model object
    $modelObj = $null
    if ($Manifest.models) { $modelObj = $Manifest.models | Where-Object { $_.name -eq $Model } | Select-Object -First 1 }
    if (-not $modelObj) { $modelObj = $Manifest.resources | Where-Object { $_.model -eq $Model } | Select-Object -First 1 }

    if ($modelObj -and $modelObj.steps) {
        # v2: expand declared steps
        foreach ($s in $modelObj.steps) {
            $kind = $s.kind
            if ($kind -eq 'drivers.inf') {
                # Expand wildcard or folder to concrete INF paths
                $paths = @()
                if ($s.path) {
                    $p = if ([System.IO.Path]::IsPathRooted($s.path)) { $s.path } else { Join-Path $RepoRoot $s.path }
                    if (Test-Path $p -PathType Container) {
                        # Add a verification step for driver signatures
                        $plan += @{ order=9; step='Verify driver signatures'; kind='drivers.verify'; path=$p }
                        $paths = Get-ChildItem -Recurse -File -Filter *.inf $p -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
                    } else {
                        $dir = Split-Path $p -Parent
                        $pattern = Split-Path $p -Leaf
                        if (Test-Path $dir) { $paths = Get-ChildItem -Recurse -File -Path $dir -Filter $pattern -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName }
                    }
                } else {
                    $driverFolder = if ($modelObj.path) { $modelObj.path } else { "drivers/$Model/" }
                    $p = Join-Path $RepoRoot $driverFolder
                    if (Test-Path $p) {
                        $plan += @{ order=9; step='Verify driver signatures'; kind='drivers.verify'; path=$p }
                        $paths = Get-ChildItem -Recurse -File -Filter *.inf $p | Select-Object -ExpandProperty FullName
                    }
                }
                foreach ($fp in $paths) {
                    $plan += @{ order=10; step='Install driver INF'; kind='drivers.inf'; path=$fp }
                }
                # Refresh device detection after installs
                $plan += @{ order=11; step='Scan devices'; kind='drivers.scan' }
            } else {
                $obj = @{ order=20; step=$s.step; kind=$kind }
                if ($s.path) {
                    if ([System.IO.Path]::IsPathRooted($s.path)) { $obj.path = $s.path }
                    else { $obj.path = (Join-Path $RepoRoot $s.path) }
                }
                if ($s.args) { $obj.args = $s.args }
                if ($s.sha256) { $obj.sha256 = $s.sha256 }
                if ($s.timeoutSec) { $obj.timeoutSec = [int]$s.timeoutSec }
                if ($s.retries) { $obj.retries = [int]$s.retries }
                if ($s.reboot) { $obj.reboot = [bool]$s.reboot }
                $plan += $obj
            }
        }
    } else {
        # v1 default expansion
        $driverFolder = if ($modelObj -and $modelObj.path) { $modelObj.path } else { "drivers/$Model/" }
        $driverAbs = Join-Path $RepoRoot $driverFolder
        $plan += @{ order=3; step='Backup user data (stub)'; kind='backup.stub' }
        if (Test-Path $driverAbs) {
            $plan += @{ order=9; step='Verify driver signatures'; kind='drivers.verify'; path=$driverAbs }
            $inf = Get-ChildItem -Recurse -File -Filter *.inf $driverAbs -ErrorAction SilentlyContinue
            foreach ($i in $inf) {
                $plan += @{ order=10; step='Install driver INF'; kind='drivers.inf'; path=$i.FullName }
            }
            $plan += @{ order=11; step='Scan devices'; kind='drivers.scan' }
        }
    }
    $plan += @{ order=99; step='Finalize'; kind='finalize' }
    return $plan
}

Export-ModuleMember -Function Get-OpryxxManifest, Resolve-OpryxxModel, New-OpryxxPlan
