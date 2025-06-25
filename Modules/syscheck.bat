@echo off
echo [%time%] Starting system file integrity check...
DISM /Online /Cleanup-Image /RestoreHealth
sfc /scannow
echo [%time%] System file check completed.
