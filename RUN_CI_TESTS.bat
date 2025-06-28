@echo off
title NEXUS AI CI/CD Performance Tests
color 0E
cls

echo.
echo ================================================================
echo           NEXUS AI CI/CD PERFORMANCE TESTS
echo ================================================================
echo.
echo 🔄 CONTINUOUS INTEGRATION TESTING:
echo.
echo   Performance Thresholds:
echo   • Memory Operations: < 50ms average
echo   • GPU Acceleration: > 50 score minimum
echo   • System Optimization: < 500ms
echo   • Leak Detection: < 2000ms
echo   • Overall Score: > 60 minimum
echo.
echo 📊 Test Categories:
echo   ✅ Memory Operations Validation
echo   ✅ GPU Performance Validation  
echo   ✅ System Optimization Speed
echo   ✅ Memory Leak Detection Speed
echo   ✅ Overall Performance Score
echo.
echo 📄 Generates: nexus_ci_report.json
echo.
echo Running CI/CD Performance Tests...
echo.

python ci_cd_integration.py

if %errorlevel%==0 (
    echo.
    echo ✅ CI/CD TESTS PASSED
    echo Performance meets all thresholds
) else (
    echo.
    echo ❌ CI/CD TESTS FAILED
    echo Performance below required thresholds
    echo Check nexus_ci_report.json for details
)

echo.
pause