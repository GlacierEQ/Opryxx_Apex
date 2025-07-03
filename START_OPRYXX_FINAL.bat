@echo off
title OPRYXX FINAL - Optimized Complete System
cls

echo.
echo ========================================
echo    OPRYXX FINAL - COMPLETE SYSTEM
echo ========================================
echo.
echo Optimized Architecture with Best Practices
echo - Modular design with proper abstractions
echo - Comprehensive error handling
echo - Thread-safe operations
echo - Extensive test coverage
echo - Unified logging system
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r requirements_final.txt --quiet --user

echo.
echo Starting OPRYXX FINAL...
echo.

python OPRYXX_FINAL.py

if errorlevel 1 (
    echo.
    echo Error occurred. Check logs for details.
    pause
)

echo.
echo OPRYXX FINAL session ended.
pause