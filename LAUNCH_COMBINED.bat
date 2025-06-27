@echo off
title OPRYXX + Todo System Integration
color 0B

echo.
echo ================================================================
echo            OPRYXX + TODO SYSTEM INTEGRATION
echo              Combined Recovery and Task Management
echo ================================================================
echo.
echo Features:
echo 🔧 Recovery Todos - Scan and manage recovery-related tasks
echo 🤖 Auto Recovery - Autonomous recovery execution
echo 🔄 Combined Operations - Integrated workflow management
echo.
echo Todo System Path: C:\opryxx_logs\files
echo OPRYXX System: Active
echo.
echo Launching combined interface...
echo.

cd /d "%~dp0"
python integration\combined_interface.py

if %errorlevel% neq 0 (
    echo.
    echo Error launching combined interface.
    echo Ensure both systems are properly configured.
    pause
)