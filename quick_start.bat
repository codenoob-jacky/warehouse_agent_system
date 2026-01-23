@echo off
echo Warehouse System Quick Start
echo ==============================
echo.
echo Select option:
echo.
echo 1. Build packaged version
echo 2. Run full version
echo 3. Build simple version
echo 4. Show project info
echo 5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Building packaged version...
    cd scripts
    call package_simple.bat
    cd ..
) else if "%choice%"=="2" (
    echo.
    echo Starting full version...
    cd full_version
    pip install -r requirements.txt
    if exist ".env" (
        python main.py
    ) else (
        copy .env.example .env
        echo Config file created. Please edit full_version\.env
        pause
    )
    cd ..
) else if "%choice%"=="3" (
    echo.
    echo Building simple version...
    call build_simple.bat
) else if "%choice%"=="4" (
    echo.
    echo Project Structure:
    echo warehouse_agent_system/
    echo   packaged_version/  - Simple version for distribution
    echo   full_version/      - Complete version for development
    echo   scripts/           - Build scripts
    echo   docs_and_guides/   - Documentation
    echo.
    pause
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice
    pause
)

echo.
echo Done!
pause