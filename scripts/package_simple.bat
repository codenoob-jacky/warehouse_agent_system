@echo off
echo Smart Warehouse System - Package Tool
echo =====================================
echo Packaged Version - Simplified for distribution
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

REM Change to packaged version directory
echo Changing to packaged version directory...
cd ..\packaged_version
echo Current directory: %CD%

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo PyInstaller install failed
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependencies install failed
    pause
    exit /b 1
)

echo Dependencies OK
echo.

REM Package
echo Packaging application...
pyinstaller --onefile --console --name=WarehouseSystem app_main.py
if errorlevel 1 (
    echo Package failed
    pause
    exit /b 1
)

REM Create release folder
echo Creating release folder...
if not exist "..\..\release" mkdir "..\..\release"
if not exist "..\..\release\WarehouseSystem" mkdir "..\..\release\WarehouseSystem"

REM Copy files
echo Copying files...
copy "dist\WarehouseSystem.exe" "..\..\release\WarehouseSystem\"
copy ".env.example" "..\..\release\WarehouseSystem\.env"

REM Create start script
echo Creating start script...
(
echo @echo off
echo echo Smart Warehouse System - Packaged Version
echo echo ==========================================
echo echo Starting system...
echo echo Browser will open automatically
echo echo Access: http://localhost:8000
echo echo.
echo timeout /t 2 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystem.exe
echo pause
) > "..\..\release\WarehouseSystem\start.bat"

REM Create readme
echo Creating readme...
(
echo Smart Warehouse System - Packaged Version
echo ==========================================
echo.
echo Features:
echo - Online OCR recognition ^(OCR.Space^)
echo - Smart document parsing
echo - Excel data export
echo - Web interface
echo.
echo How to use:
echo 1. Double click start.bat
echo 2. Wait for browser to open
echo 3. Upload document images
echo 4. View OCR results and Excel export
echo.
echo Requirements:
echo - Windows 7/8/10/11
echo - Internet connection ^(for OCR^)
echo - 2GB RAM, 100MB disk space
echo.
echo Generated Excel file: warehouse_data.xlsx
) > "..\..\release\WarehouseSystem\README.txt"

REM Cleanup
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

cd ..\..

echo.
echo Package complete!
echo Location: release\WarehouseSystem\
echo Run: Double click start.bat
echo.

set /p test="Test now? (y/n): "
if /i "%test%"=="y" (
    cd "release\WarehouseSystem"
    call "start.bat"
    cd ..\..\scripts
)

pause