import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import os
import uuid
from datetime import datetime
import json
import re
import threading

# 尝试导入金蝶模块，如果失败则使用备用方案
try:
    from packaged_version.simple_kingdee import SimpleKingdeeDB, parse_document_enhanced
    KINGDEE_AVAILABLE = True
except ImportError:
    KINGDEE_AVAILABLE = False
    # 备用解析函数
    def parse_document_enhanced(text):
        return {
            'document_type': '未知',
            'bill_no': '未识别',
            'date': '未识别',
            'supplier': '未识别',
            'customer': '未识别',
            'amount': '未识别',
            'items': []
        }
    
    # 备用数据库类
    class SimpleKingdeeDB:
        def __init__(self, db_path):
            self.db_path = db_path
        
        def save_document(self, data):
            return {
                'success': False,
                'error': '金蝶数据库模块未找到，请检查安装',
                'bill_no': '',
                'message': ''
            }

class WarehouseOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能仓管系统 - Ultra Simple")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置默认API密钥和OCR服务
        self.api_key = "helloworld"
        self.ocr_service = "ocr_space"  # 默认使用OCR.Space
        
        # 金蝶数据库路径
        self.kingdee_db_path = None
        
        # 创建界面
        self.create_widgets()
        
        # 扫描金蝶数据库（在界面创建后）
        self.scan_kingdee_database()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="📋 智能仓管系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # API配置区域
        config_frame = ttk.LabelFrame(main_frame, text="🔑 OCR API 配置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # OCR服务选择
        ttk.Label(config_frame, text="OCR服务:").grid(row=0, column=0, sticky=tk.W)
        self.ocr_service_var = tk.StringVar(value="ocr_space")
        ocr_combo = ttk.Combobox(config_frame, textvariable=self.ocr_service_var, width=20, state="readonly")
        ocr_combo['values'] = ('OCR.Space (免费)', '百度OCR', '腾讯OCR')
        ocr_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        ocr_combo.bind('<<ComboboxSelected>>', self.on_ocr_service_change)
        
        # API密钥输入
        ttk.Label(config_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W)
        self.api_key_var = tk.StringVar(value=self.api_key)
        self.api_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=40)
        self.api_entry.grid(row=1, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # Secret Key输入（百度OCR用）
        self.secret_label = ttk.Label(config_frame, text="Secret Key:")
        self.secret_label.grid(row=2, column=0, sticky=tk.W)
        self.secret_key_var = tk.StringVar()
        self.secret_entry = ttk.Entry(config_frame, textvariable=self.secret_key_var, width=40)
        self.secret_entry.grid(row=2, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # 默认隐藏Secret Key输入
        self.secret_label.grid_remove()
        self.secret_entry.grid_remove()
        
        ttk.Button(config_frame, text="设置", command=self.set_api_key).grid(row=1, column=2, padx=(10, 0))
        
        # 信息显示
        self.info_label = ttk.Label(config_frame, text="免费API密钥: helloworld (25,000次/月)", foreground="gray")
        self.info_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 金蝶数据库配置
        db_frame = ttk.LabelFrame(main_frame, text="📁 金蝶数据库配置", padding="10")
        db_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(db_frame, text="数据库路径:").grid(row=0, column=0, sticky=tk.W)
        self.db_path_var = tk.StringVar()
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=50, state="readonly")
        db_entry.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(db_frame, text="浏览", command=self.browse_kingdee_db).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(db_frame, text="重新扫描", command=self.rescan_kingdee_db).grid(row=0, column=3, padx=(5, 0))
        
        self.db_status_label = ttk.Label(db_frame, text="正在扫描...", foreground="orange")
        self.db_status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 文件上传区域
        upload_frame = ttk.LabelFrame(main_frame, text="📸 上传单据图片", padding="10")
        upload_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Label(upload_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W)
        file_entry = ttk.Entry(upload_frame, textvariable=self.file_path_var, width=50, state="readonly")
        file_entry.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(upload_frame, text="浏览", command=self.browse_file).grid(row=0, column=2, padx=(10, 0))
        
        # 处理按钮
        process_btn = ttk.Button(upload_frame, text="🔄 开始处理", command=self.process_document)
        process_btn.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(upload_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="📋 处理结果", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建Notebook来分页显示结果
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # OCR结果页
        ocr_frame = ttk.Frame(self.notebook)
        self.notebook.add(ocr_frame, text="OCR识别")
        
        self.ocr_text = scrolledtext.ScrolledText(ocr_frame, height=8, wrap=tk.WORD)
        self.ocr_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 解析结果页
        parse_frame = ttk.Frame(self.notebook)
        self.notebook.add(parse_frame, text="解析结果")
        
        self.parse_text = scrolledtext.ScrolledText(parse_frame, height=8, wrap=tk.WORD)
        self.parse_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 金蝶结果页
        kingdee_frame = ttk.Frame(self.notebook)
        self.notebook.add(kingdee_frame, text="金蝶数据库")
        
        self.kingdee_text = scrolledtext.ScrolledText(kingdee_frame, height=8, wrap=tk.WORD)
        self.kingdee_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        config_frame.columnconfigure(1, weight=1)
        db_frame.columnconfigure(1, weight=1)
        upload_frame.columnconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        for frame in [ocr_frame, parse_frame, kingdee_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
    
    def on_ocr_service_change(self, event=None):
        """处理OCR服务选择变化"""
        service = self.ocr_service_var.get()
        if "OCR.Space" in service:
            self.ocr_service = "ocr_space"
            self.api_key_var.set("helloworld")
            self.secret_key_var.set("")
            # 隐藏Secret Key输入
            self.secret_label.grid_remove()
            self.secret_entry.grid_remove()
            self.info_label.config(text="免费API密钥: helloworld (25,000次/月)")
        elif "百度OCR" in service:
            self.ocr_service = "baidu"
            self.api_key_var.set("")
            self.secret_key_var.set("")
            # 显示Secret Key输入
            self.secret_label.grid(row=2, column=0, sticky=tk.W)
            self.secret_entry.grid(row=2, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
            self.info_label.config(text="需要百度AI开放平台API Key和Secret Key")
        elif "腾讯OCR" in service:
            self.ocr_service = "tencent"
            self.api_key_var.set("")
            self.secret_key_var.set("")
            # 显示Secret Key输入（腾讯使用SecretId/SecretKey）
            self.secret_label.grid(row=2, column=0, sticky=tk.W)
            self.secret_entry.grid(row=2, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
            self.info_label.config(text="需要腾讯云API SecretId和SecretKey")
    
    def scan_kingdee_database(self):
        """扫描金蝶数据库"""
        import glob
        
        # 常见的金蝶数据库路径
        search_paths = [
            r"C:\KDW\*.MDB",
            r"C:\KDW\*.ACCDB", 
            r"C:\KDMAIN\*.MDB",
            r"C:\KDMAIN\*.ACCDB",
            r"C:\Program Files\Kingdee\*.MDB",
            r"C:\Program Files\Kingdee\*.ACCDB",
            r"C:\Program Files (x86)\Kingdee\*.MDB",
            r"C:\Program Files (x86)\Kingdee\*.ACCDB",
            r"D:\KDW\*.MDB",
            r"D:\KDW\*.ACCDB"
        ]
        
        found_databases = []
        for pattern in search_paths:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if os.path.exists(file_path):
                        found_databases.append(file_path)
            except:
                continue
        
        if found_databases:
            # 优先选择KDMAIN.MDB
            main_db = None
            for db in found_databases:
                if "KDMAIN.MDB" in db.upper():
                    main_db = db
                    break
            
            self.kingdee_db_path = main_db or found_databases[0]
            self.db_path_var.set(self.kingdee_db_path)
            if KINGDEE_AVAILABLE:
                self.db_status_label.config(text=f"✅ 已找到数据库: {os.path.basename(self.kingdee_db_path)}", foreground="green")
            else:
                self.db_status_label.config(text=f"⚠️ 已找到数据库但金蝶模块未安装: {os.path.basename(self.kingdee_db_path)}", foreground="orange")
        else:
            if KINGDEE_AVAILABLE:
                self.db_status_label.config(text="⚠️ 未找到金蝶数据库，请手动选择", foreground="orange")
            else:
                self.db_status_label.config(text="⚠️ 金蝶模块未安装，数据库功能不可用", foreground="red")
    
    def browse_kingdee_db(self):
        """手动选择金蝶数据库"""
        file_path = filedialog.askopenfilename(
            title="选择金蝶数据库文件",
            filetypes=[
                ("Access数据库", "*.mdb *.accdb"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.kingdee_db_path = file_path
            self.db_path_var.set(file_path)
            self.db_status_label.config(text=f"✅ 已选择数据库: {os.path.basename(file_path)}", foreground="green")
    
    def rescan_kingdee_db(self):
        """重新扫描金蝶数据库"""
        self.db_status_label.config(text="🔄 正在重新扫描...", foreground="orange")
        self.root.update()
        self.scan_kingdee_database()
    
    def set_api_key(self):
        """设置API密钥"""
        self.api_key = self.api_key_var.get()
        self.secret_key = self.secret_key_var.get()
        if self.ocr_service == "baidu" and self.secret_key:
            messagebox.showinfo("成功", f"API密钥已更新\nAPI Key: {self.api_key[:10]}...\nSecret Key: {self.secret_key[:10]}...")
        else:
            messagebox.showinfo("成功", f"API密钥已更新: {self.api_key}")
    
    def browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择单据图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def process_document(self):
        """处理文档"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 清空之前的结果
        self.ocr_text.delete(1.0, tk.END)
        self.parse_text.delete(1.0, tk.END)
        self.kingdee_text.delete(1.0, tk.END)
        
        # 显示处理中状态
        self.progress.start()
        self.ocr_text.insert(tk.END, "🔄 正在进行OCR识别，请稍候...\n")
        
        # 在后台线程中处理
        thread = threading.Thread(target=self._process_in_background, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def _process_in_background(self, file_path):
        """后台处理文档"""
        try:
            # 根据OCR服务类型调用不同API
            if self.ocr_service == "ocr_space":
                text_content = self._ocr_space_api(file_path)
            elif self.ocr_service == "baidu":
                text_content = self._baidu_ocr_api(file_path)
            elif self.ocr_service == "tencent":
                text_content = self._tencent_ocr_api(file_path)
            else:
                raise Exception("不支持的OCR服务")
            
            # 增强解析
            parsed_data = parse_document_enhanced(text_content)
            
            # 保存到金蝶数据库
            kingdee_db = SimpleKingdeeDB(self.kingdee_db_path)
            save_result = kingdee_db.save_document(parsed_data)
            
            # 更新UI
            self.root.after(0, self._update_results, text_content, parsed_data, save_result)
                
        except Exception as e:
            self.root.after(0, self._show_error, f"处理失败: {str(e)}")
    
    def _ocr_space_api(self, file_path):
        """调用OCR.Space API"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'apikey': self.api_key,
                'language': 'chs',
                'isOverlayRequired': 'false',
                'detectOrientation': 'false',
                'scale': 'true',
                'OCREngine': '2'
            }
            
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('IsErroredOnProcessing'):
                text_content = ""
                for parsed_result in result.get('ParsedResults', []):
                    text_content += parsed_result.get('ParsedText', '')
                return text_content
            else:
                error_msg = result.get('ErrorMessage', ['OCR处理失败'])[0]
                raise Exception(f"OCR.Space处理失败: {error_msg}")
        else:
            raise Exception(f"OCR.Space API错误: {response.status_code}")
    
    def _baidu_ocr_api(self, file_path):
        """调用百度OCR API"""
        import base64
        
        # 读取图片并转换为base64
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 检查API Key和Secret Key
        if not self.api_key or not hasattr(self, 'secret_key') or not self.secret_key:
            raise Exception("百度OCR需要API Key和Secret Key，请在上方输入框中填写")
        
        # 获取access_token
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        token_params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key.strip(),
            "client_secret": self.secret_key.strip()
        }
        
        token_response = requests.post(token_url, params=token_params)
        if token_response.status_code != 200:
            raise Exception("百度OCR获取token失败")
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            raise Exception("百度OCR token获取失败，请检查API Key和Secret Key")
        
        # 调用OCR API
        ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
        ocr_data = {'image': image_data}
        
        ocr_response = requests.post(ocr_url, data=ocr_data, timeout=30)
        if ocr_response.status_code == 200:
            result = ocr_response.json()
            text_content = ""
            for item in result.get('words_result', []):
                text_content += item['words'] + "\n"
            return text_content
        else:
            raise Exception(f"百度OCR API错误: {ocr_response.status_code}")
    
    def _tencent_ocr_api(self, file_path):
        """调用腾讯OCR API（简化实现）"""
        # 简化处理，这里只是一个示例框架
        # 实际使用需要完整的腾讯云签名算法
        raise Exception("腾讯OCR暂未实现，请使用OCR.Space或百度OCR")
    
    def _update_results(self, text_content, parsed_data, save_result):
        """更新结果显示"""
        self.progress.stop()
        
        # 显示OCR结果
        self.ocr_text.delete(1.0, tk.END)
        self.ocr_text.insert(tk.END, "✅ OCR识别完成\n\n")
        self.ocr_text.insert(tk.END, f"识别到的文字内容:\n{'-'*40}\n")
        self.ocr_text.insert(tk.END, text_content)
        
        # 显示解析结果
        self.parse_text.delete(1.0, tk.END)
        self.parse_text.insert(tk.END, "📋 智能解析结果\n\n")
        self.parse_text.insert(tk.END, f"单据类型: {parsed_data.get('document_type', '未知')}\n")
        self.parse_text.insert(tk.END, f"单据号: {parsed_data.get('bill_no', '未识别')}\n")
        self.parse_text.insert(tk.END, f"日期: {parsed_data.get('date', '未识别')}\n")
        self.parse_text.insert(tk.END, f"供应商: {parsed_data.get('supplier', '未识别')}\n")
        self.parse_text.insert(tk.END, f"客户: {parsed_data.get('customer', '未识别')}\n")
        self.parse_text.insert(tk.END, f"金额: {parsed_data.get('amount', '未识别')}\n\n")
        
        if parsed_data.get('items'):
            self.parse_text.insert(tk.END, "商品明细:\n")
            for i, item in enumerate(parsed_data['items'], 1):
                self.parse_text.insert(tk.END, f"{i}. {item}\n")
        
        # 显示金蝶结果
        self.kingdee_text.delete(1.0, tk.END)
        self.kingdee_text.insert(tk.END, "💾 金蝶数据库保存结果\n\n")
        
        if save_result.get('success'):
            self.kingdee_text.insert(tk.END, f"✅ 保存成功!\n")
            self.kingdee_text.insert(tk.END, f"单据号: {save_result.get('bill_no', '')}\n")
            self.kingdee_text.insert(tk.END, f"消息: {save_result.get('message', '')}\n")
        else:
            self.kingdee_text.insert(tk.END, f"❌ 保存失败\n")
            self.kingdee_text.insert(tk.END, f"错误: {save_result.get('error', '')}\n")
        
        # 切换到第一个标签页
        self.notebook.select(0)
        
        # 显示完成消息
        messagebox.showinfo("完成", "文档处理完成！")
    
    def _show_error(self, error_msg):
        """显示错误"""
        self.progress.stop()
        self.ocr_text.delete(1.0, tk.END)
        self.ocr_text.insert(tk.END, f"❌ 错误: {error_msg}")
        messagebox.showerror("错误", error_msg)

def main():
    """主函数"""
    root = tk.Tk()
    app = WarehouseOCRApp(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()