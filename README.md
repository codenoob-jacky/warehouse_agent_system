# 智能仓管系统

基于AI的智能仓管系统，支持纸质单据OCR识别、自动数据验证和金蝶ERP系统集成。

## 🎯 版本说明

### Ultra Simple 版本（推荐）
- **Web版**: `ultra_simple.py` - 浏览器界面
- **GUI版**: `ultra_simple_gui.py` - 桌面程序界面
- **特点**: 单文件，超轻量级（GUI版~15MB，Web版~20MB）
- **功能**: 在线OCR + 本地金蝶数据库
- **依赖**: GUI版仅2个包，Web版5个包
- **适用**: 中小企业，设备要求极低

### 打包版本
- **目录**: `packaged_version/`
- **特点**: 模块化，易维护
- **功能**: 在线OCR + Excel导出
- **适用**: 企业分发

### 完整版本
- **目录**: `full_version/`
- **特点**: 功能完整，支持多代理
- **功能**: 本地+在线OCR + 完整金蝶集成
- **适用**: 开发测试，高级用户

## 📁 项目结构

```
warehouse_agent_system/
├── packaged_version/          # 🎯 打包版本（简化，用于分发）
│   ├── config/               # 简化配置
│   ├── utils/                # 核心工具
│   ├── main.py              # 简化主程序
│   ├── app_main.py          # 启动器
│   ├── requirements.txt     # 最小依赖
│   └── README.md           # 打包版说明
├── full_version/             # 🔧 完整版本（开发使用）
│   ├── config/              # 完整配置
│   ├── utils/               # 完整工具集
│   ├── agents/              # 多代理系统
│   ├── tests/               # 测试文件
│   ├── main.py             # 完整主程序
│   ├── requirements.txt    # 完整依赖
│   └── .env.example       # 完整配置模板
├── scripts/                 # 🛠️ 构建和打包脚本
│   ├── package_simple.bat  # 打包版专用打包脚本
│   ├── 一键打包.bat         # 完整版打包脚本
│   ├── 绿色版打包.bat       # 绿色版打包脚本
│   └── 便携版打包.bat       # 便携版打包脚本
├── docs_and_guides/         # 📚 文档和指南
│   └── api_guide.py        # API获取指南
├── Dockerfile              # Docker配置
├── .gitignore             # Git忽略文件
└── README.md              # 项目主说明
```

## 🚀 快速开始

### 方案一：Ultra Simple版（推荐）
```bash
# GUI桌面版本（推荐）
python ultra_simple_gui.py

# Web浏览器版本
python ultra_simple.py

# 打包GUI版
双击 build_gui.bat

# 打包Web版
双击 build_ultra_simple.bat
```

### 方案二：打包版（企业分发）
```bash
# 1. 打包成exe
cd scripts
双击 package_simple.bat

# 2. 分发给用户
将 release\WarehouseSystem\ 整个文件夹给用户

# 3. 用户使用
双击 start.bat 即可运行
```

### 方案三：完整版（开发使用）
```bash
# 1. 进入完整版目录
cd full_version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件配置参数

# 4. 运行系统
python main.py
```

### 方案四：Docker部署
```bash
# 构建镜像
docker build -t warehouse-system .

# 运行容器
docker run -p 8000:8000 warehouse-system
```

## 💡 版本对比

| 功能 | Ultra Simple GUI | Ultra Simple Web | 打包版 | 完整版 |
|------|-----------------|-----------------|--------|--------|
| **界面类型** | 🖥️ 桌面GUI | 🌐 Web浏览器 | 🌐 Web浏览器 | 🌐 Web浏览器 |
| **OCR识别** | ✅ 在线OCR | ✅ 在线OCR | ✅ 在线OCR | ✅ 在线+本地OCR |
| **数据导出** | ✅ 金蝶DB | ✅ 金蝶DB | ✅ Excel | ✅ Excel+金蝶API |
| **金蝶集成** | ✅ 本地DB | ✅ 本地DB | ❌ | ✅ 完整集成 |
| **文件大小** | 极小(~15MB) | 小(~20MB) | 中(~50MB) | 大(~280MB) |
| **依赖数量** | 极少(2个) | 少(5个) | 低(8个) | 高(15+个) |
| **端口冲突** | ❌ 无 | ⚠️ 可能 | ⚠️ 可能 | ⚠️ 可能 |
| **启动速度** | ⭐ 极快 | ⭐ 快 | ⭐ 快 | 🐌 较慢 |
| **适用场景** | 中小企业首选 | 中小企业 | 企业分发 | 开发测试 |

> **推荐**: GUI版本无需浏览器，无端口冲突，更像传统桌面软件

## 🎯 核心功能

- **📸 智能OCR识别**: 支持拍照识别纸质入库单、出库单
- **🤖 多代理协作**: OCR代理、验证代理、金蝶集成代理协同工作
- **🔗 多种金蝶集成**: 支持在线版、本地数据库版、Excel导出版
- **✅ 数据验证**: 智能验证单据数据完整性和准确性
- **🌐 Web界面**: 简洁易用的Web操作界面
- **📊 库存查询**: 实时查询商品库存信息

## 🌐 在线OCR vs 本地OCR

### 在线OCR优势（推荐中小企业）
- ✅ **零配置要求**：无需安装大型模型文件
- ✅ **设备要求低**：任何能上网的电脑都能用
- ✅ **识别精度高**：大厂算法持续优化
- ✅ **成本更低**：免费额度通常够用
- ✅ **维护简单**：无需更新模型

### 支持的在线OCR服务
- **OCR.Space**（免费推荐）：每月25,000次免费
- **百度OCR**：每月1,000次免费，付费便宜
- **腾讯OCR**：每月1,000次免费
- **Google Vision**：每月1,000次免费

## 🔍 支持的金蝶版本

### 本地数据库版本
- **金蝶KIS**: Access数据库 (.MDB/.ACCDB)
- **金蝶K3**: SQL Server数据库
- **其他版本**: 可通过调整SQL语句适配

### 常见数据库路径
- `C:\KDW\KDMAIN.MDB`
- `C:\KDMAIN\*.MDB`
- `C:\Program Files\Kingdee\*.MDB`

## ⚙️ 系统要求

### 打包版
- Windows 7/8/10/11
- 网络连接（用于在线OCR）
- 2GB内存，100MB硬盘空间

### 完整版
- Python 3.8+
- Windows/Linux/macOS
- 网络连接
- 4GB内存，500MB硬盘空间

## 🔧 常见问题

### 依赖冲突
- 打包版：使用精简依赖，避免冲突
- 完整版：修复了langchain版本冲突

### 编码问题
- 使用英文文件名避免中文编码问题
- 统一使用UTF-8编码

### 打包失败
- 推荐使用打包版的简化方案
- 避免复杂依赖导致的打包问题

## 📞 技术支持

- 🐛 问题反馈：提交Issue
- 📖 详细文档：查看各版本README
- 🔧 API指南：docs_and_guides/api_guide.py
- 💬 技术交流：欢迎讨论和建议

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。