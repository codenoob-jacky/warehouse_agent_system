@echo off
chcp 65001 >nul
echo 📦 智能仓管系统一键打包工具
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python 3.8+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 安装打包工具
echo 📥 安装PyInstaller打包工具...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/
if errorlevel 1 (
    echo ❌ PyInstaller安装失败
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装项目依赖...
pip install fastapi uvicorn pydantic python-multipart aiofiles openpyxl pandas pyodbc pillow requests -i https://pypi.tuna.tsinghua.edu.cn/simple/
if errorlevel 1 (
    echo ❌ 依赖安装失败，尝试默认源...
    pip install fastapi uvicorn pydantic python-multipart aiofiles openpyxl pandas pyodbc pillow requests
)

echo ✅ 依赖安装完成
echo.

REM 创建打包配置
echo ⚙️ 生成打包配置...
python build_exe.py

REM 开始打包
echo 🔨 开始打包程序（这可能需要几分钟）...
pyinstaller --onefile --console --name="WarehouseSystem" ^
    --add-data="config;config" ^
    --add-data="utils;utils" ^
    --add-data="agents;agents" ^
    --add-data=".env.example;." ^
    --hidden-import="requests" ^
    --hidden-import="fastapi" ^
    --hidden-import="uvicorn" ^
    --hidden-import="pydantic" ^
    --hidden-import="PIL" ^
    --hidden-import="openpyxl" ^
    --hidden-import="pandas" ^
    --hidden-import="pyodbc" ^
    app_main.py

if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

REM 创建发布目录
echo 📁 创建发布目录...
if not exist "release" mkdir release
if not exist "release\WarehouseSystem" mkdir "release\WarehouseSystem"

REM 复制文件
echo 📋 复制必要文件...
copy "dist\WarehouseSystem.exe" "release\WarehouseSystem\"
copy ".env.example" "release\WarehouseSystem\.env"
copy "README.md" "release\WarehouseSystem\"

REM 创建启动脚本
echo 🚀 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🏪 智能仓管系统启动中...
echo echo 请稍候，系统正在启动...
echo echo.
echo echo 💡 使用说明:
echo echo 1. 系统启动后会自动打开浏览器
echo echo 2. 访问地址: http://localhost:8000
echo echo 3. 上传纸质单据图片进行识别
echo echo 4. 按Ctrl+C可停止系统
echo echo.
echo timeout /t 2 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystem.exe
echo pause
) > "release\WarehouseSystem\start.bat"

REM 创建使用说明
echo 📖 创建使用说明...
(
echo # 智能仓管系统 - 使用说明
echo.
echo ## 🚀 快速开始
echo 1. 双击"启动系统.bat"启动程序
echo 2. 等待浏览器自动打开
echo 3. 上传纸质单据图片
echo 4. 查看识别结果
echo.
echo ## 💡 功能特点
echo - 📸 纸质单据OCR识别
echo - 🤖 智能数据解析
echo - 📊 Excel数据导出
echo - 🔗 金蝶系统集成
echo.
echo ## ⚙️ 系统要求
echo - Windows 7/8/10/11
echo - 网络连接（用于在线OCR）
echo - 2GB内存，100MB硬盘空间
echo.
echo ## 📞 技术支持
echo 如有问题请检查网络连接和防火墙设置
) > "release\WarehouseSystem\README.txt"

REM 清理临时文件
echo 🧹 清理临时文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo ✅ 打包完成！
echo.
echo 📁 程序位置: release\WarehouseSystem\
echo 🚀 运行方法: 双击"start.bat"
echo 📦 文件大小: 约50-100MB
echo.
echo 💡 分发说明:
echo 1. 将整个"智能仓管系统"文件夹复制给用户
echo 2. 用户无需安装Python即可运行
echo 3. 首次运行会自动创建配置文件
echo.

REM 询问是否立即测试
set /p test="是否立即测试程序？(y/n): "
if /i "%test%"=="y" (
    echo 🧪 启动测试...
    cd "release\WarehouseSystem"
    call "start.bat"
)

echo.
echo 🎉 打包流程完成！
pause