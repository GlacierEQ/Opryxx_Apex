@echo off
echo [%time%] Starting file organization...
set "DESKTOP=%USERPROFILE%\Desktop"
set "DOWNLOADS=%USERPROFILE%\Downloads"
mkdir "%DESKTOP%\Shortcuts" 2>nul
move /Y "%DESKTOP%\*.lnk" "%DESKTOP%\Shortcuts\" 2>nul
mkdir "%DOWNLOADS%\Images" "%DOWNLOADS%\Documents" "%DOWNLOADS%\Videos" "%DOWNLOADS%\Music" "%DOWNLOADS%\Others" 2>nul
move /Y "%DOWNLOADS%\*.jpg" "%DOWNLOADS%\*.png" "%DOWNLOADS%\*.gif" "%DOWNLOADS%\Images\" 2>nul
move /Y "%DOWNLOADS%\*.doc" "%DOWNLOADS%\*.docx" "%DOWNLOADS%\*.pdf" "%DOWNLOADS%\*.txt" "%DOWNLOADS%\Documents\" 2>nul
move /Y "%DOWNLOADS%\*.mp4" "%DOWNLOADS%\*.avi" "%DOWNLOADS%\*.mkv" "%DOWNLOADS%\Videos\" 2>nul
move /Y "%DOWNLOADS%\*.mp3" "%DOWNLOADS%\*.wav" "%DOWNLOADS%\*.flac" "%DOWNLOADS%\Music\" 2>nul
move /Y "%DOWNLOADS%\*.*" "%DOWNLOADS%\Others\" 2>nul
echo [%time%] File organization completed.
