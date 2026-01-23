@echo off
echo Warehouse System
echo ================
echo.
echo 1 - Build simple version
echo 2 - Run full version  
echo 3 - Exit
echo.

set /p choice="Choice: "

if "%choice%"=="1" call build_simple.bat
if "%choice%"=="2" (
    cd full_version
    python main.py
    cd ..
)
if "%choice%"=="3" exit

pause