"""
简化版金蝶数据库处理
只处理本地Access数据库，不依赖重型库
"""
import pyodbc
import os
import re
from datetime import datetime
from typing import Dict, Any, List

class SimpleKingdeeDB:
    def __init__(self, db_path: str = None):
        # 常见金蝶数据库路径
        self.possible_paths = [
            r"C:\KDW\KDMAIN.MDB",
            r"C:\KDMAIN\KDMAIN.MDB", 
            r"C:\Program Files\Kingdee\KDMAIN.MDB",
            r"D:\KDW\KDMAIN.MDB"
        ]
        
        self.db_path = db_path or self.find_kingdee_db()
        self.connection = None
    
    def find_kingdee_db(self) -> str:
        """查找金蝶数据库"""
        for path in self.possible_paths:
            if os.path.exists(path):
                return path
        return ""
    
    def connect(self) -> bool:
        """连接数据库"""
        if not self.db_path:
            return False
        
        try:
            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_path};"
            self.connection = pyodbc.connect(conn_str)
            return True
        except:
            return False
    
    def save_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存单据到金蝶数据库，失败时保存到Excel"""
        # 首先尝试连接金蝶数据库
        if self.connect():
            try:
                cursor = self.connection.cursor()
                
                # 生成单据号
                doc_type = parsed_data.get('document_type', 'Unknown')
                bill_no = parsed_data.get('bill_no') or self._generate_bill_no(doc_type)
                
                # 插入主表
                sql = """
                INSERT INTO ICStockBill (FBillNo, FDate, FBillType, FStatus, FRemark)
                VALUES (?, ?, ?, ?, ?)
                """
                
                bill_type = 1 if doc_type == 'Inbound' else 2
                remark = f"OCR识别导入 - {parsed_data.get('text', '')[:100]}"
                
                cursor.execute(sql, (
                    bill_no,
                    parsed_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    bill_type,
                    0,  # 未审核
                    remark
                ))
                
                self.connection.commit()
                
                return {
                    'success': True,
                    'bill_no': bill_no,
                    'message': f'单据已保存到金蝶数据库: {bill_no}'
                }
                
            except Exception as e:
                # 金蝶数据库保存失败，尝试Excel备用方案
                return self._save_to_excel_backup(parsed_data, f"金蝶数据库保存失败: {str(e)}")
            finally:
                if self.connection:
                    self.connection.close()
        else:
            # 无法连接金蝶数据库，使用Excel备用方案
            return self._save_to_excel_backup(parsed_data, "无法连接金蝶数据库")
    
    def _save_to_excel_backup(self, parsed_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Excel备用保存方案"""
        try:
            import pandas as pd
            
            excel_path = "warehouse_data.xlsx"
            
            # 准备数据
            record = {
                '单据号': parsed_data.get('bill_no', ''),
                '日期': parsed_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                '类型': '入库单' if parsed_data.get('document_type') == 'Inbound' else '出库单' if parsed_data.get('document_type') == 'Outbound' else '未知',
                '供应商/客户': parsed_data.get('supplier', '') or parsed_data.get('customer', ''),
                '总金额': parsed_data.get('amount', ''),
                '识别内容': parsed_data.get('text', '')[:200] + '...' if len(parsed_data.get('text', '')) > 200 else parsed_data.get('text', '')
            }
            
            # 读取现有数据或创建新文件
            try:
                existing_df = pd.read_excel(excel_path)
                new_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
            except:
                new_df = pd.DataFrame([record])
            
            # 保存到Excel
            new_df.to_excel(excel_path, index=False)
            
            return {
                'success': True,
                'bill_no': record['单据号'],
                'message': f'金蝶数据库不可用，已保存到Excel备用文件: {excel_path}\n原因: {reason}',
                'backup_mode': True
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': f'金蝶数据库和Excel备用方案都失败\n金蝶: {reason}\nExcel: {str(e)}'
            }
    
    def _generate_bill_no(self, doc_type: str) -> str:
        """生成单据号"""
        prefix = "RK" if doc_type == "Inbound" else "CK"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}{timestamp}"

def parse_document_enhanced(text: str) -> Dict[str, Any]:
    """增强的文档解析"""
    result = {
        'document_type': 'Unknown',
        'bill_no': '',
        'date': '',
        'amount': '',
        'supplier': '',
        'customer': '',
        'items': [],
        'text': text
    }
    
    # 单据类型
    if re.search(r'(入库单|入货单|收货单)', text):
        result['document_type'] = 'Inbound'
    elif re.search(r'(出库单|出货单|发货单)', text):
        result['document_type'] = 'Outbound'
    
    # 单据号
    bill_match = re.search(r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)', text)
    if bill_match:
        result['bill_no'] = bill_match.group(2)
    
    # 日期
    date_match = re.search(r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
    if date_match:
        result['date'] = date_match.group(2).replace('年', '-').replace('月', '-').replace('日', '')
    
    # 供应商/客户
    if result['document_type'] == 'Inbound':
        supplier_match = re.search(r'(供应商|供货商|厂商)[:：]\s*([^\n\r]+)', text)
        if supplier_match:
            result['supplier'] = supplier_match.group(2).strip()
    else:
        customer_match = re.search(r'(客户|收货方|收货人)[:：]\s*([^\n\r]+)', text)
        if customer_match:
            result['customer'] = customer_match.group(2).strip()
    
    # 总金额
    amount_match = re.search(r'(总金额|合计|总计)[:：]\s*([0-9,]+\.?\d*)', text)
    if amount_match:
        result['amount'] = amount_match.group(2)
    
    # 商品明细（简单提取）
    lines = text.split('\n')
    for line in lines:
        # 匹配包含商品名称和数量的行
        if re.search(r'[\u4e00-\u9fa5]{2,}.*\d+.*[件箱台套个]', line):
            result['items'].append(line.strip())
    
    return result