function Invoke-OpryxxWindowsUpdateReset {
    Write-Host '[WU Reset] Stopping services...'
    $svcs = 'wuauserv','bits','cryptsvc'
    foreach ($s in $svcs) { try { Stop-Service -Name $s -Force -ErrorAction SilentlyContinue } catch {} }
    $sd = "$env:SystemRoot\SoftwareDistribution"
    $cr = "$env:SystemRoot\System32\catroot2"
    try { Rename-Item -Path $sd -NewName ('SoftwareDistribution.bak_' + (Get-Date -Format 'yyyyMMdd_HHmmss')) -ErrorAction SilentlyContinue } catch {}
    try { Rename-Item -Path $cr -NewName ('catroot2.bak_' + (Get-Date -Format 'yyyyMMdd_HHmmss')) -ErrorAction SilentlyContinue } catch {}
    Write-Host '[WU Reset] Starting services...'
    foreach ($s in $svcs) { try { Start-Service -Name $s -ErrorAction SilentlyContinue } catch {} }
}

function Invoke-OpryxxNetworkReset {
    Write-Host '[Net Reset] Winsock reset'
    try { netsh winsock reset | Out-Host } catch {}
    Write-Host '[Net Reset] TCP/IP reset'
    try { netsh int ip reset | Out-Host } catch {}
    Write-Host '[Net Reset] DNS flush/register'
    try { ipconfig /flushdns | Out-Host } catch {}
    try { ipconfig /registerdns | Out-Host } catch {}
}

function Get-OpryxxDismSource {
    $candidates = @()
    # Search typical SxS paths on available drives
    Get-PSDrive -PSProvider FileSystem | ForEach-Object {
        $dl = $_.Name + ':\\'
        $paths = @(
            (Join-Path $dl 'sources\sxs'),
            (Join-Path $dl 'Windows\WinSxS')
        )
        foreach ($p in $paths) { if (Test-Path $p) { $candidates += $p } }
    }
    # Return unique, prefer sxs-like
    return ($candidates | Sort-Object -Unique)
}

function New-OpryxxRestorePoint {
    param([string]$Description = 'Opryxx Pre-Repair')
    try { Checkpoint-Computer -Description $Description -RestorePointType 'MODIFY_SETTINGS' -ErrorAction Stop } catch {}
}

function Invoke-OpryxxBootRepair {
    param([switch]$Aggressive)
    try {
        $backup = "C:\\BCD_Backup_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.bak'
        bcdedit /export $backup | Out-Null
        Write-Host ("[BootRepair] BCD exported to {0}" -f $backup)
    } catch { Write-Host "[BootRepair] BCD backup failed: $($_.Exception.Message)" }
    if ($Aggressive) {
        try { bootrec /FixMbr | Out-Host } catch {}
        try { bootrec /FixBoot | Out-Host } catch {}
        try { bootrec /RebuildBcd | Out-Host } catch {}
    }
}

function Invoke-OpryxxBcdRebuildSafe {
    param([switch]$Aggressive)
    $out = @()
    $backup = $null
    try {
        $backup = "C:\\BCD_Backup_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.bak'
        bcdedit /export $backup | Out-Null
        $out += "[BCD] Exported to $backup"
    } catch { $out += "[BCD] Export failed: $($_.Exception.Message)" }
    try {
        $out += '[BCD] Running bootrec /RebuildBcd'
        $res = (bootrec /RebuildBcd) 2>&1 | Out-String
        $out += $res.Trim()
    } catch { $out += "[BCD] Rebuild failed: $($_.Exception.Message)" }
    if ($Aggressive) {
        try { $out += '[BCD] Running bootrec /FixMbr'; bootrec /FixMbr | Out-Null } catch { $out += "[BCD] FixMbr failed: $($_.Exception.Message)" }
        try { $out += '[BCD] Running bootrec /FixBoot'; bootrec /FixBoot | Out-Null } catch { $out += "[BCD] FixBoot failed: $($_.Exception.Message)" }
    }
    return [pscustomobject]@{ ok=$true; backup=$backup; log=$out }
}

