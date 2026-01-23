# 部署指南

## 🎯 版本选择

### Ultra Simple 版本（推荐中小企业）
- **文件**: `ultra_simple.py`
- **优势**: 单文件，超轻量，直接运行
- **适用**: 设备配置低，需要本地金蝶数据库集成

### 打包版本（推荐企业分发）
- **目录**: `packaged_version/`
- **优势**: 模块化，易维护，Excel导出
- **适用**: 需要分发给多个用户

### 完整版本（推荐开发者）
- **目录**: `full_version/`
- **优势**: 功能完整，支持多代理
- **适用**: 开发测试，高级功能需求

## 🚀 快速部署

### Ultra Simple 版本
```bash
# 1. 安装依赖
pip install -r simple_requirements.txt

# 2. 直接运行
python ultra_simple.py

# 3. 访问系统
http://localhost:8000
```

### 打包成exe
```bash
# Ultra Simple 版本打包
双击 build_ultra_simple.bat

# 打包版本打包
cd scripts
双击 package_simple.bat
```

## 🔧 配置说明

### OCR配置
- **免费方案**: 使用默认API Key `helloworld`
- **付费方案**: 申请百度OCR或腾讯OCR

### 金蝶数据库
- **自动检测**: 系统会自动扫描常见路径
- **手动配置**: 如果检测失败，需要手动指定数据库路径

### 常见路径
- `C:\KDW\KDMAIN.MDB`
- `C:\KDMAIN\KDMAIN.MDB`
- `C:\Program Files\Kingdee\KDMAIN.MDB`

## 📦 分发说明

### 给最终用户
1. 使用Ultra Simple版本打包
2. 将整个文件夹复制给用户
3. 用户双击start.bat即可使用

### 给技术用户
1. 提供源代码
2. 用户自行安装Python环境
3. 按照README运行

## 🔍 故障排除

### 端口占用
- 错误: `error while attempting to bind on address ('0.0.0.0', 8000)`
- 解决: 关闭占用8000端口的程序，或修改代码使用其他端口

### 金蝶数据库连接失败
- 检查数据库路径是否正确
- 确认安装了Microsoft Access Database Engine
- 检查数据库文件权限

### OCR识别失败
- 检查网络连接
- 确认API Key有效
- 尝试更换OCR服务