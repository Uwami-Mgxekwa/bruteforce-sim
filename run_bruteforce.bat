@echo off
echo ========================================
echo   Brute Force Simulator Launcher
echo ========================================
echo Select mode to run:
echo 1. Server Mode
echo 2. Attack Mode
echo.
set /p mode="Enter 1 or 2: "

if "%mode%"=="1" (
    echo Starting Server...
    python bruteforce.py --mode server
) else if "%mode%"=="2" (
    echo Starting Attacker...
    python bruteforce.py --mode attack
) else (
    echo Invalid choice. Showing help instead...
    python bruteforce.py --help
)

echo.
pause
