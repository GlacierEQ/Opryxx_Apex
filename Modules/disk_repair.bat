@echo off
echo [STATUS] OPRYXX: Scheduling disk check for C: (requires reboot)...
echo Y | chkdsk C: /f /r
echo [STATUS] OPRYXX: Disk check for C: scheduled.
exit /b 0