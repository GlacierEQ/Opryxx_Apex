@echo off
title OPRYXX EMERGENCY HARDWARE RESCUE
color 0C

echo.
echo ███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗███╗   ██╗ ██████╗██╗   ██╗
echo ██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║██╔════╝╚██╗ ██╔╝
echo █████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗  ██╔██╗ ██║██║      ╚████╔╝ 
echo ██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██║╚██╗██║██║       ╚██╔╝  
echo ███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗██║ ╚████║╚██████╗   ██║   
echo ╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝   
echo.
echo HARDWARE RESCUE SYSTEM
echo ======================

REM Check for admin privileges
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This script requires administrator privileges!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [INFO] Administrator privileges confirmed
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Installing Python...
    winget install Python.Python.3.11
    if errorlevel 1 (
        echo Please install Python manually from python.org
        pause
        exit /b 1
    )
)

echo [INFO] Python detected
echo.

REM Install required packages
echo [INSTALL] Installing rescue dependencies...
python -m pip install --upgrade pip
python -m pip install wmi psutil

echo.
echo EMERGENCY RESCUE OPTIONS:
echo =========================
echo 1. Dell Inspiron 2-in-1 7040 Boot Loop Fix
echo 2. Samsung 4TB SSD BitLocker Recovery
echo 3. WD Drive Recovery
echo 4. Full Hardware Rescue Scan
echo 5. BitLocker Emergency Unlock
echo 6. Create Recovery USB
echo 7. Emergency Data Backup
echo.

set /p choice="Select rescue option (1-7): "

if "%choice%"=="1" (
    echo [RESCUE] Dell Boot Loop Fix...
    python recovery\hardware_rescue.py
) else if "%choice%"=="2" (
    echo [RESCUE] Samsung SSD BitLocker Recovery...
    python recovery\bitlocker_rescue.py
) else if "%choice%"=="3" (
    echo [RESCUE] WD Drive Recovery...
    python recovery\hardware_rescue.py
) else if "%choice%"=="4" (
    echo [RESCUE] Full Hardware Scan...
    python recovery\hardware_rescue.py
) else if "%choice%"=="5" (
    echo [RESCUE] BitLocker Emergency Unlock...
    python recovery\bitlocker_rescue.py
) else if "%choice%"=="6" (
    echo [RESCUE] Creating Recovery USB...
    set /p usb_drive="Enter USB drive letter (e.g., E): "
    python -c "from recovery.hardware_rescue import HardwareRescue; HardwareRescue().create_recovery_usb('%usb_drive%')"
) else if "%choice%"=="7" (
    echo [RESCUE] Emergency Data Backup...
    python -c "from recovery.hardware_rescue import HardwareRescue; HardwareRescue().emergency_data_recovery()"
) else (
    echo [ERROR] Invalid choice
    pause
    exit /b 1
)

echo.
echo [INFO] Rescue operation completed
echo Check C:\OPRYXX_RECOVERY\ for logs and recovered data
pause