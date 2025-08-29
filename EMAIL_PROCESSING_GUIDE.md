# Gmail邮件处理功能使用指南

## 功能概述

本功能扩展了原有的客服助手，增加了Gmail邮件处理能力，能够：

1. 🔍 **搜索财务邮件** - 自动搜索标题包含 invoice、order、statement 的邮件
2. 📊 **解析财务信息** - 识别收款/付款状态、金额、币种、日期等信息
3. 💾 **导出JSON数据** - 将解析结果保存为结构化JSON格式
4. 📈 **生成统计摘要** - 提供邮件数量和金额统计

## 安装依赖

```bash
# 安装新增的Python依赖
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4 lxml requests psycopg2-binary python-dotenv

# 或者使用uv安装
uv pip install -r requirements.txt
```

## Gmail API配置

### 1. 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Gmail API

### 2. 配置OAuth 2.0凭据

1. 在左侧菜单选择 "API和服务" > "凭据"
2. 点击 "创建凭据" > "OAuth 2.0客户端ID"
3. 选择应用类型为 "桌面应用"
4. 下载凭据文件
5. 将文件重命名为 `credentials.json` 并放置在项目根目录

### 3. 首次运行认证

首次运行时会自动打开浏览器进行OAuth认证：

```bash
# 运行邮件处理测试
python email_processor.py
```

按照提示完成Google账户授权，系统会自动生成 `token.json` 文件存储访问令牌。

## 功能使用

### 通过Agent工具调用

```bash
# 调用邮件处理功能
agentcore invoke '{"prompt": "请处理我的财务邮件"}'

# 获取邮件统计摘要  
agentcore invoke '{"prompt": "显示财务邮件统计信息"}'
```

### 直接Python调用

```python
from email_processor import process_financial_emails

# 处理财务邮件
result = process_financial_emails()
print(f"找到 {len(result)} 封财务邮件")
```

## 输出格式

处理后的数据保存为 `financial_emails.json`，格式如下：

```json
[
  {
    "id": "邮件ID",
    "subject": "邮件主题",
    "from": "发件人",
    "date": "发送日期",
    "body_preview": "邮件内容预览",
    "financial_info": {
      "type": "invoice/order/statement",
      "status": "收款/付款/完成付款/其他",
      "counterparty": "交易对手",
      "amount": 100.0,
      "currency": "USD",
      "dates": {
        "due_date": "2024-12-31",
        "issue_date": "2024-12-01"
      },
      "subject": "原始邮件主题"
    }
  }
]
```

## 状态识别规则

- **收款**: 包含 "payment received", "paid in full" 等短语
- **付款**: 包含 "payment due", "please pay", "amount due" 等短语  
- **完成付款**: 包含 "make payment", "pay now", "payment required" 等短语
- **其他**: 不符合以上条件的邮件

## 故障排除

### 常见问题

1. **认证错误**
   - 确保 `credentials.json` 文件正确配置
   - 删除 `token.json` 重新认证

2. **权限不足**
   - 检查Gmail API是否已启用
   - 确认OAuth范围包含 `gmail.readonly`

3. **依赖缺失**
   - 运行 `pip install -r requirements.txt` 安装所有依赖

### 调试模式

如需调试，可以修改 `email_processor.py` 中的日志级别：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 安全注意事项

- 🔒 `credentials.json` 包含敏感信息，不要提交到版本控制
- 🔒 `token.json` 包含访问令牌，同样需要保护
- 📧 只请求了 `gmail.readonly` 权限，无法修改邮件
- 🗑️ 定期清理不再需要的令牌文件

## 汇率转换功能

### 配置汇率API

1. **免费API**: 系统默认使用免费的Frankfurter API
2. **付费API**: 如需更稳定的服务，可注册 [exchangerate-api.com](https://www.exchangerate-api.com/)
3. **API密钥**: 在 `.env` 文件中设置 `EXCHANGE_RATE_API_KEY=your_key_here`

### 支持的币种

- ✅ USD (美元) - 基准货币
- ✅ EUR (欧元)
- ✅ GBP (英镑) 
- ✅ JPY (日元)
- ✅ CNY (人民币)
- ✅ CAD (加元)
- ✅ AUD (澳元)
- ✅ 其他主要货币

## PostgreSQL数据库配置

### 1. 安装PostgreSQL

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# 下载安装包: https://www.postgresql.org/download/windows/
```

### 2. 创建数据库

```sql
CREATE DATABASE financial_emails_db;
CREATE USER financial_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE financial_emails_db TO financial_user;
```

### 3. 环境变量配置

创建 `.env` 文件：

```env
# 直接连接配置
DATABASE_URL=postgresql://financial_user:your_password@localhost:5432/financial_emails_db

# MCP连接配置 (可选)
MCP_DATABASE_URL=postgresql://financial_user:your_password@mcp-server:5432/financial_emails_db
MCP_SERVER_URL=http://localhost:8000
MCP_ENABLED=false

EXCHANGE_RATE_API_KEY=your_exchangerate_api_key_here
```

### 4. MCP配置

要启用MCP连接：

1. **设置MCP服务器**: 确保MCP服务器运行并配置好数据库连接
2. **启用MCP**: 在 `.env` 中设置 `MCP_ENABLED=true`
3. **配置MCP URL**: 设置 `MCP_SERVER_URL` 和 `MCP_DATABASE_URL`

### 5. 自动建表

在直接连接模式下，首次运行时系统会自动创建所需的数据表结构。
在MCP模式下，表结构由MCP服务器管理。

## 数据库查询功能

### 通过Agent工具查询

```bash
# 查询所有财务邮件
agentcore invoke '{"prompt": "查询财务邮件记录"}'

# 按类型查询
agentcore invoke '{"prompt": "查询所有发票记录"}'

# 按状态查询  
agentcore invoke '{"prompt": "查询待付款的订单"}'

# 获取统计摘要
agentcore invoke '{"prompt": "显示财务统计信息"}'
```

### 直接数据库访问

```python
from database_service import DatabaseService

# 查询数据
db_service = DatabaseService()
emails = db_service.get_financial_emails(10)
stats = db_service.get_summary_stats()

print(f"总记录数: {stats['total_records']}")
print(f"USD总金额: ${stats['total_usd_amount']:.2f}")
```

## 扩展开发

如需自定义解析规则，可以修改以下函数：

- `_extract_financial_info()` - 财务信息提取逻辑
- `_identify_status()` - 状态识别规则  
- `_extract_amount_and_currency()` - 金额和币种提取
- `_extract_dates()` - 日期信息提取
- `ExchangeRateService` - 汇率服务配置
- `DatabaseService` - 数据库模式设计

欢迎提交改进建议和Pull Request！