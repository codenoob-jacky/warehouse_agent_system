import os

class Config:
    # 基础配置
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "warehouse-simple-key")
    
    # OCR配置
    OCR_MODE = os.getenv("OCR_MODE", "online")
    OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")
    
    # 金蝶配置
    KINGDEE_TYPE = os.getenv("KINGDEE_TYPE", "excel")
    KINGDEE_EXCEL_PATH = os.getenv("KINGDEE_EXCEL_PATH", "./kingdee_data.xlsx")
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}