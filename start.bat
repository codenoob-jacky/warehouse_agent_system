@echo off
echo Warehouse System - Quick Start
echo ==============================
echo.
echo Current directory: %CD%
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
    echo Checking for scripts\package_simple.bat...
    if exist "scripts\package_simple.bat" (
        echo Found package_simple.bat, entering scripts directory...
        cd scripts
        echo Current directory: %CD%
        echo Calling package_simple.bat...
        call package_simple.bat
        echo Returned from package_simple.bat
        cd ..
        echo Back to main directory: %CD%
    ) else (
        echo Error: scripts\package_simple.bat not found
        echo Current directory contents:
        dir
        pause
    )
) else if "%choice%"=="2" (
    echo.
    echo Starting full version...
    echo Checking full_version directory...
    if exist "full_version\main.py" (
        echo Found main.py, entering full_version directory...
        cd full_version
        echo Current directory: %CD%
        echo Checking for requirements.txt...
        if exist "requirements.txt" (
            echo Found requirements.txt, installing dependencies...
            pip install -r requirements.txt
        ) else (
            echo Warning: requirements.txt not found in %CD%
            dir
        )
        echo Checking for .env file...
        if exist ".env" (
            echo Found .env, starting application...
            python main.py
        ) else (
            echo .env not found, checking for .env.example...
            if exist ".env.example" (
                echo Creating .env from .env.example...
                copy .env.example .env
                echo Config file created. You may edit .env if needed.
            )
            echo Starting application...
            python main.py
        )
        cd ..
    ) else (
        echo Error: full_version\main.py not found
        echo Current files in directory:
        dir
        pause
    )
) else if "%choice%"=="3" (
    echo.
    echo Building simple version...
    if exist "build_simple.bat" (
        call build_simple.bat
    ) else (
        echo Error: build_simple.bat not found
        pause
    )
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