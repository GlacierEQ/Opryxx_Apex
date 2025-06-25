:: OPRYXX_HOME 4.0+ Supernova Edition
@echo off
setlocal enabledelayedexpansion

:: === Welcome Header ===
echo ============================================
echo     OPRYXX HOME 4.0+
echo  Supernova Edition Launcher
echo ============================================

:: === Check for administrative privileges ===
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    echo Please run it as administrator.
    pause
    exit /b
)

:: === Create backup + temp folders if missing ===
set "BACKUP=%USERPROFILE%\OpryxxBackups"
if not exist "%BACKUP%" mkdir "%BACKUP%"
echo Backup folder verified: %BACKUP%

:: === Clean temp files (optional safe locations) ===
set "TEMP=%TEMP%"
echo Cleaning TEMP folder: %TEMP%
del /q /f "%TEMP%\*.*" >nul 2>&1
for /d %%p in ("%TEMP%\*.*") do rmdir "%%p" /s /q >nul 2>&1
echo Temp folder cleaned.

:: === Check disk space (C:) ===
echo Checking disk space...
dir C:\ >nul

:: === Intelligent File Organization ===
echo Setting up intelligent file organization system...

:: --- Check if Python is installed ---
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and add it to the PATH.
    pause
    exit /b
)

:: --- Create Python script for file organization ---
echo Creating Python script for intelligent file organization...
(
echo import os
echo import shutil
echo from datetime import datetime
echo 
echo def organize_files(directory):
echo     image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
echo     document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.rtf']
echo     video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
echo     music_extensions = ['.mp3', '.wav', '.flac', '.aac']
echo     archive_extensions = ['.zip', '.rar', '.7z']
echo     software_extensions = ['.exe', '.msi', '.pkg']
echo     
echo     os.makedirs(os.path.join(directory, 'Images'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Documents'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Videos'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Music'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Archives'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Software'), exist_ok=True)
echo     os.makedirs(os.path.join(directory, 'Others'), exist_ok=True)
echo     
echo     for filename in os.listdir(directory):
echo         filepath = os.path.join(directory, filename)
echo         if os.path.isfile(filepath):
echo             file_extension = os.path.splitext(filename)[1].lower()
echo             try:
echo                 if file_extension in image_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Images', filename))
echo                 elif file_extension in document_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Documents', filename))
echo                 elif file_extension in video_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Videos', filename))
echo                 elif file_extension in music_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Music', filename))
echo                 elif file_extension in archive_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Archives', filename))
echo                 elif file_extension in software_extensions:
echo                     shutil.move(filepath, os.path.join(directory, 'Software', filename))
echo                 else:
echo                     shutil.move(filepath, os.path.join(directory, 'Others', filename))
echo                 print(f"Moved {filename} to appropriate folder")
echo             except Exception as e:
echo                 print(f"Error moving {filename}: {e}")
echo 
echo if __name__ == "__main__":
echo     downloads_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
echo     organize_files(downloads_dir)
)> organize_downloads.py

:: --- Run Python script for Downloads folder ---
echo Organizing Downloads folder using Python...
python organize_downloads.py

:: === Launch the Repair System ===
echo Launching OPRYXX_REPAIR 4.0+...
call "%~dp0OPRYXX_REPAIR.bat"

:: === Exit gracefully ===
echo.
echo OPRYXX Home complete. Exiting.
pause
