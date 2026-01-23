@echo off
echo Simple Package Tool
echo ===================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit
)

echo Python found. Starting package process...
echo.

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

REM Go to packaged version
cd packaged_version

REM Install dependencies
echo Installing dependencies...
pip install fastapi uvicorn pydantic python-multipart openpyxl pandas pillow requests

REM Package
echo Packaging to exe...
pyinstaller --onefile --console --name=WarehouseSystem app_main.py

REM Create output folder
mkdir ..\output 2>nul
copy dist\WarehouseSystem.exe ..\output\
copy .env.example ..\output\.env

REM Create simple start script
echo @echo off > ..\output\start.bat
echo echo Starting Warehouse System... >> ..\output\start.bat
echo start http://localhost:8000 >> ..\output\start.bat
echo WarehouseSystem.exe >> ..\output\start.bat
echo pause >> ..\output\start.bat

REM Cleanup
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

cd ..

echo.
echo Done! Files are in 'output' folder:
echo - WarehouseSystem.exe
echo - start.bat
echo - .env
echo.
pause