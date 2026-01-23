@echo off
echo Ultra Simple Warehouse System - Package Tool
echo ===========================================
echo Lightweight version for exe packaging
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

REM Install minimal dependencies
echo Installing minimal dependencies...
pip install -r simple_requirements.txt
if errorlevel 1 (
    echo Dependencies install failed
    pause
    exit /b 1
)

echo Dependencies OK
echo.

REM Package ultra_simple.py
echo Packaging ultra_simple.py...
pyinstaller --onefile --console --name=WarehouseSystemUltra ultra_simple.py
if errorlevel 1 (
    echo Package failed
    pause
    exit /b 1
)

REM Create release folder
echo Creating release folder...
if not exist "release_ultra" mkdir "release_ultra"
if not exist "release_ultra\WarehouseSystem" mkdir "release_ultra\WarehouseSystem"

REM Copy files
echo Copying files...
copy "dist\WarehouseSystemUltra.exe" "release_ultra\WarehouseSystem\"

REM Create start script
echo Creating start script...
(
echo @echo off
echo echo Ultra Simple Warehouse System
echo echo ============================
echo echo Features:
echo echo - Online OCR recognition
echo echo - Local Kingdee database integration
echo echo - Lightweight ^(~20MB^)
echo echo.
echo echo Starting system...
echo timeout /t 2 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystemUltra.exe
echo pause
) > "release_ultra\WarehouseSystem\start.bat"

REM Create readme
echo Creating readme...
(
echo Ultra Simple Warehouse System
echo =============================
echo.
echo Features:
echo - Online OCR recognition ^(OCR.Space^)
echo - Local Kingdee database integration
echo - Lightweight executable ^(~20MB^)
echo - No heavy dependencies
echo.
echo Requirements:
echo - Windows 7/8/10/11
echo - Internet connection ^(for OCR^)
echo - Kingdee database at C:\KDW\KDMAIN.MDB
echo - Microsoft Access Database Engine
echo.
echo How to use:
echo 1. Double click start.bat
echo 2. Upload document images
echo 3. View OCR results and database save status
echo.
echo Kingdee Integration:
echo - Auto-detects database at common paths
echo - Saves documents to ICStockBill table
echo - Supports both inbound and outbound documents
) > "release_ultra\WarehouseSystem\README.txt"

REM Cleanup
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo Package complete!
echo Location: release_ultra\WarehouseSystem\
echo Size: ~20MB (ultra lightweight)
echo Run: Double click start.bat
echo.

set /p test="Test now? (y/n): "
if /i "%test%"=="y" (
    cd "release_ultra\WarehouseSystem"
    call "start.bat"
)

pause