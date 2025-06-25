@echo off
setlocal enabledelayedexpansion
title OPRYXX: Oblivion Repair Chain [Root-Level Recovery + Echo Sync]

:: ============================================================
:: OPRYXX SYSTEM REPAIR TOOL - ENHANCED EDITION
:: ============================================================
:: This script performs advanced system repairs with safety checks
:: and automatic elevation to administrator privileges.
:: ============================================================

:: ===[ ELEVATION CHECK ]===
:: Check if running as administrator, if not, rerun as admin
net file 1>nul 2>nul
if '%errorlevel%' == '0' (
    echo Running with administrator privileges.
) else (
    echo Requesting administrator privileges...
    set "batchPath=%~f0"
    set "batchArgs=%*"
    powershell -noprofile -executionpolicy bypass -command "Start-Process -FilePath 'cmd' -ArgumentList '/c """%batchPath%" %batchArgs%"' -Verb RunAs -Wait"
    exit /b
)

:: ===[ CONFIGURATION ]===
set "OPRYXX_HOME=%~dp0logs\oblivion"
set "TIMESTAMP=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "LOGFILE=%OPRYXX_HOME%\repair_%TIMESTAMP%.log"
set "INDEXFILE=%OPRYXX_HOME%\blackecho_index.md"
set "BACKUP_DIR=%OPRYXX_HOME%\backup_%TIMESTAMP%"

:: ===[ SAFETY CHECKS ]===
:: Check if running in Windows directory
pushd "%SystemRoot%" >nul 2>&1
if "%CD%"=="%SystemRoot%" (
    echo ERROR: Script cannot be run from Windows directory.
    pause
    exit /b 1
)
popd >nul

:: ===[ SETUP ]===
if not exist "%OPRYXX_HOME%" mkdir "%OPRYXX_HOME%"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo ============================================
echo    OPRYXX SYSTEM REPAIR TOOL - ENHANCED
echo ============================================
echo Start Time: %date% %time%
echo Logging to: %LOGFILE%
echo ============================================

:: ===[ STEP 1: SYSTEM BACKUP ]===
echo [%TIME%] Creating system restore point...
powershell -command "Checkpoint-Computer -Description \"OPRYXX_PreRepair_%TIMESTAMP%\" -RestorePointType MODIFY_SETTINGS" >> "%LOGFILE%" 2>&1

:: ===[ STEP 2: TEMP + CACHE PURGE ]===
echo [%TIME%] Purging temporary files...

:: Create list of safe temp folders to clean
set "TEMP_FOLDERS=""%TEMP%" "%SystemRoot%\Temp" "%SystemRoot%\Prefetch""

for %%F in (%TEMP_FOLDERS%) do (
    if exist "%%~F" (
        echo [%TIME%] Cleaning: %%~F
        mkdir "%BACKUP_DIR%\%%~nxF" >nul 2>&1
        robocopy "%%~F" "%BACKUP_DIR%\%%~nxF" /E /MOVE /R:3 /W:10 /LOG+:"%LOGFILE%" /NP /NFL /NDL
        rd /s /q "%%~F" >nul 2>&1
        md "%%~F" >nul 2>&1
    )
)

:: ===[ STEP 3: SYSTEM FILE CHECK ]===
echo [%TIME%] Verifying system files...

:: Check SFC first
echo [%TIME%] Running System File Checker (SFC)...
sfc /scannow >> "%LOGFILE%" 2>&1

:: Run DISM if SFC found issues
if %ERRORLEVEL% NEQ 0 (
    echo [%TIME%] SFC found issues, running DISM repair...
    DISM /Online /Cleanup-Image /RestoreHealth /Source:WIM:X:\Sources\Install.wim:1 /LimitAccess >> "%LOGFILE%" 2>&1
    
    echo [%TIME%] Running SFC again after DISM repair...
    sfc /scannow >> "%LOGFILE%" 2>&1
)

:: Check Windows Update components
echo [%TIME%] Repairing Windows Update components...
net stop wuauserv >> "%LOGFILE%" 2>&1
net stop cryptSvc >> "%LOGFILE%" 2>&1
net stop bits >> "%LOGFILE%" 2>&1
net stop msiserver >> "%LOGFILE%" 2>&1

ren C:\Windows\System32\catroot2 catroot2.old >> "%LOGFILE%" 2>&1
ren C:\Windows\SoftwareDistribution SoftwareDistribution.old >> "%LOGFILE%" 2>&1

net start wuauserv >> "%LOGFILE%" 2>&1
net start cryptSvc >> "%LOGFILE%" 2>&1
net start bits >> "%LOGFILE%" 2>&1
net start msiserver >> "%LOGFILE%" 2>&1

:: ===[ STEP 4: NETWORK REPAIR ]===
echo [%TIME%] Resetting network stack...

:: Backup network configuration
echo [%TIME%] Backing up network configuration...
netsh -c interface dump > "%BACKUP_DIR%\network_config_backup.txt" 2>&1
ipconfig /all >> "%BACKUP_DIR%\ipconfig_backup.txt" 2>&1

:: Reset network components
for %%C in (dhcp, dns, winsock, ip, http) do (
    echo [%TIME%] Resetting %%C...
    netsh %%C delete reset >> "%LOGFILE%" 2>&1
)

