@echo off
chcp 65001 >nul
echo 📦 智能仓管系统绿色版打包工具
echo ========================================
echo 这将创建一个绿色版程序，用户只需要有Python即可运行
echo.

REM 创建发布目录
echo 📁 创建发布目录...
if exist "绿色版" rmdir /s /q "绿色版"
mkdir "绿色版"
mkdir "绿色版\智能仓管系统"

REM 复制核心文件
echo 📋 复制程序文件...
xcopy "*.py" "绿色版\智能仓管系统\" /Y
xcopy "config" "绿色版\智能仓管系统\config\" /E /I /Y
xcopy "utils" "绿色版\智能仓管系统\utils\" /E /I /Y
xcopy "agents" "绿色版\智能仓管系统\agents\" /E /I /Y
xcopy "tests" "绿色版\智能仓管系统\tests\" /E /I /Y
copy "requirements.txt" "绿色版\智能仓管系统\"
copy ".env.example" "绿色版\智能仓管系统\.env"
copy "README.md" "绿色版\智能仓管系统\"

REM 创建一键安装脚本
echo 🔧 创建安装脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 📦 智能仓管系统 - 一键安装
echo echo ========================================
echo echo.
echo echo 正在检查Python环境...
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ❌ 未找到Python环境
echo     echo 💡 请先安装Python 3.8+: https://www.python.org/downloads/
echo     echo 安装时记得勾选"Add Python to PATH"
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ Python环境检查通过
echo echo 📥 正在安装依赖包...
echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
echo if errorlevel 1 ^(
echo     echo ❌ 依赖安装失败，尝试使用默认源...
echo     pip install -r requirements.txt
echo ^)
echo.
echo echo ✅ 安装完成！
echo echo 💡 现在可以双击"启动系统.bat"运行程序
echo pause
) > "绿色版\智能仓管系统\一键安装.bat"

REM 创建启动脚本
echo 🚀 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🏪 智能仓管系统
echo echo ========================================
echo echo 基于AI的仓管单据识别和处理系统
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
echo echo ⏳ 请稍候...
echo timeout /t 3 /nobreak ^>nul
echo start http://localhost:8000
echo python main.py
echo pause
) > "绿色版\智能仓管系统\启动系统.bat"

