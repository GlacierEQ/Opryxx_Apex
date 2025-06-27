@echo off
echo [STATUS] OPRYXX: Resetting network stack...
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /renew
ipconfig /flushdns
echo [STATUS] OPRYXX: Network stack reset complete.
exit /b 0