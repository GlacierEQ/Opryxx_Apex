@echo off
echo [%time%] Starting memory management optimization...
powershell -Command "& {Clear-DnsClientCache; Write-Host 'DNS Cache cleared'}"
wmic computersystem where name="%computername%" set AutomaticManagedPagefile=True
echo [%time%] Memory management optimization completed.