Export-ModuleMember -Function Invoke-OpryxxWindowsUpdateReset, Invoke-OpryxxNetworkReset, Get-OpryxxDismSource, New-OpryxxRestorePoint, Invoke-OpryxxBootRepair, Invoke-OpryxxBcdRebuildSafe
function Get-OpryxxBootDiagnostics {
    $result = [pscustomobject]@{
        osRoot = $env:SystemRoot
        systemDrive = $env:SystemDrive
        bcd = @{ ok=$false; exported=$null; defaultIdentifier=$null; entries=$null }
        winre = @{ enabled=$null; location=$null; image=$null }
        files = @{
            winload = Test-Path (Join-Path $env:SystemRoot 'System32\\winload.efi')
            winresume = Test-Path (Join-Path $env:SystemRoot 'System32\\winresume.efi')
            bcdStore = Test-Path 'C:\\Boot\\BCD'
        }
        esp = @{ present=$false; driveLetter=$null }
        secureBoot = $null
    }
    try {
        $bcd = (bcdedit /enum) 2>$null | Out-String
        if ($bcd) {
            $result.bcd.ok = $true
            $def = ($bcd -split "`n") | Where-Object { $_ -match 'default\s+\{[0-9a-fA-F\-]+\}' } | Select-Object -First 1
            if ($def) { $result.bcd.defaultIdentifier = ($def -replace '.*\{','{' ).Trim() }
        }
    } catch {}
    try {
        $re = (reagentc /info) 2>&1 | Out-String
        if ($re) {
            $lines = $re -split "`n"
            foreach ($ln in $lines) {
                if ($ln -match 'Windows RE status\s*:\s*(\w+)') { $result.winre.enabled = ($matches[1] -eq 'Enabled') }
                if ($ln -match 'Windows RE location\s*:\s*(.+)$') { $result.winre.location = $matches[1].Trim() }
                if ($ln -match 'Recovery image location\s*:\s*(.+)$') { $result.winre.image = $matches[1].Trim() }
            }
        }
    } catch {}
    try {
        $espPart = Get-Partition -ErrorAction SilentlyContinue | Where-Object { $_.GptType -match 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b' }
        if ($espPart) {
            $result.esp.present = $true
            $vol = Get-Volume -Partition $espPart -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($vol) { $result.esp.driveLetter = $vol.DriveLetter }
        }
    } catch {}
    try { $result.secureBoot = (Confirm-SecureBootUEFI -ErrorAction Stop) } catch { $result.secureBoot = $null }
    return $result
}

function Enable-OpryxxWinRE {
    try {
        $out = (reagentc /enable) 2>&1 | Out-String
        return [pscustomobject]@{ ok=$true; output=$out }
    } catch { return [pscustomobject]@{ ok=$false; error=$_.Exception.Message } }
}

Export-ModuleMember -Function Get-OpryxxBootDiagnostics, Enable-OpryxxWinRE -Alias *
function Test-OpryxxBootFailure {
    [CmdletBinding()]
    param([int]$LookbackHours = 12)
    $diag = Get-OpryxxBootDiagnostics
    $os = Get-CimInstance Win32_OperatingSystem
    $bootTime = try { $os.LastBootUpTime } catch { Get-Date }.ToUniversalTime()
    $since = (Get-Date).AddHours(-[math]::Abs($LookbackHours))
    $events = @()
    try {
        $events = Get-WinEvent -FilterHashtable @{ LogName='System'; StartTime=$since } -ErrorAction SilentlyContinue | Where-Object { $_.Id -in 41, 6008 }
    } catch {}
    $unclean = $events | Where-Object { $_.TimeCreated -gt $bootTime }
    $bcdOk = ($diag.bcd -and $diag.bcd.ok)
    $espOk = ($diag.esp -and $diag.esp.present)
    $filesOk = ($diag.files -and $diag.files.winload -and $diag.files.winresume)
    $winreDisabled = ($diag.winre -and $diag.winre.enabled -eq $false)
    $score = 0
    if (-not $bcdOk) { $score += 2 }
    if (-not $espOk) { $score += 2 }
    if (-not $filesOk) { $score += 2 }
    if ($unclean) { $score += 1 }
    if ($winreDisabled) { $score += 1 }
    $fail = $score -ge 2
    return [pscustomobject]@{ bootFailure=$fail; score=$score; unclean=($unclean|Measure-Object).Count; diag=$diag }
}

function Invoke-OpryxxFixBootCritical {
    [CmdletBinding()]
    param([switch]$Aggressive)
    $log = @()
    try {
        $diag = Get-OpryxxBootDiagnostics
        if ($diag.winre -and $diag.winre.enabled -ne $true) { $null = Enable-OpryxxWinRE; $log += '[AutoRepair] WinRE enabled' }
    } catch { $log += "[AutoRepair] WinRE enable failed: $($_.Exception.Message)" }
    try { $log += '[AutoRepair] bootrec /FixMbr'; bootrec /FixMbr | Out-Null } catch { $log += "[AutoRepair] FixMbr failed: $($_.Exception.Message)" }
    try { $log += '[AutoRepair] bootrec /FixBoot'; bootrec /FixBoot | Out-Null } catch { $log += "[AutoRepair] FixBoot failed: $($_.Exception.Message)" }
    if ($Aggressive) {
        try { $log += '[AutoRepair] bootrec /RebuildBcd'; bootrec /RebuildBcd | Out-Null } catch { $log += "[AutoRepair] RebuildBcd failed: $($_.Exception.Message)" }
    }
    return [pscustomobject]@{ ok=$true; log=$log }
}

function Register-OpryxxBootAutoRepair {
    [CmdletBinding()]
    param([string]$RepoRoot)
    $base = Join-Path $env:ProgramData 'Opryxx'
    $modDir = Join-Path $base 'Modules'
    $scriptPath = Join-Path $base 'AutoBootRepair.ps1'
    try { New-Item -ItemType Directory -Force -Path $modDir | Out-Null } catch {}
    $src = if ($RepoRoot) { Join-Path (Join-Path $RepoRoot 'lib') 'Opryxx.Repair.psm1' } else { Join-Path $PSScriptRoot 'Opryxx.Repair.psm1' }
    if (Test-Path $src) { Copy-Item -Force -Path $src -Destination (Join-Path $modDir 'Opryxx.Repair.psm1') }
    @"
try {
  Import-Module '$modDir\Opryxx.Repair.psm1' -Force
  $res = Test-OpryxxBootFailure
  if ($res.bootFailure) {
    $fix = Invoke-OpryxxFixBootCritical -Aggressive
    try {
      $logDir = Join-Path $env:ProgramData 'Opryxx\Logs'
      New-Item -ItemType Directory -Force -Path $logDir | Out-Null
      ('$((Get-Date).ToString('u'))`r`n' + ($res | ConvertTo-Json -Depth 6) + '`r`n' + ($fix | ConvertTo-Json -Depth 6)) | Set-Content (Join-Path $logDir ('AutoBootRepair_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log'))
    } catch {}
  }
} catch {}
"@ | Set-Content -Path $scriptPath
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay (New-TimeSpan -Minutes 1)
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -RunLevel Highest
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden)
    try { Register-ScheduledTask -TaskName 'OpryxxAutoBootRepair' -InputObject $task -Force | Out-Null } catch {}
    return [pscustomobject]@{ ok=$true; script=$scriptPath; modulePath=(Join-Path $modDir 'Opryxx.Repair.psm1') }
}

function Get-OpryxxBootAutoRepair {
    try { $t = Get-ScheduledTask -TaskName 'OpryxxAutoBootRepair' -ErrorAction Stop; return [pscustomobject]@{ installed=$true; state=$t.State } } catch { return [pscustomobject]@{ installed=$false } }
}

Export-ModuleMember -Function Test-OpryxxBootFailure, Invoke-OpryxxFixBootCritical, Register-OpryxxBootAutoRepair, Get-OpryxxBootAutoRepair
