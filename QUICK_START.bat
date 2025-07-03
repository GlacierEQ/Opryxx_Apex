@echo off
title OPRYXX QUICK START
color 0A

echo ================================================
echo           OPRYXX QUICK START INSTALLER
echo ================================================
echo.
echo This will create a complete OPRYXX installer package
echo with executable (.exe) file that you can run anywhere.
echo.
echo Press any key to start building the installer...
pause >nul

echo.
echo [1/3] Installing required packages...
python -m pip install pyinstaller psutil --quiet

echo [2/3] Creating installer package...
python CREATE_INSTALLER.py

echo.
echo [3/3] INSTALLATION COMPLETE!
echo.
echo ================================================
echo              HOW TO INSTALL OPRYXX
echo ================================================
echo.
echo 1. Go to the "OPRYXX_INSTALLER" folder
echo 2. RIGHT-CLICK on "INSTALL.bat"
echo 3. Select "Run as administrator"
echo 4. Follow the installation prompts
echo 5. Launch OPRYXX from Desktop shortcut
echo.
echo ================================================
echo.
echo Opening installer folder now...
start "" "OPRYXX_INSTALLER"

echo.
echo OPRYXX installer package is ready!
echo Right-click INSTALL.bat and run as administrator.
echo.
pause