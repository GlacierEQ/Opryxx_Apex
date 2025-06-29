@echo off
title OPRYXX MASTER SYSTEM LAUNCHER
color 0A
cls

echo.
echo ================================================================
echo                OPRYXX MASTER SYSTEM LAUNCHER
echo ================================================================
echo.
echo ORGANIZED SYSTEM STRUCTURE
echo.
echo Available Systems:
echo.
echo [1] MEGA OPRYXX - Ultimate Recovery System
echo [2] AI WORKBENCH - Intelligent PC Manager  
echo [3] ULTIMATE AI OPTIMIZER - 24/7 Auto-Fix
echo [4] Emergency Recovery - Instant Fix
echo [5] Maintenance Control - System Maintenance
echo [6] System Verification - Check All Systems
echo [7] Exit
echo.
set /p choice="Select system to launch (1-7): "

if "%choice%"=="1" goto mega_opryxx
if "%choice%"=="2" goto ai_workbench
if "%choice%"=="3" goto ultimate_ai
if "%choice%"=="4" goto emergency
if "%choice%"=="5" goto maintenance
if "%choice%"=="6" goto verification
if "%choice%"=="7" goto exit
goto invalid

:mega_opryxx
echo Launching MEGA OPRYXX...
cd /d "%~dp0"
python gui/MEGA_OPRYXX.py
goto menu

:ai_workbench
echo Launching AI WORKBENCH...
cd /d "%~dp0"
python ai/AI_WORKBENCH.py
goto menu

:ultimate_ai
echo Launching ULTIMATE AI OPTIMIZER...
cd /d "%~dp0"
python ai/ULTIMATE_AI_OPTIMIZER.py
goto menu

:emergency
echo Launching Emergency Recovery...
cd /d "%~dp0"
python recovery/immediate_safe_mode_exit.py
goto menu

:maintenance
echo Launching Maintenance Control...
cd /d "%~dp0"
python maintenance/maintenance_pipeline.py
goto menu

:verification
echo Running System Verification...
cd /d "%~dp0"
python verification/VERIFY_MEGA.py
goto menu

:invalid
echo Invalid choice. Please select 1-7.
pause
goto menu

:menu
echo.
echo Return to menu? (Y/N)
set /p return=
if /i "%return%"=="Y" goto start
goto exit

:exit
echo.
echo OPRYXX Master System - Session Ended
pause
exit /b 0

:start
cls
goto menu
