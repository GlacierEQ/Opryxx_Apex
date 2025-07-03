@echo off
title ULTIMATE UNIFIED SYSTEM LAUNCHER
color 0A

echo ================================================
echo        ULTIMATE UNIFIED SYSTEM LAUNCHER
echo     GPU/NPU Priority • Intelligent AI • Full-Stack
echo ================================================
echo.

echo [STEP 1/4] Installing required packages...
python -m pip install psutil numpy torch --quiet --disable-pip-version-check
if errorlevel 1 (
    echo Installing basic packages only...
    python -m pip install psutil numpy --quiet --disable-pip-version-check
)

echo [STEP 2/4] Checking system compatibility...
python -c "import psutil, numpy; print('✅ Core packages ready')"
if errorlevel 1 (
    echo ❌ Package installation failed
    pause
    exit /b 1
)

echo [STEP 3/4] Initializing GPU/NPU acceleration...
python -c "
try:
    import torch
    if torch.cuda.is_available():
        print('✅ GPU acceleration available:', torch.cuda.get_device_name(0))
    else:
        print('⚠️ GPU not available - CPU fallback mode')
except:
    print('⚠️ PyTorch not available - CPU fallback mode')
"

echo [STEP 4/4] Launching Ultimate Unified System...
echo.
echo ================================================
echo            SYSTEM STARTING...
echo ================================================
echo.

python ULTIMATE_UNIFIED_SYSTEM.py

echo.
echo Ultimate Unified System has been closed.
pause