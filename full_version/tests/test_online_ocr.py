"""
在线OCR服务测试和对比
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.online_ocr import OnlineOCRManager, create_online_ocr_config

def create_simple_test_image(output_path: str = "simple_test.png"):
    """创建简单的测试图片"""
    width, height = 600, 400
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 使用默认字体
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # 绘制文字
    y = 50
    texts = [
        "入库单",
        "单据号: RK20240101001", 
        "日期: 2024-01-01",
        "供应商: 测试供应商",
        "商品A 10件 100元",
        "商品B 5箱 200元",
        "总金额: 1500元"
    ]
    
    for text in texts:
        draw.text((50, y), text, fill='black', font=font)
        y += 40
    
    image.save(output_path)
    print(f"✅ 测试图片已创建: {output_path}")
    return output_path

def test_online_ocr_services():
    """测试各种在线OCR服务"""
    print("🌐 在线OCR服务测试")
    print("=" * 50)
    
    # 创建测试图片
    test_image = create_simple_test_image()
    
    # 测试配置
    configs = {
        "免费OCR.Space": {
            'online_ocr': {
                'ocr_space': {
                    'enabled': True,
                    'api_key': 'helloworld',
                    'timeout': 30
                }
            }
        },
        
        "百度OCR (需要配置)": {
            'online_ocr': {
                'baidu': {
                    'enabled': False,  # 需要真实API密钥
                    'api_key': 'your_api_key',
                    'secret_key': 'your_secret_key',
                    'timeout': 30
                }
            }
        }
    }
    
    for service_name, config in configs.items():
        print(f"\n🔍 测试 {service_name}...")
        print("-" * 30)
        
        try:
            ocr_manager = OnlineOCRManager(config)
            
            start_time = time.time()
            result = ocr_manager.extract_text(test_image)
            end_time = time.time()
            
            print(f"✅ 识别成功！耗时: {end_time - start_time:.2f}秒")
            print(f"识别到 {len(result)} 行文字:")
            
            for i, item in enumerate(result[:5], 1):  # 只显示前5行
                print(f"  {i}. {item['text']}")
            
            if len(result) > 5:
                print(f"  ... 还有 {len(result) - 5} 行")
                
        except Exception as e:
            print(f"❌ 识别失败: {str(e)}")
    
    # 清理测试文件
    if os.path.exists(test_image):
        os.remove(test_image)

def compare_ocr_services():
    """对比不同OCR服务的特点"""
    print("\n📊 在线OCR服务对比")
    print("=" * 60)
    
    services = [
        {
            "名称": "OCR.Space",
            "费用": "免费",
            "限制": "每月25,000次",
            "中文支持": "良好",
            "速度": "快",
            "推荐度": "⭐⭐⭐⭐⭐"
        },
        {
            "名称": "百度OCR",
            "费用": "付费",
            "限制": "每月1000次免费",
            "中文支持": "优秀",
            "速度": "很快",
            "推荐度": "⭐⭐⭐⭐"
        },
        {
            "名称": "腾讯OCR",
            "费用": "付费", 
            "限制": "每月1000次免费",
            "中文支持": "优秀",
            "速度": "很快",
            "推荐度": "⭐⭐⭐⭐"
        },
        {
            "名称": "Google Vision",
            "费用": "付费",
            "限制": "每月1000次免费",
            "中文支持": "良好",
            "速度": "快",
            "推荐度": "⭐⭐⭐"
        }
    ]
    
    # 打印表格
    print(f"{'服务名称':<15} {'费用':<8} {'限制':<18} {'中文支持':<8} {'速度':<6} {'推荐度'}")
    print("-" * 60)
    
    for service in services:
        print(f"{service['名称']:<15} {service['费用']:<8} {service['限制']:<18} {service['中文支持']:<8} {service['速度']:<6} {service['推荐度']}")

def show_online_ocr_advantages():
    """展示在线OCR的优势"""
    print("\n💡 在线OCR vs 本地OCR")
    print("=" * 40)
    
    print("🌐 在线OCR优势:")
    print("  ✅ 无需安装大型模型文件")
    print("  ✅ 对设备配置要求极低")
    print("  ✅ 识别精度通常更高")
    print("  ✅ 支持更多语言和格式")
    print("  ✅ 自动更新和优化")
    print("  ✅ 节省本地存储空间")
    
    print("\n💻 本地OCR优势:")
    print("  ✅ 完全离线工作")
    print("  ✅ 数据隐私更安全")
    print("  ✅ 无网络依赖")
    print("  ✅ 无API调用限制")
    
    print("\n🎯 推荐方案:")
    print("  📱 中小企业: 在线OCR (OCR.Space免费版)")
    print("  🏢 大企业: 付费在线OCR (百度/腾讯)")
    print("  🔒 保密要求高: 本地OCR")

def main():
    """主函数"""
    print("🔍 在线OCR完整测试")
    print("=" * 50)
    
    # 1. 服务对比
    compare_ocr_services()
    
    # 2. 优势分析
    show_online_ocr_advantages()
    
    # 3. 实际测试
    choice = input("\n是否进行实际OCR测试？(y/n): ")
    if choice.lower() == 'y':
        test_online_ocr_services()
    
    print("\n🎉 测试完成！")
    print("\n📝 配置建议:")
    print("1. 修改 .env 文件: OCR_MODE=online")
    print("2. 使用免费的 OCR.Space: OCR_SPACE_API_KEY=helloworld")
    print("3. 如需更高精度，申请百度OCR API")

if __name__ == "__main__":
    main()