@echo off
title OPRYXX UNIFIED SYSTEM
cls
echo.
echo ========================================
echo    OPRYXX UNIFIED SYSTEM LAUNCHER
echo ========================================
echo.
echo Starting unified system...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install requirements if needed
echo Installing requirements...
pip install psutil pywin32 wmi --quiet --user

REM Launch the unified system
echo Launching OPRYXX Unified System...
python UNIFIED_FULL_STACK_GUI.py

if errorlevel 1 (
    echo.
    echo Trying alternative launcher...
    python master_start.py
)

echo.
echo OPRYXX session ended.
pause
