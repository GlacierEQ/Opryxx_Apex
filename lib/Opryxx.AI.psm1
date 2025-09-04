function Get-OpryxxKnowledgePath {
    $dir = Join-Path $env:ProgramData 'Opryxx\AI'
    try { New-Item -ItemType Directory -Force -Path $dir | Out-Null } catch {}
    return (Join-Path $dir 'knowledge.json')
}

function Get-OpryxxKnowledge {
    $path = Get-OpryxxKnowledgePath
    if (Test-Path $path) {
        try { return (Get-Content $path -Raw | ConvertFrom-Json) } catch { }
    }
    return [pscustomobject]@{ steps=@{}; runs=0 }
}

function Save-OpryxxKnowledge {
    param($Obj)
    $path = Get-OpryxxKnowledgePath
    $Obj | ConvertTo-Json -Depth 6 | Set-Content $path
}

function Update-OpryxxKnowledge {
    param($Ctx,$Entry)
    $k = Get-OpryxxKnowledge
    $steps = @{}
    if ($k.steps) { $k.steps.PSObject.Properties | ForEach-Object { $steps[$_.Name] = $_.Value } }
    $name = [string]$Entry.step
    if (-not $steps.ContainsKey($name)) { $steps[$name] = @{ success=0; error=0; exit=0; missing=0; warning=0; other=0 } }
    $status = [string]$Entry.status
    switch -Regex ($status) {
        '^success$' { $steps[$name].success++ }
        '^error$'   { $steps[$name].error++ }
        '^exit_'    { $steps[$name].exit++ }
        '^missing$' { $steps[$name].missing++ }
        '^warning$' { $steps[$name].warning++ }
        default     { $steps[$name].other++ }
    }
    $k.steps = $steps
    Save-OpryxxKnowledge -Obj $k
    return $k
}

function Get-OpryxxAdjustments {
    param($Ctx,$Plan,[int]$CurrentIndex)
    $events = @()
    if (Test-Path $Ctx.LogPath) {
        $cur = Get-Content $Ctx.LogPath -Raw | ConvertFrom-Json
        if ($cur) { $events = @($cur) }
    }
    $recent = $events | Select-Object -Last 20
    $hasRepairFailure = $false
    foreach ($e in $recent) {
        if ($e.step -like 'Repair*' -or $e.step -like 'repair*') {
            if ($e.status -ne 'success') { $hasRepairFailure = $true; break }
        }
    }
    $toInsert = @()
    if ($hasRepairFailure) {
        $toInsert += @{ order=8; step='Network stack reset (pre-reboot)'; kind='repair.net.reset' }
        $toInsert += @{ order=9; step='Repair: DISM (pre-reboot)'; kind='repair.dism'; timeoutSec=3600 }
    }
    # Knowledge-driven additions: if many driver install errors historically, rescan devices early
    try {
        $k = Get-OpryxxKnowledge
        if ($k.steps -and $k.steps['Install driver INF'] -and $k.steps['Install driver INF'].error -ge 3) {
            $toInsert += @{ order=7; step='Pre-reboot device rescan'; kind='drivers.scan' }
        }
    } catch {}
    return ,$toInsert
}

Export-ModuleMember -Function Get-OpryxxAdjustments, Get-OpryxxKnowledge, Update-OpryxxKnowledge
