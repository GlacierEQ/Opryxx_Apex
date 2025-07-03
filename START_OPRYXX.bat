@echo off
title OPRYXX SYSTEM LAUNCHER
color 0A

echo.
echo  ██████╗ ██████╗ ██████╗ ██╗   ██╗██╗  ██╗██╗  ██╗
echo ██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝╚██╗██╔╝╚██╗██╔╝
echo ██║   ██║██████╔╝██████╔╝ ╚████╔╝  ╚███╔╝  ╚███╔╝ 
echo ██║   ██║██╔═══╝ ██╔══██╗  ╚██╔╝   ██╔██╗  ██╔██╗ 
echo ╚██████╔╝██║     ██║  ██║   ██║   ██╔╝ ██╗██╔╝ ██╗
echo  ╚═════╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo ULTIMATE PC OPTIMIZATION SYSTEM
echo ================================

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "OPRYXX_MASTER.py" (
    echo [ERROR] OPRYXX_MASTER.py not found!
    echo Please run this from the OPRYXX_LOGS directory
    pause
    exit /b 1
)

echo [INFO] Starting OPRYXX Master Controller...
echo.

REM Run the master controller
python OPRYXX_MASTER.py

echo.
echo [INFO] OPRYXX system has stopped
pause