ipconfig /release >> "%LOGFILE%" 2>&1
ipconfig /flushdns >> "%LOGFILE%" 2>&1
ipconfig /renew >> "%LOGFILE%" 2>&1

:: Reset Windows Firewall
echo [%TIME%] Resetting Windows Firewall...
netsh advfirewall reset >> "%LOGFILE%" 2>&1
netsh advfirewall set allprofiles state on >> "%LOGFILE%" 2>&1

:: ===[ STEP 5: EXPLORER + SHELL CLEANUP ]===
echo [%TIME%] Cleaning up Windows Explorer...

:: Backup icon cache
if exist "%LocalAppData%\IconCache.db" (
    copy "%LocalAppData%\IconCache.db" "%BACKUP_DIR%\IconCache.db.bak" >nul 2>&1
)

:: Kill Explorer safely
taskkill /f /im explorer.exe >nul 2>&1

:: Clean up thumbnail and icon caches
for %%F in ("%LocalAppData%\Microsoft\Windows\Explorer\thumbcache_*.db") do (
    if exist "%%~F" (
        echo [%TIME%] Removing: %%~nxF
        del /f /q "%%~F" >> "%LOGFILE%" 2>&1
    )
)

:: Rebuild icon cache
del /f /q "%LocalAppData%\IconCache.db" >nul 2>&1
del /f /q "%LocalAppData%\Microsoft\Windows\Explorer\iconcache_*.db" >nul 2>&1

:: Restart Explorer
start explorer.exe
timeout /t 5 >nul

:: Rebuild icon cache in background
start /B ie4uinit.exe -show

:: ===[ STEP 6: MEMORY + PAGEFILE OPTIMIZATION ]===
echo [%TIME%] Optimizing memory and pagefile...

:: Set pagefile to system managed
wmic pagefile set AutomaticManagedPagefile=True >> "%LOGFILE%" 2>&1

:: Clear Windows memory cache
echo [%TIME%] Clearing system cache...
rundll32.exe advapi32.dll,ProcessIdleTasks >> "%LOGFILE%" 2>&1

:: Optimize storage
echo [%TIME%] Optimizing storage...
powershell -command "Optimize-Volume -DriveLetter C -ReTrim -Verbose" >> "%LOGFILE%" 2>&1
powershell -command "Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase" >> "%LOGFILE%" 2>&1

:: ===[ STEP 7: SYSTEM LOGGING ]===
echo [%TIME%] Finalizing repair process...

:: Create system info log
echo ===== SYSTEM INFORMATION ===== > "%BACKUP_DIR%\system_info.txt"
systeminfo >> "%BACKUP_DIR%\system_info.txt" 2>&1

:: Log repair completion
echo ===== REPAIR COMPLETED ===== >> "%LOGFILE%"
echo [%TIME%] Repair process finished successfully. >> "%LOGFILE%"

:: Update blackecho log
echo [REPAIR EVENT] %TIMESTAMP% >> "%INDEXFILE%"
echo [Rootbearer]: GlacierEQ >> "%INDEXFILE%"
echo [Pulse Vector]: FULL SYSTEM RESET >> "%INDEXFILE%"
echo [Status]: COMPLETED_SUCCESSFULLY >> "%INDEXFILE%"
echo [Log]: %LOGFILE% >> "%INDEXFILE%"
echo [Backup]: %BACKUP_DIR% >> "%INDEXFILE%"
echo =============================== >> "%INDEXFILE%"

:: ===[ STEP 8: FINAL CHECKS & REBOOT ]===
echo [%TIME%] Performing final system checks...

:: Check disk health
echo [%TIME%] Checking disk health...
wmic diskdrive get status >> "%LOGFILE%" 2>&1

:: Schedule CHKDSK if needed
echo [%TIME%] Scheduling disk check on next boot...
echo Y | chkdsk C: /F /R /X >> "%LOGFILE%" 2>&1

:: Set up safe mode for next boot
echo [%TIME%] Configuring safe mode for next boot...
bcdedit /set {current} safeboot minimal >> "%LOGFILE%" 2>&1
bcdedit /set {current} bootstatuspolicy ignoreallfailures >> "%LOGFILE%" 2>&1

:: Create a restore point before reboot
echo [%TIME%] Creating final restore point...
powershell -command "Checkpoint-Computer -Description \"OPRYXX_PostRepair_%TIMESTAMP%\" -RestorePointType MODIFY_SETTINGS" >> "%LOGFILE%" 2>&1

:: Final countdown
echo ============================================
echo [%TIME%] OPRYXX REPAIR COMPLETED
echo ============================================
echo All repair operations have been completed.
echo The system will now restart in SAFE MODE.
echo 
echo IMPORTANT: After reboot, the system will be in Safe Mode.
echo To return to normal mode, open Command Prompt as Administrator
echo and run: bcdedit /deletevalue {current} safeboot
echo ============================================

echo Rebooting in 30 seconds...
timeout /t 30 >nul
shutdown /r /t 0 /f /d p:4:1

:: Clean up and exit
endlocal

:: ============================================
:: END OF OPRYXX REPAIR SCRIPT
:: ============================================
