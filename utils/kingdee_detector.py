import os
import glob
from typing import List, Dict

def find_kingdee_databases() -> List[Dict[str, str]]:
    """查找本地金蝶数据库文件"""
    databases = []
    
    # 常见的金蝶安装路径
    common_paths = [
        r"C:\KDW\*.MDB",
        r"C:\KDW\*.ACCDB", 
        r"C:\KDMAIN\*.MDB",
        r"C:\KDMAIN\*.ACCDB",
        r"C:\Program Files\Kingdee\*.MDB",
        r"C:\Program Files\Kingdee\*.ACCDB",
        r"C:\Program Files (x86)\Kingdee\*.MDB",
        r"C:\Program Files (x86)\Kingdee\*.ACCDB",
        r"D:\KDW\*.MDB",
        r"D:\KDW\*.ACCDB",
        r"D:\KDMAIN\*.MDB",
        r"D:\KDMAIN\*.ACCDB"
    ]
    
    print("🔍 正在搜索金蝶数据库文件...")
    
    for pattern in common_paths:
        try:
            files = glob.glob(pattern)
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    databases.append({
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'size_mb': round(file_size, 2),
                        'modified': os.path.getmtime(file_path)
                    })
        except Exception as e:
            continue
    
    return databases

def detect_kingdee_version(db_path: str) -> str:
    """检测金蝶版本"""
    try:
        import pyodbc
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 检查表结构来判断版本
        tables = cursor.tables()
        table_names = [table.table_name for table in tables]
        
        if 'ICStockBill' in table_names:
            return "金蝶KIS"
        elif 'T_IM_BILL' in table_names:
            return "金蝶K3"
        else:
            return "未知版本"
            
    except Exception as e:
        return f"检测失败: {str(e)}"

def generate_config(db_path: str) -> str:
    """生成配置代码"""
    return f"""
# 本地金蝶数据库配置
KINGDEE_TYPE=local
KINGDEE_DB_TYPE=access
KINGDEE_DB_PATH={db_path}

# 如果是SQL Server版本，使用以下配置：
# KINGDEE_DB_TYPE=sqlserver
# KINGDEE_SERVER=localhost
# KINGDEE_LOCAL_DATABASE=AIS
# KINGDEE_LOCAL_USERNAME=sa
# KINGDEE_LOCAL_PASSWORD=your-password
"""

def main():
    """主函数"""
    print("🏪 金蝶数据库检测工具")
    print("=" * 50)
    
    # 查找数据库
    databases = find_kingdee_databases()
    
    if not databases:
        print("❌ 未找到金蝶数据库文件")
        print("\n💡 可能的原因：")
        print("1. 金蝶软件未安装")
        print("2. 数据库文件在其他位置")
        print("3. 使用的是SQL Server版本")
        print("\n📝 手动配置方法：")
        print("1. 找到金蝶安装目录")
        print("2. 查找 .MDB 或 .ACCDB 文件")
        print("3. 在 .env 文件中配置 KINGDEE_DB_PATH")
        return
    
    print(f"✅ 找到 {len(databases)} 个数据库文件：")
    print()
    
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db['name']}")
        print(f"   路径: {db['path']}")
        print(f"   大小: {db['size_mb']} MB")
        
        # 检测版本
        version = detect_kingdee_version(db['path'])
        print(f"   版本: {version}")
        print()
    
    # 让用户选择
    if len(databases) == 1:
        selected_db = databases[0]
        print(f"🎯 自动选择: {selected_db['name']}")
    else:
        try:
            choice = input(f"请选择数据库 (1-{len(databases)}): ")
            selected_db = databases[int(choice) - 1]
        except (ValueError, IndexError):
            print("❌ 选择无效")
            return
    
    # 生成配置
    print("\n📋 生成的配置：")
    config = generate_config(selected_db['path'])
    print(config)
    
    # 保存到文件
    try:
        with open('.env.kingdee', 'w', encoding='utf-8') as f:
            f.write(config)
        print("✅ 配置已保存到 .env.kingdee 文件")
        print("请将内容复制到 .env 文件中")
    except Exception as e:
        print(f"❌ 保存配置失败: {str(e)}")
    
    # 测试连接
    test_choice = input("\n是否测试数据库连接？(y/n): ")
    if test_choice.lower() == 'y':
        test_connection(selected_db['path'])

def test_connection(db_path: str):
    """测试数据库连接"""
    print("\n🔗 测试数据库连接...")
    
    try:
        import pyodbc
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 查询表数量
        tables = cursor.tables()
        table_count = len([table for table in tables])
        
        print(f"✅ 连接成功！")
        print(f"📊 数据库包含 {table_count} 个表")
        
        # 检查关键表
        cursor.execute("SELECT name FROM MSysObjects WHERE Type=1 AND Flags=0")
        table_names = [row[0] for row in cursor.fetchall()]
        
        key_tables = ['ICStockBill', 't_ICItem', 't_Supplier', 't_Organization']
        found_tables = [table for table in key_tables if table in table_names]
        
        if found_tables:
            print(f"🎯 找到关键表: {', '.join(found_tables)}")
        else:
            print("⚠️  未找到标准的金蝶表结构，可能需要调整SQL语句")
        
        conn.close()
        
    except ImportError:
        print("❌ 缺少 pyodbc 库，请运行: pip install pyodbc")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("\n💡 可能的解决方案：")
        print("1. 安装 Microsoft Access Database Engine")
        print("2. 检查数据库文件是否被占用")
        print("3. 确认文件路径正确")

if __name__ == "__main__":
    main()