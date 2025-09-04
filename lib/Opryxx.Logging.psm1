function New-OpryxxRunContext {
    param([string]$Root)
    $runId = (Get-Date -Format 'yyyyMMdd_HHmmss')
    $dir = Join-Path $Root ("run_" + $runId)
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    return [pscustomobject]@{ Id=$runId; Root=$dir; LogPath=(Join-Path $dir 'events.json'); StatePath=(Join-Path $dir 'state.json'); PlanPath=(Join-Path $dir 'plan.json'); ResultPath=(Join-Path $dir 'result.json') }
}

function Open-OpryxxRunContext {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "Run context not found: $Path" }
    return [pscustomobject]@{ Id=(Split-Path $Path -Leaf); Root=$Path; LogPath=(Join-Path $Path 'events.json'); StatePath=(Join-Path $Path 'state.json'); PlanPath=(Join-Path $Path 'plan.json'); ResultPath=(Join-Path $Path 'result.json') }
}

function Add-OpryxxEvent {
    param($Ctx,[string]$Step,[string]$Status,$Details)
    $entry = @{timestamp=(Get-Date); step=$Step; status=$Status; details=$Details}
    $arr = @()
    if (Test-Path $Ctx.LogPath) { $cur = Get-Content $Ctx.LogPath -Raw | ConvertFrom-Json; if ($cur) { $arr=@($cur) } }
    $arr += $entry
    $arr | ConvertTo-Json -Depth 6 | Set-Content $Ctx.LogPath
    try {
        Import-Module (Join-Path $PSScriptRoot 'Opryxx.AI.psm1') -Force -ErrorAction SilentlyContinue
        if (Get-Command -Name Update-OpryxxKnowledge -ErrorAction SilentlyContinue) {
            Update-OpryxxKnowledge -Ctx $Ctx -Entry $entry | Out-Null
        }
    } catch {}
}

function Set-OpryxxState {
    param($Ctx,[string]$Key,$Value)
    $map = @{}
    if (Test-Path $Ctx.StatePath) { $obj = Get-Content $Ctx.StatePath -Raw | ConvertFrom-Json; if ($obj) { $obj.PSObject.Properties | % { $map[$_.Name]=$_.Value } } }
    $map[$Key] = $Value
    $map | ConvertTo-Json -Depth 6 | Set-Content $Ctx.StatePath
}

function Get-OpryxxState {
    param($Ctx)
    if (Test-Path $Ctx.StatePath) {
        $obj = Get-Content $Ctx.StatePath -Raw | ConvertFrom-Json
        if ($obj) {
            $map = @{}
            $obj.PSObject.Properties | ForEach-Object { $map[$_.Name] = $_.Value }
            return $map
        }
    }
    return @{}
}

function Write-OpryxxResult {
    param($Ctx,$Result)
    $Result | ConvertTo-Json -Depth 6 | Set-Content $Ctx.ResultPath
}

Export-ModuleMember -Function New-OpryxxRunContext, Open-OpryxxRunContext, Add-OpryxxEvent, Set-OpryxxState, Get-OpryxxState, Write-OpryxxResult
