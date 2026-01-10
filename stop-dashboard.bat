@echo off
REM BMAD Dash - Stop Dashboard Server
REM Double-click this file to stop the server

echo ========================================
echo BMAD Dash - Stopping Dashboard
echo ========================================
echo.

REM Kill any Flask servers on port 5000
echo Looking for running server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Stopping server (PID: %%a)
    taskkill /F /PID %%a
)

echo.
echo Server stopped.
echo.
pause
