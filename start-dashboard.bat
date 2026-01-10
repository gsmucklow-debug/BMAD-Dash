@echo off
REM BMAD Dash - Start Dashboard Server
REM Double-click this file to start the server and open the dashboard

echo ========================================
echo BMAD Dash - Starting Dashboard
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Kill any existing Python processes running app.py
echo Checking for existing server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq BMAD Dash Server*" >nul 2>&1

echo.
echo Starting Flask backend server...
echo.

REM Start the Flask server in a new window
start "BMAD Dash Server" cmd /c "python -m backend.app"

REM Wait for server to start
echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

REM Open browser
echo Opening dashboard in browser...
start http://localhost:5000

echo.
echo ========================================
echo Dashboard should now be open!
echo ========================================
echo.
echo Server is running in a separate window.
echo To stop the server, run stop-dashboard.bat
echo or close the "BMAD Dash Server" window.
echo.
pause
