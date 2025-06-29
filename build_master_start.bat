@echo off
echo ===============================================
echo    OPRYXX MASTER START - BUILD UTILITY
echo    Enterprise-Grade System Optimizer
echo ===============================================
echo.

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Setting up build environment...

:: Create and activate virtual environment
if not exist "venv" (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat

:: Install required packages with specific versions for stability
echo [2/5] Installing dependencies...
pip install --upgrade pip
pip install pyinstaller==5.13.0
pip install pywin32==306
pip install wmi==1.5.1
pip install psutil==5.9.5
pip install pywin32-ctypes==0.2.0

:: Create build directory
if not exist "build" mkdir build

:: Create the executable with optimized settings
echo [3/5] Building executable...
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "OPRYXX_Master_Start" ^
    --icon=NONE ^
    --add-data "master_start.py;." ^
    --distpath ".\dist" ^
    --workpath ".\build" ^
    --specpath ".\build" ^
    --clean ^
    --noconsole ^
    --upx-dir=.\upx ^
    master_start.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

:: Create version file
echo [4/5] Creating version info...
echo # OPRYXX Master Start Version Information> "dist\version.txt"
echo Version: 1.0.0>> "dist\version.txt"
echo Build Date: %date% %time%>> "dist\version.txt"
echo Build Machine: %COMPUTERNAME%>> "dist\version.txt"

:: Create final package
echo [5/5] Creating final package...
if not exist "dist\package" mkdir "dist\package"
copy "dist\OPRYXX_Master_Start.exe" "dist\package\"
copy "MASTER_START_README.md" "dist\package\README.txt"
copy "dist\version.txt" "dist\package\"

:: Create a zip archive
powershell -Command "Compress-Archive -Path 'dist\package\*' -DestinationPath 'dist\OPRYXX_Master_Start_Package.zip' -Force"

:: Final status
echo.
echo ===============================================
echo    BUILD COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo Executable: %CD%\dist\OPRYXX_Master_Start.exe
echo Package:    %CD%\dist\OPRYXX_Master_Start_Package.zip
echo.
echo [INFO] To run the application:
echo       1. Navigate to the 'dist' folder
echo       2. Right-click on OPRYXX_Master_Start.exe
echo       3. Select 'Run as administrator'
echo.
pause
