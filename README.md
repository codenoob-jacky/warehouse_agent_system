# 智能仓管系统 - 金蝶云专业版

基于AI的智能仓管系统，专为**金蝶KIS云专业版 v7.0.0.9 / v16.0**定制开发。

支持纸质单据OCR识别、自动解析并保存到金蝶云系统。

## 🎯 版本信息

- **金蝶版本**: KIS云专业版 v7.0.0.9 / v16.0
- **应用平台**: v2.2.1
- **集成方式**: WebAPI
- **依赖**: 仅需 requests

## 📁 项目结构

```
warehouse_agent_system/
├── kingdee_cloud_v7.py           # 金蝶云API核心模块
├── kingdee_cloud_app.py          # GUI应用程序
├── .env.kingdee_cloud            # 配置文件模板
├── requirements_kingdee_cloud.txt # 依赖列表
├── install_kingdee_cloud.bat     # 安装脚本
├── start_kingdee_cloud.bat       # 启动脚本
├── KINGDEE_CLOUD_README.md       # 详细文档
├── docs_and_guides/              # 参考文档
└── README.md                     # 本文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
# 方式一：使用脚本（推荐）
双击 install_kingdee_cloud.bat

# 方式二：手动安装
pip install -r requirements_kingdee_cloud.txt
```

### 2. 配置金蝶云
编辑 `.env.kingdee_cloud` 文件，填入您的金蝶云信息：
```ini
KINGDEE_BASE_URL=http://your-server-ip/K3Cloud
KINGDEE_ACCT_ID=your_account_id
KINGDEE_USERNAME=your_username
KINGDEE_PASSWORD=your_password
```

### 3. 启动程序
```bash
# 方式一：使用脚本（推荐）
双击 start_kingdee_cloud.bat

# 方式二：手动启动
python kingdee_cloud_app.py
```

## 💡 核心优势

- ✅ **极简依赖**: 仅需 requests 库
- ✅ **云端集成**: 直连金蝶云，无需本地数据库
- ✅ **OCR识别**: 支持OCR.Space、百度OCR等
- ✅ **图形界面**: 简洁易用的桌面程序
- ✅ **快速部署**: 5分钟完成配置
- ✅ **专业定制**: 针对金蝶云v7.0/v16.0优化

## 🎯 核心功能

- **📸 智能OCR识别**: 支持拍照识别纸质入库单、出库单
- **🔗 金蝶云集成**: 通过WebAPI直连金蝶云系统
- **✅ 自动解析**: 智能提取单据号、日期、供应商等信息
- **💾 自动保存**: 解析后自动保存到金蝶云
- **🖥️ 图形界面**: 简洁易用的桌面操作界面

## 🌐 支持的OCR服务

- **OCR.Space**（免费推荐）：每月25,000次免费
- **百度OCR**：每月1,000次免费
- **腾讯OCR**：每月1,000次免费

## 🔍 支持的单据类型

### 入库单 (STK_InStock)
- 单据类型编码: `RKD01`
- 自动识别：单据号、日期、供应商、物料明细

### 出库单 (SAL_OUTSTOCK)
- 单据类型编码: `CKD01`
- 自动识别：单据号、日期、客户、物料明细

## ⚙️ 系统要求

- Python 3.8+
- Windows/Linux/macOS
- 网络连接（访问金蝶云和OCR服务）
- 2GB内存，50MB硬盘空间

## 🔧 常见问题

### 连接失败
- 检查金蝶云服务器地址是否正确
- 确认账套ID、用户名、密码
- 验证网络连通性

### 保存失败
- 检查必填字段是否完整
- 确认供应商/客户编码存在
- 验证物料编码存在于金蝶系统

### OCR识别不准确
- 使用清晰的图片
- 确保文字方向正确
- 可更换OCR服务

## 📞 技术支持

- 🐛 问题反馈：提交Issue
- 📖 详细文档：查看 KINGDEE_CLOUD_README.md
- 🔧 API指南：docs_and_guides/
- 💬 技术交流：欢迎讨论和建议

## 📚 相关文档

- [详细使用文档](KINGDEE_CLOUD_README.md)
- [配置文件说明](.env.kingdee_cloud)
- [API核心代码](kingdee_cloud_v7.py)

## 📄 许可证

本项目采用MIT许可证。