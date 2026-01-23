from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import shutil
from typing import Dict, Any
import uuid
from datetime import datetime

from config.settings import Config
from utils.ocr_processor import SimpleOCRProcessor
from utils.excel_exporter import ExcelExporter

# 确保目录存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# 初始化应用
app = FastAPI(
    title="Smart Warehouse System - Packaged Version",
    description="Simplified AI-based warehouse document recognition system",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
ocr_processor = SimpleOCRProcessor(Config.OCR_SPACE_API_KEY)
excel_exporter = ExcelExporter(Config.KINGDEE_EXCEL_PATH)

# 存储处理结果
processing_results = {}

def allowed_file(filename: str) -> bool:
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Warehouse System</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .upload-area { border: 2px dashed #ddd; padding: 40px; text-align: center; margin: 20px 0; border-radius: 8px; }
            .upload-area:hover { border-color: #007bff; background: #f8f9fa; }
            input[type="file"] { margin: 20px 0; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .success { border-left: 4px solid #28a745; }
            .error { border-left: 4px solid #dc3545; }
            .loading { text-align: center; color: #666; }
            .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Smart Warehouse System</h1>
            <div class="info">
                <strong>📦 Packaged Version</strong> - Simplified OCR recognition system<br>
                Supports online OCR recognition and Excel export
            </div>
            
            <div class="upload-area">
                <h3>📸 Upload Document Image</h3>
                <p>Supports PNG, JPG, JPEG, PDF formats, max 16MB</p>
                <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,.pdf" />
                <br>
                <button onclick="uploadFile()">Start Processing</button>
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading">🔄 Processing, please wait...</div>';
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>✅ Processing Successful</h3>
                            <p><strong>Task ID:</strong> ${result.task_id}</p>
                            <p><strong>Processing Time:</strong> ${result.processed_at}</p>
                            <button onclick="getResult('${result.task_id}')">View Details</button>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <h3>❌ Processing Failed</h3>
                            <p>${result.error}</p>
                        `;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>❌ Network Error</h3>
                        <p>${error.message}</p>
                    `;
                }
            }
            
            async function getResult(taskId) {
                try {
                    const response = await fetch(`/result/${taskId}`);
                    const result = await response.json();
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = `
                        <h3>📋 Processing Details</h3>
                        <pre style="background: #f1f1f1; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px;">${JSON.stringify(result, null, 2)}</pre>
                    `;
                } catch (error) {
                    alert('Failed to get result: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """上传并处理单据图片"""
    
    # 验证文件
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    if file.size and file.size > Config.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # 生成唯一文件名
    task_id = str(uuid.uuid4())
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{task_id}.{file_extension}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 后台处理
        background_tasks.add_task(process_document_task, task_id, file_path)
        
        return {
            "success": True,
            "task_id": task_id,
            "filename": file.filename,
            "processed_at": datetime.now().isoformat(),
            "message": "File uploaded successfully, processing in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

async def process_document_task(task_id: str, file_path: str):
    """后台处理任务"""
    try:
        # OCR处理
        ocr_result = ocr_processor.process_document(file_path)
        
        if ocr_result['success']:
            # 保存到Excel
            excel_result = excel_exporter.save_document(ocr_result['data'])
            ocr_result['excel_result'] = excel_result
        
        # 存储结果
        processing_results[task_id] = {
            "task_id": task_id,
            "file_path": file_path,
            "result": ocr_result,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        processing_results[task_id] = {
            "task_id": task_id,
            "file_path": file_path,
            "error": str(e),
            "processed_at": datetime.now().isoformat()
        }

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取处理结果"""
    if task_id not in processing_results:
        raise HTTPException(status_code=404, detail="Task not found or still processing")
    
    return processing_results[task_id]

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0 - Packaged",
        "ocr_mode": "online",
        "export_mode": "excel"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)