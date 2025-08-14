@echo off
title OPRYXX UNIFIED FULL STACK SYSTEM
color 0A
cls

echo.
echo ================================================================
echo           OPRYXX UNIFIED FULL STACK SYSTEM LAUNCHER
echo ================================================================
echo.
echo Launching the Unified Full Stack GUI...
echo.

cd /d "%~dp0"
python UNIFIED_FULL_STACK_GUI.py

echo.
echo OPRYXX Unified System - Session Ended
pause
exit /b 0
