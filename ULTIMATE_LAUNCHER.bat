@echo off
title ULTIMATE OPRYXX LAUNCHER - Maximum Power Integration
color 0A
cls

echo.
echo ================================================================
echo                ULTIMATE OPRYXX LAUNCHER
echo                   MAXIMUM POWER INTEGRATION
echo ================================================================
echo.
echo 🚀 LAUNCHING ULTIMATE MASTER GUI...
echo ✅ Transparent Operation Tracking
echo ✅ AI Workbench Integration  
echo ✅ Real-time System Health Monitoring
echo ✅ Comprehensive Error Handling
echo ✅ Full System Integration
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Install required packages if needed
echo 📦 Checking dependencies...
pip install psutil >nul 2>&1

REM Launch the Ultimate Master GUI
echo 🚀 Starting Ultimate Master GUI...
python ULTIMATE_MASTER_GUI.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to launch Ultimate Master GUI
    echo Check the log files for details
    pause
)

echo.
echo 🎉 Ultimate Master GUI session ended
pause