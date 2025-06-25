@echo off
echo [%time%] Starting network stack reset...
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
ipconfig /release
ipconfig /renew
echo [%time%] Network stack reset completed.
