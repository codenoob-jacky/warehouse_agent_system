"""
智能仓管系统打包脚本
将Python程序打包成可执行文件
"""

import os
import sys
import shutil
from pathlib import Path

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('utils', 'utils'),
        ('agents', 'agents'),
        ('static', 'static'),
        ('.env.example', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'paddleocr',
        'requests',
        'fastapi',
        'uvicorn',
        'pydantic',
        'PIL',
        'openpyxl',
        'pandas',
        'pyodbc',
        'crewai',
        'langchain'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='智能仓管系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
"""
    
    with open('warehouse_system.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller配置文件已创建")

def create_build_script():
    """创建构建脚本"""
    build_script = """@echo off
echo 🏗️ 开始打包智能仓管系统...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境
    pause
    exit /b 1
)

REM 安装打包工具
echo 📦 安装PyInstaller...
pip install pyinstaller

REM 安装依赖
echo 📥 安装项目依赖...
pip install -r requirements.txt

REM 创建配置文件
echo ⚙️ 创建打包配置...
python build_exe.py

REM 开始打包
echo 🔨 开始打包程序...
pyinstaller warehouse_system.spec --clean

REM 复制必要文件
echo 📋 复制配置文件...
if not exist "dist\\智能仓管系统" mkdir "dist\\智能仓管系统"
copy ".env.example" "dist\\智能仓管系统\\.env"
copy "README.md" "dist\\智能仓管系统\\"

REM 创建启动脚本
echo 🚀 创建启动脚本...
echo @echo off > "dist\\智能仓管系统\\启动系统.bat"
echo echo 🏪 启动智能仓管系统... >> "dist\\智能仓管系统\\启动系统.bat"
echo echo 请稍候，系统正在启动... >> "dist\\智能仓管系统\\启动系统.bat"
echo echo. >> "dist\\智能仓管系统\\启动系统.bat"
echo start http://localhost:8000 >> "dist\\智能仓管系统\\启动系统.bat"
echo "智能仓管系统.exe" >> "dist\\智能仓管系统\\启动系统.bat"

echo.
echo ✅ 打包完成！
echo 📁 程序位置: dist\\智能仓管系统\\
echo 🚀 运行方法: 双击"启动系统.bat"
echo.
pause
"""
    
    with open('build.bat', 'w', encoding='gbk') as f:
        f.write(build_script)
    
    print("✅ 构建脚本已创建")

def create_portable_main():
    """创建便携版主程序"""
    portable_main = '''import os
import sys
import webbrowser
import time
from pathlib import Path

# 设置环境变量
os.environ.setdefault('OCR_MODE', 'online')
os.environ.setdefault('OCR_SPACE_API_KEY', 'helloworld')
os.environ.setdefault('KINGDEE_TYPE', 'excel')

def check_config():
    """检查配置文件"""
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 创建默认配置文件...")
        default_config = """# 智能仓管系统配置
# OCR模式 (local/online)
OCR_MODE=online
OCR_SPACE_API_KEY=helloworld

# 金蝶系统类型 (online/local/excel)
KINGDEE_TYPE=excel
KINGDEE_EXCEL_PATH=./kingdee_data.xlsx

# 文件上传
UPLOAD_FOLDER=./uploads
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(default_config)
        print("✅ 配置文件已创建")

