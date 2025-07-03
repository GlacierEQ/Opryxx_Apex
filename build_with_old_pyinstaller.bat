@echo off
echo Installing older version of PyInstaller...
pip uninstall -y pyinstaller
pip install "pyinstaller<5.8.0"

echo Cleaning up previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "MEGA_OPRYXX.spec" del "MEGA_OPRYXX.spec"

echo Running PyInstaller with minimal options...
pyinstaller ^
    --name MEGA_OPRYXX ^
    --onefile ^
    --noconfirm ^
    --clean ^
    --log-level WARN ^
    --noupx ^
    --windowed ^
    --icon=NONE ^
    gui/MEGA_OPRYXX.py

echo.
if exist "dist\MEGA_OPRYXX.exe" (
    echo Build successful!
    echo Executable created at: %CD%\dist\MEGA_OPRYXX.exe
) else (
    echo Build failed. Check the output above for errors.
)

pause
