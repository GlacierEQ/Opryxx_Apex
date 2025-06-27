@echo off
title Installing ULTIMATE AI OPTIMIZER Dependencies
color 0A

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██         INSTALLING AI OPTIMIZER DEPENDENCIES              ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

echo 🔧 Installing required dependencies for ULTIMATE AI OPTIMIZER...
echo.

echo Installing psutil for system monitoring...
pip install psutil>=5.9.0

if %errorlevel%==0 (
    echo ✅ psutil installed successfully
) else (
    echo ❌ Failed to install psutil
    echo Trying alternative installation...
    python -m pip install psutil
)

echo.
echo 🚀 Dependencies installation completed!
echo.
echo Ready to launch ULTIMATE AI OPTIMIZER!
echo.
pause