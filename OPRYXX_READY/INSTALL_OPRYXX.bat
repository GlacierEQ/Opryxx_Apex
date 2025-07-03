@echo off
title OPRYXX INSTALLER
cls
echo.
echo ========================================
echo         OPRYXX SYSTEM INSTALLER
echo ========================================
echo.
echo This will install OPRYXX Unified System
echo.
pause

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\OPRYXX
echo Creating directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
copy /Y "*.py" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.txt" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.bat" "%INSTALL_DIR%\" >nul 2>&1

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
echo @echo off > "%DESKTOP%\OPRYXX.bat"
echo cd /d "%INSTALL_DIR%" >> "%DESKTOP%\OPRYXX.bat"
echo call START_OPRYXX.bat >> "%DESKTOP%\OPRYXX.bat"

echo.
echo ========================================
echo     INSTALLATION COMPLETED!
echo ========================================
echo.
echo OPRYXX has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: OPRYXX.bat
echo.
echo To start OPRYXX:
echo 1. Double-click OPRYXX.bat on desktop
echo 2. Or run START_OPRYXX.bat from install folder
echo.
pause
