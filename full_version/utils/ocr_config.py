from typing import Dict, Any
import os

class OptimizedOCRConfig:
    """优化的OCR配置，适合中小企业使用"""
    
    @staticmethod
    def get_cpu_config() -> Dict[str, Any]:
        """CPU模式配置（推荐）"""
        return {
            'use_gpu': False,
            'use_angle_cls': True,  # 支持文字方向检测
            'lang': 'ch',          # 中文识别
            'det_model_dir': None,  # 使用默认检测模型
            'rec_model_dir': None,  # 使用默认识别模型
            'cls_model_dir': None,  # 使用默认分类模型
            'use_space_char': True, # 识别空格
            'drop_score': 0.5,     # 置信度阈值
            'max_text_length': 25   # 最大文本长度
        }
    
    @staticmethod
    def get_gpu_config() -> Dict[str, Any]:
        """GPU模式配置（需要NVIDIA显卡）"""
        return {
            'use_gpu': True,
            'gpu_mem': 500,        # GPU内存限制(MB)
            'use_angle_cls': True,
            'lang': 'ch',
            'det_model_dir': None,
            'rec_model_dir': None,
            'cls_model_dir': None,
            'use_space_char': True,
            'drop_score': 0.5,
            'max_text_length': 25
        }
    
    @staticmethod
    def get_fast_config() -> Dict[str, Any]:
        """快速模式配置（牺牲精度换速度）"""
        return {
            'use_gpu': False,
            'use_angle_cls': False,  # 关闭方向检测
            'lang': 'ch',
            'det_model_dir': None,
            'rec_model_dir': None,
            'use_space_char': False,
            'drop_score': 0.3,      # 降低置信度要求
            'max_text_length': 15
        }
    
    @staticmethod
    def get_accurate_config() -> Dict[str, Any]:
        """高精度模式配置（速度较慢）"""
        return {
            'use_gpu': False,
            'use_angle_cls': True,
            'lang': 'ch',
            'det_model_dir': None,
            'rec_model_dir': None,
            'cls_model_dir': None,
            'use_space_char': True,
            'drop_score': 0.7,      # 提高置信度要求
            'max_text_length': 50,
            'det_db_thresh': 0.3,   # 检测阈值
            'det_db_box_thresh': 0.5 # 框选阈值
        }

def get_ocr_config(mode: str = 'cpu') -> Dict[str, Any]:
    """获取OCR配置
    
    Args:
        mode: 配置模式 ('cpu', 'gpu', 'fast', 'accurate')
    
    Returns:
        OCR配置字典
    """
    config_map = {
        'cpu': OptimizedOCRConfig.get_cpu_config,
        'gpu': OptimizedOCRConfig.get_gpu_config,
        'fast': OptimizedOCRConfig.get_fast_config,
        'accurate': OptimizedOCRConfig.get_accurate_config
    }
    
    if mode not in config_map:
        mode = 'cpu'  # 默认使用CPU模式
    
    return config_map[mode]()

def check_gpu_available() -> bool:
    """检查GPU是否可用"""
    try:
        import paddle
        return paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    except:
        return False

def auto_select_config() -> Dict[str, Any]:
    """自动选择最佳配置"""
    if check_gpu_available():
        print("✅ 检测到GPU，使用GPU加速模式")
        return get_ocr_config('gpu')
    else:
        print("ℹ️  未检测到GPU，使用CPU模式")
        return get_ocr_config('cpu')

# 使用示例
if __name__ == "__main__":
    print("🔍 OCR配置选择器")
    print("=" * 30)
    
    # 检查GPU
    gpu_available = check_gpu_available()
    print(f"GPU可用: {'是' if gpu_available else '否'}")
    
    # 显示配置选项
    print("\n📋 可用配置:")
    print("1. CPU模式 - 适合普通电脑，无需特殊硬件")
    print("2. GPU模式 - 需要NVIDIA显卡，识别速度快")
    print("3. 快速模式 - 牺牲精度换取速度")
    print("4. 高精度模式 - 识别精度高但速度慢")
    
    # 推荐配置
    if gpu_available:
        print("\n💡 推荐: GPU模式")
        recommended_config = get_ocr_config('gpu')
    else:
        print("\n💡 推荐: CPU模式")
        recommended_config = get_ocr_config('cpu')
    
    print(f"\n推荐配置: {recommended_config}")