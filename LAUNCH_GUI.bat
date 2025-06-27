@echo off
title OPRYXX Modern GUI Launcher
color 0A

echo.
echo ================================================================
echo                OPRYXX RECOVERY SYSTEM v2.0
echo                    Modern GUI Interface
echo ================================================================
echo.
echo Features:
echo ⚡ System Optimization - Scan and optimize your system
echo 🔮 Predictive Analysis - Monitor health and get warnings  
echo 🔧 Automated Troubleshooting - Diagnose and fix issues
echo.
echo Launching GUI...
echo.

python gui\modern_interface.py

if %errorlevel% neq 0 (
    echo.
    echo Error launching GUI. Ensure Python is installed.
    pause
)