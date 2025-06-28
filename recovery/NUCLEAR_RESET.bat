@echo off
title NUCLEAR RESET - Complete System Wipe and Reinstall
color 0C
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██              ⚠️  NUCLEAR RESET WARNING  ⚠️                ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🚨 THIS WILL COMPLETELY WIPE YOUR ENTIRE PC! 🚨
echo.
echo What this does:
echo   💥 DELETES EVERYTHING on your hard drive
echo   🔥 Removes Windows, programs, files, EVERYTHING
echo   ⚡ Installs fresh Windows 11 from scratch
echo   🚀 Results in brand new, clean PC
echo.
echo ⚠️  CRITICAL WARNINGS:
echo   - ALL DATA WILL BE PERMANENTLY LOST
echo   - ALL PROGRAMS WILL BE DELETED  
echo   - ALL SETTINGS WILL BE ERASED
echo   - THIS CANNOT BE UNDONE
echo.
echo 💾 BEFORE PROCEEDING:
echo   1. Backup ALL important files to external drive
echo   2. Note down software licenses and keys
echo   3. Have Windows 11 product key ready
echo   4. Create bootable Windows 11 USB drive
echo.
echo 🎯 NUCLEAR RESET PROCESS:
echo   [1] Show complete step-by-step guide
echo   [2] Exit (recommended - backup first!)
echo.
set /p choice="Your choice (1-2): "

if "%choice%"=="1" goto show_guide
if "%choice%"=="2" goto exit
goto invalid

:show_guide
cls
echo.
echo 🚀 NUCLEAR RESET - COMPLETE GUIDE
echo ================================================================
echo.
echo STEP 1: PREPARATION (DO THIS FIRST!)
echo   💾 Backup all important files to external drive
echo   🔑 Write down Windows 11 product key
echo   📱 Note software licenses you'll need to reinstall
echo   🛠️ Create Windows 11 bootable USB drive
echo.
echo STEP 2: CREATE BOOTABLE USB
echo   1. Download Windows 11 from Microsoft website
echo   2. Use Media Creation Tool or Rufus
echo   3. Create bootable USB (8GB+ required)
echo   4. Test USB boots properly
echo.
echo STEP 3: NUCLEAR WIPE PROCESS
echo   1. Insert bootable USB drive
echo   2. Restart PC and press F12 (or F2/DEL for BIOS)
echo   3. Select USB drive from boot menu
echo   4. Boot into Windows 11 installer
echo   5. Select "Custom: Install Windows only (advanced)"
echo   6. DELETE ALL PARTITIONS (this nukes everything!)
echo   7. Select unallocated space
echo   8. Click "New" to create fresh partition
echo   9. Click "Next" - Windows installs clean
echo.
echo STEP 4: POST-INSTALL
echo   1. Complete Windows 11 setup
echo   2. Install drivers and updates
echo   3. Install NEXUS AI system
echo   4. Restore backed up files
echo.
echo 🎉 RESULT: Brand new PC with NEXUS AI optimization!
echo.
pause
goto menu

:invalid
echo Invalid choice. Please select 1 or 2.
pause
goto menu

:menu
echo.
echo Return to menu? (Y/N)
set /p return=
if /i "%return%"=="Y" cls && goto start
goto exit

:exit
echo.
echo 🛡️ NUCLEAR RESET CANCELLED
echo.
echo Smart choice! Always backup first.
echo When ready, run this again for the complete guide.
echo.
pause
exit /b 0

:start
goto show_guide