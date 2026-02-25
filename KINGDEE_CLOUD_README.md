# 金蝶KIS云专业版 v7.0/v16.0 定制说明

## 📋 版本信息
- **金蝶版本**: KIS云专业版 v7.0.0.9 / v16.0
- **应用平台**: v2.2.1
- **集成方式**: WebAPI

## 🚀 快速开始

### 1. 运行程序
```bash
python kingdee_cloud_app.py
```

### 2. 配置金蝶云连接
在界面中填写：
- **服务器地址**: `http://your-server-ip/K3Cloud` 或 `http://your-domain.com/K3Cloud`
- **账套ID**: 您的账套编号
- **用户名**: 金蝶云用户名
- **密码**: 金蝶云密码

### 3. 测试连接
点击"测试连接"按钮，确保能成功连接到金蝶云

### 4. 处理单据
1. 选择单据图片
2. 选择单据类型（入库单/出库单）
3. 点击"开始处理"

## 🔧 核心文件说明

### kingdee_cloud_v7.py
金蝶云专业版API集成核心模块，包含：
- `KingdeeCloudV7`: 金蝶云API封装类
  - `login()`: 登录认证
  - `save_inbound()`: 保存入库单
  - `save_outbound()`: 保存出库单
- `parse_ocr_to_kingdee()`: OCR文本解析为金蝶格式

### kingdee_cloud_app.py
图形界面应用程序，提供：
- 金蝶云连接配置
- OCR识别配置
- 单据上传和处理
- 结果展示

### .env.kingdee_cloud
配置文件模板，包含所有必要的配置项

## 📊 支持的单据类型

### 入库单 (STK_InStock)
- 单据类型编码: `RKD01`
- 必填字段:
  - 单据号 (FBillNo)
  - 日期 (FDate)
  - 供应商 (FSupplierId)
  - 库存组织 (FStockOrgId)
  - 明细行 (FInStockEntry)

### 出库单 (SAL_OUTSTOCK)
- 单据类型编码: `CKD01`
- 必填字段:
  - 单据号 (FBillNo)
  - 日期 (FDate)
  - 客户 (FCustomerID)
  - 库存组织 (FStockOrgId)
  - 明细行 (FEntity)

## 🔑 API接口说明

### 1. 登录接口
```
POST /K3Cloud/Kingdee.BOS.WebApi.ServicesStub.AuthService.ValidateUser.common.kdsvc
```

### 2. 保存单据接口
```
POST /K3Cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc
```

## ⚙️ 自定义配置

### 修改默认组织编码
在 `kingdee_cloud_v7.py` 中修改：
```python
"FStockOrgId": {"FNumber": "100"}  # 改为您的组织编码
```

### 修改默认仓库编码
```python
"FStockId": {"FNumber": "CK01"}  # 改为您的仓库编码
```

### 修改单据类型
```python
"FBillTypeID": {"FNumber": "RKD01"}  # 改为您的单据类型编码
```

## 🐛 常见问题

### 1. 连接失败
- 检查服务器地址是否正确
- 确认网络连通性
- 验证账套ID、用户名、密码

### 2. 保存失败
- 检查必填字段是否完整
- 确认供应商/客户编码存在
- 验证物料编码存在
- 查看错误信息中的具体原因

### 3. OCR识别不准确
- 使用清晰的图片
- 确保文字方向正确
- 可以更换OCR服务（百度OCR等）

## 📝 数据映射说明

### OCR识别 → 金蝶字段映射

| OCR识别内容 | 金蝶字段 | 说明 |
|------------|---------|------|
| 单据号 | FBillNo | 可自动生成 |
| 日期 | FDate | 格式: YYYY-MM-DD |
| 供应商 | FSupplierId.FNumber | 需要编码 |
| 客户 | FCustomerID.FNumber | 需要编码 |
| 物料编码 | FMaterialId.FNumber | 必须存在 |
| 数量 | FQty | 数值 |
| 单价 | FPrice | 数值 |
| 仓库 | FStockId.FNumber | 需要编码 |

## 🔐 安全建议

1. **不要在代码中硬编码密码**
2. **使用环境变量或配置文件存储敏感信息**
3. **定期更换API密钥**
4. **限制API访问权限**

## 📞 技术支持

如有问题，请检查：
1. 金蝶云版本是否匹配
2. API接口是否启用
3. 用户权限是否足够
4. 网络连接是否正常

## 🎯 下一步优化

- [ ] 支持批量导入
- [ ] 添加审核功能
- [ ] 支持更多单据类型
- [ ] 增加数据验证
- [ ] 添加日志记录
