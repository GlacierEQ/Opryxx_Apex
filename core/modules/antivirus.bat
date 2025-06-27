@echo off
echo [%time%] Starting Windows Defender quick scan...
if exist "%ProgramFiles%\Windows Defender\MpCmdRun.exe" (
    "%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Scan -ScanType 1
) else (
    echo Windows Defender not found.
)
echo [%time%] Antivirus scan completed.
