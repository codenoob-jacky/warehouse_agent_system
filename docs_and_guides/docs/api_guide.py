"""
在线OCR API获取指南
详细说明如何获取各种OCR服务的API密钥
"""

def show_ocr_space_guide():
    """OCR.Space API获取指南（推荐，完全免费）"""
    print("🆓 OCR.Space - 完全免费，推荐首选")
    print("=" * 50)
    print("🔗 官网: https://ocr.space/ocrapi")
    print()
    print("📝 获取步骤:")
    print("1. 无需注册！直接使用免费API Key: 'helloworld'")
    print("2. 免费额度: 每月25,000次调用")
    print("3. 支持中文识别")
    print("4. 即开即用，零门槛")
    print()
    print("⚙️ 配置方法:")
    print("OCR_SPACE_API_KEY=helloworld")
    print()
    print("💡 如需更高额度:")
    print("1. 访问 https://ocr.space/ocrapi")
    print("2. 点击 'Get Free API Key'")
    print("3. 填写邮箱获取专属API Key")
    print("4. 免费用户: 每月25,000次")
    print("5. 付费用户: $1.50/1000次")

def show_baidu_ocr_guide():
    """百度OCR API获取指南（中文最强）"""
    print("\n🇨🇳 百度OCR - 中文识别最强")
    print("=" * 50)
    print("🔗 官网: https://ai.baidu.com/tech/ocr")
    print()
    print("📝 获取步骤:")
    print("1. 访问百度AI开放平台: https://ai.baidu.com/")
    print("2. 点击右上角'控制台'，登录百度账号")
    print("3. 选择'文字识别' -> '创建应用'")
    print("4. 填写应用信息:")
    print("   - 应用名称: 仓管系统OCR")
    print("   - 应用类型: 不限制")
    print("   - 应用描述: 仓管单据识别")
    print("5. 创建成功后获得:")
    print("   - API Key (AppID)")
    print("   - Secret Key")
    print()
    print("💰 价格:")
    print("- 免费额度: 每月1,000次")
    print("- 付费价格: ¥1.5/1000次")
    print("- 高精度版: ¥3/1000次")
    print()
    print("⚙️ 配置方法:")
    print("BAIDU_OCR_ENABLED=True")
    print("BAIDU_OCR_API_KEY=你的API_Key")
    print("BAIDU_OCR_SECRET_KEY=你的Secret_Key")

def show_recommended_setup():
    """推荐配置方案"""
    print("\n🎯 推荐配置方案")
    print("=" * 50)
    
    print("💡 方案一: 零成本入门（推荐）")
    print("OCR_MODE=online")
    print("OCR_SPACE_API_KEY=helloworld")
    print("- 适合: 刚开始使用，月处理量<25,000张")
    print("- 优点: 完全免费，即开即用")
    print()
    
    print("💡 方案二: 中文优化")
    print("OCR_MODE=online")
    print("BAIDU_OCR_ENABLED=True")
    print("BAIDU_OCR_API_KEY=你的密钥")
    print("- 适合: 中文单据多，要求精度高")
    print("- 优点: 中文识别最准确")

def main():
    """主函数"""
    print("🔑 在线OCR API获取完整指南")
    print("=" * 60)
    
    show_ocr_space_guide()
    show_baidu_ocr_guide()
    show_recommended_setup()
    
    print("\n🎉 立即开始:")
    print("1. 修改 .env 文件: OCR_MODE=online")
    print("2. 设置: OCR_SPACE_API_KEY=helloworld")
    print("3. 运行: python main.py")

if __name__ == "__main__":
    main()