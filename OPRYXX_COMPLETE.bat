@echo off
title OPRYXX COMPLETE SYSTEM - READY TO USE
cls

echo.
echo ========================================
echo    OPRYXX COMPLETE SYSTEM READY
echo ========================================
echo.
echo Complete AI-Powered System with Recovery
echo.
echo Your system includes:
echo   - AI Optimization Engine
echo   - Samsung SSD Recovery (BitLocker)
echo   - Dell Inspiron 7040 Recovery
echo   - Unified Full Stack GUI
echo   - Master System Launcher
echo   - Recovery Master Interface
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from python.org
    echo Then run this launcher again.
    echo.
    pause
    exit /b 1
)

echo Python detected. Installing/updating requirements...
echo.

REM Install required packages
pip install psutil pywin32 wmi numpy tkinter --quiet --user

echo.
echo ========================================
echo    CHOOSE YOUR OPRYXX COMPONENT
echo ========================================
echo.
echo 1. Recovery Master (Samsung SSD + Dell Recovery)
echo 2. AI Optimization Engine
echo 3. Unified Full Stack GUI
echo 4. Master System Launcher
echo 5. Samsung SSD Recovery Only
echo 6. Dell Inspiron Recovery Only
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto recovery_master
if "%choice%"=="2" goto ai_engine
if "%choice%"=="3" goto full_stack
if "%choice%"=="4" goto master_launcher
if "%choice%"=="5" goto samsung_only
if "%choice%"=="6" goto dell_only
if "%choice%"=="7" goto exit
goto invalid_choice

:recovery_master
echo.
echo Starting OPRYXX Recovery Master...
echo This includes Samsung SSD and Dell Inspiron recovery
echo.
if exist "RECOVERY_MASTER.py" (
    python RECOVERY_MASTER.py
) else (
    echo ERROR: RECOVERY_MASTER.py not found!
)
goto end

:ai_engine
echo.
echo Starting AI Optimization Engine...
echo.
if exist "AI_OPTIMIZATION_ENGINE.py" (
    python AI_OPTIMIZATION_ENGINE.py
) else (
    echo ERROR: AI_OPTIMIZATION_ENGINE.py not found!
)
goto end

:full_stack
echo.
echo Starting Unified Full Stack GUI...
echo.
if exist "UNIFIED_FULL_STACK_GUI.py" (
    python UNIFIED_FULL_STACK_GUI.py
) else (
    echo ERROR: UNIFIED_FULL_STACK_GUI.py not found!
)
goto end

:master_launcher
echo.
echo Starting Master System Launcher...
echo.
if exist "UNIFIED_MASTER_LAUNCHER.py" (
    python UNIFIED_MASTER_LAUNCHER.py
) else (
    echo ERROR: UNIFIED_MASTER_LAUNCHER.py not found!
)
goto end

:samsung_only
echo.
echo Starting Samsung SSD Recovery...
echo.
if exist "SAMSUNG_SSD_RECOVERY.py" (
    python SAMSUNG_SSD_RECOVERY.py
) else (
    echo ERROR: SAMSUNG_SSD_RECOVERY.py not found!
)
goto end

:dell_only
echo.
echo Starting Dell Inspiron Recovery...
echo.
if exist "DELL_INSPIRON_RECOVERY.py" (
    python DELL_INSPIRON_RECOVERY.py
) else (
    echo ERROR: DELL_INSPIRON_RECOVERY.py not found!
)
goto end

:invalid_choice
echo.
echo Invalid choice. Please select 1-7.
echo.
pause
goto start

:exit
echo.
echo Exiting OPRYXX Complete System.
echo.
goto end

:end
echo.
echo OPRYXX session ended.
pause