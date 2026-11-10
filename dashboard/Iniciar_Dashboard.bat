@echo off
chcp 65001 >nul
title Dashboard Sensor de Odor (ESP32 + SQLite + Firebase)
cd /d "%~dp0"

REM Verifica se o servidor já está ativo na porta 8080
powershell -NoProfile -Command "try { $null = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/api/state' -UseBasicParsing -TimeoutSec 1; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    start "" "http://localhost:8080"
    exit /b 0
)

set "PY_EXE=python"
if exist "%~dp0..\.venv\Scripts\python.exe" set "PY_EXE=%~dp0..\.venv\Scripts\python.exe"
if exist "%~dp0.venv\Scripts\python.exe" set "PY_EXE=%~dp0.venv\Scripts\python.exe"

start "Servidor Sensor de Odor (Porta 8080)" /min "%PY_EXE%" "%~dp0server.py"
timeout /t 2 /nobreak >nul
start "" "http://localhost:8080"
exit /b 0
