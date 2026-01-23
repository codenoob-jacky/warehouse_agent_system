from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
import requests
import base64
import os
import uuid
from datetime import datetime
import json
import re
from packaged_version.simple_kingdee import SimpleKingdeeDB, parse_document_enhanced

app = FastAPI(title="Warehouse OCR System")

# 全局变量存储API密钥
OCR_API_KEY = "helloworld"

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Warehouse OCR System</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { text-align: center; color: #333; }
        .config { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .upload { border: 2px dashed #ddd; padding: 30px; text-align: center; border-radius: 5px; }
        input, button { margin: 10px 0; padding: 10px; }
        button { background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Warehouse OCR System</h1>
        
        <div class="config">
            <h3>🔑 OCR API Configuration</h3>
            <input type="text" id="apiKey" placeholder="Enter OCR API Key (default: helloworld)" style="width: 300px;">
            <button onclick="setApiKey()">Set API Key</button>
            <p><small>Free API Key: helloworld (25,000 uses/month)</small></p>
            <p><small>📁 Kingdee DB: Auto-detect from C:\KDW\KDMAIN.MDB</small></p>
        </div>
        
        <div class="upload">
            <h3>📸 Upload Document</h3>
            <input type="file" id="fileInput" accept=".png,.jpg,.jpeg">
            <br>
            <button onclick="processDocument()">Process Document</button>
        </div>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>

    <script>
        let currentApiKey = 'helloworld';
        
        function setApiKey() {
            const apiKey = document.getElementById('apiKey').value;
            if (apiKey) {
                currentApiKey = apiKey;
                alert('API Key updated: ' + apiKey);
            }
        }
        
        async function processDocument() {
            const fileInput = document.getElementById('fileInput');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files[0]) {
                alert('Please select a file');
                return;
            }
            
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>🔄 Processing...</p>';
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('api_key', currentApiKey);
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <h3>✅ OCR Results</h3>
                        <p><strong>Document Type:</strong> ${result.document_type}</p>
                        <p><strong>Extracted Text:</strong></p>
                        <pre style="background: white; padding: 10px; border-radius: 3px;">${result.text}</pre>
                        <p><strong>Parsed Data:</strong></p>
                        <pre style="background: white; padding: 10px; border-radius: 3px;">${JSON.stringify(result.parsed_data, null, 2)}</pre>
                        <p><strong>Kingdee Result:</strong></p>
                        <pre style="background: white; padding: 10px; border-radius: 3px;">${JSON.stringify(result.kingdee_result, null, 2)}</pre>
                    `;
                } else {
                    resultDiv.innerHTML = `<p>❌ Error: ${result.error}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p>❌ Network Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
    """

@app.post("/process")
async def process_document(file: UploadFile = File(...), api_key: str = "helloworld"):
    """处理文档"""
    try:
        # 保存临时文件
        temp_file = f"temp_{uuid.uuid4().hex}.{file.filename.split('.')[-1]}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 调用在线OCR
        with open(temp_file, 'rb') as f:
            files = {'file': f}
            data = {
                'apikey': api_key,
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
        
        # 删除临时文件
        os.remove(temp_file)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('IsErroredOnProcessing'):
                # 提取文字
                text_content = ""
                for parsed_result in result.get('ParsedResults', []):
                    text_content += parsed_result.get('ParsedText', '')
                
                # 增强解析
                parsed_data = parse_document_enhanced(text_content)
                document_type = parsed_data['document_type']
                
                # 保存到金蝶数据库
                kingdee_db = SimpleKingdeeDB()
                save_result = kingdee_db.save_document(parsed_data)
                
                return {
                    'success': True,
                    'text': text_content,
                    'document_type': document_type,
                    'parsed_data': parsed_data,
                    'kingdee_result': save_result
                }
            else:
                return {'success': False, 'error': 'OCR processing failed'}
        else:
            return {'success': False, 'error': f'OCR API error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)