@echo off
echo OPRYXX System Installer
echo ======================

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    winget install Python.Python.3.11
    if errorlevel 1 (
        echo Please install Python manually from python.org
        pause
        exit /b 1
    )
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install psutil numpy torch torchvision torchaudio flask flask-socketio matplotlib wmi pyopencl

REM Create desktop shortcut
echo Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
echo @echo off > "%desktop%\OPRYXX System.bat"
echo cd /d "%~dp0" >> "%desktop%\OPRYXX System.bat"
echo python OPRYXX_LAUNCHER.py >> "%desktop%\OPRYXX System.bat"

echo.
echo Installation complete!
echo Double-click "OPRYXX System.bat" on your desktop to start
pause
