from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import shutil
from typing import Dict, Any
import uuid
from datetime import datetime
import json

# 简化配置
OCR_MODE = os.getenv("OCR_MODE", "online")
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")
KINGDEE_TYPE = os.getenv("KINGDEE_TYPE", "excel")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# 初始化应用
app = FastAPI(
    title="Smart Warehouse System",
    description="AI-based warehouse document recognition system",
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

# 存储处理结果
processing_results = {}

def allowed_file(filename: str) -> bool:
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def simple_ocr_process(image_path: str) -> Dict[str, Any]:
    """简化的OCR处理"""
    try:
        import requests
        
        # 使用OCR.Space API
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'apikey': OCR_SPACE_API_KEY,
                'language': 'chs',
                'isOverlayRequired': 'false',
                'detectOrientation': 'false',
                'scale': 'true',
                'OCREngine': '2'
            }
            
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('IsErroredOnProcessing'):
                text_content = ""
                for parsed_result in result.get('ParsedResults', []):
                    text_content += parsed_result.get('ParsedText', '')
                
                # 简单解析
                parsed_data = {
                    'document_type': 'unknown',
                    'text_content': text_content,
                    'basic_info': {},
                    'items': []
                }
                
                # 检测单据类型
                if any(word in text_content for word in ['入库单', '入货单', '收货单']):
                    parsed_data['document_type'] = 'inbound'
                elif any(word in text_content for word in ['出库单', '出货单', '发货单']):
                    parsed_data['document_type'] = 'outbound'
                
                return {
                    'success': True,
                    'data': parsed_data
                }
            else:
                return {'success': False, 'error': 'OCR processing failed'}
        else:
            return {'success': False, 'error': f'OCR API error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'OCR failed: {str(e)}'}

def save_to_excel(data: Dict[str, Any]) -> Dict[str, Any]:
    """保存到Excel"""
    try:
        import pandas as pd
        from datetime import datetime
        
        excel_path = "kingdee_data.xlsx"
        
        # 准备数据
        main_data = {
            '单据号': data.get('basic_info', {}).get('document_number', ''),
            '日期': datetime.now().strftime('%Y-%m-%d'),
            '类型': data.get('document_type', ''),
            '内容': data.get('text_content', '')[:100] + '...' if len(data.get('text_content', '')) > 100 else data.get('text_content', '')
        }
        
        # 创建或追加到Excel
        try:
            existing_df = pd.read_excel(excel_path)
            new_df = pd.concat([existing_df, pd.DataFrame([main_data])], ignore_index=True)
        except:
            new_df = pd.DataFrame([main_data])
        
        new_df.to_excel(excel_path, index=False)
        
        return {
            'success': True,
            'message': f'数据已保存到 {excel_path}',
            'excel_path': excel_path
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Excel保存失败: {str(e)}'}

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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Smart Warehouse System</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Upload document images for automatic OCR recognition
            </p>
            
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
                        <pre style="background: #f1f1f1; padding: 15px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
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
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # 生成唯一文件名
    task_id = str(uuid.uuid4())
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{task_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
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
        ocr_result = simple_ocr_process(file_path)
        
        if ocr_result['success']:
            # 保存到Excel
            excel_result = save_to_excel(ocr_result['data'])
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
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)