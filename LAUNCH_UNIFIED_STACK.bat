@echo off
echo ================================================
echo    UNIFIED FULL STACK SYSTEM LAUNCHER
echo ================================================
echo.

echo [1/3] Verifying system components...
python VERIFY_SIMPLE.py
if errorlevel 1 (
    echo ERROR: System verification failed!
    pause
    exit /b 1
)

echo.
echo [2/3] System verification PASSED
echo [3/3] Launching Unified Full Stack GUI...
echo.

python UNIFIED_FULL_STACK_GUI.py

echo.
echo Unified Full Stack System has been closed.
pause