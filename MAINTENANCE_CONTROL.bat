@echo off
REM OPRYXX Maintenance Control Center
REM Automated maintenance pipeline with GANDALF PE integration

title OPRYXX Maintenance Control Center
color 0B
cls

echo.
echo ================================================================
echo              OPRYXX MAINTENANCE CONTROL CENTER
echo           GANDALF PE Integration and Update Pipeline
echo ================================================================
echo.

:main_menu
echo Available Operations:
echo.
echo [1] Run Maintenance Cycle
echo [2] Check for Updates
echo [3] Build Custom PE Image
echo [4] Update GANDALF PE
echo [5] Verify System Integrity
echo [6] View Maintenance Logs
echo [7] Schedule Automatic Updates
echo [8] Backup Current Configuration
echo [9] Exit
echo.
set /p choice="Select operation (1-9): "

if "%choice%"=="1" goto maintenance_cycle
if "%choice%"=="2" goto check_updates
if "%choice%"=="3" goto build_pe
if "%choice%"=="4" goto update_gandalf
if "%choice%"=="5" goto verify_system
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto schedule_updates
if "%choice%"=="8" goto backup_config
if "%choice%"=="9" goto exit
goto invalid_choice

:maintenance_cycle
echo.
echo ================================================================
echo                 RUNNING MAINTENANCE CYCLE
echo ================================================================
echo.
echo This will perform:
echo - Update checks
echo - Log cleanup
echo - Tool verification
echo - Recovery image updates
echo - Functionality tests
echo.
pause
python maintenance_pipeline.py
echo.
echo Maintenance cycle completed. Check logs for details.
pause
goto main_menu

:check_updates
echo.
echo ================================================================
echo                   CHECKING FOR UPDATES
echo ================================================================
echo.
echo Checking updates for:
echo - GANDALF PE
echo - OPRYXX Tools
echo - System Components
echo - Driver Packages
echo.
python update_manager.py --check-all
echo.
echo Update check completed.
pause
goto main_menu

:build_pe
echo.
echo ================================================================
echo               BUILDING CUSTOM PE IMAGE
echo ================================================================
echo.
echo This will create a custom Windows PE image with:
echo - GANDALF Windows 11 PE base
echo - OPRYXX Recovery Suite
echo - Enhanced recovery tools
echo - Latest drivers
echo.
echo WARNING: This process may take 30-60 minutes
echo.
set /p confirm="Continue with PE build? (Y/N): "
if /i "%confirm%"=="Y" (
    python pe_builder.py
    echo.
    echo PE build process completed.
) else (
    echo PE build cancelled.
)
pause
goto main_menu

:update_gandalf
echo.
echo ================================================================
echo                 UPDATING GANDALF PE
echo ================================================================
echo.
echo Current: GANDALF Windows 11 PE x64 Redstone 9 Spring 2025
echo Checking for: GANDALF Windows 11 PE x64 Redstone 10 Summer 2025
echo.
echo This will:
echo 1. Download latest GANDALF PE
echo 2. Backup current configuration
echo 3. Integrate OPRYXX tools
echo 4. Create new recovery image
echo.
set /p confirm="Proceed with GANDALF PE update? (Y/N): "
if /i "%confirm%"=="Y" (
    echo Downloading GANDALF PE update...
    python update_manager.py --update-gandalf
    echo.
    echo GANDALF PE update completed.
) else (
    echo Update cancelled.
)
pause
goto main_menu

:verify_system
echo.
echo ================================================================
echo                VERIFYING SYSTEM INTEGRITY
echo ================================================================
echo.
echo Running comprehensive system verification:
echo.
echo [1] Tool Integrity Check
python update_manager.py --verify
echo.
echo [2] Recovery Functionality Test
python maintenance_pipeline.py --test-only
echo.
echo [3] Boot Configuration Verification
bcdedit /enum | findstr /C:"Windows Boot Manager"
if %errorlevel%==0 (
    echo ✓ Boot configuration OK
) else (
    echo ✗ Boot configuration issues detected
)
echo.
echo System verification completed.
pause
goto main_menu

