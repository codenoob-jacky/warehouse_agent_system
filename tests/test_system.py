import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from agents.warehouse_agents import SimpleWarehouseAgent
from utils.ocr_processor import SmartDocumentProcessor
from utils.kingdee_integration import KingdeeIntegration

def test_ocr_processor():
    """测试OCR处理器"""
    print("🔍 测试OCR处理器...")
    
    try:
        processor = SmartDocumentProcessor(Config.OCR_CONFIG)
        print("✅ OCR处理器初始化成功")
        
        # 这里可以添加实际的图片测试
        # result = processor.process_document("test_image.jpg")
        # print(f"OCR结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ OCR处理器测试失败: {str(e)}")

def test_kingdee_integration():
    """测试金蝶集成"""
    print("🔗 测试金蝶集成...")
    
    try:
        integration = KingdeeIntegration(Config.KINGDEE_CONFIG)
        print("✅ 金蝶集成初始化成功")
        
        # 测试登录（需要配置正确的金蝶参数）
        # login_result = integration.api.login()
        # print(f"登录结果: {login_result}")
        
    except Exception as e:
        print(f"❌ 金蝶集成测试失败: {str(e)}")

def test_simple_agent():
    """测试简单代理"""
    print("🤖 测试简单代理...")
    
    try:
        config = {
            'OCR_CONFIG': Config.OCR_CONFIG,
            'KINGDEE_CONFIG': Config.KINGDEE_CONFIG,
            'AGENT_CONFIG': Config.AGENT_CONFIG
        }
        
        agent = SimpleWarehouseAgent(config)
        print("✅ 简单代理初始化成功")
        
        # 测试数据验证
        test_data = {
            'document_type': 'inbound',
            'basic_info': {
                'document_number': 'TEST001',
                'date': '2024-01-01',
                'supplier': '测试供应商'
            },
            'items': [
                {
                    'item_code': 'ITEM001',
                    'item_name': '测试商品',
                    'quantity': 10,
                    'unit_price': 100.0,
                    'amount': 1000.0
                }
            ]
        }
        
        validation_result = agent._validate_data(test_data)
        print(f"数据验证结果: {json.dumps(validation_result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 简单代理测试失败: {str(e)}")

def test_mock_document_processing():
    """模拟单据处理流程"""
    print("📋 模拟单据处理流程...")
    
    # 模拟OCR识别结果
    mock_ocr_result = {
        'success': True,
        'data': {
            'document_type': 'inbound',
            'basic_info': {
                'document_number': 'RK20240101001',
                'date': '2024-01-01',
                'supplier': '北京测试供应商有限公司',
                'warehouse': '主仓库'
            },
            'items': [
                {
                    'item_code': 'ITEM001',
                    'item_name': '测试商品A',
                    'quantity': 10,
                    'unit': '件',
                    'unit_price': 100.0,
                    'amount': 1000.0
                },
                {
                    'item_code': 'ITEM002',
                    'item_name': '测试商品B',
                    'quantity': 5,
                    'unit': '箱',
                    'unit_price': 200.0,
                    'amount': 1000.0
                }
            ],
            'processed_at': datetime.now().isoformat()
        }
    }
    
    print("模拟OCR识别结果:")
    print(json.dumps(mock_ocr_result, ensure_ascii=False, indent=2))
    
    # 模拟数据验证
    try:
        config = {
            'OCR_CONFIG': Config.OCR_CONFIG,
            'KINGDEE_CONFIG': Config.KINGDEE_CONFIG,
            'AGENT_CONFIG': Config.AGENT_CONFIG
        }
        
        agent = SimpleWarehouseAgent(config)
        validation_result = agent._validate_data(mock_ocr_result['data'])
        
        print("\n数据验证结果:")
        print(json.dumps(validation_result, ensure_ascii=False, indent=2))
        
        if validation_result['valid']:
            print("✅ 数据验证通过，可以同步到金蝶系统")
        else:
            print("❌ 数据验证失败，需要人工检查")
            
    except Exception as e:
        print(f"❌ 模拟处理失败: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 智能仓管系统测试开始")
    print("=" * 50)
    
    # 检查配置
    print(f"📁 上传目录: {Config.UPLOAD_FOLDER}")
    print(f"🔧 OCR配置: {Config.OCR_CONFIG}")
    print(f"🔗 金蝶配置: {Config.KINGDEE_CONFIG}")
    print()
    
    # 运行测试
    test_ocr_processor()
    print()
    
    test_kingdee_integration()
    print()
    
    test_simple_agent()
    print()
    
    test_mock_document_processing()
    print()
    
    print("=" * 50)
    print("🎉 测试完成")
    
    # 提示下一步
    print("\n📝 下一步操作:")
    print("1. 配置 .env 文件中的金蝶系统参数")
    print("2. 准备测试用的单据图片")
    print("3. 运行 python main.py 启动Web服务")
    print("4. 访问 http://localhost:8000 测试完整功能")

if __name__ == "__main__":
    main()