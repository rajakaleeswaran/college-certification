@echo off
echo ==========================================
echo   CertPortal - Student Certification Portal
echo ==========================================
echo.
cd /d "%~dp0"

echo [1/2] Checking & installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo [2/2] Starting server...
echo Server running at: http://localhost:5000
echo.
start http://localhost:5000
python app.py
pause
