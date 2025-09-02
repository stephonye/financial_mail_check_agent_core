# AWS Bedrock AgentCore 部署指南

## 部署架构

本项目使用标准的AWS Bedrock AgentCore部署模式：

```
+-------------------+     +---------------------+     +-------------------+
|   AWS CodeBuild   | --> | Amazon ECR Registry | --> | Bedrock AgentCore |
+-------------------+     +---------------------+     +-------------------+
       |                         |                             |
       v                         v                             v
 源代码构建 &测试          容器镜像存储            Agent运行时环境
```

## 前置要求

### 1. AWS账户配置

```bash
# 配置AWS CLI
aws configure
# 或使用AWS SSO
aws configure sso
```

### 2. 所需IAM权限

确保您的IAM用户/角色具有以下权限：

```yaml
- bedrock-agentcore:*
- codebuild:*
- ecr:*
- iam:CreateRole
- iam:PassRole
- iam:GetRole
- logs:*
- s3:GetObject
- s3:PutObject
```

### 3. 环境准备

```bash
# 安装Bedrock AgentCore SDK
pip install bedrock-agentcore

# 验证安装
agentcore --version
```

## 本地环境设置

### 1. 克隆代码库
```bash
git clone <repository-url>
cd aws_agent_core
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 验证安装
```bash
python -c "import tool_manager; import credential_manager; print('Dependencies installed successfully')"
```

## 应用配置

### 1. Gmail API配置
#### 创建Google Cloud项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用Gmail API:
   - 导航到 "APIs & Services" > "Library"
   - 搜索 "Gmail API"
   - 点击并启用

#### 创建凭据
1. 导航到 "APIs & Services" > "Credentials"
2. 点击 "Create Credentials" > "OAuth client ID"
3. 选择应用类型为 "Desktop application"
4. 下载凭据文件并重命名为 `credentials.json`
5. 将文件放置在项目根目录

### 2. 数据库配置
#### 本地测试配置
创建 `.env` 文件:
```bash
touch .env
```

在 `.env` 文件中添加:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/financial_emails
MCP_ENABLED=false
```

#### AWS RDS配置(可选)
1. 在AWS RDS中创建PostgreSQL实例
2. 配置安全组以允许来自AgentCore的连接
3. 更新 `.env` 文件中的 `DATABASE_URL`

### 3. 汇率API配置
在 `.env` 文件中添加汇率API密钥:
```env
EXCHANGE_API_KEY=your_exchange_api_key
```

## 部署步骤

### 1. 配置部署文件

复制模板配置文件：

```bash
cp .bedrock_agentcore.yaml.template .bedrock_agentcore.yaml
```

编辑 `.bedrock_agentcore.yaml`，更新以下配置：

```yaml
aws:
  account: 'YOUR_AWS_ACCOUNT_ID'  # 替换为您的AWS账户ID
  execution_role: arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/AmazonBedrockAgentCoreExecutionRole
  ecr_repository: YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/financial-email-processor
```

### 2. 本地测试

#### 2.1. 本地运行测试
```bash
# 本地运行测试
agentcore launch --local

# 测试Agent功能
agentcore invoke '{"prompt": "测试连接"}'
```

#### 2.2. 本地API测试
```bash
# 测试健康检查端点
curl http://localhost:8080/health

# 测试就绪检查端点
curl http://localhost:8080/ready

# 测试基本功能
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how can you help me?"}'
```

#### 2.3. 凭证测试
确保Gmail认证正常工作：
```bash
# 运行应用并检查Gmail认证
python customer_support.py
```

### 3. 构建Docker镜像

```bash
# 本地构建测试
docker build -t financial-email-processor .

# 运行测试容器
docker run -p 8080:8080 financial-email-processor
```

### 4. 部署到AWS

```bash
# 部署到Bedrock AgentCore
agentcore launch

# 查看部署状态
agentcore status

# 查看日志
agentcore logs
```

### 5. 环境变量配置

在AWS管理控制台中配置环境变量：

