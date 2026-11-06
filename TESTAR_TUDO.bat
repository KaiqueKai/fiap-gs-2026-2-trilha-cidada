@echo off
cd /d "%~dp0"
title Trilha Cidada - Bateria de Testes
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0TESTAR_TUDO.ps1"
set RESULTADO=%ERRORLEVEL%
echo.
if not "%RESULTADO%"=="0" echo A bateria encontrou falhas. Consulte o resultado acima.
pause
exit /b %RESULTADO%
