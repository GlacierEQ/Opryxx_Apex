function Invoke-OpryxxPlan {
    param(
        $Plan,
        [switch]$DryRun,
        $Ctx,
        [string]$RepoRoot,
        [string[]]$AllowedRoots,
        [int]$StartIndex = 0,
        [string]$ApexPath
    )
    $allowed = @()
    if ($RepoRoot) { $allowed += $RepoRoot }
    if ($AllowedRoots) { $allowed += $AllowedRoots }
    Import-Module (Join-Path $PSScriptRoot 'Opryxx.Security.psm1') -Force
    Import-Module (Join-Path $PSScriptRoot 'Opryxx.Repair.psm1') -Force -ErrorAction SilentlyContinue
    Import-Module (Join-Path $PSScriptRoot 'Opryxx.Logging.psm1') -Force
    Import-Module (Join-Path $PSScriptRoot 'Opryxx.Resume.psm1') -Force -ErrorAction SilentlyContinue
    Import-Module (Join-Path $PSScriptRoot 'Opryxx.AI.psm1') -Force -ErrorAction SilentlyContinue

    function Invoke-WithTimeout {
        param([string]$File,[string[]]$Args,[int]$TimeoutSec=900)
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $File
        $psi.Arguments = ($Args -join ' ')
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $p = New-Object System.Diagnostics.Process
        $p.StartInfo = $psi
        [void]$p.Start()
        if (-not $p.WaitForExit($TimeoutSec * 1000)) {
            try { $p.Kill() } catch {}
            return 408 # timeout
        }
        return $p.ExitCode
    }

    function Invoke-WithProgress {
        param(
            [string]$File,
            [string[]]$Args,
            [int]$TimeoutSec=3600,
            $Ctx,
            [string]$StepName,
            [regex[]]$Patterns
        )
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $File
        $psi.Arguments = ($Args -join ' ')
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $p = New-Object System.Diagnostics.Process
        $p.StartInfo = $psi
        $null = $p.Start()
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $out = New-Object System.Text.StringBuilder
        $err = New-Object System.Text.StringBuilder
        $lastPct = -1
        $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSec)
        while (-not $p.HasExited) {
            while (-not $p.StandardOutput.EndOfStream) {
                $line = $p.StandardOutput.ReadLine()
                $null = $out.AppendLine($line)
                $pct = $null
                if ($Patterns -and $Patterns.Count -gt 0) {
                    foreach ($rx in $Patterns) {
                        $m = $rx.Match($line)
                        if ($m.Success) {
                            $val = $m.Groups[1].Value
                            if (-not $val) { continue }
                            try { $pct = [double]$val } catch { $pct = $null }
                            if ($pct -ge 0 -and $pct -le 100) { break }
                        }
                    }
                } else {
                    $m = [regex]::Match($line,'(\d{1,3})\s*%')
                    if ($m.Success) { $pct = [double]$m.Groups[1].Value }
                }
                if ($pct -ne $null) {
                    $ip = [math]::Round($pct)
                    if ($ip -ne $lastPct) {
                        $lastPct = $ip
                        Add-OpryxxEvent -Ctx $Ctx -Step $StepName -Status 'running' -Details @{ progress=$ip }
                    }
                }
            }
            while (-not $p.StandardError.EndOfStream) { $null = $err.AppendLine($p.StandardError.ReadLine()) }
            Start-Sleep -Milliseconds 100
            if ([DateTime]::UtcNow -gt $deadline) {
                try { $p.Kill() } catch {}
                return @{ exitCode=408; stdout=$out.ToString(); stderr=$err.ToString() }
            }
        }
        # Drain remaining
        while (-not $p.StandardOutput.EndOfStream) { $null = $out.AppendLine($p.StandardOutput.ReadLine()) }
        while (-not $p.StandardError.EndOfStream) { $null = $err.AppendLine($p.StandardError.ReadLine()) }
        return @{ exitCode=$p.ExitCode; stdout=$out.ToString(); stderr=$err.ToString() }
    }
    # Cache hardware IDs for optional INF filtering
    $hwIds = $null
    if ($env:OPRYXX_FILTER_INF -eq '1') {
        try {
            $hwIds = (Get-PnpDevice -PresentOnly -ErrorAction Stop | Select-Object -ExpandProperty InstanceId) + (Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | ForEach-Object { $_.HardwareID } | Where-Object { $_ })
            $hwIds = $hwIds | ForEach-Object { $_.ToLowerInvariant() } | Sort-Object -Unique
        } catch {
            $hwIds = @()
        }
    }

    # Work on a mutable plan list
    $planList = New-Object System.Collections.ArrayList
    foreach ($s in $Plan) { [void]$planList.Add($s) }
    # Determine starting index
    $i = [int]$StartIndex
    $state = Get-OpryxxState -Ctx $Ctx
    if ($state.ContainsKey('index') -and ($StartIndex -eq 0)) { $i = [int]$state['index'] }
    $total = $planList.Count
    for (; $i -lt $planList.Count; $i++) {
        $step = $planList[$i]
        $kind = $step.kind
        $name = $step.step
        Set-OpryxxState -Ctx $Ctx -Key 'index' -Value $i
        $t0 = Get-Date
        if ($DryRun) {
            Write-Host ("[DRY RUN] {0}" -f $name)
            continue
        }
        # Emit running event and overall progress hint
        Add-OpryxxEvent -Ctx $Ctx -Step $name -Status 'running' -Details @{ index=($i+1); total=$total; kind=$kind; progress=0 }
        Add-OpryxxEvent -Ctx $Ctx -Step 'overall' -Status 'progress' -Details @{ index=$i; total=$total; percent=[math]::Round(($i*100.0)/[math]::Max($total,1),0) }
        $status = 'success'
        $details = @{}
        try {
        switch ($kind) {
            'detect' { Write-Host 'Detecting environment...'; }
            'backup.stub' { Write-Host 'Backup (stub)'; }
            'repair.wu.reset' { Invoke-OpryxxWindowsUpdateReset }
            'repair.restore_point' { New-OpryxxRestorePoint }
            'repair.net.reset' { Invoke-OpryxxNetworkReset }
            'repair.sfc' {
                $pat = [regex]'Verification\s+(\d{1,3})%'
                $res = Invoke-WithProgress -File 'sfc.exe' -Args @('/scannow') -TimeoutSec 5400 -Ctx $Ctx -StepName $name -Patterns @($pat)
                if ($res.exitCode -ne 0) { $status = "exit_$($res.exitCode)" }
                $details.exitCode = $res.exitCode
            }
            'repair.dism' {
                $srcs = Get-OpryxxDismSource -ErrorAction SilentlyContinue
                $args = @('/Online','/Cleanup-Image','/RestoreHealth')
                if ($srcs -and $srcs.Count -gt 0) { $args += "/Source:$($srcs -join ';')" }
                $to = 5400; if ($step -and $step.PSObject.Properties['timeoutSec']) { $to = [int]$step.timeoutSec }
                $pat = [regex]'(\d{1,3})\.?\d*%'
                $res = Invoke-WithProgress -File 'dism.exe' -Args $args -TimeoutSec $to -Ctx $Ctx -StepName $name -Patterns @($pat)
                if ($res.exitCode -ne 0) { $status = "exit_$($res.exitCode)" }
                $details.exitCode = $res.exitCode
            }
            'drivers.verify' {
                $path = $step.path
                $ok = 0; $bad = 0; $total = 0
                if (Test-Path $path) {
                    $targets = @()
                    if (Test-Path $path -PathType Container) {
                        $targets = Get-ChildItem -Recurse -File -Include *.cat,*.sys,*.exe -Path $path -ErrorAction SilentlyContinue
                    } else {
                        $targets = @(Get-Item -LiteralPath $path -ErrorAction SilentlyContinue)
                    }
                    foreach ($t in $targets) {
                        $total++
                        try {
                            $sig = Get-AuthenticodeSignature -FilePath $t.FullName -ErrorAction Stop
                            if ($sig.Status -eq 'Valid') { $ok++ } else { $bad++ }
                        } catch { $bad++ }
                    }
                } else { $status='missing' }
                $details.okCount = $ok; $details.badCount = $bad; $details.total = $total; $details.path = $path
                if ($bad -gt 0 -and $status -eq 'success') { $status = 'warning' }
            }
            'drivers.inf' {
                $inf = $step.path
                if (Test-Path $inf) {
                    # Guardrails: ensure path is within allowed roots
                    $ok = $false
                    foreach ($root in $allowed) { if (Test-PathWithin -Path $inf -Root $root) { $ok = $true; break } }
                    if (-not $ok) { Write-Host ("Blocked driver path (outside allowed roots): {0}" -f $inf); break }
                    if ($hwIds -and $hwIds.Count -gt 0) {
                        try {
                            $content = (Get-Content -Raw -ErrorAction Stop -Path $inf).ToLowerInvariant()
                            $match = $false
                            foreach ($id in $hwIds) { if ($content.Contains($id)) { $match = $true; break } }
                            if (-not $match) { Write-Host ("Skipping INF (no PNPID match): {0}" -f $inf); $status='skipped'; break }
                        } catch {}
                    }
                    # Quick INF metadata
                    try {
                        $lines = Get-Content -Raw -Path $inf
                        $prov = ($lines -split "`n" | Where-Object { $_ -match '^\s*Provider' } | Select-Object -First 1)
                        if ($prov) { $details.provider = ($prov -replace '.*=','').Trim() }
                        $cls = ($lines -split "`n" | Where-Object { $_ -match '^\s*Class\s*=' } | Select-Object -First 1)
                        if ($cls) { $details.class = ($cls -replace '.*=','').Trim() }
                        $ver = ($lines -split "`n" | Where-Object { $_ -match '^\s*DriverVer\s*=' } | Select-Object -First 1)
                        if ($ver) { $details.driverVer = ($ver -replace '.*=','').Trim() }
                    } catch {}
                    Write-Host ("Installing driver: {0}" -f $inf)
                    $to = 900; if ($step -and $step.PSObject.Properties['timeoutSec']) { $to = [int]$step.timeoutSec }
                    $code = Invoke-WithTimeout -File 'pnputil.exe' -Args @('/add-driver',"$inf",'/install') -TimeoutSec $to
                    if ($code -ne 0) { $status = "exit_$code" }
                    $details.exitCode = $code; $details.inf = $inf
                } else {
                    Write-Host ("INF missing: {0}" -f $inf)
                    $status = 'missing'
                }
            }
            'drivers.scan' {
                Write-Host 'Scanning for device changes (pnputil)'
                $code = Invoke-WithTimeout -File 'pnputil.exe' -Args @('/scan-devices') -TimeoutSec 300
                if ($code -ne 0) { $status = "exit_$code" }
                $details.exitCode = $code
            }
            'repair.boot' {
                $aggr = $false; if ($step -and $step.PSObject.Properties['args']) { if ($step.args -contains 'Aggressive') { $aggr = $true } }
                Invoke-OpryxxBootRepair -Aggressive:$aggr
            }
            'exe' {
                $path = $step.path; $args = @(); if ($step.args) { $args = $step.args }
                if (-not (Test-Path $path)) { Write-Host ("EXE missing: {0}" -f $path); $status='missing'; break }
                $ok = $false; foreach ($root in $allowed) { if (Test-PathWithin -Path $path -Root $root) { $ok=$true; break } }
                if (-not $ok) { Write-Host ("Blocked EXE: {0}" -f $path); $status='blocked'; break }
                if ($step.sha256) { if (-not (Test-FileHash -Path $path -Sha256 $step.sha256)) { Write-Host 'Hash mismatch'; $status='hash_mismatch'; break } }
                $to = 1800; if ($step -and $step.PSObject.Properties['timeoutSec']) { $to = [int]$step.timeoutSec }
                $code = Invoke-WithTimeout -File $path -Args $args -TimeoutSec $to
                if ($code -ne 0) { $status = "exit_$code" }
                $details.exitCode = $code
            }
            'msi' {
                $path = $step.path; $args = @(); if ($step.args) { $args = $step.args }
                if (-not (Test-Path $path)) { Write-Host ("MSI missing: {0}" -f $path); $status='missing'; break }
                $ok = $false; foreach ($root in $allowed) { if (Test-PathWithin -Path $path -Root $root) { $ok=$true; break } }
                if (-not $ok) { Write-Host ("Blocked MSI: {0}" -f $path); $status='blocked'; break }
                if ($step.sha256) { if (-not (Test-FileHash -Path $path -Sha256 $step.sha256)) { Write-Host 'Hash mismatch'; $status='hash_mismatch'; break } }
                $msiArgs = @('/i',"$path",'/qn') + $args
                $to = 1800; if ($step -and $step.PSObject.Properties['timeoutSec']) { $to = [int]$step.timeoutSec }
                $code = Invoke-WithTimeout -File 'msiexec.exe' -Args $msiArgs -TimeoutSec $to
                if ($code -ne 0) { $status = "exit_$code" }
                $details.exitCode = $code
            }
            'script' {
                $path = $step.path; $args = @(); if ($step.args) { $args = $step.args }
                if (-not (Test-Path $path)) { Write-Host ("Script missing: {0}" -f $path); $status='missing'; break }
                $ok = $false; foreach ($root in $allowed) { if (Test-PathWithin -Path $path -Root $root) { $ok=$true; break } }
                if (-not $ok) { Write-Host ("Blocked script: {0}" -f $path); $status='blocked'; break }
                $to = 1800; if ($step -and $step.PSObject.Properties['timeoutSec']) { $to = [int]$step.timeoutSec }
                $code = Invoke-WithTimeout -File 'powershell.exe' -Args @('-NoProfile','-ExecutionPolicy','Bypass','-File',"$path") + $args -TimeoutSec $to
                if ($code -ne 0) { $status = "exit_$code" }
                $details.exitCode = $code
            }
            'finalize' { Write-Host 'Finalizing...' }
            'reboot' { $step.reboot = $true }
            default { Write-Host ("Skipping unknown kind: {0}" -f $kind) }
        }
        } catch { $status = 'error'; $details.error = $_.Exception.Message }
        $dur = ((Get-Date)-$t0).TotalSeconds
        $details.durationSec = [math]::Round($dur,2)
        Add-OpryxxEvent -Ctx $Ctx -Step $name -Status $status -Details $details
        # Update overall progress after completion
        Add-OpryxxEvent -Ctx $Ctx -Step 'overall' -Status 'progress' -Details @{ index=($i+1); total=$total; percent=[math]::Round((($i+1)*100.0)/[math]::Max($total,1),0) }

        # Handle reboot scheduling if requested by step
        if ($step.PSObject.Properties['reboot'] -and $step.reboot) {
            try {
                $adds = Get-OpryxxAdjustments -Ctx $Ctx -Plan $planList -CurrentIndex $i
                if ($adds -and $adds.Count -gt 0) {
                    $inserted = 0
                    foreach ($ns in $adds) { $null = $planList.Insert($i+1+$inserted, $ns); $inserted++ }
                    # Persist updated plan
                    $planList | ConvertTo-Json -Depth 6 | Set-Content $Ctx.PlanPath
                    Add-OpryxxEvent -Ctx $Ctx -Step 'pre_reboot_plan_adjust' -Status 'inserted' -Details @{count=$inserted}
                }
            } catch {}
            # Schedule resume
            $sched = Schedule-OpryxxResume -Ctx $Ctx -ApexPath $ApexPath
            Add-OpryxxEvent -Ctx $Ctx -Step 'reboot_schedule' -Status ($sched.method) -Details $sched
            if ($env:OPRYXX_TEST_NO_REBOOT -eq '1') {
                Write-Host '[TEST] Would reboot now; skipping due to OPRYXX_TEST_NO_REBOOT=1'
                break
            } else {
                Restart-Computer -Force
            }
        }
    }
}

Export-ModuleMember -Function Invoke-OpryxxPlan
