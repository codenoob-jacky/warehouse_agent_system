@echo off
echo Smart Warehouse System - Simple Package Tool
echo =============================================
echo Packaged Version - One-Click Build
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python environment OK
echo.

REM Change to packaged version directory
cd packaged_version

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller install failed, trying with mirror...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/
)

REM Install dependencies
echo Installing dependencies...
pip install fastapi uvicorn pydantic python-multipart openpyxl pandas pillow requests >nul 2>&1
if errorlevel 1 (
    echo Dependencies install failed, trying with mirror...
    pip install fastapi uvicorn pydantic python-multipart openpyxl pandas pillow requests -i https://pypi.tuna.tsinghua.edu.cn/simple/
)

echo Dependencies installed
echo.

REM Package application
echo Packaging application...
echo This may take a few minutes, please wait...
pyinstaller --onefile --console --name=WarehouseSystem --distpath=../release/dist --workpath=../release/build app_main.py >nul 2>&1
if errorlevel 1 (
    echo Package failed, trying with verbose output...
    pyinstaller --onefile --console --name=WarehouseSystem --distpath=../release/dist --workpath=../release/build app_main.py
    if errorlevel 1 (
        echo Package failed
        pause
        exit /b 1
    )
)

REM Create release structure
echo Creating release structure...
cd ..
if not exist "release" mkdir release
if not exist "release\WarehouseSystem" mkdir "release\WarehouseSystem"

REM Copy files
echo Copying files...
copy "release\dist\WarehouseSystem.exe" "release\WarehouseSystem\" >nul
copy "packaged_version\.env.example" "release\WarehouseSystem\.env" >nul

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
echo echo Features:
echo echo - Online OCR recognition
echo echo - Smart document parsing  
echo echo - Excel data export
echo echo - Web interface
echo echo.
echo timeout /t 3 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystem.exe
echo pause
) > "release\WarehouseSystem\start.bat"

REM Create readme
echo Creating readme...
(
echo Smart Warehouse System - Packaged Version
echo ==========================================
echo.
echo Quick Start:
echo 1. Double click start.bat
echo 2. Wait for browser to open
echo 3. Upload document images
echo 4. View OCR results
echo.
echo Features:
echo - Online OCR recognition ^(OCR.Space^)
echo - Smart document parsing
echo - Excel data export
echo - Web interface
echo.
echo System Requirements:
echo - Windows 7/8/10/11
echo - Internet connection
echo - 2GB RAM, 100MB disk space
echo.
echo Generated Files:
echo - warehouse_data.xlsx ^(Excel export^)
echo - uploads/ ^(uploaded images^)
echo.
echo Configuration:
echo Edit .env file to change settings
echo.
echo Support:
echo Check network connection if OCR fails
echo Ensure port 8000 is not occupied
) > "release\WarehouseSystem\README.txt"

REM Cleanup
echo Cleaning up...
if exist "release\build" rmdir /s /q "release\build" >nul 2>&1
if exist "release\dist" rmdir /s /q "release\dist" >nul 2>&1
if exist "packaged_version\*.spec" del "packaged_version\*.spec" >nul 2>&1

echo.
echo ========================================
echo Package Complete!
echo ========================================
echo.
echo Location: release\WarehouseSystem\
echo Size: Approximately 50-80MB
echo.
echo Distribution:
echo 1. Copy entire WarehouseSystem folder to users
echo 2. Users run start.bat to launch
echo 3. No Python installation required
echo.
echo Files included:
echo - WarehouseSystem.exe ^(main program^)
echo - start.bat ^(launch script^)
echo - .env ^(configuration^)
echo - README.txt ^(user guide^)
echo.

set /p test="Test the packaged application now? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Launching test...
    cd "release\WarehouseSystem"
    call "start.bat"
    cd ..\..
)

echo.
echo Build process completed successfully!
pause