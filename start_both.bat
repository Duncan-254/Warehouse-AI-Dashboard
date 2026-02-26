@echo off
title Warehouse AI - Full System

echo.
echo ===============================================
echo   Starting Full Attendance System
echo ===============================================
echo.

echo [1/2] Launching face detection...
start "Face Detection" python main.py

echo.
echo [2/2] Launching dashboard...
timeout /t 10 /nobreak >nul

start "Dashboard" cmd /k "C:\Users\duncan\AppData\Local\Microsoft\WindowsApps\python3.13.exe" -m streamlit run dashboard.py

echo.
echo ===============================================
echo   System running!
echo   - Detection window: shows camera + logs
echo   - Dashboard: opens in browser[](http://localhost:8501)
echo ===============================================
pause