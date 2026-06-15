@echo off
chcp 65001 >nul
title AI Learning Coach
cd /d "%~dp0"
python run_app.py