```bash
# 必需的环境变量
AWS_REGION=us-east-1

# 可选的环境变量  
MCP_ENABLED=false
LOG_LEVEL=INFO
```

## 部署模式

### 开发模式

```bash
# 本地开发模式（快速迭代）
agentcore launch --local --hot-reload
```

### 生产模式

```bash
# 生产环境部署
agentcore launch --env production
```

### 蓝绿部署

```bash
# 蓝绿部署（零停机）
agentcore launch --strategy blue-green
```

## 监控和日志

### CloudWatch监控

```bash
# 查看CloudWatch日志
agentcore logs --follow

# 查看特定时间段的日志
agentcore logs --start-time "2024-01-01T00:00:00" --end-time "2024-01-01T23:59:59"
```

### 性能监控

```bash
# 查看性能指标
agentcore metrics

# 查看CPU和内存使用情况
agentcore metrics --resource-utilization
```

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 检查IAM角色权限
   aws iam get-role --role-name AmazonBedrockAgentCoreExecutionRole
   ```

2. **构建失败**
   ```bash
   # 查看详细构建日志
   agentcore logs --build
   ```

3. **容器启动失败**
   ```bash
   # 检查容器日志
   docker logs <container_id>
   ```

4. **工具管理器问题**
   ```bash
   # 检查工具注册状态
   python -c "from tool_manager import tool_manager; print(tool_manager.get_tool_statistics())"
   ```

5. **凭证管理问题**
   ```bash
   # 检查凭证文件
   ls -la secret.key credentials.json
   
   # 检查凭证管理器
   python -c "from credential_manager import credential_manager; print(credential_manager.list_credentials())"
   ```

6. **权限控制问题**
   ```bash
   # 检查权限配置
   cat permissions.json
   
   # 测试权限检查
   python -c "from permission_controller import permission_controller; print(permission_controller.check_user_permission('default_user', 'access_database'))"
   ```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 使用调试模式部署
agentcore launch --debug
```

## 自动化部署

### GitHub Actions

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to AWS Bedrock AgentCore

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to Bedrock AgentCore
      run: |
        pip install bedrock-agentcore
        agentcore launch
```

## 成本优化

### 资源配置

在 `.bedrock_agentcore.yaml` 中调整资源限制：

```yaml
resources:
  cpu: 1024      # 1 vCPU
  memory: 2048   # 2GB RAM
  ephemeral_storage: 20 # 20GB临时存储
```

### 自动缩放

```yaml
scaling:
  min_capacity: 1
  max_capacity: 5
  target_cpu_utilization: 70
```

## 安全最佳实践

1. **使用IAM角色而不是访问密钥**
2. **启用VPC网络隔离**
3. **定期轮转凭据**
4. **启用CloudTrail日志记录**
5. **使用AWS Secrets Manager管理敏感信息**

### 凭证安全管理

应用使用凭证管理器来安全存储敏感信息：

```python
# 凭证加密存储示例
from credential_manager import credential_manager

# 存储Gmail凭证
credential_manager.store_credential(
    "gmail_token", 
    token_json, 
    "Gmail API凭证"
)
```

### 权限控制

应用实现了基于角色的权限控制：

```python
# 权限检查示例
from permission_controller import permission_controller

# 检查用户权限
if permission_controller.check_user_permission(user_id, "access_database"):
    # 允许数据库访问
    pass
```

### 工具管理安全

所有工具都通过工具管理器注册和管理，确保只有授权的工具可以被调用：

```python
# 工具注册示例
from tool_manager import tool_manager

# 注册工具
tool_manager.register_tool(
    "process_financial_emails", 
    "1.0.0", 
    "搜索和处理Gmail中的财务邮件", 
    "邮件工具", 
    process_financial_emails_tool
)
```

## 支持的联系方式

如有部署问题，请参考：
- [AWS Bedrock AgentCore文档](https://docs.aws.amazon.com/bedrock/latest/agentcoreguide/)
- [AWS开发者论坛](https://forums.aws.amazon.com/)
- [GitHub Issues](https://github.com/your-repo/issues)