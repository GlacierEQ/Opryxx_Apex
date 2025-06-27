@echo off
echo [STATUS] OPRYXX: Running System File Checker (SFC)...
sfc /scannow
echo [STATUS] OPRYXX: Running DISM RestoreHealth...
DISM /Online /Cleanup-Image /RestoreHealth
echo [STATUS] OPRYXX: System file scan and repair complete.
exit /b 0