:view_logs
echo.
echo ================================================================
echo                   MAINTENANCE LOGS
echo ================================================================
echo.
echo Available log categories:
echo.
dir /b logs 2>nul
if %errorlevel%==0 (
    echo.
    echo [A] View Latest Maintenance Log
    echo [B] View Update History
    echo [C] View Build Logs
    echo [D] View Error Logs
    echo [E] Open Log Directory
    echo [F] Return to Main Menu
    echo.
    set /p log_choice="Select option (A-F): "
    
    if /i "%log_choice%"=="A" (
        for /f "delims=" %%i in ('dir logs\maintenance_*.json /b /od 2^>nul') do set latest_maintenance=%%i
        if defined latest_maintenance (
            echo Opening: !latest_maintenance!
            notepad logs\!latest_maintenance!
        ) else (
            echo No maintenance logs found
        )
    ) else if /i "%log_choice%"=="B" (
        if exist update_history.json (
            notepad update_history.json
        ) else (
            echo No update history found
        )
    ) else if /i "%log_choice%"=="C" (
        for /f "delims=" %%i in ('dir logs\pe_build_*.log /b /od 2^>nul') do set latest_build=%%i
        if defined latest_build (
            notepad logs\!latest_build!
        ) else (
            echo No build logs found
        )
    ) else if /i "%log_choice%"=="D" (
        for /f "delims=" %%i in ('dir logs\*error*.log /b /od 2^>nul') do set latest_error=%%i
        if defined latest_error (
            notepad logs\!latest_error!
        ) else (
            echo No error logs found
        )
    ) else if /i "%log_choice%"=="E" (
        explorer logs
    )
) else (
    echo No log directories found
    echo Creating logs directory...
    mkdir logs
)
pause
goto main_menu

:schedule_updates
echo.
echo ================================================================
echo               SCHEDULE AUTOMATIC UPDATES
echo ================================================================
echo.
echo Configure automatic update schedule:
echo.
echo [1] Daily checks
echo [2] Weekly checks  
echo [3] Monthly checks
echo [4] Disable automatic updates
echo [5] View current schedule
echo.
set /p sched_choice="Select option (1-5): "

if "%sched_choice%"=="1" (
    echo Setting up daily update checks...
    python update_manager.py --schedule daily
) else if "%sched_choice%"=="2" (
    echo Setting up weekly update checks...
    python update_manager.py --schedule weekly
) else if "%sched_choice%"=="3" (
    echo Setting up monthly update checks...
    python update_manager.py --schedule monthly
) else if "%sched_choice%"=="4" (
    echo Disabling automatic updates...
    python update_manager.py --schedule disable
) else if "%sched_choice%"=="5" (
    echo Current schedule:
    if exist update_schedule.json (
        type update_schedule.json
    ) else (
        echo No schedule configured
    )
)
echo.
echo Schedule configuration completed.
pause
goto main_menu

:backup_config
echo.
echo ================================================================
echo              BACKUP CURRENT CONFIGURATION
echo ================================================================
echo.
echo Creating backup of:
echo - OPRYXX tools and configuration
echo - Recovery scripts
echo - Maintenance settings
echo - Update history
echo.
set backup_name=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set backup_name=%backup_name: =0%
echo Backup name: %backup_name%
echo.
mkdir backups\%backup_name% 2>nul

echo Backing up OPRYXX tools...
copy *.py backups\%backup_name%\ >nul 2>&1
copy *.bat backups\%backup_name%\ >nul 2>&1
copy *.json backups\%backup_name%\ >nul 2>&1
copy *.md backups\%backup_name%\ >nul 2>&1

echo Backing up logs...
xcopy logs backups\%backup_name%\logs\ /E /I /Q >nul 2>&1

echo Creating backup manifest...
echo Backup created: %date% %time% > backups\%backup_name%\backup_info.txt
echo OPRYXX Version: 2.0 >> backups\%backup_name%\backup_info.txt
echo GANDALF PE: Windows 11 PE x64 Redstone 9 Spring 2025 >> backups\%backup_name%\backup_info.txt

echo.
echo Backup completed: backups\%backup_name%
echo.
pause
goto main_menu

:invalid_choice
echo.
echo Invalid choice. Please select 1-9.
pause
goto main_menu

:exit
echo.
echo ================================================================
echo           OPRYXX MAINTENANCE CONTROL CENTER
echo                    Session Ended
echo ================================================================
echo.
echo Maintenance Summary:
echo - System Status: Ready
echo - Last Maintenance: Check logs for details
echo - Next Scheduled: Check update_schedule.json
echo.
echo Thank you for using OPRYXX Maintenance Control Center
echo.
pause
exit /b 0