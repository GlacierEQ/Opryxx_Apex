@echo off
title OPRYXX Deep PC Repair Launcher
color 0A

echo.
echo ===============================================
echo    OPRYXX DEEP PC REPAIR SYSTEM LAUNCHER
echo ===============================================
echo.

echo [1] Test GUI Connections
echo [2] Start Deep PC Repair
echo [3] Run Both (Recommended)
echo [4] Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" goto test_gui
if "%choice%"=="2" goto deep_repair
if "%choice%"=="3" goto run_both
if "%choice%"=="4" goto exit

:test_gui
echo.
echo Starting GUI Connection Tester...
python gui_connection_tester.py
pause
goto menu

:deep_repair
echo.
echo Starting Deep PC Repair...
python deep_pc_repair.py
pause
goto menu

:run_both
echo.
echo Starting GUI Connection Tester first...
start python gui_connection_tester.py
timeout /t 3 /nobreak >nul
echo.
echo Starting Deep PC Repair...
python deep_pc_repair.py
pause
goto menu

:menu
cls
goto start

:exit
echo.
echo Exiting OPRYXX Deep PC Repair Launcher...
timeout /t 2 /nobreak >nul
exit

:start
echo.
echo ===============================================
echo    OPRYXX DEEP PC REPAIR SYSTEM LAUNCHER
echo ===============================================
echo.

echo [1] Test GUI Connections
echo [2] Start Deep PC Repair
echo [3] Run Both (Recommended)
echo [4] Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" goto test_gui
if "%choice%"=="2" goto deep_repair
if "%choice%"=="3" goto run_both
if "%choice%"=="4" goto exit

echo Invalid choice. Please select 1-4.
timeout /t 2 /nobreak >nul
goto start