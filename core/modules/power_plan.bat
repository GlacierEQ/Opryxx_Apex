@echo off
echo [%time%] Setting High Performance power plan...
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
echo [%time%] Power plan set.