def main():
    """主函数"""
    print("🏪 智能仓管系统")
    print("=" * 40)
    print("基于AI的仓管单据识别和处理系统")
    print("支持纸质单据OCR识别和金蝶ERP集成")
    print()
    
    # 检查配置
    check_config()
    
    # 创建必要目录
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("🚀 正在启动系统...")
    print("📱 系统启动后会自动打开浏览器")
    print("🌐 访问地址: http://localhost:8000")
    print()
    print("💡 使用说明:")
    print("1. 拍照上传纸质单据")
    print("2. 系统自动OCR识别")
    print("3. 智能解析单据内容")
    print("4. 一键同步到金蝶系统")
    print()
    print("⏳ 请稍候...")
    
    # 延迟启动浏览器
    import threading
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动主程序
    try:
        from main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    except KeyboardInterrupt:
        print("\\n👋 系统已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("\\n💡 解决方案:")
        print("1. 检查端口8000是否被占用")
        print("2. 检查网络连接")
        print("3. 重新启动程序")
        input("\\n按任意键退出...")

if __name__ == "__main__":
    main()
'''
    
    with open('portable_main.py', 'w', encoding='utf-8') as f:
        f.write(portable_main)
    
    print("✅ 便携版主程序已创建")

def create_installer():
    """创建安装程序脚本"""
    installer_script = '''
; 智能仓管系统安装脚本
; 使用Inno Setup创建

[Setup]
AppName=智能仓管系统
AppVersion=1.0
DefaultDirName={pf}\\智能仓管系统
DefaultGroupName=智能仓管系统
OutputDir=installer
OutputBaseFilename=智能仓管系统安装包
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\智能仓管系统\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\智能仓管系统"; Filename: "{app}\\启动系统.bat"; WorkingDir: "{app}"
Name: "{group}\\卸载智能仓管系统"; Filename: "{uninstallexe}"
Name: "{commondesktop}\\智能仓管系统"; Filename: "{app}\\启动系统.bat"; WorkingDir: "{app}"

[Run]
Filename: "{app}\\启动系统.bat"; Description: "启动智能仓管系统"; Flags: nowait postinstall skipifsilent
'''
    
    with open('installer.iss', 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("✅ 安装程序脚本已创建")

def create_readme():
    """创建发布说明"""
    readme_content = """# 智能仓管系统 - 可执行版本

## 🎯 系统简介
基于AI的智能仓管系统，支持纸质单据OCR识别和金蝶ERP集成。
专为中小企业设计，无需Python环境即可运行。

## 🚀 快速开始

### 方法一：直接运行（推荐）
1. 解压文件到任意目录
2. 双击"启动系统.bat"
3. 等待浏览器自动打开
4. 开始使用！

### 方法二：手动启动
1. 双击"智能仓管系统.exe"
2. 手动打开浏览器访问 http://localhost:8000

## 💡 使用说明

### 基本操作
1. 📸 拍照上传纸质单据（入库单/出库单）
2. 🤖 系统自动OCR识别文字内容
3. 📋 智能解析提取关键信息
4. 💾 一键同步到金蝶系统或导出Excel

### 支持格式
- 图片格式：PNG, JPG, JPEG
- 单据类型：入库单、出库单
- 输出格式：金蝶数据库、Excel文件

## ⚙️ 配置说明

### OCR配置（默认在线模式）
- 使用免费的OCR.Space服务
- 每月25,000次免费识别
- 无需额外配置

### 金蝶集成（默认Excel模式）
- 自动生成Excel文件：kingdee_data.xlsx
- 包含单据主表和明细表
- 可手动导入金蝶系统

### 高级配置
编辑 .env 文件可修改：
- OCR服务类型
- 金蝶集成方式
- 文件存储路径

## 🔧 系统要求
- Windows 7/8/10/11
- 2GB内存
- 100MB硬盘空间
- 网络连接（用于在线OCR）

## 📞 技术支持
- 遇到问题请查看系统日志
- 确保网络连接正常
- 检查防火墙设置

## 🎉 版本信息
- 版本：1.0
- 更新日期：2024年1月
- 支持系统：Windows
"""
    
    with open('发布说明.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 发布说明已创建")

def main():
    """主函数"""
    print("📦 智能仓管系统打包工具")
    print("=" * 40)
    
    # 创建所有必要文件
    create_spec_file()
    create_build_script()
    create_portable_main()
    create_installer()
    create_readme()
    
    print("\n🎉 打包文件创建完成！")
    print("\n📋 使用步骤:")
    print("1. 双击 build.bat 开始打包")
    print("2. 等待打包完成")
    print("3. 在 dist/智能仓管系统/ 目录找到可执行文件")
    print("4. 双击 启动系统.bat 运行程序")
    
    print("\n📁 生成的文件:")
    print("- warehouse_system.spec (PyInstaller配置)")
    print("- build.bat (自动打包脚本)")
    print("- portable_main.py (便携版主程序)")
    print("- installer.iss (安装程序脚本)")
    print("- 发布说明.md (用户手册)")

if __name__ == "__main__":
    main()