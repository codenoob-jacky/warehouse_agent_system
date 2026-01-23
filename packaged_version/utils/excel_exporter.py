import pandas as pd
import os
from typing import Dict, Any
from datetime import datetime

class ExcelExporter:
    def __init__(self, excel_path: str = "./kingdee_data.xlsx"):
        self.excel_path = excel_path
        self.ensure_excel_exists()
    
    def ensure_excel_exists(self):
        """确保Excel文件存在"""
        if not os.path.exists(self.excel_path):
            # 创建空的Excel文件
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                pd.DataFrame(columns=['单据号', '日期', '类型', '供应商/客户', '总金额', '识别内容']).to_excel(
                    writer, sheet_name='单据记录', index=False)
    
    def save_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存单据到Excel"""
        try:
            basic_info = data.get('basic_info', {})
            
            # 准备数据
            record = {
                '单据号': basic_info.get('document_number', ''),
                '日期': basic_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                '类型': '入库单' if data.get('document_type') == 'inbound' else '出库单' if data.get('document_type') == 'outbound' else '未知',
                '供应商/客户': basic_info.get('supplier', '') or basic_info.get('customer', ''),
                '总金额': basic_info.get('total_amount', ''),
                '识别内容': data.get('text_content', '')[:200] + '...' if len(data.get('text_content', '')) > 200 else data.get('text_content', '')
            }
            
            # 读取现有数据
            try:
                existing_df = pd.read_excel(self.excel_path, sheet_name='单据记录')
                new_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
            except:
                new_df = pd.DataFrame([record])
            
            # 保存到Excel
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                new_df.to_excel(writer, sheet_name='单据记录', index=False)
            
            return {
                'success': True,
                'message': f'数据已保存到 {self.excel_path}',
                'excel_path': self.excel_path,
                'record_count': len(new_df)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Excel保存失败: {str(e)}'}