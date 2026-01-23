import requests
import re
from typing import Dict, List, Any
from datetime import datetime

class SimpleOCRProcessor:
    def __init__(self, api_key: str = "helloworld"):
        self.api_key = api_key
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """处理单据图片，返回结构化数据"""
        try:
            # 调用OCR.Space API
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'apikey': self.api_key,
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
                    # 提取文字内容
                    text_content = ""
                    for parsed_result in result.get('ParsedResults', []):
                        text_content += parsed_result.get('ParsedText', '')
                    
                    # 简单解析
                    parsed_data = self._parse_text(text_content)
                    parsed_data['processed_at'] = datetime.now().isoformat()
                    parsed_data['source_image'] = image_path
                    
                    return {
                        'success': True,
                        'data': parsed_data
                    }
                else:
                    error_msg = result.get('ErrorMessage', ['OCR processing failed'])[0]
                    return {'success': False, 'error': error_msg}
            else:
                return {'success': False, 'error': f'OCR API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'OCR failed: {str(e)}'}
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """简单解析文字内容"""
        result = {
            'document_type': 'unknown',
            'text_content': text,
            'basic_info': {},
            'items': []
        }
        
        # 检测单据类型
        if any(word in text for word in ['入库单', '入货单', '收货单']):
            result['document_type'] = 'inbound'
        elif any(word in text for word in ['出库单', '出货单', '发货单']):
            result['document_type'] = 'outbound'
        
        # 提取基本信息
        # 单据号
        bill_no_match = re.search(r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)', text)
        if bill_no_match:
            result['basic_info']['document_number'] = bill_no_match.group(2)
        
        # 日期
        date_match = re.search(r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
        if date_match:
            result['basic_info']['date'] = date_match.group(2)
        
        # 供应商/客户
        if result['document_type'] == 'inbound':
            supplier_match = re.search(r'(供应商|供货商|厂商)[:：]\s*([^\n\r]+)', text)
            if supplier_match:
                result['basic_info']['supplier'] = supplier_match.group(2).strip()
        elif result['document_type'] == 'outbound':
            customer_match = re.search(r'(客户|收货方|收货人)[:：]\s*([^\n\r]+)', text)
            if customer_match:
                result['basic_info']['customer'] = customer_match.group(2).strip()
        
        # 总金额
        amount_match = re.search(r'(总金额|合计|总计)[:：]\s*([0-9,]+\.?\d*)', text)
        if amount_match:
            result['basic_info']['total_amount'] = amount_match.group(2)
        
        return result