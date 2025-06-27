@echo off
:: GANDALFS Update and Maintenance Script for OPRYXX
:: This script provides an easy way to manage GANDALFS updates and maintenance

setlocal enabledelayedexpansion

:: Configuration
set "PYTHON=python"
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%..\logs"
set "CONFIG_DIR=%SCRIPT_DIR%..\config"
set "BACKUP_DIR=%SCRIPT_DIR%..\backups"

:: Create necessary directories
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "LOG_FILE=%LOG_DIR%\gandalfs_update_%dt:~0,8%_%dt:~8,6%.log"

:: Function to log messages
:log
    echo [%TIME%] %* >> "%LOG_FILE%"
    echo [%TIME%] %*
    goto :eof

:: Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    call :log "Running with administrator privileges"
) else (
    call :log "WARNING: Not running as administrator. Some operations may fail."
)

:: Display menu
:menu
    echo.
    echo ====================================
    echo    GANDALFS Maintenance for OPRYXX   
    echo ====================================
    echo.
    echo 1. Check for updates
    echo 2. Install updates
    echo 3. Run maintenance tasks
    echo 4. Install scheduled task (weekly)
    echo 5. View logs
    echo 6. Check system compatibility
    echo 7. Exit
    echo.
    set /p "choice=Enter your choice (1-7): "

    if "%choice%"=="1" goto check_updates
    if "%choice%"=="2" goto install_updates
    if "%choice%"=="3" goto run_maintenance
    if "%choice%"=="4" goto install_task
    if "%choice%"=="5" goto view_logs
    if "%choice%"=="6" goto check_compatibility
    if "%choice%"=="7" goto exit_script
    
    echo Invalid choice. Please try again.
    timeout /t 2 >nul
    cls
    goto menu

:check_updates
    call :log "Checking for GANDALFS updates..."
    %PYTHON% "%SCRIPT_DIR%gandalfs_update_manager.py" --check
    pause
    goto menu

:install_updates
    call :log "Installing GANDALFS updates..."
    %PYTHON% "%SCRIPT_DIR%gandalfs_update_manager.py" --download
    %PYTHON% "%SCRIPT_DIR%gandalfs_update_manager.py" --apply
    pause
    goto menu

:run_maintenance
    call :log "Running GANDALFS maintenance tasks..."
    %PYTHON% "%SCRIPT_DIR%gandalfs_maintenance.py" --run-maintenance
    pause
    goto menu

:install_task
    call :log "Installing scheduled task..."
    %PYTHON% "%SCRIPT_DIR%gandalfs_maintenance.py" --install-task
    pause
    goto menu

:view_logs
    call :log "Opening logs directory..."
    if exist "%LOG_DIR%" (
        explorer "%LOG_DIR%"
    ) else (
        call :log "Log directory not found: %LOG_DIR%"
    )
    pause
    goto menu

:check_compatibility
    call :log "Checking system compatibility..."
    %PYTHON% "%SCRIPT_DIR%gandalfs_maintenance.py" --run-maintenance
    pause
    goto menu

:exit_script
    call :log "Exiting GANDALFS Maintenance"
    exit /b 0
