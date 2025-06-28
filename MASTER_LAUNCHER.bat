@echo off
title OPRYXX MASTER SYSTEM - PEAK PERFORMANCE
color 0A
cls

echo.
echo ================================================================
echo           OPRYXX MASTER SYSTEM - PEAK PERFORMANCE
echo ================================================================
echo.
echo System Status: OPTIMIZED AND READY
echo Power Level: 100%%
echo.
echo Available Systems:
echo.
echo [1] MEGA OPRYXX - Ultimate Recovery System
echo [2] AI WORKBENCH - Intelligent PC Manager  
echo [3] ULTIMATE AI OPTIMIZER - 24/7 Auto-Fix
echo [4] Emergency Recovery - Instant Fix
echo [5] System Verification - Check All Systems
echo [6] Exit
echo.
set /p choice="Select system (1-6): "

if "%choice%"=="1" goto mega_opryxx
if "%choice%"=="2" goto ai_workbench  
if "%choice%"=="3" goto ultimate_ai
if "%choice%"=="4" goto emergency
if "%choice%"=="5" goto verification
if "%choice%"=="6" goto exit
goto invalid

:mega_opryxx
echo Launching MEGA OPRYXX...
python gui/MEGA_OPRYXX.py
goto menu

:ai_workbench
echo Launching AI WORKBENCH...
python ai/AI_WORKBENCH.py
goto menu

:ultimate_ai
echo Launching ULTIMATE AI OPTIMIZER...
python ai/ULTIMATE_AI_OPTIMIZER.py
goto menu

:emergency
echo Emergency Recovery...
python recovery/immediate_safe_mode_exit.py
goto menu

:verification
echo System Verification...
python verification/VERIFY_MEGA.py
goto menu

:invalid
echo Invalid choice.
pause
goto menu

:menu
echo.
echo Return to menu? (Y/N)
set /p return=
if /i "%return%"=="Y" cls && goto menu
goto exit

:exit
echo OPRYXX Master System - Peak Performance Achieved
pause
