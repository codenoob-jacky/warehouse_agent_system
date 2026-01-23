@echo off
echo 🚀 启动智能仓管系统...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖包
echo 📦 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📥 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 创建必要目录
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static
if not exist "data" mkdir data

REM 检查配置文件
if not exist ".env" (
    echo ⚠️  未找到.env配置文件，复制示例配置...
    copy .env.example .env
    echo.
    echo 📝 请编辑.env文件配置以下参数:
    echo    - OPENAI_API_KEY: OpenAI API密钥
    echo    - KINGDEE_BASE_URL: 金蝶服务器地址
    echo    - KINGDEE_USERNAME: 金蝶用户名
    echo    - KINGDEE_PASSWORD: 金蝶密码
    echo    - KINGDEE_DATABASE: 金蝶数据库
    echo.
    echo 配置完成后重新运行此脚本
    pause
    exit /b 0
)

REM 运行测试
echo 🧪 运行系统测试...
python tests\test_system.py
if errorlevel 1 (
    echo ⚠️  测试发现问题，但继续启动服务...
    echo.
)

REM 启动服务
echo.
echo 🌐 启动Web服务...
echo 访问地址: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.

python main.py