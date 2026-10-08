@echo off
title BBB-Scribe - Transcriptor de Clases a Texto
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" transcribe.py %*
) else (
    python transcribe.py %*
)
pause
