"""
金蝶KIS云专业版 v7.0/v16.0 - 简化版仓管系统
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import os
from datetime import datetime
import threading
from kingdee_cloud_v7 import KingdeeCloudV7, parse_ocr_to_kingdee

class KingdeeCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("金蝶云专业版仓管系统 v7.0/v16.0")
        self.root.geometry("900x700")
        
        # 配置
        self.config = {
            'base_url': '',
            'acct_id': '',
            'username': '',
            'password': ''
        }
        self.ocr_api_key = 'helloworld'
        self.kingdee = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        ttk.Label(main_frame, text="📋 金蝶云专业版仓管系统", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 金蝶云配置
        config_frame = ttk.LabelFrame(main_frame, text="🔧 金蝶云配置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(config_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.url_var, width=50).grid(
            row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="账套ID:").grid(row=1, column=0, sticky=tk.W)
        self.acct_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.acct_var, width=50).grid(
            row=1, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="用户名:").grid(row=2, column=0, sticky=tk.W)
        self.user_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.user_var, width=50).grid(
            row=2, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(config_frame, text="密码:").grid(row=3, column=0, sticky=tk.W)
        self.pwd_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.pwd_var, width=50, show="*").grid(
            row=3, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(config_frame, text="测试连接", command=self.test_connection).grid(
            row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.conn_status = ttk.Label(config_frame, text="未连接", foreground="gray")
        self.conn_status.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # OCR配置
        ocr_frame = ttk.LabelFrame(main_frame, text="🔑 OCR配置", padding="10")
        ocr_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(ocr_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W)
        self.ocr_key_var = tk.StringVar(value=self.ocr_api_key)
        ttk.Entry(ocr_frame, textvariable=self.ocr_key_var, width=50).grid(
            row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # 文件上传
        upload_frame = ttk.LabelFrame(main_frame, text="📸 上传单据", padding="10")
        upload_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_var = tk.StringVar()
        ttk.Entry(upload_frame, textvariable=self.file_var, width=50, state="readonly").grid(
            row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        ttk.Button(upload_frame, text="选择文件", command=self.browse_file).grid(row=0, column=1)
        
        # 单据类型
        ttk.Label(upload_frame, text="单据类型:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.doc_type_var = tk.StringVar(value="inbound")
        ttk.Radiobutton(upload_frame, text="入库单", variable=self.doc_type_var, value="inbound").grid(
            row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Radiobutton(upload_frame, text="出库单", variable=self.doc_type_var, value="outbound").grid(
            row=2, column=1, sticky=tk.W)
        
        ttk.Button(upload_frame, text="🚀 开始处理", command=self.process_document).grid(
            row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.progress = ttk.Progressbar(upload_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 结果显示
        result_frame = ttk.LabelFrame(main_frame, text="📋 处理结果", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        config_frame.columnconfigure(1, weight=1)
        upload_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def test_connection(self):
        """测试金蝶云连接"""
        self.config['base_url'] = self.url_var.get()
        self.config['acct_id'] = self.acct_var.get()
        self.config['username'] = self.user_var.get()
        self.config['password'] = self.pwd_var.get()
        
        if not all([self.config['base_url'], self.config['acct_id'], 
                   self.config['username'], self.config['password']]):
            messagebox.showerror("错误", "请填写完整配置")
            return
        
        self.conn_status.config(text="连接中...", foreground="orange")
        self.root.update()
        
        self.kingdee = KingdeeCloudV7(self.config)
        if self.kingdee.login():
            self.conn_status.config(text="✅ 连接成功", foreground="green")
            messagebox.showinfo("成功", "金蝶云连接成功！")
        else:
            self.conn_status.config(text="❌ 连接失败", foreground="red")
            messagebox.showerror("失败", "金蝶云连接失败，请检查配置")
    
    def browse_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择单据图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_var.set(file_path)
    
    def process_document(self):
        """处理文档"""
        if not self.kingdee:
            messagebox.showerror("错误", "请先测试连接")
            return
        
        file_path = self.file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择有效文件")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🔄 处理中...\n")
        self.progress.start()
        
        thread = threading.Thread(target=self._process_in_background, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def _process_in_background(self, file_path):
        """后台处理"""
        try:
            # OCR识别
            ocr_text = self._ocr_image(file_path)
            
            # 解析
            doc_type = self.doc_type_var.get()
            parsed_data = parse_ocr_to_kingdee(ocr_text, doc_type)
            
            # 保存到金蝶
            if doc_type == 'inbound':
                result = self.kingdee.save_inbound(parsed_data)
            else:
                result = self.kingdee.save_outbound(parsed_data)
            
            self.root.after(0, self._show_result, ocr_text, parsed_data, result)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _ocr_image(self, file_path):
        """OCR识别"""
        with open(file_path, 'rb') as f:
            resp = requests.post(
                'https://api.ocr.space/parse/image',
                files={'file': f},
                data={'apikey': self.ocr_key_var.get(), 'language': 'chs', 'OCREngine': '2'},
                timeout=30
            )
        
        if resp.status_code == 200:
            result = resp.json()
            if not result.get('IsErroredOnProcessing'):
                return result['ParsedResults'][0]['ParsedText']
        raise Exception("OCR识别失败")
    
    def _show_result(self, ocr_text, parsed_data, result):
        """显示结果"""
        self.progress.stop()
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, "=== OCR识别结果 ===\n")
        self.result_text.insert(tk.END, f"{ocr_text}\n\n")
        
        self.result_text.insert(tk.END, "=== 解析结果 ===\n")
        self.result_text.insert(tk.END, f"单据号: {parsed_data.get('bill_no', '未识别')}\n")
        self.result_text.insert(tk.END, f"日期: {parsed_data.get('date', '未识别')}\n\n")
        
        self.result_text.insert(tk.END, "=== 金蝶云保存结果 ===\n")
        if result.get('success'):
            self.result_text.insert(tk.END, f"✅ 保存成功\n")
            self.result_text.insert(tk.END, f"单据号: {result.get('bill_no')}\n")
            self.result_text.insert(tk.END, f"ID: {result.get('id')}\n")
            messagebox.showinfo("成功", "单据已保存到金蝶云！")
        else:
            self.result_text.insert(tk.END, f"❌ 保存失败\n")
            self.result_text.insert(tk.END, f"错误: {result.get('error')}\n")
            messagebox.showerror("失败", f"保存失败: {result.get('error')}")
    
    def _show_error(self, error):
        """显示错误"""
        self.progress.stop()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"❌ 错误: {error}")
        messagebox.showerror("错误", error)

if __name__ == "__main__":
    root = tk.Tk()
    app = KingdeeCloudApp(root)
    root.mainloop()
