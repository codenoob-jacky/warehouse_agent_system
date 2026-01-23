import requests
import base64
import json
import time
from typing import Dict, List, Any, Optional
from PIL import Image
import io
import os

class OnlineOCRService:
    """在线OCR服务基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('timeout', 30)
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """提取文字 - 子类需要实现"""
        raise NotImplementedError

class BaiduOCR(OnlineOCRService):
    """百度OCR API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.secret_key = config.get('secret_key', '')
        self.access_token = None
    
    def get_access_token(self):
        """获取访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access_token')
            return True
        return False
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """百度OCR识别"""
        if not self.access_token:
            if not self.get_access_token():
                raise Exception("获取百度OCR访问令牌失败")
        
        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'image': image_data,
            'access_token': self.access_token
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=self.timeout)
        
        if response.status_code == 200:
            result = response.json()
            extracted_data = []
            
            for item in result.get('words_result', []):
                extracted_data.append({
                    'text': item['words'],
                    'confidence': 0.9,  # 百度API不返回置信度，设置默认值
                    'position': item.get('location', {})
                })
            
            return extracted_data
        else:
            raise Exception(f"百度OCR请求失败: {response.text}")

class TencentOCR(OnlineOCRService):
    """腾讯OCR API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_id = config.get('secret_id', '')
        self.secret_key = config.get('secret_key', '')
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """腾讯OCR识别"""
        # 这里需要实现腾讯云OCR的签名算法
        # 为简化示例，这里只是框架
        extracted_data = []
        # TODO: 实现腾讯OCR API调用
        return extracted_data

