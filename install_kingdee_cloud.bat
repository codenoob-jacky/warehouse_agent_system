@echo off
chcp 65001 >nul
echo ========================================
echo 金蝶云专业版仓管系统 - 依赖安装
echo ========================================
echo.

echo 正在安装依赖...
pip install -r requirements_kingdee_cloud.txt

echo.
echo ========================================
echo 安装完成！
echo.
echo 运行程序: python kingdee_cloud_app.py
echo ========================================
pause
