from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
import shutil
from typing import Dict, Any, List
import uuid
from datetime import datetime
import json

from config.settings import Config
from agents.warehouse_agents import WarehouseAgentSystem, SimpleWarehouseAgent

# 初始化应用
app = FastAPI(
    title="智能仓管系统",
    description="基于AI的仓管单据识别和处理系统，支持金蝶ERP集成",
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

# 确保上传目录存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化代理系统
config = {
    'OCR_CONFIG': Config.OCR_CONFIG,
    'KINGDEE_TYPE': Config.KINGDEE_TYPE,
    'KINGDEE_ONLINE_CONFIG': Config.KINGDEE_ONLINE_CONFIG,
    'KINGDEE_LOCAL_CONFIG': Config.KINGDEE_LOCAL_CONFIG,
    'KINGDEE_EXCEL_CONFIG': Config.KINGDEE_EXCEL_CONFIG,
    'AGENT_CONFIG': Config.AGENT_CONFIG
}

# 根据需要选择多代理或单代理
USE_MULTI_AGENT = True
if USE_MULTI_AGENT:
    agent_system = WarehouseAgentSystem(config)
else:
    agent_system = SimpleWarehouseAgent(config)

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
        <title>智能仓管系统</title>
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
            <h1>🏪 智能仓管系统</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                上传纸质单据图片，自动识别并同步到金蝶系统
            </p>
            
            <div class="upload-area">
                <h3>📸 上传单据图片</h3>
                <p>支持 PNG, JPG, JPEG, PDF 格式，最大 16MB</p>
                <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,.pdf" />
                <br>
                <button onclick="uploadFile()">开始处理</button>
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('请选择文件');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading">🔄 正在处理中，请稍候...</div>';
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>✅ 处理成功</h3>
                            <p><strong>任务ID:</strong> ${result.task_id}</p>
                            <p><strong>处理时间:</strong> ${result.processed_at}</p>
                            <button onclick="getResult('${result.task_id}')">查看详细结果</button>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <h3>❌ 处理失败</h3>
                            <p>${result.error}</p>
                        `;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>❌ 网络错误</h3>
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
                        <h3>📋 处理详情</h3>
                        <pre style="background: #f1f1f1; padding: 15px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
                    `;
                } catch (error) {
                    alert('获取结果失败: ' + error.message);
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
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    if file.size > Config.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件太大")
    
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
            "message": "文件上传成功，正在后台处理"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

async def process_document_task(task_id: str, file_path: str):
    """后台处理任务"""
    try:
        # 处理文档
        result = agent_system.process_document(file_path)
        
        # 存储结果
        processing_results[task_id] = {
            "task_id": task_id,
            "file_path": file_path,
            "result": result,
            "processed_at": datetime.now().isoformat()
        }
        
        # 清理文件（可选）
        # os.remove(file_path)
        
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
        raise HTTPException(status_code=404, detail="任务不存在或正在处理中")
    
    return processing_results[task_id]

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/inventory/{item_code}")
async def check_inventory(item_code: str, warehouse_code: str = None):
    """查询库存接口"""
    try:
        if USE_MULTI_AGENT:
            result = agent_system.kingdee_integration.check_inventory(item_code, warehouse_code)
        else:
            result = agent_system.kingdee_integration.check_inventory(item_code, warehouse_code)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.post("/api/manual-entry")
async def manual_entry(document_data: Dict[str, Any]):
    """手动录入单据接口"""
    try:
        # 验证数据
        if not document_data.get('document_type'):
            raise HTTPException(status_code=400, detail="缺少单据类型")
        
        # 处理单据
        if document_data['document_type'] == 'inbound':
            if USE_MULTI_AGENT:
                result = agent_system.kingdee_integration.process_inbound_document(document_data)
            else:
                result = agent_system.kingdee_integration.process_inbound_document(document_data)
        elif document_data['document_type'] == 'outbound':
            if USE_MULTI_AGENT:
                result = agent_system.kingdee_integration.process_outbound_document(document_data)
            else:
                result = agent_system.kingdee_integration.process_outbound_document(document_data)
        else:
            raise HTTPException(status_code=400, detail="不支持的单据类型")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)