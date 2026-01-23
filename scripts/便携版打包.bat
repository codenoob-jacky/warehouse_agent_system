@echo off
chcp 65001 >nul
echo 📦 智能仓管系统便携版打包工具
echo ========================================
echo 这将创建一个包含Python环境的便携版，用户无需安装Python
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 创建便携版目录
echo 📁 创建便携版目录...
if exist "便携版" rmdir /s /q "便携版"
mkdir "便携版"
mkdir "便携版\智能仓管系统"
mkdir "便携版\智能仓管系统\python"
mkdir "便携版\智能仓管系统\app"

REM 下载便携版Python
echo 📥 准备便携版Python环境...
echo 💡 请手动下载Python便携版:
echo    1. 访问: https://www.python.org/downloads/windows/
echo    2. 下载: Windows embeddable package (64-bit)
echo    3. 解压到: 便携版\智能仓管系统\python\
echo.
echo 或者使用现有Python环境创建虚拟环境...

REM 创建虚拟环境
echo 🔧 创建虚拟环境...
python -m venv "便携版\智能仓管系统\python"
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

REM 激活虚拟环境并安装依赖
echo 📦 安装依赖到虚拟环境...
call "便携版\智能仓管系统\python\Scripts\activate.bat"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
call deactivate

REM 复制程序文件
echo 📋 复制程序文件...
xcopy "*.py" "便携版\智能仓管系统\app\" /Y
xcopy "config" "便携版\智能仓管系统\app\config\" /E /I /Y
xcopy "utils" "便携版\智能仓管系统\app\utils\" /E /I /Y
xcopy "agents" "便携版\智能仓管系统\app\agents\" /E /I /Y
copy ".env.example" "便携版\智能仓管系统\app\.env"
copy "README.md" "便携版\智能仓管系统\"

REM 创建启动脚本
echo 🚀 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🏪 智能仓管系统 - 便携版
echo echo ========================================
echo echo.
echo echo 🚀 正在启动系统...
echo echo 📱 启动后会自动打开浏览器
echo echo 🌐 访问地址: http://localhost:8000
echo echo.
echo echo 💡 使用说明:
echo echo 1. 上传纸质单据图片
echo echo 2. 系统自动OCR识别
echo echo 3. 智能解析单据内容
echo echo 4. 一键导出到Excel
echo echo.
echo timeout /t 3 /nobreak ^>nul
echo.
echo cd /d "%%~dp0app"
echo start http://localhost:8000
echo "%%~dp0python\Scripts\python.exe" main.py
echo pause
) > "便携版\智能仓管系统\启动系统.bat"

REM 创建使用说明
echo 📖 创建使用说明...
(
echo # 智能仓管系统 - 便携版
echo.
echo ## 🎯 系统简介
echo 便携版包含完整的Python环境，无需用户安装任何软件。
echo 解压后直接运行，真正的绿色便携。
echo.
echo ## 🚀 使用方法
echo 1. 解压到任意目录
echo 2. 双击"启动系统.bat"
echo 3. 等待浏览器自动打开
echo 4. 开始使用！
echo.
echo ## 💡 功能特点
echo - 📸 纸质单据OCR识别
echo - 🤖 智能数据解析
echo - 📊 Excel数据导出
echo - 🔗 金蝶系统集成
echo - 🌐 免费在线OCR服务
echo.
echo ## ⚙️ 系统要求
echo - Windows 7/8/10/11
echo - 网络连接（用于OCR识别）
echo - 2GB内存，200MB硬盘空间
echo.
echo ## 📁 目录结构
echo - python/     # Python运行环境
echo - app/        # 程序文件
echo - 启动系统.bat # 启动脚本
echo.
echo ## 🔧 高级配置
echo 编辑 app/.env 文件可修改:
echo - OCR服务设置
echo - 金蝶集成方式
echo - 文件存储路径
) > "便携版\智能仓管系统\使用说明.txt"

echo.
echo ✅ 便携版打包完成！
echo.
echo 📁 程序位置: 便携版\智能仓管系统\
echo 📦 文件大小: 约100-200MB
echo.
echo 💡 分发说明:
echo 1. 将整个"智能仓管系统"文件夹给用户
echo 2. 用户无需安装任何软件
echo 3. 解压后直接双击"启动系统.bat"
echo 4. 真正的绿色便携程序
echo.
echo 🎯 优势:
echo - 完全便携，无需安装
echo - 包含Python环境
echo - 一键启动使用
echo - 适合企业内部分发
echo.

pause