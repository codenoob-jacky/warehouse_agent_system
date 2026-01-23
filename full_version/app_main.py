import os
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
        print("\n👋 系统已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("\n💡 解决方案:")
        print("1. 检查端口8000是否被占用")
        print("2. 检查网络连接")
        print("3. 重新启动程序")
        input("\n按任意键退出...")

if __name__ == "__main__":
    main()