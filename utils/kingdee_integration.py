import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import base64

class KingdeeAPI:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['base_url'].rstrip('/')
        self.username = config['username']
        self.password = config['password']
        self.database = config['database']
        self.timeout = config.get('timeout', 30)
        self.session_id = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def login(self) -> bool:
        """登录金蝶系统"""
        try:
            login_data = {
                "acctid": self.database,
                "username": self.username,
                "password": self.password,
                "lcid": 2052  # 中文
            }
            
            response = requests.post(
                f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.AuthService.ValidateUser.common.kdsvc",
                json=login_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('LoginResultType') == 1:
                    self.session_id = response.cookies.get('ASP.NET_SessionId')
                    return True
            
            return False
            
        except Exception as e:
            print(f"金蝶登录失败: {str(e)}")
            return False

    def create_inbound_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建入库单"""
        if not self.session_id:
            if not self.login():
                return {'success': False, 'error': '登录失败'}
        
        try:
            # 构建入库单数据结构
            kingdee_data = self._build_inbound_data(order_data)
            
            # 调用金蝶API
            response = requests.post(
                f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc",
                json={
                    "formid": "STK_InStock",  # 入库单表单ID
                    "data": kingdee_data
                },
                headers=self.headers,
                cookies={'ASP.NET_SessionId': self.session_id},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('Result', {}).get('ResponseStatus', {}).get('IsSuccess'):
                    return {
                        'success': True,
                        'bill_no': result['Result']['Id'],
                        'message': '入库单创建成功'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('Result', {}).get('ResponseStatus', {}).get('Errors', ['未知错误'])
                    }
            
            return {'success': False, 'error': f'HTTP错误: {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': f'创建入库单失败: {str(e)}'}

    def create_outbound_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建出库单"""
        if not self.session_id:
            if not self.login():
                return {'success': False, 'error': '登录失败'}
        
        try:
            # 构建出库单数据结构
            kingdee_data = self._build_outbound_data(order_data)
            
            # 调用金蝶API
            response = requests.post(
                f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc",
                json={
                    "formid": "SAL_OUTSTOCK",  # 出库单表单ID
                    "data": kingdee_data
                },
                headers=self.headers,
                cookies={'ASP.NET_SessionId': self.session_id},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('Result', {}).get('ResponseStatus', {}).get('IsSuccess'):
                    return {
                        'success': True,
                        'bill_no': result['Result']['Id'],
                        'message': '出库单创建成功'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('Result', {}).get('ResponseStatus', {}).get('Errors', ['未知错误'])
                    }
            
            return {'success': False, 'error': f'HTTP错误: {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': f'创建出库单失败: {str(e)}'}

    def query_inventory(self, item_code: str = None, warehouse_code: str = None) -> Dict[str, Any]:
        """查询库存"""
        if not self.session_id:
            if not self.login():
                return {'success': False, 'error': '登录失败'}
        
        try:
            query_data = {
                "FormId": "STK_Inventory",
                "FieldKeys": "FMaterialId,FStockId,FQty,FAvailableQty",
                "FilterString": ""
            }
            
            # 构建查询条件
            filters = []
            if item_code:
                filters.append(f"FMaterialId.FNumber='{item_code}'")
            if warehouse_code:
                filters.append(f"FStockId.FNumber='{warehouse_code}'")
            
            if filters:
                query_data["FilterString"] = " AND ".join(filters)
            
            response = requests.post(
                f"{self.base_url}/K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.ExecuteBillQuery.common.kdsvc",
                json=query_data,
                headers=self.headers,
                cookies={'ASP.NET_SessionId': self.session_id},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'data': result.get('Result', [])
                }
            
            return {'success': False, 'error': f'HTTP错误: {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': f'查询库存失败: {str(e)}'}

    def _build_inbound_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建入库单数据结构"""
        basic_info = order_data.get('basic_info', {})
        items = order_data.get('items', [])
        
        # 基本信息
        kingdee_data = {
            "FBillNo": basic_info.get('document_number', ''),
            "FDate": self._format_date(basic_info.get('date', '')),
            "FSupplierId": {"FNumber": basic_info.get('supplier', '')},
            "FStockOrgId": {"FNumber": "001"},  # 默认库存组织
            "FPurOrgId": {"FNumber": "001"},   # 默认采购组织
            "FStockId": {"FNumber": basic_info.get('warehouse', 'DEFAULT')},
            "FInStockEntry": []
        }
        
        # 明细行
        for item in items:
            entry = {
                "FMaterialId": {"FNumber": item.get('item_code', '')},
                "FQty": item.get('quantity', 0),
                "FPrice": item.get('unit_price', 0),
                "FAmount": item.get('amount', 0),
                "FStockId": {"FNumber": basic_info.get('warehouse', 'DEFAULT')}
            }
            kingdee_data["FInStockEntry"].append(entry)
        
        return kingdee_data

    def _build_outbound_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建出库单数据结构"""
        basic_info = order_data.get('basic_info', {})
        items = order_data.get('items', [])
        
        # 基本信息
        kingdee_data = {
            "FBillNo": basic_info.get('document_number', ''),
            "FDate": self._format_date(basic_info.get('date', '')),
            "FCustomerId": {"FNumber": basic_info.get('customer', '')},
            "FSaleOrgId": {"FNumber": "001"},  # 默认销售组织
            "FStockOrgId": {"FNumber": "001"}, # 默认库存组织
            "FStockId": {"FNumber": basic_info.get('warehouse', 'DEFAULT')},
            "FSALOUTSTOCKEntry": []
        }
        
        # 明细行
        for item in items:
            entry = {
                "FMaterialId": {"FNumber": item.get('item_code', '')},
                "FQty": item.get('quantity', 0),
                "FPrice": item.get('unit_price', 0),
                "FAmount": item.get('amount', 0),
                "FStockId": {"FNumber": basic_info.get('warehouse', 'DEFAULT')}
            }
            kingdee_data["FSALOUTSTOCKEntry"].append(entry)
        
        return kingdee_data

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # 处理各种日期格式
        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
        date_str = date_str.replace('/', '-')
        
        try:
            # 尝试解析日期
            if len(date_str.split('-')) == 3:
                return date_str
            else:
                return datetime.now().strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

class KingdeeIntegration:
    def __init__(self, config: Dict[str, Any]):
        self.api = KingdeeAPI(config)
    
    def process_inbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理入库单据"""
        try:
            result = self.api.create_inbound_order(parsed_data)
            return result
        except Exception as e:
            return {'success': False, 'error': f'处理入库单失败: {str(e)}'}
    
    def process_outbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理出库单据"""
        try:
            result = self.api.create_outbound_order(parsed_data)
            return result
        except Exception as e:
            return {'success': False, 'error': f'处理出库单失败: {str(e)}'}
    
    def check_inventory(self, item_code: str, warehouse_code: str = None) -> Dict[str, Any]:
        """检查库存"""
        try:
            result = self.api.query_inventory(item_code, warehouse_code)
            return result
        except Exception as e:
            return {'success': False, 'error': f'查询库存失败: {str(e)}'}