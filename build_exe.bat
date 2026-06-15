@echo off
chcp 65001 >nul
title Build AI Learning Coach Launcher EXE
cd /d "%~dp0"
echo This only builds the launcher exe. It does not package Python or app dependencies.
python -m pip install pyinstaller
python -m PyInstaller --onefile --name AI_Learning_Coach_Launcher run_app.py
if exist dist\AI_Learning_Coach_Launcher.exe copy /Y dist\AI_Learning_Coach_Launcher.exe .\AI_Learning_Coach_Launcher.exe
pause
