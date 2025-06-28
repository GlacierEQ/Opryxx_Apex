@echo off
title NEXUS AI Performance Dashboard
color 0B
cls

echo.
echo ================================================================
echo           NEXUS AI PERFORMANCE DASHBOARD
echo ================================================================
echo.
echo 📊 PERFORMANCE VISUALIZATION FEATURES:
echo.
echo   🚀 Run Benchmark - Execute comprehensive performance tests
echo   📈 View History - Track performance over time
echo   💾 Export Results - Save results to JSON format
echo   📊 Real-time Scoring - 0-100 performance rating
echo   🎮 GPU Monitoring - Hardware acceleration tracking
echo   💾 Memory Analysis - Detailed memory operation metrics
echo.
echo 🎯 BENCHMARK CATEGORIES:
echo   Memory Operations (40 points) - Array, object, string ops
echo   GPU Performance (30 points) - Hardware acceleration
echo   System Optimization (20 points) - Optimization speed
echo   Leak Detection (10 points) - Memory leak detection
echo.
echo 🏆 PERFORMANCE RATINGS:
echo   80-100 points - EXCELLENT PERFORMANCE
echo   60-79 points  - GOOD PERFORMANCE
echo   Below 60      - NEEDS OPTIMIZATION
echo.
echo Launching Performance Dashboard...
echo.

python performance_dashboard.py

pause