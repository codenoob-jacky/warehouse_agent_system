import os
import json
from typing import Dict, List, Any, Optional
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import re
from datetime import datetime

class DocumentOCR:
    def __init__(self, config: Dict[str, Any]):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=config.get('lang', 'ch'),
            use_gpu=config.get('use_gpu', False)
        )
        
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """从图片中提取文字"""
        try:
            result = self.ocr.ocr(image_path, cls=True)
            extracted_data = []
            
            for idx in range(len(result)):
                res = result[idx]
                if res is None:
                    continue
                    
                for line in res:
                    box = line[0]  # 坐标
                    text = line[1][0]  # 文字
                    confidence = line[1][1]  # 置信度
                    
                    extracted_data.append({
                        'text': text,
                        'confidence': confidence,
                        'position': box
                    })
            
            return extracted_data
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")

class DocumentParser:
    def __init__(self):
        # 入库单关键字模式
        self.inbound_patterns = {
            'document_type': r'(入库单|入货单|收货单)',
            'document_number': r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)',
            'date': r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
            'supplier': r'(供应商|供货商|厂商)[:：]\s*([^\n\r]+)',
            'warehouse': r'(仓库|库房)[:：]\s*([^\n\r]+)',
            'total_amount': r'(总金额|合计|总计)[:：]\s*([0-9,]+\.?\d*)',
        }
        
        # 出库单关键字模式
        self.outbound_patterns = {
            'document_type': r'(出库单|出货单|发货单)',
            'document_number': r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)',
            'date': r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
            'customer': r'(客户|收货方|收货人)[:：]\s*([^\n\r]+)',
            'warehouse': r'(仓库|库房)[:：]\s*([^\n\r]+)',
            'total_amount': r'(总金额|合计|总计)[:：]\s*([0-9,]+\.?\d*)',
        }
        
        # 商品明细模式
        self.item_patterns = {
            'item_code': r'([A-Z0-9\-]{6,})',
            'item_name': r'[\u4e00-\u9fa5]{2,}',
            'quantity': r'(\d+\.?\d*)\s*(个|件|箱|包|台|套)',
            'unit_price': r'(\d+\.?\d*)\s*元',
            'amount': r'(\d+\.?\d*)\s*元'
        }

    def parse_document(self, ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析单据内容"""
        full_text = ' '.join([item['text'] for item in ocr_results])
        
        # 判断单据类型
        doc_type = self._detect_document_type(full_text)
        
        if doc_type == 'inbound':
            return self._parse_inbound_document(full_text, ocr_results)
        elif doc_type == 'outbound':
            return self._parse_outbound_document(full_text, ocr_results)
        else:
            return {'error': '无法识别单据类型'}

    def _detect_document_type(self, text: str) -> str:
        """检测单据类型"""
        if re.search(self.inbound_patterns['document_type'], text):
            return 'inbound'
        elif re.search(self.outbound_patterns['document_type'], text):
            return 'outbound'
        return 'unknown'

    def _parse_inbound_document(self, text: str, ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析入库单"""
        result = {
            'document_type': 'inbound',
            'basic_info': {},
            'items': [],
            'raw_ocr': ocr_results
        }
        
        # 提取基本信息
        for key, pattern in self.inbound_patterns.items():
            match = re.search(pattern, text)
            if match and len(match.groups()) > 1:
                result['basic_info'][key] = match.group(2).strip()
            elif match:
                result['basic_info'][key] = match.group(1).strip()
        
        # 提取商品明细
        result['items'] = self._extract_items(text)
        
        return result

    def _parse_outbound_document(self, text: str, ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析出库单"""
        result = {
            'document_type': 'outbound',
            'basic_info': {},
            'items': [],
            'raw_ocr': ocr_results
        }
        
        # 提取基本信息
        for key, pattern in self.outbound_patterns.items():
            match = re.search(pattern, text)
            if match and len(match.groups()) > 1:
                result['basic_info'][key] = match.group(2).strip()
            elif match:
                result['basic_info'][key] = match.group(1).strip()
        
        # 提取商品明细
        result['items'] = self._extract_items(text)
        
        return result

    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """提取商品明细"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 尝试匹配商品信息
            item = {}
            
            # 商品编码
            code_match = re.search(self.item_patterns['item_code'], line)
            if code_match:
                item['item_code'] = code_match.group(1)
            
            # 商品名称
            name_match = re.search(self.item_patterns['item_name'], line)
            if name_match:
                item['item_name'] = name_match.group(0)
            
            # 数量
            qty_match = re.search(self.item_patterns['quantity'], line)
            if qty_match:
                item['quantity'] = float(qty_match.group(1))
                item['unit'] = qty_match.group(2)
            
            # 单价
            price_match = re.search(self.item_patterns['unit_price'], line)
            if price_match:
                item['unit_price'] = float(price_match.group(1))
            
            # 金额
            amount_match = re.search(self.item_patterns['amount'], line)
            if amount_match:
                item['amount'] = float(amount_match.group(1))
            
            if len(item) >= 2:  # 至少有2个字段才认为是有效商品行
                items.append(item)
        
        return items

class SmartDocumentProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.ocr = DocumentOCR(config)
        self.parser = DocumentParser()
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """处理单据图片，返回结构化数据"""
        try:
            # OCR识别
            ocr_results = self.ocr.extract_text(image_path)
            
            # 解析结构化数据
            parsed_data = self.parser.parse_document(ocr_results)
            
            # 添加处理时间戳
            parsed_data['processed_at'] = datetime.now().isoformat()
            parsed_data['source_image'] = image_path
            
            return {
                'success': True,
                'data': parsed_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }