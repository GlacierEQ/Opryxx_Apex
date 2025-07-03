@echo off
title OPRYXX ULTIMATE LAUNCHER
color 0A

echo.
echo  ██████╗ ██████╗ ██████╗ ██╗   ██╗██╗  ██╗██╗  ██╗
echo ██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝╚██╗██╔╝╚██╗██╔╝
echo ██║   ██║██████╔╝██████╔╝ ╚████╔╝  ╚███╔╝  ╚███╔╝ 
echo ██║   ██║██╔═══╝ ██╔══██╗  ╚██╔╝   ██╔██╗  ██╔██╗ 
echo ╚██████╔╝██║     ██║  ██║   ██║   ██╔╝ ██╗██╔╝ ██╗
echo  ╚═════╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo ULTIMATE UNIFIED SYSTEM LAUNCHER
echo ================================

REM Check for admin privileges
net session >nul 2>&1
if errorlevel 1 (
    echo [INFO] Running with standard privileges
    echo [INFO] Some features may require administrator access
) else (
    echo [OK] Administrator privileges detected
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if we're in the right directory
if not exist "OPRYXX_UNIFIED_LAUNCHER.py" (
    echo [ERROR] OPRYXX_UNIFIED_LAUNCHER.py not found!
    echo Please run this from the OPRYXX_LOGS directory
    pause
    exit /b 1
)

echo [LAUNCH] Starting OPRYXX Unified System...
echo.

REM Run the unified launcher
python OPRYXX_UNIFIED_LAUNCHER.py

echo.
echo [INFO] OPRYXX system has stopped
pause