# Smart Warehouse System - Packaged Version

## 🎯 项目结构说明

```
warehouse_agent_system/
├── packaged_version/          # 打包版本（简化）
│   ├── config/
│   │   └── settings.py       # 简化配置
│   ├── utils/
│   │   ├── ocr_processor.py  # 简化OCR处理
│   │   └── excel_exporter.py # Excel导出
│   ├── main.py              # 简化主程序
│   ├── app_main.py          # 启动器
│   ├── requirements.txt     # 最小依赖
│   └── .env.example        # 配置模板
├── 完整版本文件...           # 原有的完整功能版本
└── package_simple.bat       # 打包版专用打包脚本
```

## 🚀 使用方法

### 打包版本（推荐分发）
```bash
# 1. 打包成exe
双击 package_simple.bat

# 2. 分发给用户
将 release\WarehouseSystem\ 整个文件夹给用户

# 3. 用户使用
双击 start.bat 即可运行
```

### 完整版本（开发使用）
```bash
# 1. 直接运行
python main.py

# 2. 或使用绿色版
双击 绿色版打包.bat
```

## 💡 版本对比

| 功能 | 打包版 | 完整版 |
|------|--------|--------|
| OCR识别 | ✅ 在线OCR | ✅ 在线+本地OCR |
| 数据导出 | ✅ Excel | ✅ Excel+金蝶API |
| 多代理系统 | ❌ | ✅ CrewAI多代理 |
| 本地OCR | ❌ | ✅ PaddleOCR |
| 金蝶API集成 | ❌ | ✅ 完整集成 |
| 文件大小 | 小(~50MB) | 大(~200MB+) |
| 依赖复杂度 | 低 | 高 |
| 打包成功率 | 高 | 中等 |

## 🎯 推荐使用场景

**打包版**：
- 企业内部分发
- 不懂技术的用户
- 简单OCR需求
- 快速部署

**完整版**：
- 开发和测试
- 高级功能需求
- 定制化开发
- 技术用户

## 📦 打包版特点

- **零依赖**：用户无需安装Python
- **即开即用**：双击启动，自动打开浏览器
- **功能精简**：只保留核心OCR和Excel导出
- **稳定可靠**：依赖少，兼容性好
- **体积小**：适合网络分发

这样的结构让你可以：
1. 用完整版进行开发和测试
2. 用打包版生成分发给用户的exe程序
3. 两个版本互不干扰，便于管理