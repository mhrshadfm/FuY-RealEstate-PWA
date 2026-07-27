@echo off
title Alborz Filing Monitor Installer

echo ==========================================
echo     Alborz Filing Monitor Installer
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/7] Checking Python...

python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo Python is not installed.
    echo Please install Python 3.11+
    pause
    exit
)

echo.
echo [2/7] Creating Virtual Environment...

if not exist venv (
    python -m venv venv
)

echo.
echo [3/7] Activating Virtual Environment...

call venv\Scripts\activate.bat

echo.
echo [4/7] Updating pip...

python -m pip install --upgrade pip

echo.
echo [5/7] Installing Requirements...

pip install -r requirements.txt

echo.
echo [6/7] Creating Required Folders...

if not exist logs mkdir logs
if not exist daily mkdir daily
if not exist state mkdir state

echo.
echo [7/7] Installation Finished.

echo.

pause