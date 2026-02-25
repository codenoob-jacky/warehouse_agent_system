"""
金蝶KIS云专业版 v7.0.0.9 / v16.0 集成模块
支持应用平台版本 v2.2.1
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any

class KingdeeCloudV7:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['base_url'].rstrip('/')
        self.acct_id = config['acct_id']
        self.username = config['username']
        self.password = config['password']
        self.app_id = config.get('app_id', '')
        self.app_secret = config.get('app_secret', '')
        self.cookies = {}
        
    def login(self) -> bool:
        """登录金蝶云"""
        try:
            url = f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.AuthService.ValidateUser.common.kdsvc"
            data = {
                "acctID": self.acct_id,
                "username": self.username,
                "password": self.password,
                "lcid": 2052
            }
            
            resp = requests.post(url, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                if result.get('LoginResultType') == 1:
                    self.cookies = resp.cookies.get_dict()
                    return True
            return False
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def save_inbound(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存入库单"""
        if not self.cookies and not self.login():
            return {'success': False, 'error': '登录失败'}
        
        try:
            url = f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc"
            
            bill_data = {
                "Model": {
                    "FBillNo": data.get('bill_no', ''),
                    "FDate": data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    "FStockOrgId": {"FNumber": "100"},
                    "FPurchaseOrgId": {"FNumber": "100"},
                    "FSupplierId": {"FNumber": data.get('supplier_code', 'GYS001')},
                    "FStockDirect": "GENERAL",
                    "FBillTypeID": {"FNumber": "RKD01"},
                    "FInStockEntry": []
                }
            }
            
            for item in data.get('items', []):
                entry = {
                    "FMaterialId": {"FNumber": item.get('material_code', '')},
                    "FUnitID": {"FNumber": item.get('unit', 'Pcs')},
                    "FQty": item.get('qty', 0),
                    "FPrice": item.get('price', 0),
                    "FStockId": {"FNumber": data.get('warehouse', 'CK01')}
                }
                bill_data["Model"]["FInStockEntry"].append(entry)
            
            payload = {
                "formid": "STK_InStock",
                "data": bill_data
            }
            
            resp = requests.post(url, json=payload, cookies=self.cookies, timeout=30)
            result = resp.json()
            
            if result.get('Result', {}).get('ResponseStatus', {}).get('IsSuccess'):
                return {
                    'success': True,
                    'bill_no': result['Result']['Number'],
                    'id': result['Result']['Id']
                }
            else:
                errors = result.get('Result', {}).get('ResponseStatus', {}).get('Errors', [])
                return {'success': False, 'error': str(errors)}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_outbound(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存出库单"""
        if not self.cookies and not self.login():
            return {'success': False, 'error': '登录失败'}
        
        try:
            url = f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc"
            
            bill_data = {
                "Model": {
                    "FBillNo": data.get('bill_no', ''),
                    "FDate": data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    "FStockOrgId": {"FNumber": "100"},
                    "FSaleOrgId": {"FNumber": "100"},
                    "FCustomerID": {"FNumber": data.get('customer_code', 'KH001')},
                    "FStockDirect": "GENERAL",
                    "FBillTypeID": {"FNumber": "CKD01"},
                    "FEntity": []
                }
            }
            
            for item in data.get('items', []):
                entry = {
                    "FMaterialId": {"FNumber": item.get('material_code', '')},
                    "FUnitID": {"FNumber": item.get('unit', 'Pcs')},
                    "FQty": item.get('qty', 0),
                    "FPrice": item.get('price', 0),
                    "FStockId": {"FNumber": data.get('warehouse', 'CK01')}
                }
                bill_data["Model"]["FEntity"].append(entry)
            
            payload = {
                "formid": "SAL_OUTSTOCK",
                "data": bill_data
            }
            
            resp = requests.post(url, json=payload, cookies=self.cookies, timeout=30)
            result = resp.json()
            
            if result.get('Result', {}).get('ResponseStatus', {}).get('IsSuccess'):
                return {
                    'success': True,
                    'bill_no': result['Result']['Number'],
                    'id': result['Result']['Id']
                }
            else:
                errors = result.get('Result', {}).get('ResponseStatus', {}).get('Errors', [])
                return {'success': False, 'error': str(errors)}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

def parse_ocr_to_kingdee(ocr_text: str, doc_type: str) -> Dict[str, Any]:
    """将OCR文本解析为金蝶格式"""
    import re
    
    result = {
        'bill_no': '',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'items': []
    }
    
    # 提取单据号
    bill_match = re.search(r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)', ocr_text)
    if bill_match:
        result['bill_no'] = bill_match.group(2)
    
    # 提取日期
    date_match = re.search(r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', ocr_text)
    if date_match:
        result['date'] = date_match.group(2).replace('年', '-').replace('月', '-').replace('日', '')
    
    # 提取供应商/客户
    if doc_type == 'inbound':
        supplier_match = re.search(r'(供应商|供货商)[:：]\s*([^\n\r]+)', ocr_text)
        if supplier_match:
            result['supplier_code'] = supplier_match.group(2).strip()
    else:
        customer_match = re.search(r'(客户|收货方)[:：]\s*([^\n\r]+)', ocr_text)
        if customer_match:
            result['customer_code'] = customer_match.group(2).strip()
    
    return result
