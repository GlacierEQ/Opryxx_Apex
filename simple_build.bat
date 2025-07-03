@echo off
echo Building MEGA_OPRYXX executable...

REM Clean up old build directories
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "MEGA_OPRYXX.spec" del "MEGA_OPRYXX.spec"

REM Run PyInstaller with minimal options
pyinstaller ^
    --name MEGA_OPRYXX ^
    --onefile ^
    --noconfirm ^
    --clean ^
    --log-level WARN ^
    gui/MEGA_OPRYXX.py

echo.
if exist "dist\MEGA_OPRYXX.exe" (
    echo Build successful!
    echo Executable created at: %CD%\dist\MEGA_OPRYXX.exe
) else (
    echo Build failed. Check the output above for errors.
)

pause
