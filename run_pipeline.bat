@echo off
REM FinancePy Daily Pipeline - Scheduled Task Launcher
REM This script is designed to run as a Windows Scheduled Task at 1 PM daily
REM It uses the local .venv (no conda overhead)

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Get today's date in YYYY-MM-DD format
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)

REM Path to .venv Python
set PYTHON=.venv\Scripts\python.exe

REM Path to logs
set LOGS_DIR=logs
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
set LOG_FILE=%LOGS_DIR%\pipeline_%mydate%.log

REM Run pipeline with logging to both console and file
echo. >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Pipeline Run: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

REM Execute pipeline
"%PYTHON%" run_daily.py --date %mydate% --log-level INFO >> "%LOG_FILE%" 2>&1

REM Check exit code
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Pipeline completed at %time% >> "%LOG_FILE%"
    exit /b 0
) else (
    echo [ERROR] Pipeline failed with code %ERRORLEVEL% at %time% >> "%LOG_FILE%"
    exit /b 1
)
