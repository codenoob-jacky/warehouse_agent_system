import os
from typing import Dict, Any

class Config:
    # 基础配置
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "warehouse-agent-secret-key")
    
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")
    
    # Redis配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # 金蝶系统配置
    KINGDEE_TYPE = os.getenv("KINGDEE_TYPE", "local")  # online, local, excel
    
    # 在线金蝶配置
    KINGDEE_ONLINE_CONFIG = {
        "base_url": os.getenv("KINGDEE_BASE_URL", "http://localhost:8080"),
        "username": os.getenv("KINGDEE_USERNAME", ""),
        "password": os.getenv("KINGDEE_PASSWORD", ""),
        "database": os.getenv("KINGDEE_DATABASE", ""),
        "timeout": 30
    }
    
    # 本地金蝶数据库配置
    KINGDEE_LOCAL_CONFIG = {
        "db_type": os.getenv("KINGDEE_DB_TYPE", "access"),  # access, sqlserver, sqlite
        "db_path": os.getenv("KINGDEE_DB_PATH", r"C:\KDW\KDMAIN.MDB"),  # Access数据库路径
        "server": os.getenv("KINGDEE_SERVER", "localhost"),
        "database": os.getenv("KINGDEE_LOCAL_DATABASE", "AIS"),
        "username": os.getenv("KINGDEE_LOCAL_USERNAME", "sa"),
        "password": os.getenv("KINGDEE_LOCAL_PASSWORD", "")
    }
    
    # Excel导出配置
    KINGDEE_EXCEL_CONFIG = {
        "excel_path": os.getenv("KINGDEE_EXCEL_PATH", "./kingdee_data.xlsx")
    }
    
    # OCR配置
    OCR_MODE = os.getenv("OCR_MODE", "online")  # local, online
    OCR_CONFIG = {
        "mode": OCR_MODE,
        "use_gpu": os.getenv("OCR_USE_GPU", "False").lower() == "true",
        "lang": "ch",
        "use_angle_cls": True,
        "use_space_char": True,
        "drop_score": 0.5,
        # 在线OCR配置
        "online_ocr": {
            "ocr_space": {
                "enabled": True,
                "api_key": os.getenv("OCR_SPACE_API_KEY", "helloworld"),
                "timeout": 30
            },
            "baidu": {
                "enabled": os.getenv("BAIDU_OCR_ENABLED", "False").lower() == "true",
                "api_key": os.getenv("BAIDU_OCR_API_KEY", ""),
                "secret_key": os.getenv("BAIDU_OCR_SECRET_KEY", ""),
                "timeout": 30
            }
        }
    }
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # 代理配置
    AGENT_CONFIG = {
        "max_iterations": 5,
        "verbose": True,
        "memory": True
    }

# 环境变量模板
ENV_TEMPLATE = """
# 基础配置
DEBUG=True
SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_URL=sqlite:///warehouse.db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# 金蝶系统类型 (online/local/excel)
KINGDEE_TYPE=local

# 在线金蝶系统
KINGDEE_BASE_URL=http://your-kingdee-server:8080
KINGDEE_USERNAME=your-username
KINGDEE_PASSWORD=your-password
KINGDEE_DATABASE=your-database

# 本地金蝶数据库
KINGDEE_DB_TYPE=access
KINGDEE_DB_PATH=C:\KDW\KDMAIN.MDB
KINGDEE_SERVER=localhost
KINGDEE_LOCAL_DATABASE=AIS
KINGDEE_LOCAL_USERNAME=sa
KINGDEE_LOCAL_PASSWORD=

# Excel导出
KINGDEE_EXCEL_PATH=./kingdee_data.xlsx

# OCR
OCR_USE_GPU=False

# 文件上传
UPLOAD_FOLDER=./uploads
"""