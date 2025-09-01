# AWS Bedrock AgentCore 完整部署指南

本指南提供了在AWS Bedrock AgentCore上部署财务邮件处理器应用的详细步骤。

## 目录
1. [系统架构](#系统架构)
2. [前置要求](#前置要求)
3. [环境准备](#环境准备)
4. [本地开发和测试](#本地开发和测试)
5. [AWS部署配置](#aws部署配置)
6. [部署到AWS Bedrock AgentCore](#部署到aws-bedrock-agentcore)
7. [配置和集成](#配置和集成)
8. [监控和日志](#监控和日志)
9. [故障排除](#故障排除)
10. [安全最佳实践](#安全最佳实践)

## 系统架构

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

## 环境准备

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

## 本地开发和测试

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

### 4. 本地运行测试
```bash
# 本地运行测试
agentcore launch --local

# 测试Agent功能
agentcore invoke '{"prompt": "测试连接"}'
```

## AWS部署配置

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

### 2. 环境变量配置

在AWS管理控制台中配置环境变量：

```bash
# 必需的环境变量
AWS_REGION=us-east-1

# 可选的环境变量  
MCP_ENABLED=false
LOG_LEVEL=INFO
```

## 部署到AWS Bedrock AgentCore

### 1. 构建Docker镜像

```bash
# 本地构建测试
docker build -t financial-email-processor .

# 运行测试容器
docker run -p 8080:8080 financial-email-processor
```

### 2. 部署到AWS

```bash
# 部署到Bedrock AgentCore
agentcore launch

# 查看部署状态
agentcore status

# 查看日志
agentcore logs
```

### 3. 部署模式

#### 开发模式

```bash
# 本地开发模式（快速迭代）
agentcore launch --local --hot-reload
```

#### 生产模式

```bash
# 生产环境部署
agentcore launch --env production
```

#### 蓝绿部署

```bash
# 蓝绿部署（零停机）
agentcore launch --strategy blue-green
```

## 配置和集成

### 1. 创建执行角色

```bash
# 创建信任策略文件
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 创建角色
aws iam create-role \
  --role-name AmazonBedrockAgentCoreExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# 附加必要策略
aws iam attach-role-policy \
  --role-name AmazonBedrockAgentCoreExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
  --role-name AmazonBedrockAgentCoreExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

### 2. 配置Bedrock模型访问

确保您的AWS账户具有Amazon Nova Pro模型的访问权限：

```bash
# 检查可用的Bedrock模型
aws bedrock list-foundation-models --query 'modelSummaries[?modelName.contains(`Nova`)]'
```

### 3. 配置安全组和网络

如果使用AWS RDS数据库，请确保配置适当的安全组规则以允许来自Bedrock AgentCore的连接。

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

### 凭证安全

我们的应用使用凭证管理器来安全存储敏感信息：

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

## 支持的联系方式

如有部署问题，请参考：
- [AWS Bedrock AgentCore文档](https://docs.aws.amazon.com/bedrock/latest/agentcoreguide/)
- [AWS开发者论坛](https://forums.aws.amazon.com/)
- [GitHub Issues](https://github.com/your-repo/issues)

## 附录

### 环境变量参考
| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接字符串 | postgresql://user:pass@host:5432/db |
| MCP_ENABLED | 是否启用MCP连接 | true/false |
| EXCHANGE_API_KEY | 汇率API密钥 | your_api_key |

### IAM策略参考
确保执行角色具有以下权限:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket/*",
                "arn:aws:s3:::your-bucket"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

本部署指南提供了在AWS Bedrock AgentCore上部署财务邮件处理器应用的完整指南。按照这些步骤，您应该能够成功部署和运行应用。