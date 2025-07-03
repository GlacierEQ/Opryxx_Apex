@echo off
title MASTER RECOVERY LAUNCHER - Dell Inspiron 7040 & MSI Summit 16 2024
color 0A

echo ================================================
echo        MASTER RECOVERY LAUNCHER
echo ================================================
echo.
echo TARGET SYSTEMS:
echo ✅ Dell Inspiron 2-in-1 7040 (Boot Loop Recovery)
echo ✅ MSI Summit 16 2024 (Performance Optimization)
echo ✅ Samsung 4TB SSD (RAW + BitLocker Recovery)
echo ✅ WD Notebook Drives (RAW Partition Recovery)
echo.
echo ================================================
echo.

echo Select Recovery Operation:
echo.
echo 1. EMERGENCY BOOT RECOVERY (Dell Inspiron 7040)
echo 2. COMPLETE DATA RECOVERY (All Systems)
echo 3. BITLOCKER RECOVERY (Samsung SSD)
echo 4. ULTIMATE BOOT RECOVERY (Advanced)
echo 5. ULTIMATE UNIFIED SYSTEM (Full GUI)
echo.
echo Q. Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto emergency_boot
if /i "%choice%"=="2" goto complete_recovery
if /i "%choice%"=="3" goto bitlocker_recovery
if /i "%choice%"=="4" goto ultimate_boot
if /i "%choice%"=="5" goto unified_system
if /i "%choice%"=="Q" goto quit

echo Invalid choice. Please try again.
pause
goto start

:emergency_boot
echo.
echo 🚨 LAUNCHING EMERGENCY BOOT RECOVERY...
echo Specialized for Dell Inspiron 2-in-1 7040 Boot Loops
echo.
python ULTIMATE_BOOT_RECOVERY.py
goto end

:complete_recovery
echo.
echo 🚀 LAUNCHING COMPLETE DATA RECOVERY...
echo All systems: Dell, MSI, Samsung SSD, WD Drives
echo.
python ULTIMATE_DATA_RECOVERY.py
goto end

:bitlocker_recovery
echo.
echo 🔓 LAUNCHING BITLOCKER RECOVERY...
echo Samsung 4TB SSD RAW + BitLocker Specialist
echo.
python BITLOCKER_RECOVERY.py
goto end

:ultimate_boot
echo.
echo 💾 LAUNCHING ULTIMATE BOOT RECOVERY...
echo Advanced boot repair and system recovery
echo.
python ULTIMATE_BOOT_RECOVERY.py
goto end

:unified_system
echo.
echo 🎮 LAUNCHING ULTIMATE UNIFIED SYSTEM...
echo Complete GUI with GPU/NPU acceleration
echo.
python ULTIMATE_UNIFIED_SYSTEM.py
goto end

:quit
echo.
echo Exiting Master Recovery Launcher...
goto end

:end
echo.
echo Recovery operation completed.
echo.
pause