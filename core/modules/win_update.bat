@echo off
echo [%time%] Checking for Windows updates...
powershell -Command "Install-WindowsUpdate -AcceptAll -AutoReboot"
echo [%time%] Windows update check completed.
