@echo off
echo [OPRYXX_STATUS] Starting Deep System Analysis...

:: System Information
echo Gathering system information...
systeminfo > "%TEMP%\opryxx_sysinfo.txt" 2>&1

:: Disk Information
echo Analyzing disk space...
wmic logicaldisk get caption,description,providername,size,freespace > "%TEMP%\opryxx_disk.txt" 2>&1

:: Running Processes
echo Analyzing running processes...
tasklist /v > "%TEMP%\opryxx_processes.txt" 2>&1

:: Network Information
echo Analyzing network configuration...
ipconfig /all > "%TEMP%\opryxx_network.txt" 2>&1
netstat -ano > "%TEMP%\opryxx_netstat.txt" 2>&1

:: System Event Logs (Last 5 entries)
echo Extracting system event logs...
wevtutil qe System /c:5 /rd:true /f:text > "%TEMP%\opryxx_syslog.txt" 2>&1
wevtutil qe Application /c:5 /rd:true /f:text > "%TEMP%\opryxx_applog.txt" 2>&1

:: Startup Items
echo Analyzing startup items...
wmic startup get caption,command,location,user > "%TEMP%\opryxx_startup.txt" 2>&1

echo [OPRYXX_STATUS] Deep System Analysis Complete.
exit /b 0
