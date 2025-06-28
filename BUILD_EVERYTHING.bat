@echo off
title Building NEXUS AI System - EXE and Installer
color 0A
cls

echo.
echo ================================================================
echo           BUILDING NEXUS AI SYSTEM
echo         Creating EXE Files and Installer
echo ================================================================
echo.

echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Creating EXE files...
python build_tools/create_exe.py

echo.
echo Step 3: Creating installer script...
python build_tools/create_installer.py

echo.
echo ================================================================
echo                    BUILD COMPLETE!
echo ================================================================
echo.
echo Created Files:
echo   dist/NEXUS_AI_Ultimate.exe - Main AI system
echo   dist/MEGA_OPRYXX.exe - Recovery system  
echo   dist/AI_Workbench.exe - AI workbench
echo   nexus_installer.nsi - Installer script
echo.
echo To create installer:
echo   1. Download NSIS from https://nsis.sourceforge.io/
echo   2. Install NSIS
echo   3. Run: makensis nexus_installer.nsi
echo.
echo Your NEXUS AI system is now ready for distribution!
echo.
pause