@echo off
echo [%time%] Starting Explorer cache cleanup...
taskkill /f /im explorer.exe 2>nul
del /f "%userprofile%\AppData\Local\IconCache.db" 2>nul
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\iconcache*" 2>nul
del /f "%userprofile%\AppData\Local\Microsoft\Windows\Explorer\thumbcache*" 2>nul
start explorer.exe
echo [%time%] Explorer cache cleanup completed.
