import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

# Set default config
os.environ.setdefault('OCR_MODE', 'online')
os.environ.setdefault('OCR_SPACE_API_KEY', 'helloworld')
os.environ.setdefault('KINGDEE_TYPE', 'excel')

def check_config():
    """Check config file"""
    env_file = Path('.env')
    if not env_file.exists():
        print("Creating default config...")
        default_config = """# Smart Warehouse System Config
# OCR Mode (online recommended)
OCR_MODE=online
OCR_SPACE_API_KEY=helloworld

# Kingdee System Type (excel simple)
KINGDEE_TYPE=excel
KINGDEE_EXCEL_PATH=./kingdee_data.xlsx

# File Upload
UPLOAD_FOLDER=./uploads
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(default_config)
        print("Config file created")

def main():
    """Main function"""
    print("Smart Warehouse System")
    print("=" * 40)
    print("AI-based warehouse document recognition system")
    print("Supports OCR recognition and Kingdee ERP integration")
    print()
    
    # Check config
    check_config()
    
    # Create directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("Starting system...")
    print("Browser will open automatically")
    print("Access: http://localhost:8000")
    print()
    print("Instructions:")
    print("1. Upload document images")
    print("2. System auto OCR recognition")
    print("3. Smart parse document content")
    print("4. Export to Excel")
    print()
    print("Please wait...")
    
    # Delayed browser launch
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start FastAPI app
    try:
        from simple_main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
    except KeyboardInterrupt:
        print("\nSystem closed")
    except Exception as e:
        print(f"Start failed: {str(e)}")
        print("\nSolutions:")
        print("1. Check if dependencies installed")
        print("2. Check if port 8000 is occupied")
        print("3. Check network connection")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()