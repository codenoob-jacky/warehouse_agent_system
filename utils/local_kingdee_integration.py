import pyodbc
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json

class LocalKingdeeDB:
    def __init__(self, config: Dict[str, Any]):
        self.db_type = config.get('db_type', 'access')  # access, sqlserver, sqlite
        self.db_path = config.get('db_path', '')
        self.server = config.get('server', '')
        self.database = config.get('database', '')
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.connection = None
        
    def connect(self) -> bool:
        """连接数据库"""
        try:
            if self.db_type == 'access':
                # Access数据库连接
                conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_path};"
                self.connection = pyodbc.connect(conn_str)
            elif self.db_type == 'sqlserver':
                # SQL Server连接
                conn_str = f"DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
                self.connection = pyodbc.connect(conn_str)
            elif self.db_type == 'sqlite':
                # SQLite连接（用于测试）
                self.connection = sqlite3.connect(self.db_path)
            
            return True
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            return False

    def create_inbound_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建入库单"""
        if not self.connection:
            if not self.connect():
                return {'success': False, 'error': '数据库连接失败'}
        
        try:
            cursor = self.connection.cursor()
            basic_info = order_data.get('basic_info', {})
            items = order_data.get('items', [])
            
            # 生成单据号
            bill_no = basic_info.get('document_number') or self._generate_bill_no('RK')
            
            # 插入主表
            main_sql = """
            INSERT INTO ICStockBill (
                FBillNo, FDate, FSupplyID, FDeptID, FEmpID, 
                FBillType, FStatus, FAmount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            total_amount = sum(item.get('amount', 0) for item in items)
            
            cursor.execute(main_sql, (
                bill_no,
                basic_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                self._get_supplier_id(basic_info.get('supplier', '')),
                1,  # 默认部门
                1,  # 默认员工
                1,  # 入库单类型
                0,  # 未审核状态
                total_amount
            ))
            
            # 获取主表ID
            main_id = cursor.lastrowid if self.db_type == 'sqlite' else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            
            # 插入明细表
            for i, item in enumerate(items):
                detail_sql = """
                INSERT INTO ICStockBillEntry (
                    FID, FEntryID, FItemID, FQty, FPrice, FAmount,
                    FStockID, FBatchNo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(detail_sql, (
                    main_id,
                    i + 1,
                    self._get_item_id(item.get('item_code', '')),
                    item.get('quantity', 0),
                    item.get('unit_price', 0),
                    item.get('amount', 0),
                    self._get_stock_id(basic_info.get('warehouse', '')),
                    ''  # 批次号
                ))
            
            self.connection.commit()
            
            return {
                'success': True,
                'bill_no': bill_no,
                'main_id': main_id,
                'message': '入库单创建成功'
            }
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return {'success': False, 'error': f'创建入库单失败: {str(e)}'}

    def create_outbound_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建出库单"""
        if not self.connection:
            if not self.connect():
                return {'success': False, 'error': '数据库连接失败'}
        
        try:
            cursor = self.connection.cursor()
            basic_info = order_data.get('basic_info', {})
            items = order_data.get('items', [])
            
            # 生成单据号
            bill_no = basic_info.get('document_number') or self._generate_bill_no('CK')
            
            # 插入主表
            main_sql = """
            INSERT INTO ICStockBill (
                FBillNo, FDate, FCustID, FDeptID, FEmpID, 
                FBillType, FStatus, FAmount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            total_amount = sum(item.get('amount', 0) for item in items)
            
            cursor.execute(main_sql, (
                bill_no,
                basic_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                self._get_customer_id(basic_info.get('customer', '')),
                1,  # 默认部门
                1,  # 默认员工
                2,  # 出库单类型
                0,  # 未审核状态
                total_amount
            ))
            
            # 获取主表ID
            main_id = cursor.lastrowid if self.db_type == 'sqlite' else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            
            # 插入明细表
            for i, item in enumerate(items):
                detail_sql = """
                INSERT INTO ICStockBillEntry (
                    FID, FEntryID, FItemID, FQty, FPrice, FAmount,
                    FStockID, FBatchNo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(detail_sql, (
                    main_id,
                    i + 1,
                    self._get_item_id(item.get('item_code', '')),
                    item.get('quantity', 0),
                    item.get('unit_price', 0),
                    item.get('amount', 0),
                    self._get_stock_id(basic_info.get('warehouse', '')),
                    ''  # 批次号
                ))
            
            self.connection.commit()
            
            return {
                'success': True,
                'bill_no': bill_no,
                'main_id': main_id,
                'message': '出库单创建成功'
            }
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return {'success': False, 'error': f'创建出库单失败: {str(e)}'}

    def query_inventory(self, item_code: str = None, warehouse_code: str = None) -> Dict[str, Any]:
        """查询库存"""
        if not self.connection:
            if not self.connect():
                return {'success': False, 'error': '数据库连接失败'}
        
        try:
            cursor = self.connection.cursor()
            
            sql = """
            SELECT i.FNumber, i.FName, s.FName as FStockName, 
                   inv.FQty, inv.FAmount
            FROM ICInventory inv
            LEFT JOIN t_ICItem i ON inv.FItemID = i.FItemID
            LEFT JOIN t_Stock s ON inv.FStockID = s.FItemID
            WHERE 1=1
            """
            
            params = []
            if item_code:
                sql += " AND i.FNumber = ?"
                params.append(item_code)
            if warehouse_code:
                sql += " AND s.FNumber = ?"
                params.append(warehouse_code)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            inventory_data = []
            for row in results:
                inventory_data.append({
                    'item_code': row[0],
                    'item_name': row[1],
                    'warehouse': row[2],
                    'quantity': row[3],
                    'amount': row[4]
                })
            
            return {
                'success': True,
                'data': inventory_data
            }
            
        except Exception as e:
            return {'success': False, 'error': f'查询库存失败: {str(e)}'}

    def _generate_bill_no(self, prefix: str) -> str:
        """生成单据号"""
        today = datetime.now().strftime('%Y%m%d')
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM ICStockBill WHERE FBillNo LIKE ?",
                (f"{prefix}{today}%",)
            )
            count = cursor.fetchone()[0] + 1
            return f"{prefix}{today}{count:03d}"
        except:
            return f"{prefix}{today}001"

    def _get_supplier_id(self, supplier_name: str) -> int:
        """获取供应商ID"""
        if not supplier_name:
            return 1
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT FItemID FROM t_Supplier WHERE FName = ?", (supplier_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                # 创建新供应商
                cursor.execute(
                    "INSERT INTO t_Supplier (FNumber, FName) VALUES (?, ?)",
                    (f"GYS{datetime.now().strftime('%Y%m%d%H%M%S')}", supplier_name)
                )
                return cursor.lastrowid if self.db_type == 'sqlite' else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        except:
            return 1

    def _get_customer_id(self, customer_name: str) -> int:
        """获取客户ID"""
        if not customer_name:
            return 1
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT FItemID FROM t_Organization WHERE FName = ?", (customer_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                # 创建新客户
                cursor.execute(
                    "INSERT INTO t_Organization (FNumber, FName) VALUES (?, ?)",
                    (f"KH{datetime.now().strftime('%Y%m%d%H%M%S')}", customer_name)
                )
                return cursor.lastrowid if self.db_type == 'sqlite' else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        except:
            return 1

    def _get_item_id(self, item_code: str) -> int:
        """获取商品ID"""
        if not item_code:
            return 1
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT FItemID FROM t_ICItem WHERE FNumber = ?", (item_code,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                # 创建新商品
                cursor.execute(
                    "INSERT INTO t_ICItem (FNumber, FName) VALUES (?, ?)",
                    (item_code, f"商品_{item_code}")
                )
                return cursor.lastrowid if self.db_type == 'sqlite' else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        except:
            return 1

    def _get_stock_id(self, warehouse_name: str) -> int:
        """获取仓库ID"""
        if not warehouse_name:
            return 1
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT FItemID FROM t_Stock WHERE FName = ?", (warehouse_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 1  # 默认仓库
        except:
            return 1

    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()

class LocalKingdeeIntegration:
    def __init__(self, config: Dict[str, Any]):
        self.db = LocalKingdeeDB(config)
    
    def process_inbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理入库单据"""
        try:
            result = self.db.create_inbound_order(parsed_data)
            return result
        except Exception as e:
            return {'success': False, 'error': f'处理入库单失败: {str(e)}'}
    
    def process_outbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理出库单据"""
        try:
            result = self.db.create_outbound_order(parsed_data)
            return result
        except Exception as e:
            return {'success': False, 'error': f'处理出库单失败: {str(e)}'}
    
    def check_inventory(self, item_code: str, warehouse_code: str = None) -> Dict[str, Any]:
        """检查库存"""
        try:
            result = self.db.query_inventory(item_code, warehouse_code)
            return result
        except Exception as e:
            return {'success': False, 'error': f'查询库存失败: {str(e)}'}

# Excel导出功能（适合没有数据库的情况）
class ExcelKingdeeIntegration:
    def __init__(self, config: Dict[str, Any]):
        self.excel_path = config.get('excel_path', './kingdee_data.xlsx')
        self.ensure_excel_exists()
    
    def ensure_excel_exists(self):
        """确保Excel文件存在"""
        if not os.path.exists(self.excel_path):
            # 创建空的Excel文件
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                pd.DataFrame(columns=['单据号', '日期', '类型', '供应商/客户', '仓库', '总金额']).to_excel(
                    writer, sheet_name='单据主表', index=False)
                pd.DataFrame(columns=['单据号', '商品编码', '商品名称', '数量', '单价', '金额']).to_excel(
                    writer, sheet_name='单据明细', index=False)
                pd.DataFrame(columns=['商品编码', '商品名称', '仓库', '库存数量', '库存金额']).to_excel(
                    writer, sheet_name='库存明细', index=False)
    
    def process_inbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理入库单据"""
        try:
            basic_info = parsed_data.get('basic_info', {})
            items = parsed_data.get('items', [])
            
            bill_no = basic_info.get('document_number', f"RK{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # 读取现有数据
            main_df = pd.read_excel(self.excel_path, sheet_name='单据主表')
            detail_df = pd.read_excel(self.excel_path, sheet_name='单据明细')
            
            # 添加主表数据
            new_main = pd.DataFrame([{
                '单据号': bill_no,
                '日期': basic_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                '类型': '入库单',
                '供应商/客户': basic_info.get('supplier', ''),
                '仓库': basic_info.get('warehouse', ''),
                '总金额': sum(item.get('amount', 0) for item in items)
            }])
            main_df = pd.concat([main_df, new_main], ignore_index=True)
            
            # 添加明细数据
            for item in items:
                new_detail = pd.DataFrame([{
                    '单据号': bill_no,
                    '商品编码': item.get('item_code', ''),
                    '商品名称': item.get('item_name', ''),
                    '数量': item.get('quantity', 0),
                    '单价': item.get('unit_price', 0),
                    '金额': item.get('amount', 0)
                }])
                detail_df = pd.concat([detail_df, new_detail], ignore_index=True)
            
            # 保存到Excel
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                main_df.to_excel(writer, sheet_name='单据主表', index=False)
                detail_df.to_excel(writer, sheet_name='单据明细', index=False)
                # 保持库存表不变
                try:
                    inventory_df = pd.read_excel(self.excel_path, sheet_name='库存明细')
                    inventory_df.to_excel(writer, sheet_name='库存明细', index=False)
                except:
                    pass
            
            return {
                'success': True,
                'bill_no': bill_no,
                'message': '入库单已保存到Excel'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'处理失败: {str(e)}'}
    
    def process_outbound_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理出库单据"""
        try:
            basic_info = parsed_data.get('basic_info', {})
            items = parsed_data.get('items', [])
            
            bill_no = basic_info.get('document_number', f"CK{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # 读取现有数据
            main_df = pd.read_excel(self.excel_path, sheet_name='单据主表')
            detail_df = pd.read_excel(self.excel_path, sheet_name='单据明细')
            
            # 添加主表数据
            new_main = pd.DataFrame([{
                '单据号': bill_no,
                '日期': basic_info.get('date', datetime.now().strftime('%Y-%m-%d')),
                '类型': '出库单',
                '供应商/客户': basic_info.get('customer', ''),
                '仓库': basic_info.get('warehouse', ''),
                '总金额': sum(item.get('amount', 0) for item in items)
            }])
            main_df = pd.concat([main_df, new_main], ignore_index=True)
            
            # 添加明细数据
            for item in items:
                new_detail = pd.DataFrame([{
                    '单据号': bill_no,
                    '商品编码': item.get('item_code', ''),
                    '商品名称': item.get('item_name', ''),
                    '数量': item.get('quantity', 0),
                    '单价': item.get('unit_price', 0),
                    '金额': item.get('amount', 0)
                }])
                detail_df = pd.concat([detail_df, new_detail], ignore_index=True)
            
            # 保存到Excel
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                main_df.to_excel(writer, sheet_name='单据主表', index=False)
                detail_df.to_excel(writer, sheet_name='单据明细', index=False)
                # 保持库存表不变
                try:
                    inventory_df = pd.read_excel(self.excel_path, sheet_name='库存明细')
                    inventory_df.to_excel(writer, sheet_name='库存明细', index=False)
                except:
                    pass
            
            return {
                'success': True,
                'bill_no': bill_no,
                'message': '出库单已保存到Excel'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'处理失败: {str(e)}'}
    
    def check_inventory(self, item_code: str, warehouse_code: str = None) -> Dict[str, Any]:
        """检查库存"""
        try:
            inventory_df = pd.read_excel(self.excel_path, sheet_name='库存明细')
            
            if item_code:
                inventory_df = inventory_df[inventory_df['商品编码'] == item_code]
            if warehouse_code:
                inventory_df = inventory_df[inventory_df['仓库'] == warehouse_code]
            
            return {
                'success': True,
                'data': inventory_df.to_dict('records')
            }
            
        except Exception as e:
            return {'success': False, 'error': f'查询失败: {str(e)}'}