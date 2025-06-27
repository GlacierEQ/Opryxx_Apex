@echo off
:: OPRYXX Recovery Assistant for Dell Inspiron 2-in-1
:: This script automates the recovery process for systems stuck in Safe Mode

:: Set console window title
title OPRYXX Recovery Assistant - Dell Inspiron 2-in-1

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Set error handling
setlocal enabledelayedexpansion

:: Set colors
color 0A

:: Create log directory
set "logdir=C:\OPRYXX_Recovery_Logs"
mkdir "%logdir%" 2>nul
set "logfile=%logdir%\recovery_%date:/=-%_%time::=-%.log"
set "logfile=!logfile: =_!"

echo =========================================== >> "%logfile%"
echo OPRYXX Recovery Assistant - %date% %time% >> "%logfile%"
echo =========================================== >> "%logfile%"

echo OPRYXX Recovery Assistant for Dell Inspiron 2-in-1
echo ===========================================
echo This tool will help recover your system from Safe Mode boot issues.
echo All actions will be logged to: %logfile%
echo.

:check_python
:: Check if Python is installed
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not found in PATH. Checking common installation locations...
    
    set "python_path="
    
    :: Check common Python installation paths
    if exist "%ProgramFiles%\Python39\python.exe" set "python_path=%ProgramFiles%\Python39\python.exe"
    if exist "%ProgramFiles%\Python310\python.exe" set "python_path=%ProgramFiles%\Python310\python.exe"
    if exist "%ProgramFiles%\Python311\python.exe" set "python_path=%ProgramFiles%\Python311\python.exe"
    if exist "%ProgramFiles%\Python312\python.exe" set "python_path=%ProgramFiles%\Python312\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python39\python.exe" set "python_path=%LocalAppData%\Programs\Python\Python39\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "python_path=%LocalAppData%\Programs\Python\Python310\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "python_path=%LocalAppData%\Programs\Python\Python311\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "python_path=%LocalAppData%\Programs\Python\Python312\python.exe"
    
    if defined python_path (
        echo Found Python at: !python_path!
        set "python_cmd=!python_path!"
    ) else (
        echo Python not found. Please install Python 3.9 or later and try again.
        echo You can download Python from: https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
) else (
    set "python_cmd=python"
)

:check_script
:: Check if safe_mode_recovery.py exists in the same directory
set "script_path=%~dp0safe_mode_recovery.py"
if not exist "%script_path%" (
    echo Error: safe_mode_recovery.py not found in the current directory.
    echo Please make sure both OPRYXX_Recovery_Assistant.bat and safe_mode_recovery.py
    echo are in the same directory.
    pause
    exit /b 1
)

:run_recovery
echo.
echo ===========================================
echo Starting OPRYXX Recovery Process
echo ===========================================
echo This may take several minutes. Please be patient...
echo.

echo [1/4] Creating system restore point...
%python_cmd% "%script_path%" --create-restore-point >> "%logfile%" 2>&1
if %errorLevel% neq 0 (
    echo Warning: Failed to create system restore point. Continuing anyway...
) else (
    echo ✓ System restore point created successfully.
)

echo [2/4] Disabling Safe Mode boot options...
%python_cmd% "%script_path%" --disable-safe-mode >> "%logfile%" 2>&1
if %errorLevel% neq 0 (
    echo Error: Failed to disable Safe Mode boot options.
    echo Check the log file for details: %logfile%
    pause
    exit /b 1
) else (
    echo ✓ Safe Mode boot options disabled.
)

echo [3/4] Repairing boot configuration...
%python_cmd% "%script_path%" --repair-boot >> "%logfile%" 2>&1
if %errorLevel% neq 0 (
    echo Warning: Some boot repair operations may have failed.
    echo Check the log file for details: %logfile%
) else (
    echo ✓ Boot configuration repaired successfully.
)

echo [4/4] Completing OS installation...
%python_cmd% "%script_path%" --complete-installation >> "%logfile%" 2>&1
if %errorLevel% neq 0 (
    echo Warning: Some installation completion steps may have failed.
    echo Check the log file for details: %logfile%
) else (
    echo ✓ OS installation completed successfully.
)

:complete
echo.
echo ===========================================
echo RECOVERY PROCESS COMPLETED
echo ===========================================
echo.
echo Recovery process has completed. Please restart your computer.
echo.
echo Log file: %logfile%
echo.

:choice
set /p choice=Would you like to restart now? [Y/N] 
if /i "!choice!"=="y" (
    shutdown /r /t 30 /c "OPRYXX Recovery: Restarting to complete recovery..."
    echo System will restart in 30 seconds. Please save any open work.
) else (
    echo Please restart your computer as soon as possible to complete the recovery.
)

pause
exit /b 0
