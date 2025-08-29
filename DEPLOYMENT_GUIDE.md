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

```bash
# 本地运行测试
agentcore launch --local

# 测试Agent功能
agentcore invoke '{"prompt": "测试连接"}'
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

## 支持的联系方式

如有部署问题，请参考：
- [AWS Bedrock AgentCore文档](https://docs.aws.amazon.com/bedrock/latest/agentcoreguide/)
- [AWS开发者论坛](https://forums.aws.amazon.com/)
- [GitHub Issues](https://github.com/your-repo/issues)