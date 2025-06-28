@echo off
title ENHANCED PERFORMANCE AI - GPU/NPU Accelerated
color 0E
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██       ENHANCED PERFORMANCE AI - HARDWARE ACCELERATED      ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🚀 HARDWARE ACCELERATION FEATURES:
echo.
echo   🎮 GPU Acceleration - NVIDIA/AMD GPU optimization
echo   🧠 NPU Acceleration - Intel AI processing units
echo   💾 Advanced Memory - Aggressive memory optimization
echo   ⚡ Performance Modes - BALANCED/PERFORMANCE/ULTRA/EXTREME
echo   🔧 Memory Leak Detection - Auto-terminate memory hogs
echo   🚀 GPU Memory Management - Optimize VRAM usage
echo.
echo 🎯 PERFORMANCE MODES:
echo   BALANCED  - 60 second optimization cycles
echo   PERFORMANCE - 30 second cycles
echo   ULTRA     - 15 second cycles  
echo   EXTREME   - 5 second cycles (maximum performance)
echo.
echo 💡 HARDWARE DETECTED:
python -c "from enhancements.gpu_acceleration import GPUAcceleration; gpu=GPUAcceleration()"
echo.
echo Launching Enhanced Performance AI...
echo.

python ENHANCED_PERFORMANCE_AI.py

if %errorlevel% neq 0 (
    echo.
    echo Error launching Enhanced Performance AI
    echo Installing required dependencies...
    pip install psutil
    echo.
    echo Retrying launch...
    python ENHANCED_PERFORMANCE_AI.py
)

pause