function Schedule-OpryxxResume {
    param($Ctx,[string]$ApexPath)
    $taskName = "OpryxxResume_" + $Ctx.Id
    $psCmd = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$ApexPath`" -ResumePath `"$($Ctx.Root)`""
    try {
        schtasks /Create /TN $taskName /SC ONSTART /RU SYSTEM /TR $psCmd /F | Out-Null
        return @{ method='schtasks'; task=$taskName }
    } catch {
        try {
            New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" -Force | Out-Null
            New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" -Name $taskName -Value $psCmd -PropertyType String -Force | Out-Null
            return @{ method='runonce'; name=$taskName }
        } catch {
            return @{ method='none'; error=$_.Exception.Message }
        }
    }
}

Export-ModuleMember -Function Schedule-OpryxxResume

