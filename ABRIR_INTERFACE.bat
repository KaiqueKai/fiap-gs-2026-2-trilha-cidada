@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 main.py --gui
) else (
    python main.py --gui
)
if errorlevel 1 pause
