@echo off
title Push to GitHub - Roots Dental
color 0b
echo ===================================================================
echo   Pushing Roots Dental and Buds Child Clinic to GitHub
echo   Repository: https://github.com/Irfanshkhdev/dental.git
echo ===================================================================
echo.

set "PATH=C:\Users\Asus vivobook\AppData\Local\Programs\MinGit\cmd;C:\Users\Asus vivobook\AppData\Local\Programs\MinGit\mingw64\bin;%PATH%"
cd /d "c:\Users\Asus vivobook\Downloads\dental_clinic_django-v2 (1)"

echo [*] Checking Git version...
git.exe --version
echo.

echo [*] Pushing branch 'main' to GitHub origin...
echo (If a browser window appears, click 'Sign in with your browser' to authorize)
echo.
git.exe push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================================
    echo   SUCCESS! All code and photos pushed to GitHub!
    echo   View your repository at: https://github.com/Irfanshkhdev/dental
    echo ===================================================================
) else (
    echo.
    echo ===================================================================
    echo   Push paused or needs credentials.
    echo   You can also generate a GitHub Personal Access Token at:
    echo   https://github.com/settings/tokens/new?scopes=repo
    echo ===================================================================
)

echo.
pause
