@echo off
title OPRYXX AUTOMATED OS REINSTALL
color 0C
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██           OPRYXX AUTOMATED OS REINSTALL                   ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🤖 FULLY AUTOMATED WINDOWS 11 REINSTALL
echo.
echo This will:
echo   💾 Auto-backup your data
echo   📥 Download Windows 11 ISO
echo   💿 Create bootable USB
echo   ⚙️ Configure unattended install
echo   🔄 Auto-reboot and reinstall
echo   🚀 Restore OPRYXX system
echo.
echo ⚠️ WARNING: This will COMPLETELY WIPE your PC!
echo.
echo [Y] Start Automated Reinstall
echo [N] Cancel
echo.
set /p choice="Continue? (Y/N): "

if /i "%choice%"=="Y" goto start_reinstall
if /i "%choice%"=="N" goto cancel
goto invalid

:start_reinstall
echo.
echo 🚀 Starting OPRYXX Automated OS Reinstall...
echo.
python recovery/automated_os_reinstall.py
goto end

:cancel
echo.
echo ❌ Automated reinstall cancelled
goto end

:invalid
echo Invalid choice. Please enter Y or N.
pause
goto start

:end
pause