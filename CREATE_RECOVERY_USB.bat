@echo off
title OPRYXX Recovery USB Creator
color 0A
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██           OPRYXX RECOVERY USB CREATOR                     ██
echo ██          Hiren's Boot + OPRYXX Integration                ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🛠️ CREATES ULTIMATE RECOVERY USB
echo.
echo What this USB will do:
echo   🚀 Boot when your PC fails to start
echo   🤖 Auto-detect and fix boot issues
echo   💾 Backup your data automatically
echo   🔧 Automated Windows 11 reinstall
echo   💿 Restore all drivers automatically
echo   🛠️ Access to Hiren's Boot tools
echo.
echo 📋 Requirements:
echo   • 16GB+ USB drive (will be erased)
echo   • Internet connection
echo   • Administrator privileges
echo.
echo ⚠️ WARNING: USB drive will be completely erased!
echo.
echo Insert USB drive and press any key to continue...
pause >nul

echo.
echo 🔍 Detecting USB drives...
wmic logicaldisk where drivetype=2 get deviceid,size,volumename

echo.
echo 🚀 Creating OPRYXX Recovery USB...
echo.
echo Step 1: Downloading Hiren's Boot PE...
echo Step 2: Backing up system drivers...
echo Step 3: Creating integrated recovery USB...
echo Step 4: Adding OPRYXX automation...
echo.

python recovery/hirens_opryxx_integration.py

if %errorlevel%==0 (
    echo.
    echo ✅ RECOVERY USB CREATED SUCCESSFULLY!
    echo.
    echo 🎯 HOW TO USE:
    echo   1. When PC fails to boot, insert USB
    echo   2. Boot from USB (press F12 during startup)
    echo   3. Select "OPRYXX Recovery System"
    echo   4. Choose automated recovery option
    echo   5. OPRYXX handles everything automatically!
    echo.
    echo 🚨 BOOT FAILURE RECOVERY:
    echo   • PC won't start? Boot from this USB
    echo   • Corrupted Windows? Auto-reinstall
    echo   • Missing drivers? Auto-restore
    echo   • Data backup? Automatic
    echo.
    echo 💡 TIP: Keep this USB safe - it's your ultimate recovery tool!
) else (
    echo.
    echo ❌ Error creating recovery USB
    echo Please run as Administrator and try again
)

echo.
pause