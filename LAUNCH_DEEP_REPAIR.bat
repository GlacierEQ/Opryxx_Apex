@echo off
title OPRYXX Deep PC Repair Launcher
color 0A
cls

echo.
echo ================================================================
echo                OPRYXX DEEP PC REPAIR SYSTEM
echo ================================================================
echo.
echo [1] Test All GUI Connections
echo [2] Start Deep PC Repair
echo [3] Emergency Repair Mode
echo [4] Launch MEGA OPRYXX
echo [5] Exit
echo.
set /p choice="Select option (1-5): "

if "%choice%"=="1" goto test_gui
if "%choice%"=="2" goto deep_repair
if "%choice%"=="3" goto emergency
if "%choice%"=="4" goto mega_opryxx
if "%choice%"=="5" goto exit

:test_gui
echo Testing GUI connections...
python gui_connection_tester.py
goto menu

:deep_repair
echo Starting Deep PC Repair...
python deep_pc_repair.py
goto menu

:emergency
echo Emergency Repair Mode...
python deep_pc_repair.py --emergency
goto menu

:mega_opryxx
echo Launching MEGA OPRYXX...
python gui/MEGA_OPRYXX.py
goto menu

:menu
echo.
echo Return to menu? (Y/N)
set /p return=
if /i "%return%"=="Y" goto start
goto exit

:exit
echo.
echo OPRYXX Deep Repair - Session Ended
pause
exit /b 0

:start
cls
goto menu