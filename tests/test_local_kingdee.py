import sqlite3
import os
from datetime import datetime

def create_test_database(db_path: str = "test_kingdee.db"):
    """创建测试用的金蝶数据库结构"""
    
    # 删除已存在的数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建供应商表
    cursor.execute("""
    CREATE TABLE t_Supplier (
        FItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        FNumber VARCHAR(50) UNIQUE,
        FName VARCHAR(100),
        FAddress VARCHAR(200),
        FContact VARCHAR(50),
        FPhone VARCHAR(50),
        FCreateDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建客户表
    cursor.execute("""
    CREATE TABLE t_Organization (
        FItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        FNumber VARCHAR(50) UNIQUE,
        FName VARCHAR(100),
        FAddress VARCHAR(200),
        FContact VARCHAR(50),
        FPhone VARCHAR(50),
        FCreateDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建商品表
    cursor.execute("""
    CREATE TABLE t_ICItem (
        FItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        FNumber VARCHAR(50) UNIQUE,
        FName VARCHAR(100),
        FModel VARCHAR(50),
        FUnit VARCHAR(20),
        FPrice DECIMAL(18,4),
        FCreateDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建仓库表
    cursor.execute("""
    CREATE TABLE t_Stock (
        FItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        FNumber VARCHAR(50) UNIQUE,
        FName VARCHAR(100),
        FAddress VARCHAR(200),
        FCreateDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建单据主表
    cursor.execute("""
    CREATE TABLE ICStockBill (
        FID INTEGER PRIMARY KEY AUTOINCREMENT,
        FBillNo VARCHAR(50) UNIQUE,
        FDate DATE,
        FSupplyID INTEGER,
        FCustID INTEGER,
        FDeptID INTEGER,
        FEmpID INTEGER,
        FBillType INTEGER,  -- 1:入库 2:出库
        FStatus INTEGER,    -- 0:未审核 1:已审核
        FAmount DECIMAL(18,4),
        FRemark TEXT,
        FCreateDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (FSupplyID) REFERENCES t_Supplier(FItemID),
        FOREIGN KEY (FCustID) REFERENCES t_Organization(FItemID)
    )
    """)
    
    # 创建单据明细表
    cursor.execute("""
    CREATE TABLE ICStockBillEntry (
        FEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
        FID INTEGER,
        FEntryID_Line INTEGER,
        FItemID INTEGER,
        FQty DECIMAL(18,4),
        FPrice DECIMAL(18,4),
        FAmount DECIMAL(18,4),
        FStockID INTEGER,
        FBatchNo VARCHAR(50),
        FRemark TEXT,
        FOREIGN KEY (FID) REFERENCES ICStockBill(FID),
        FOREIGN KEY (FItemID) REFERENCES t_ICItem(FItemID),
        FOREIGN KEY (FStockID) REFERENCES t_Stock(FItemID)
    )
    """)
    
    # 创建库存表
    cursor.execute("""
    CREATE TABLE ICInventory (
        FID INTEGER PRIMARY KEY AUTOINCREMENT,
        FItemID INTEGER,
        FStockID INTEGER,
        FQty DECIMAL(18,4),
        FAmount DECIMAL(18,4),
        FLastUpdateDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (FItemID) REFERENCES t_ICItem(FItemID),
        FOREIGN KEY (FStockID) REFERENCES t_Stock(FItemID)
    )
    """)
    
    # 插入测试数据
    print("插入测试数据...")
    
    # 供应商
    cursor.execute("INSERT INTO t_Supplier (FNumber, FName) VALUES ('GYS001', '北京测试供应商')")
    cursor.execute("INSERT INTO t_Supplier (FNumber, FName) VALUES ('GYS002', '上海供应商有限公司')")
    
    # 客户
    cursor.execute("INSERT INTO t_Organization (FNumber, FName) VALUES ('KH001', '深圳测试客户')")
    cursor.execute("INSERT INTO t_Organization (FNumber, FName) VALUES ('KH002', '广州客户公司')")
    
    # 商品
    cursor.execute("INSERT INTO t_ICItem (FNumber, FName, FUnit, FPrice) VALUES ('ITEM001', '测试商品A', '件', 100.00)")
    cursor.execute("INSERT INTO t_ICItem (FNumber, FName, FUnit, FPrice) VALUES ('ITEM002', '测试商品B', '箱', 200.00)")
    cursor.execute("INSERT INTO t_ICItem (FNumber, FName, FUnit, FPrice) VALUES ('ITEM003', '测试商品C', '台', 500.00)")
    
    # 仓库
    cursor.execute("INSERT INTO t_Stock (FNumber, FName) VALUES ('CK001', '主仓库')")
    cursor.execute("INSERT INTO t_Stock (FNumber, FName) VALUES ('CK002', '备用仓库')")
    
    # 初始库存
    cursor.execute("INSERT INTO ICInventory (FItemID, FStockID, FQty, FAmount) VALUES (1, 1, 100, 10000)")
    cursor.execute("INSERT INTO ICInventory (FItemID, FStockID, FQty, FAmount) VALUES (2, 1, 50, 10000)")
    cursor.execute("INSERT INTO ICInventory (FItemID, FStockID, FQty, FAmount) VALUES (3, 1, 20, 10000)")
    
    conn.commit()
    conn.close()
    
    print(f"测试数据库创建完成: {db_path}")
    return db_path

def test_local_integration():
    """测试本地金蝶集成"""
    from utils.local_kingdee_integration import LocalKingdeeIntegration
    
    # 创建测试数据库
    db_path = create_test_database()
    
    # 配置
    config = {
        'db_type': 'sqlite',
        'db_path': db_path
    }
    
    # 测试集成
    integration = LocalKingdeeIntegration(config)
    
    # 测试入库单
    print("\n测试创建入库单...")
    inbound_data = {
        'basic_info': {
            'document_number': 'RK20240101001',
            'date': '2024-01-01',
            'supplier': '北京测试供应商',
            'warehouse': '主仓库'
        },
        'items': [
            {
                'item_code': 'ITEM001',
                'item_name': '测试商品A',
                'quantity': 10,
                'unit_price': 100.0,
                'amount': 1000.0
            },
            {
                'item_code': 'ITEM002',
                'item_name': '测试商品B',
                'quantity': 5,
                'unit_price': 200.0,
                'amount': 1000.0
            }
        ]
    }
    
    result = integration.process_inbound_document(inbound_data)
    print(f"入库单结果: {result}")
    
    # 测试出库单
    print("\n测试创建出库单...")
    outbound_data = {
        'basic_info': {
            'document_number': 'CK20240101001',
            'date': '2024-01-01',
            'customer': '深圳测试客户',
            'warehouse': '主仓库'
        },
        'items': [
            {
                'item_code': 'ITEM001',
                'item_name': '测试商品A',
                'quantity': 5,
                'unit_price': 100.0,
                'amount': 500.0
            }
        ]
    }
    
    result = integration.process_outbound_document(outbound_data)
    print(f"出库单结果: {result}")
    
    # 测试库存查询
    print("\n测试库存查询...")
    result = integration.check_inventory('ITEM001')
    print(f"库存查询结果: {result}")

def test_excel_integration():
    """测试Excel集成"""
    from utils.local_kingdee_integration import ExcelKingdeeIntegration
    
    config = {
        'excel_path': './test_kingdee.xlsx'
    }
    
    integration = ExcelKingdeeIntegration(config)
    
    # 测试入库单
    print("\n测试Excel入库单...")
    inbound_data = {
        'basic_info': {
            'document_number': 'RK20240101001',
            'date': '2024-01-01',
            'supplier': '北京测试供应商',
            'warehouse': '主仓库'
        },
        'items': [
            {
                'item_code': 'ITEM001',
                'item_name': '测试商品A',
                'quantity': 10,
                'unit_price': 100.0,
                'amount': 1000.0
            }
        ]
    }
    
    result = integration.process_inbound_document(inbound_data)
    print(f"Excel入库单结果: {result}")
    
    print(f"Excel文件已创建: {config['excel_path']}")

if __name__ == "__main__":
    print("🧪 测试本地金蝶集成...")
    
    try:
        test_local_integration()
        print("\n" + "="*50)
        test_excel_integration()
        print("\n✅ 所有测试完成")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()