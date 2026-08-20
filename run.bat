@echo off
echo ==========================================
echo   CertPortal - Student Certification Portal
echo ==========================================
echo.
echo Starting server...
echo.
cd /d "%~dp0"
start http://localhost:5000
python app.py
pause