class OnlineOCRNet(OnlineOCRService):
    """OnlineOCR.net 免费服务"""
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """使用OnlineOCR.net识别"""
        try:
            # 准备文件上传
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'language': 'chs',  # 中文简体
                    'isOverlayRequired': 'false',
                    'detectOrientation': 'false',
                    'isCreateSearchablePdf': 'false',
                    'isSearchablePdfHideTextLayer': 'false'
                }
                
                # 发送请求
                response = requests.post(
                    'https://www.onlineocr.net/api/ocrUpload',
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # 解析返回的文字
                    text_content = result.get('text', '')
                    lines = text_content.split('\n')
                    
                    extracted_data = []
                    for line in lines:
                        if line.strip():
                            extracted_data.append({
                                'text': line.strip(),
                                'confidence': 0.8,  # 默认置信度
                                'position': {}
                            })
                    
                    return extracted_data
                else:
                    raise Exception(f"OnlineOCR识别失败: {result.get('message', '未知错误')}")
            else:
                raise Exception(f"OnlineOCR请求失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"OnlineOCR服务异常: {str(e)}")

class OCRSpaceAPI(OnlineOCRService):
    """OCR.Space 免费API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', 'helloworld')  # 免费API Key
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """使用OCR.Space识别"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'apikey': self.api_key,
                    'language': 'chs',  # 中文
                    'isOverlayRequired': 'false',
                    'detectOrientation': 'false',
                    'scale': 'true',
                    'OCREngine': '2'  # 使用引擎2，对中文支持更好
                }
                
                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('IsErroredOnProcessing'):
                    extracted_data = []
                    
                    for parsed_result in result.get('ParsedResults', []):
                        text_content = parsed_result.get('ParsedText', '')
                        lines = text_content.split('\n')
                        
                        for line in lines:
                            if line.strip():
                                extracted_data.append({
                                    'text': line.strip(),
                                    'confidence': 0.85,
                                    'position': {}
                                })
                    
                    return extracted_data
                else:
                    error_msg = result.get('ErrorMessage', ['未知错误'])[0]
                    raise Exception(f"OCR.Space识别失败: {error_msg}")
            else:
                raise Exception(f"OCR.Space请求失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"OCR.Space服务异常: {str(e)}")

class GoogleVisionOCR(OnlineOCRService):
    """Google Vision API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
    
    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """使用Google Vision API识别"""
        try:
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_data
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 50
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = []
                
                responses = result.get('responses', [])
                if responses and 'textAnnotations' in responses[0]:
                    for annotation in responses[0]['textAnnotations'][1:]:  # 跳过第一个完整文本
                        extracted_data.append({
                            'text': annotation['description'],
                            'confidence': 0.9,
                            'position': annotation.get('boundingPoly', {})
                        })
                
                return extracted_data
            else:
                raise Exception(f"Google Vision API请求失败: {response.text}")
                
        except Exception as e:
            raise Exception(f"Google Vision API异常: {str(e)}")

class OnlineOCRManager:
    """在线OCR管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services = {}
        self.init_services()
    
    def init_services(self):
        """初始化OCR服务"""
        ocr_config = self.config.get('online_ocr', {})
        
        # 百度OCR
        if ocr_config.get('baidu', {}).get('enabled', False):
            self.services['baidu'] = BaiduOCR(ocr_config['baidu'])
        
        # 腾讯OCR
        if ocr_config.get('tencent', {}).get('enabled', False):
            self.services['tencent'] = TencentOCR(ocr_config['tencent'])
        
        # OCR.Space (免费)
        if ocr_config.get('ocr_space', {}).get('enabled', True):  # 默认启用
            self.services['ocr_space'] = OCRSpaceAPI(ocr_config.get('ocr_space', {}))
        
        # OnlineOCR.net (免费)
        if ocr_config.get('online_ocr_net', {}).get('enabled', False):
            self.services['online_ocr_net'] = OnlineOCRNet(ocr_config.get('online_ocr_net', {}))
        
        # Google Vision
        if ocr_config.get('google_vision', {}).get('enabled', False):
            self.services['google_vision'] = GoogleVisionOCR(ocr_config['google_vision'])
    
    def extract_text(self, image_path: str, preferred_service: str = None) -> List[Dict[str, Any]]:
        """提取文字，支持服务降级"""
        
        # 服务优先级
        service_priority = [
            preferred_service,
            'baidu',
            'google_vision', 
            'ocr_space',
            'online_ocr_net',
            'tencent'
        ]
        
        # 过滤掉None和不可用的服务
        available_services = [s for s in service_priority if s and s in self.services]
        
        if not available_services:
            raise Exception("没有可用的在线OCR服务")
        
        last_error = None
        
        for service_name in available_services:
            try:
                print(f"🔍 尝试使用 {service_name} 进行OCR识别...")
                service = self.services[service_name]
                result = service.extract_text(image_path)
                print(f"✅ {service_name} 识别成功")
                return result
                
            except Exception as e:
                print(f"❌ {service_name} 识别失败: {str(e)}")
                last_error = e
                continue
        
        # 所有服务都失败
        raise Exception(f"所有在线OCR服务都失败，最后错误: {str(last_error)}")

def create_online_ocr_config() -> Dict[str, Any]:
    """创建在线OCR配置示例"""
    return {
        'online_ocr': {
            # 百度OCR (付费，但有免费额度)
            'baidu': {
                'enabled': False,
                'api_key': 'your_baidu_api_key',
                'secret_key': 'your_baidu_secret_key',
                'timeout': 30
            },
            
            # 腾讯OCR (付费，但有免费额度)
            'tencent': {
                'enabled': False,
                'secret_id': 'your_tencent_secret_id',
                'secret_key': 'your_tencent_secret_key',
                'timeout': 30
            },
            
            # OCR.Space (免费，推荐)
            'ocr_space': {
                'enabled': True,
                'api_key': 'helloworld',  # 免费API Key
                'timeout': 30
            },
            
            # OnlineOCR.net (免费，但有限制)
            'online_ocr_net': {
                'enabled': False,  # 网站可能不稳定
                'timeout': 30
            },
            
            # Google Vision (付费，但有免费额度)
            'google_vision': {
                'enabled': False,
                'api_key': 'your_google_api_key',
                'timeout': 30
            }
        }
    }

# 测试函数
def test_online_ocr():
    """测试在线OCR服务"""
    print("🧪 测试在线OCR服务")
    print("=" * 40)
    
    # 创建测试图片
    from utils.ocr_demo import OCRExplainer
    explainer = OCRExplainer()
    test_image = explainer.create_test_image("test_online_ocr.png")
    
    # 配置在线OCR
    config = create_online_ocr_config()
    ocr_manager = OnlineOCRManager(config)
    
    try:
        # 测试OCR识别
        result = ocr_manager.extract_text(test_image)
        
        print(f"\n✅ 在线OCR识别成功！")
        print(f"识别到 {len(result)} 行文字:")
        print("-" * 30)
        
        for i, item in enumerate(result, 1):
            print(f"{i}. {item['text']} (置信度: {item['confidence']:.2f})")
        
    except Exception as e:
        print(f"❌ 在线OCR测试失败: {str(e)}")
        print("\n💡 解决方案:")
        print("1. 检查网络连接")
        print("2. 配置有效的API密钥")
        print("3. 确认服务可用性")

if __name__ == "__main__":
    test_online_ocr()