@echo off
echo [%time%] Starting temporary files cleanup...
for %%D in (%TEMP% %SystemRoot%\Temp %USERPROFILE%\AppData\Local\Temp) do (
    if exist "%%D" (
        del /q /f "%%D\*.*" 2>nul
        for /d %%p in ("%%D\*.*") do rd /s /q "%%p" 2>nul
    )
)
echo [%time%] Temp cleanup completed.
