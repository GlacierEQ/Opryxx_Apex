@echo off
REM OPRYXX Emergency Recovery Launcher
REM Quick access to critical recovery operations

title OPRYXX Emergency Recovery System
color 0C
echo.
echo ================================================================
echo                OPRYXX EMERGENCY RECOVERY SYSTEM
echo                    GANDALFS Protocol Active
echo ================================================================
echo.
echo CRITICAL: This tool requires Administrator privileges
echo.
echo Available Recovery Options:
echo.
echo [1] IMMEDIATE SAFE MODE EXIT (Priority Command)
echo [2] Comprehensive System Recovery
echo [3] Boot Diagnostics Only
echo [4] Safe Mode Recovery Tools
echo [5] View Recovery Logs
echo [6] Exit
echo.
set /p choice="Select recovery option (1-6): "

if "%choice%"=="1" goto immediate_exit
if "%choice%"=="2" goto master_recovery
if "%choice%"=="3" goto diagnostics
if "%choice%"=="4" goto safe_mode_tools
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto exit
goto invalid_choice

:immediate_exit
echo.
echo ================================================================
echo           EXECUTING IMMEDIATE SAFE MODE EXIT
echo ================================================================
echo.
echo CRITICAL COMMAND: bcdedit /deletevalue {current} safeboot
echo.
pause
python immediate_safe_mode_exit.py
if %errorlevel%==0 (
    echo.
    echo SUCCESS: Safe Mode exit command executed
    echo NEXT ACTION: Reboot the system immediately
    echo.
    set /p reboot="Reboot now? (Y/N): "
    if /i "%reboot%"=="Y" shutdown /r /t 10 /c "OPRYXX Recovery Reboot"
) else (
    echo.
    echo FAILED: Safe Mode exit unsuccessful
    echo Proceeding to comprehensive recovery...
    goto master_recovery
)
pause
goto menu

:master_recovery
echo.
echo ================================================================
echo         EXECUTING COMPREHENSIVE SYSTEM RECOVERY
echo ================================================================
echo.
echo This will run the complete GANDALFS recovery protocol
echo including diagnostics, targeted recovery, and advanced repair.
echo.
pause
python master_recovery.py
echo.
echo Recovery operation completed. Check logs for details.
pause
goto menu

:diagnostics
echo.
echo ================================================================
echo              RUNNING BOOT DIAGNOSTICS
echo ================================================================
echo.
python boot_diagnostics.py
echo.
echo Diagnostics completed. Check logs for detailed report.
pause
goto menu

:safe_mode_tools
echo.
echo ================================================================
echo            SAFE MODE RECOVERY TOOLS
echo ================================================================
echo.
echo [A] Alternative Safe Mode Recovery
echo [B] Safe Mode Status Check
echo [C] Boot Configuration Analysis
echo [D] Return to Main Menu
echo.
set /p safe_choice="Select option (A-D): "

if /i "%safe_choice%"=="A" (
    python safe_mode_recovery.py
) else if /i "%safe_choice%"=="B" (
    echo Checking Safe Mode status...
    bcdedit /enum | findstr /i safeboot
    if %errorlevel%==0 (
        echo Safe Mode flags detected in boot configuration
    ) else (
        echo No Safe Mode flags found in boot configuration
    )
    echo.
    echo Environment check:
    if defined SAFEBOOT_OPTION (
        echo Currently in Safe Mode: %SAFEBOOT_OPTION%
    ) else (
        echo Not currently in Safe Mode
    )
) else if /i "%safe_choice%"=="C" (
    echo Boot Configuration Analysis:
    bcdedit /v
) else (
    goto menu
)
pause
goto menu

:view_logs
echo.
echo ================================================================
echo                   RECOVERY LOGS
echo ================================================================
echo.
echo Available log directories:
dir /b logs 2>nul
if %errorlevel%==0 (
    echo.
    set /p log_dir="Enter log directory name to view (or press Enter for latest): "
    if "%log_dir%"=="" (
        for /f "delims=" %%i in ('dir logs /b /od') do set latest=%%i
        if defined latest (
            echo Opening latest log directory: !latest!
            explorer logs\!latest!
        ) else (
            echo No log directories found
        )
    ) else (
        if exist "logs\%log_dir%" (
            explorer logs\%log_dir%
        ) else (
            echo Log directory not found: %log_dir%
        )
    )
) else (
    echo No log directories found
)
pause
goto menu

:invalid_choice
echo.
echo Invalid choice. Please select 1-6.
pause
goto menu

:menu
cls
echo.
echo ================================================================
echo                OPRYXX EMERGENCY RECOVERY SYSTEM
echo                    GANDALFS Protocol Active
echo ================================================================
echo.
echo Available Recovery Options:
echo.
echo [1] IMMEDIATE SAFE MODE EXIT (Priority Command)
echo [2] Comprehensive System Recovery
echo [3] Boot Diagnostics Only
echo [4] Safe Mode Recovery Tools
echo [5] View Recovery Logs
echo [6] Exit
echo.
set /p choice="Select recovery option (1-6): "

if "%choice%"=="1" goto immediate_exit
if "%choice%"=="2" goto master_recovery
if "%choice%"=="3" goto diagnostics
if "%choice%"=="4" goto safe_mode_tools
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto exit
goto invalid_choice

:exit
echo.
echo OPRYXX Emergency Recovery System - Session Ended
echo.
echo IMPORTANT REMINDERS:
echo - If Safe Mode flags were cleared, reboot the system
echo - Check recovery logs for detailed information
echo - Contact support if issues persist
echo.
pause
exit /b 0