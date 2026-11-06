@echo off
cd /d "%~dp0"
title Trilha Cidada - Atendimento no Terminal
where py >nul 2>nul
if not errorlevel 1 (
    py -3 main.py --terminal
) else (
    python main.py --terminal
)
echo.
echo Atendimento encerrado. Esta janela sera mantida para voce consultar o resultado.
pause
