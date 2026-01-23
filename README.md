# 智能仓管系统

基于AI多代理架构的智能仓管系统，支持纸质单据OCR识别、自动数据验证和金蝶ERP系统集成。

## 🚀 核心功能

- **📸 智能OCR识别**: 支持拍照识别纸质入库单、出库单
- **🤖 多代理协作**: OCR代理、验证代理、金蝶集成代理协同工作
- **🔗 多种金蝶集成**: 支持在线版、本地数据库版、Excel导出版
- **✅ 数据验证**: 智能验证单据数据完整性和准确性
- **🌐 Web界面**: 简洁易用的Web操作界面
- **📊 库存查询**: 实时查询商品库存信息

### 💡 特别适配中小企业

- **本地金蝶支持**: 直接读写本地Access/SQL Server数据库
- **无需联网**: 支持离线版金蝶系统
- **Excel备选**: 无数据库时可导出Excel格式
- **成本友好**: 适配盗版金蝶，降低企业成本

## 🏗️ 系统架构

```
智能仓管系统
├── 多代理系统
│   ├── OCR识别代理 - 图片文字识别
│   ├── 数据验证代理 - 数据质量检查
│   ├── 金蝶集成代理 - ERP系统同步
│   └── 协调代理 - 流程统筹管理
├── OCR处理模块
│   ├── PaddleOCR引擎 - 中文识别优化
│   └── 智能解析器 - 结构化数据提取
├── 金蝶集成模块
│   ├── API接口封装
│   ├── 单据创建功能
│   └── 库存查询功能
└── Web服务
    ├── FastAPI后端
    ├── 文件上传处理
    └── 结果查询接口
```

## 📦 安装部署

### 1. 环境要求

- Python 3.8+
- Redis (可选，用于缓存)
- 金蝶ERP系统访问权限

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置金蝶系统

系统支持三种金蝶集成方式：

#### 方式一：本地金蝶数据库（推荐）
```env
KINGDEE_TYPE=local
KINGDEE_DB_TYPE=access
KINGDEE_DB_PATH=C:\KDW\KDMAIN.MDB
```

#### 方式二：在线金蝶系统
```env
KINGDEE_TYPE=online
KINGDEE_BASE_URL=http://your-server:8080
KINGDEE_USERNAME=your-username
KINGDEE_PASSWORD=your-password
```

#### 方式三：Excel导出（无数据库）
```env
KINGDEE_TYPE=excel
KINGDEE_EXCEL_PATH=./kingdee_data.xlsx
```

**🔍 自动检测金蝶数据库：**
```bash
python utils/kingdee_detector.py
```

### 4. 启动服务

```bash
python main.py
```

访问 http://localhost:8000 使用Web界面

## 🎯 使用方法

### Web界面使用

1. 打开浏览器访问 http://localhost:8000
2. 点击"选择文件"上传单据图片
3. 点击"开始处理"进行识别
4. 查看处理结果和金蝶同步状态

### API接口使用

#### 上传单据处理
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.jpg"
```

#### 查询处理结果
```bash
curl "http://localhost:8000/result/{task_id}"
```

#### 查询库存
```bash
curl "http://localhost:8000/api/inventory/{item_code}"
```

#### 手动录入单据
```bash
curl -X POST "http://localhost:8000/api/manual-entry" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "inbound",
    "basic_info": {
      "document_number": "RK20240101001",
      "date": "2024-01-01",
      "supplier": "测试供应商"
    },
    "items": [
      {
        "item_code": "ITEM001",
        "item_name": "测试商品",
        "quantity": 10,
        "unit_price": 100.0
      }
    ]
  }'
```

## 🔧 配置说明

### OCR配置
- `OCR_USE_GPU`: 是否使用GPU加速（需要CUDA环境）
- 支持中文识别，针对中文单据优化

### 金蝶系统配置
- 需要配置金蝶服务器地址、用户名、密码和数据库
- **本地版金蝶**: 直接读写Access/SQL Server数据库文件
- **在线版金蝶**: 通过API接口同步数据
- **Excel模式**: 无数据库时导出Excel文件
- 自动处理单据号、日期、供应商/客户、商品明细等信息

### 代理系统配置
- 可选择使用多代理系统或简化的单代理系统
- 多代理系统提供更好的错误处理和流程控制
- 单代理系统性能更高，适合简单场景

## 📁 项目结构

```
warehouse_agent_system/
├── agents/                 # 代理系统
│   └── warehouse_agents.py # 多代理和单代理实现
├── config/                 # 配置文件
│   └── settings.py        # 系统配置
├── utils/                  # 工具模块
│   ├── ocr_processor.py   # OCR处理
│   └── kingdee_integration.py # 金蝶集成
├── data/                   # 数据存储
├── tests/                  # 测试文件
├── uploads/                # 上传文件目录
├── main.py                # 主应用
├── requirements.txt       # 依赖包
└── README.md             # 说明文档
```

## 🔍 支持的金蝶版本

### 本地数据库版本
- **金蝶KIS**: Access数据库 (.MDB/.ACCDB)
- **金蝶K3**: SQL Server数据库
- **其他版本**: 可通过调整SQL语句适配

### 常见数据库路径
- `C:\KDW\KDMAIN.MDB`
- `C:\KDMAIN\*.MDB`
- `C:\Program Files\Kingdee\*.MDB`

### 数据库表结构
- `ICStockBill`: 单据主表
- `ICStockBillEntry`: 单据明细表
- `t_ICItem`: 商品资料表
- `t_Supplier`: 供应商表
- `t_Organization`: 客户表

### 入库单识别字段
- 单据号、日期、供应商、仓库
- 商品编码、商品名称、数量、单价、金额
- 总金额、备注等

### 出库单识别字段
- 单据号、日期、客户、仓库
- 商品编码、商品名称、数量、单价、金额
- 总金额、备注等

## 🚨 注意事项

1. **图片质量**: 确保单据图片清晰，光线充足
2. **网络连接**: 需要稳定的网络连接访问金蝶系统
3. **权限配置**: 确保金蝶用户有创建单据的权限
4. **数据备份**: 建议定期备份处理结果和配置
5. **安全性**: 生产环境请配置HTTPS和访问控制

## 🔄 扩展功能

- 支持更多ERP系统（SAP、用友等）
- 增加更多单据类型（调拨单、盘点单等）
- 添加数据分析和报表功能
- 集成条码/二维码识别
- 支持批量处理功能

## 📞 技术支持

如有问题或建议，请提交Issue或联系开发团队。