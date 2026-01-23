"""
OCR技术详解和实现示例
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json
from paddleocr import PaddleOCR
import cv2
import numpy as np

class OCRExplainer:
    """OCR技术详解类"""
    
    def __init__(self):
        # 初始化PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # 支持文字方向检测
            lang='ch',          # 中文识别
            use_gpu=False       # 使用CPU
        )
    
    def explain_ocr_process(self):
        """解释OCR处理流程"""
        print("🔍 OCR技术详解")
        print("=" * 50)
        
        print("1️⃣ 图像预处理")
        print("   - 灰度化：彩色图片转黑白")
        print("   - 降噪：去除图片噪点")
        print("   - 二值化：黑白分明，便于识别")
        print("   - 倾斜校正：纠正拍照角度")
        
        print("\n2️⃣ 文字检测 (Text Detection)")
        print("   - 找出图片中哪些区域有文字")
        print("   - 用矩形框标出文字位置")
        print("   - 返回坐标信息")
        
        print("\n3️⃣ 文字识别 (Text Recognition)")
        print("   - 对每个文字区域进行字符识别")
        print("   - 输出具体的文字内容")
        print("   - 给出置信度分数")
        
        print("\n4️⃣ 后处理")
        print("   - 文字排序（从上到下，从左到右）")
        print("   - 格式化输出")
        print("   - 结构化数据提取")
    
    def demo_basic_ocr(self, image_path: str):
        """基础OCR演示"""
        print(f"\n📸 处理图片: {image_path}")
        
        if not os.path.exists(image_path):
            print("❌ 图片文件不存在")
            return
        
        # 执行OCR
        result = self.ocr.ocr(image_path, cls=True)
        
        print("\n🔍 OCR识别结果:")
        print("-" * 30)
        
        for idx in range(len(result)):
            res = result[idx]
            if res is None:
                continue
                
            for line_idx, line in enumerate(res):
                # line[0] = 坐标信息 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                # line[1] = (文字内容, 置信度)
                
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                print(f"第{line_idx+1}行:")
                print(f"  文字: {text}")
                print(f"  置信度: {confidence:.3f}")
                print(f"  位置: {box}")
                print()
    
    def demo_warehouse_document_ocr(self, image_path: str):
        """仓管单据OCR演示"""
        print(f"\n📋 仓管单据识别: {image_path}")
        
        if not os.path.exists(image_path):
            print("❌ 图片文件不存在")
            return
        
        # 执行OCR
        result = self.ocr.ocr(image_path, cls=True)
        
        # 提取所有文字
        all_text = []
        for idx in range(len(result)):
            res = result[idx]
            if res is None:
                continue
            for line in res:
                text = line[1][0]
                confidence = line[1][1]
                if confidence > 0.5:  # 只要置信度>0.5的文字
                    all_text.append(text)
        
        full_text = ' '.join(all_text)
        print(f"\n📝 识别到的完整文字:")
        print(full_text)
        
        # 智能解析
        self.parse_warehouse_document(full_text)
    
    def parse_warehouse_document(self, text: str):
        """解析仓管单据"""
        import re
        
        print(f"\n🧠 智能解析结果:")
        print("-" * 30)
        
        # 检测单据类型
        if re.search(r'(入库单|入货单|收货单)', text):
            print("📦 单据类型: 入库单")
            doc_type = "入库单"
        elif re.search(r'(出库单|出货单|发货单)', text):
            print("📤 单据类型: 出库单")
            doc_type = "出库单"
        else:
            print("❓ 单据类型: 未知")
            doc_type = "未知"
        
        # 提取单据号
        bill_no_match = re.search(r'(单据号|单号|编号)[:：]\s*([A-Z0-9\-]+)', text)
        if bill_no_match:
            print(f"🔢 单据号: {bill_no_match.group(2)}")
        
        # 提取日期
        date_match = re.search(r'(日期|时间)[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
        if date_match:
            print(f"📅 日期: {date_match.group(2)}")
        
        # 提取供应商/客户
        if doc_type == "入库单":
            supplier_match = re.search(r'(供应商|供货商|厂商)[:：]\s*([^\s]+)', text)
            if supplier_match:
                print(f"🏭 供应商: {supplier_match.group(2)}")
        else:
            customer_match = re.search(r'(客户|收货方|收货人)[:：]\s*([^\s]+)', text)
            if customer_match:
                print(f"👤 客户: {customer_match.group(2)}")
        
        # 提取金额
        amount_match = re.search(r'(总金额|合计|总计)[:：]\s*([0-9,]+\.?\d*)', text)
        if amount_match:
            print(f"💰 总金额: {amount_match.group(2)}")
        
        # 提取商品信息
        print(f"\n📦 商品明细:")
        lines = text.split()
        for line in lines:
            # 简单的商品识别逻辑
            if re.search(r'[\u4e00-\u9fa5]{2,}.*\d+.*元', line):
                print(f"  - {line}")
    
    def create_test_image(self, output_path: str = "test_warehouse_doc.png"):
        """创建测试用的仓管单据图片"""
        # 创建一个白色背景的图片
        width, height = 800, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 尝试使用系统字体
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            # 如果没有字体文件，使用默认字体
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 绘制单据内容
        y = 50
        
        # 标题
        draw.text((300, y), "入库单", fill='black', font=font_large)
        y += 60
        
        # 基本信息
        draw.text((50, y), "单据号: RK20240101001", fill='black', font=font_medium)
        y += 30
        draw.text((50, y), "日期: 2024-01-01", fill='black', font=font_medium)
        y += 30
        draw.text((50, y), "供应商: 北京测试供应商有限公司", fill='black', font=font_medium)
        y += 30
        draw.text((50, y), "仓库: 主仓库", fill='black', font=font_medium)
        y += 50
        
        # 表头
        draw.text((50, y), "商品编码", fill='black', font=font_medium)
        draw.text((200, y), "商品名称", fill='black', font=font_medium)
        draw.text((350, y), "数量", fill='black', font=font_medium)
        draw.text((450, y), "单价", fill='black', font=font_medium)
        draw.text((550, y), "金额", fill='black', font=font_medium)
        y += 30
        
        # 画线
        draw.line([(50, y), (650, y)], fill='black', width=1)
        y += 10
        
        # 商品明细
        items = [
            ("ITEM001", "测试商品A", "10件", "100.00元", "1000.00元"),
            ("ITEM002", "测试商品B", "5箱", "200.00元", "1000.00元"),
            ("ITEM003", "测试商品C", "2台", "500.00元", "1000.00元")
        ]
        
        for item in items:
            draw.text((50, y), item[0], fill='black', font=font_small)
            draw.text((200, y), item[1], fill='black', font=font_small)
            draw.text((350, y), item[2], fill='black', font=small)
            draw.text((450, y), item[3], fill='black', font=font_small)
            draw.text((550, y), item[4], fill='black', font=font_small)
            y += 25
        
        # 总计
        y += 20
        draw.line([(450, y), (650, y)], fill='black', width=1)
        y += 10
        draw.text((450, y), "总金额: 3000.00元", fill='black', font=font_medium)
        
        # 保存图片
        image.save(output_path)
        print(f"✅ 测试图片已创建: {output_path}")
        return output_path

def main():
    """主演示函数"""
    explainer = OCRExplainer()
    
    # 1. 解释OCR原理
    explainer.explain_ocr_process()
    
    # 2. 创建测试图片
    test_image = explainer.create_test_image()
    
    # 3. 演示基础OCR
    explainer.demo_basic_ocr(test_image)
    
    # 4. 演示仓管单据OCR
    explainer.demo_warehouse_document_ocr(test_image)
    
    print("\n" + "="*50)
    print("🎯 OCR在仓管系统中的应用:")
    print("1. 拍照上传纸质单据")
    print("2. OCR自动识别文字内容")
    print("3. 智能解析提取关键信息")
    print("4. 自动填入ERP系统")
    print("5. 大大提高录入效率")

if __name__ == "__main__":
    main()