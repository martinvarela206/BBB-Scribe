@echo off
title BBB-Scribe - Descargador de Clases BigBlueButton
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" cli.py %*
) else (
    python download.py %*
)
pause
