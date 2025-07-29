@echo off
title OPRYXX Deep PC Repair
color 0A
cls

echo.
echo ================================================================
echo                OPRYXX DEEP PC REPAIR SYSTEM
echo ================================================================
echo.
echo Starting Deep PC Repair with transparent operation feedback...
echo.

cd /d "%~dp0"
python OPRYXX_DEEP_REPAIR.py

pause