REM 创建简化的main.py
echo 🔧 创建简化启动程序...
(
echo import os
echo import sys
echo import webbrowser
echo import time
echo import threading
echo from pathlib import Path
echo.
echo # 设置默认配置
echo os.environ.setdefault^('OCR_MODE', 'online'^)
echo os.environ.setdefault^('OCR_SPACE_API_KEY', 'helloworld'^)
echo os.environ.setdefault^('KINGDEE_TYPE', 'excel'^)
echo.
echo def check_config^(^):
echo     """检查配置文件"""
echo     env_file = Path^('.env'^)
echo     if not env_file.exists^(^):
echo         print^("📝 创建默认配置文件..."^)
echo         with open^('.env', 'w', encoding='utf-8'^) as f:
echo             f.write^("""# 智能仓管系统配置
echo # OCR模式 ^(online推荐^)
echo OCR_MODE=online
echo OCR_SPACE_API_KEY=helloworld
echo.
echo # 金蝶系统类型 ^(excel简单^)
echo KINGDEE_TYPE=excel
echo KINGDEE_EXCEL_PATH=./kingdee_data.xlsx
echo.
echo # 文件上传
echo UPLOAD_FOLDER=./uploads
echo """^)
echo         print^("✅ 配置文件已创建"^)
echo.
echo def main^(^):
echo     """主函数"""
echo     print^("🏪 智能仓管系统启动中..."^)
echo     
echo     # 检查配置
echo     check_config^(^)
echo     
echo     # 创建必要目录
echo     os.makedirs^('uploads', exist_ok=True^)
echo     os.makedirs^('data', exist_ok=True^)
echo     
echo     # 延迟启动浏览器
echo     def open_browser^(^):
echo         time.sleep^(3^)
echo         webbrowser.open^('http://localhost:8000'^)
echo     
echo     threading.Thread^(target=open_browser, daemon=True^).start^(^)
echo     
echo     # 启动FastAPI应用
echo     try:
echo         import uvicorn
echo         from main import app
echo         uvicorn.run^(app, host="0.0.0.0", port=8000, log_level="error"^)
echo     except KeyboardInterrupt:
echo         print^("\\n👋 系统已关闭"^)
echo     except Exception as e:
echo         print^(f"❌ 启动失败: {str^(e^)}"^)
echo         print^("\\n💡 解决方案:"^)
echo         print^("1. 检查是否已安装依赖: python -m pip install -r requirements.txt"^)
echo         print^("2. 检查端口8000是否被占用"^)
echo         print^("3. 检查网络连接"^)
echo         input^("\\n按回车键退出..."^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > "绿色版\智能仓管系统\simple_main.py"

REM 修改启动脚本使用简化版
echo 🔄 更新启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🏪 智能仓管系统
echo echo ========================================
echo echo.
echo echo 🚀 正在启动系统...
echo echo 📱 启动后会自动打开浏览器
echo echo 🌐 访问地址: http://localhost:8000
echo echo.
echo timeout /t 2 /nobreak ^>nul
echo python simple_main.py
echo pause
) > "绿色版\智能仓管系统\启动系统.bat"

REM 创建用户手册
echo 📖 创建用户手册...
(
echo # 智能仓管系统 - 绿色版
echo.
echo ## 🎯 系统简介
echo 基于AI的智能仓管系统，支持纸质单据OCR识别。
echo 绿色版无需安装，解压即用。
echo.
echo ## 🚀 使用步骤
echo.
echo ### 首次使用
echo 1. 确保电脑已安装Python 3.8+
echo 2. 双击"一键安装.bat"安装依赖
echo 3. 双击"启动系统.bat"运行程序
echo 4. 等待浏览器自动打开
echo.
echo ### 日常使用
echo 1. 双击"启动系统.bat"
echo 2. 上传纸质单据图片
echo 3. 查看识别结果
echo 4. 导出Excel文件
echo.
echo ## 💡 功能特点
echo - 📸 支持拍照识别纸质单据
echo - 🤖 智能提取关键信息
echo - 📊 自动生成Excel报表
echo - 🔗 支持金蝶系统集成
echo - 🌐 使用免费在线OCR服务
echo.
echo ## ⚙️ 系统要求
echo - Windows 7/8/10/11
echo - Python 3.8+ ^(必须^)
echo - 网络连接 ^(用于OCR识别^)
echo - 2GB内存，500MB硬盘空间
echo.
echo ## 🔧 常见问题
echo.
echo ### Python环境问题
echo - 下载地址: https://www.python.org/downloads/
echo - 安装时勾选"Add Python to PATH"
echo - 验证安装: 命令行输入 python --version
echo.
echo ### 依赖安装失败
echo - 检查网络连接
echo - 尝试使用管理员权限运行
echo - 手动安装: pip install fastapi uvicorn requests
echo.
echo ### 程序无法启动
echo - 检查端口8000是否被占用
echo - 关闭防火墙或杀毒软件
echo - 重新运行"一键安装.bat"
echo.
echo ## 📞 技术支持
echo 遇到问题请检查:
echo 1. Python环境是否正确安装
echo 2. 网络连接是否正常
echo 3. 防火墙设置是否阻止程序运行
) > "绿色版\智能仓管系统\使用说明.md"

REM 创建依赖检查脚本
echo 🔍 创建依赖检查脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🔍 系统环境检查
echo echo ========================================
echo echo.
echo echo 检查Python环境...
echo python --version
echo if errorlevel 1 ^(
echo     echo ❌ Python未安装或未添加到PATH
echo     echo 💡 请访问 https://www.python.org/downloads/ 下载安装
echo     goto :end
echo ^)
echo echo ✅ Python环境正常
echo echo.
echo echo 检查关键依赖...
echo python -c "import fastapi; print('✅ FastAPI')" 2^>nul ^|^| echo "❌ FastAPI未安装"
echo python -c "import uvicorn; print('✅ Uvicorn')" 2^>nul ^|^| echo "❌ Uvicorn未安装"
echo python -c "import requests; print('✅ Requests')" 2^>nul ^|^| echo "❌ Requests未安装"
echo python -c "import pandas; print('✅ Pandas')" 2^>nul ^|^| echo "❌ Pandas未安装"
echo echo.
echo echo 检查网络连接...
echo ping -n 1 api.ocr.space ^>nul 2^>^&1 ^&^& echo ✅ OCR服务可访问 ^|^| echo ❌ OCR服务无法访问
echo echo.
echo echo 🎉 环境检查完成
echo :end
echo pause
) > "绿色版\智能仓管系统\环境检查.bat"

echo.
echo ✅ 绿色版打包完成！
echo.
echo 📁 程序位置: 绿色版\智能仓管系统\
echo 📦 文件大小: 约5-10MB
echo.
echo 💡 分发说明:
echo 1. 将整个"智能仓管系统"文件夹给用户
echo 2. 用户需要先安装Python 3.8+
echo 3. 运行"一键安装.bat"安装依赖
echo 4. 运行"启动系统.bat"使用程序
echo.
echo 🎯 优势:
echo - 体积小，易分发
echo - 代码可见，易维护
echo - 依赖清晰，易排错
echo - 绿色免安装
echo.

REM 询问是否立即测试
set /p test="是否立即测试程序？(y/n): "
if /i "%test%"=="y" (
    echo 🧪 启动测试...
    cd "绿色版\智能仓管系统"
    call "启动系统.bat"
)

echo.
echo 🎉 绿色版打包完成！
pause