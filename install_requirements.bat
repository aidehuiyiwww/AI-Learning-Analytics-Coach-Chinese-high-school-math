@echo off
chcp 65001 >nul
title Install AI Learning Coach Requirements
cd /d "%~dp0"
echo Checking and installing required Python libraries...
python install_requirements.py
if errorlevel 1 (
  echo.
  echo Installation failed. Please check Python and pip.
  pause
  exit /b 1
)
echo.
echo Done.
pause
