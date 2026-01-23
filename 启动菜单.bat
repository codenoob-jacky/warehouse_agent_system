@echo off
chcp 65001 >nul
echo 智能仓管系统 - 快速启动
echo ========================
echo.

echo 请选择启动方式:
echo.
echo 1. 打包版 - 生成exe程序 (推荐分发)
echo 2. 完整版 - 开发测试版本
echo 3. 简化版一键打包 (新)
echo 4. 查看项目结构
echo 5. 退出
echo.

set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 启动打包版构建...
    cd scripts
    call package_simple.bat
    cd ..
) else if "%choice%"=="2" (
    echo.
    echo 启动完整版...
    cd full_version
    echo 检查依赖...
    pip install -r requirements.txt >nul 2>&1
    if exist ".env" (
        python main.py
    ) else (
        echo 首次运行，创建配置文件...
        copy .env.example .env
        echo 请编辑 full_version\.env 文件配置参数，然后重新运行
        pause
    )
    cd ..
) else if "%choice%"=="3" (
    echo.
    echo 启动简化版一键打包...
    call build_simple.bat
) else if "%choice%"=="4" (
    echo.
    echo 项目结构:
    echo.
    echo warehouse_agent_system/
    echo ├── packaged_version/     # 打包版本 (简化)
    echo ├── full_version/         # 完整版本 (开发)
    echo ├── scripts/              # 构建脚本
    echo ├── docs_and_guides/      # 文档指南
    echo └── README.md            # 项目说明
    echo.
    echo 使用建议:
    echo - 企业分发: 使用打包版
    echo - 开发测试: 使用完整版
    echo - 快速体验: Docker部署
    echo.
    pause
) else if "%choice%"=="5" (
    echo 再见!
    exit /b 0
) else (
    echo 无效选择
    pause
    goto :eof
)

echo.
echo 操作完成!
pause