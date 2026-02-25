@echo off
chcp 65001 >nul
echo Ultra Simple Warehouse System - GUI Version Package Tool
echo ========================================================
echo Desktop GUI version for exe packaging
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

REM Install GUI dependencies
echo Installing GUI dependencies...
pip install -r gui_requirements.txt
if errorlevel 1 (
    echo Dependencies install failed
    pause
    exit /b 1
)

echo Dependencies OK
echo.

REM Package ultra_simple_gui.py
echo Packaging GUI version...
pyinstaller --onefile --windowed --name=WarehouseSystemGUI ultra_simple_gui.py
if errorlevel 1 (
    echo Package failed
    pause
    exit /b 1
)

REM Create release folder
echo Creating release folder...
if not exist "release_gui" mkdir "release_gui"
if not exist "release_gui\WarehouseSystem" mkdir "release_gui\WarehouseSystem"

REM Copy files
echo Copying files...
copy "dist\WarehouseSystemGUI.exe" "release_gui\WarehouseSystem\"

REM Create start script
echo Creating start script...
(
echo @echo off
echo echo Ultra Simple Warehouse System - GUI Version
echo echo ==========================================
echo echo Features:
echo echo - Desktop GUI interface
echo echo - Online OCR recognition
echo echo - Local Kingdee database integration
echo echo - Ultra lightweight ^(~15MB^)
echo echo.
echo echo Starting system...
echo WarehouseSystemGUI.exe
) > "release_gui\WarehouseSystem\start.bat"

REM Create readme
echo Creating readme...
(
echo Ultra Simple Warehouse System - GUI Version
echo ============================================
echo.
echo Features:
echo - Desktop GUI interface ^(no browser needed^)
echo - Online OCR recognition ^(OCR.Space^)
echo - Local Kingdee database integration
echo - Ultra lightweight executable ^(~15MB^)
echo - No web dependencies
echo.
echo Requirements:
echo - Windows 7/8/10/11
echo - Internet connection ^(for OCR^)
echo - Kingdee database at C:\KDW\KDMAIN.MDB
echo - Microsoft Access Database Engine
echo.
echo How to use:
echo 1. Double click WarehouseSystemGUI.exe
echo 2. Click Browse to select document image
echo 3. Click Process to start processing
echo 4. View results in the tabs below
echo.
echo Advantages over Web version:
echo - No browser required
echo - No port conflicts
echo - Traditional desktop feel
echo - Faster startup
) > "release_gui\WarehouseSystem\README.txt"

REM Cleanup
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo Package complete!
echo Location: release_gui\WarehouseSystem\
echo Size: ~15MB (ultra lightweight GUI)
echo Run: Double click WarehouseSystemGUI.exe
echo.

set /p test="Test now? (y/n): "
if /i "%test%"=="y" (
    cd "release_gui\WarehouseSystem"
    WarehouseSystemGUI.exe
)

pause