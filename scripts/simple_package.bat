@echo off
echo Smart Warehouse System - Simple Package Tool
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python OK
echo.

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo PyInstaller install failed
    pause
    exit /b 1
)

REM 安装依赖
echo Installing dependencies...
pip install fastapi uvicorn pydantic python-multipart aiofiles openpyxl pandas pyodbc pillow requests
if errorlevel 1 (
    echo Dependencies install failed
    pause
    exit /b 1
)

echo Dependencies OK
echo.

REM Package
echo Packaging application...
pyinstaller --onefile --console --name=WarehouseSystem app_main_en.py
if errorlevel 1 (
    echo Package failed
    pause
    exit /b 1
)

REM Create release folder
echo Creating release folder...
if not exist "release" mkdir release
if not exist "release\WarehouseSystem" mkdir "release\WarehouseSystem"

REM Copy files
echo Copying files...
copy "dist\WarehouseSystem.exe" "release\WarehouseSystem\"
copy ".env.example" "release\WarehouseSystem\.env"

REM Create start script
echo Creating start script...
(
echo @echo off
echo echo Smart Warehouse System Starting...
echo echo Please wait...
echo echo.
echo timeout /t 2 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystem.exe
echo pause
) > "release\WarehouseSystem\start.bat"

REM Create readme
echo Creating readme...
(
echo Smart Warehouse System
echo ======================
echo.
echo How to use:
echo 1. Double click start.bat
echo 2. Wait for browser to open
echo 3. Upload document images
echo 4. View OCR results
echo.
echo Requirements:
echo - Windows 7/8/10/11
echo - Internet connection
echo - 2GB RAM, 100MB disk space
) > "release\WarehouseSystem\README.txt"

REM Cleanup
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo Package complete!
echo Location: release\WarehouseSystem\
echo Run: Double click start.bat
echo.

set /p test="Test now? (y/n): "
if /i "%test%"=="y" (
    cd "release\WarehouseSystem"
    call "start.bat"
)

pause