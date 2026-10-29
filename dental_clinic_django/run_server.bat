@echo off
title Roots Dental & Buds Child Clinic Server
echo ===================================================
echo Starting Roots Dental & Buds Child Clinic Local Server...
echo ===================================================
cd /d "%~dp0"
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
pause
