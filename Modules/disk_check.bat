@echo off
echo [%time%] Checking C: for disk errors...
chkdsk C: /f /r
if %errorlevel% neq 0 (
    echo [%time%] Disk errors found. Scheduling check for next reboot...
    echo y | chkdsk C: /f /r
)
echo [%time%] Disk check completed.
