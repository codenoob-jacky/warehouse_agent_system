@echo off
chcp 65001 >nul
echo 智能仓管系统 - 简化版一键打包
echo ================================
echo 正在构建可分发的exe程序...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请从 https://www.python.org/downloads/ 安装Python 3.8+
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

REM 进入简化版目录
cd packaged_version

REM 安装打包工具
echo 正在安装PyInstaller...
pip install pyinstaller -q
if errorlevel 1 (
    echo PyInstaller安装失败，尝试使用镜像源...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/ -q
)

REM 安装依赖包
echo 正在安装依赖包...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo 依赖安装失败，尝试使用镜像源...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ -q
)

echo 依赖安装完成
echo.

REM 开始打包
echo 正在打包程序...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller --onefile --console --name=WarehouseSystem --distpath=../release/dist --workpath=../release/build app_main.py >nul 2>&1

if errorlevel 1 (
    echo 打包失败，显示详细信息...
    pyinstaller --onefile --console --name=WarehouseSystem --distpath=../release/dist --workpath=../release/build app_main.py
    if errorlevel 1 (
        echo 打包失败，请检查错误信息
        pause
        exit /b 1
    )
)

REM 创建发布结构
echo 创建发布目录...
cd ..
if not exist "release" mkdir release
if not exist "release\WarehouseSystem" mkdir "release\WarehouseSystem"

REM 复制文件
echo 复制程序文件...
copy "release\dist\WarehouseSystem.exe" "release\WarehouseSystem\" >nul
copy "packaged_version\.env.example" "release\WarehouseSystem\.env" >nul

REM 创建启动脚本
echo 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 智能仓管系统 - 简化版
echo echo ========================
echo echo 正在启动系统...
echo echo 浏览器将自动打开
echo echo 访问地址: http://localhost:8000
echo echo.
echo echo 功能特点:
echo echo - 在线OCR识别
echo echo - 智能文档解析
echo echo - Excel数据导出
echo echo - Web操作界面
echo echo.
echo timeout /t 3 /nobreak ^>nul
echo start http://localhost:8000
echo WarehouseSystem.exe
echo pause
) > "release\WarehouseSystem\启动系统.bat"

REM 创建使用说明
echo 创建使用说明...
(
echo 智能仓管系统 - 简化版使用说明
echo ================================
echo.
echo 快速开始:
echo 1. 双击"启动系统.bat"
echo 2. 等待浏览器自动打开
echo 3. 上传单据图片
echo 4. 查看识别结果
echo.
echo 主要功能:
echo - 在线OCR识别 ^(使用OCR.Space服务^)
echo - 智能文档解析
echo - Excel数据导出
echo - Web操作界面
echo.
echo 系统要求:
echo - Windows 7/8/10/11
echo - 网络连接 ^(用于OCR识别^)
echo - 2GB内存，100MB硬盘空间
echo.
echo 生成文件:
echo - warehouse_data.xlsx ^(Excel导出文件^)
echo - uploads/ ^(上传的图片文件^)
echo.
echo 配置说明:
echo 可编辑 .env 文件修改系统设置
echo.
echo 技术支持:
echo - OCR识别失败请检查网络连接
echo - 确保端口8000未被占用
echo - 如有问题请联系技术支持
) > "release\WarehouseSystem\使用说明.txt"

REM 清理临时文件
echo 清理临时文件...
if exist "release\build" rmdir /s /q "release\build" >nul 2>&1
if exist "release\dist" rmdir /s /q "release\dist" >nul 2>&1
if exist "packaged_version\*.spec" del "packaged_version\*.spec" >nul 2>&1

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 程序位置: release\WarehouseSystem\
echo 程序大小: 约50-80MB
echo.
echo 分发说明:
echo 1. 将整个WarehouseSystem文件夹复制给用户
echo 2. 用户双击"启动系统.bat"即可运行
echo 3. 无需安装Python环境
echo.
echo 包含文件:
echo - WarehouseSystem.exe ^(主程序^)
echo - 启动系统.bat ^(启动脚本^)
echo - .env ^(配置文件^)
echo - 使用说明.txt ^(用户手册^)
echo.

set /p test="是否立即测试打包的程序？(y/n): "
if /i "%test%"=="y" (
    echo.
    echo 启动测试程序...
    cd "release\WarehouseSystem"
    call "启动系统.bat"
    cd ..\..
)

echo.
echo 构建流程完成！
pause