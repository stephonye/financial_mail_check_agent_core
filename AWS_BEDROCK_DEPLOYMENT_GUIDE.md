# AWS Bedrock AgentCore 部署和测试指南

## 部署方式概述

本项目支持多种部署方式，从本地开发到生产环境部署：

### 1. 本地开发模式 (推荐用于开发测试)
```bash
# 快速启动本地开发环境
agentcore launch --local

# 启用热重载功能
agentcore launch --local --hot-reload

# 指定端口和调试模式
agentcore launch --local --port 8080 --debug
```

### 2. 云端部署模式 (生产环境)
```bash
# 部署到AWS Bedrock AgentCore
agentcore launch

# 指定环境配置
agentcore launch --env production

# 蓝绿部署策略
agentcore launch --strategy blue-green
```

### 3. Docker容器部署
```bash
# 本地构建和测试Docker镜像
docker build -t financial-email-processor .
docker run -p 8080:8080 financial-email-processor

# 使用Docker Compose启动完整环境
docker-compose up -d
```

## 部署前置要求

### AWS账户配置
```bash
# 配置AWS CLI (推荐SSO方式)
aws configure sso

# 验证AWS凭证
aws sts get-caller-identity

# 检查Bedrock访问权限
aws bedrock list-foundation-models --region us-east-1
```

### 必需IAM权限
确保您的IAM用户/角色具有以下权限：
- `bedrock-agentcore:*`
- `codebuild:*` 
- `ecr:*`
- `iam:CreateRole`, `iam:PassRole`, `iam:GetRole`
- `logs:*`
- `s3:*` (用于CodeBuild源存储)

## 配置文件设置

### 1. 使用配置模板
```bash
# 复制模板配置文件
cp .bedrock_agentcore.yaml.template .bedrock_agentcore.yaml

# 编辑配置文件，替换所有占位符
vim .bedrock_agentcore.yaml
```

### 2. 关键配置项
需要更新的配置项：
- `aws.account`: 您的AWS账户ID
- `aws.execution_role`: IAM执行角色ARN
- `aws.ecr_repository`: ECR仓库地址
- `aws.region`: AWS区域
- `bedrock_agentcore.agent_id`: Agent ID
- `codebuild.execution_role`: CodeBuild执行角色

### 3. 环境变量配置
在AWS控制台或配置文件中设置：
```yaml
environment_variables:
  - name: AWS_REGION
    value: us-east-1
  - name: LOG_LEVEL
    value: INFO
  - name: MCP_ENABLED
    value: "false"
```

## 测试方法

### 1. 本地功能测试
```bash
# 测试Agent基础功能
agentcore invoke '{"prompt": "测试健康检查"}'

# 测试邮件处理功能
agentcore invoke '{"prompt": "请搜索并处理我的财务邮件"}'

# 测试汇率转换功能
agentcore invoke '{"prompt": "将100欧元转换为美元"}'

# 测试数据库查询
agentcore invoke '{"prompt": "显示所有发票记录"}'
```

### 2. HTTP接口测试
```bash
# 健康检查
curl http://localhost:8080/health

# 就绪检查
curl http://localhost:8080/ready

# 调用Agent接口
curl -X POST http://localhost:8080/2024-01-01/runtime/invoke \
  -H "Content-Type: application/json" \
  -d '{"prompt": "处理财务邮件"}'
```

### 3. 集成测试
```bash
# 测试完整的邮件处理流程
agentcore invoke '{"prompt": "搜索Gmail中的发票邮件，提取信息并保存到数据库"}'

# 测试统计查询功能
agentcore invoke '{"prompt": "显示本月财务邮件统计信息"}'

# 测试多币种处理
agentcore invoke '{"prompt": "处理所有包含外币金额的邮件"}'
```

### 4. 性能测试
```bash
# 查看性能指标
agentcore metrics

# 查看资源使用情况
agentcore metrics --resource-utilization

# 压力测试 (使用多个并发请求)
for i in {1..10}; do
  agentcore invoke '{"prompt": "测试请求 $i"}' &
done
```

## 监控和日志

### CloudWatch监控
```bash
# 实时查看日志
agentcore logs --follow

# 查看特定时间段的日志
agentcore logs --start-time "2024-01-01T00:00:00" --end-time "2024-01-01T23:59:59"

# 查看构建日志
agentcore logs --build

# 查看错误日志
agentcore logs --level ERROR
```

### 自定义监控指标
```bash
# 查看请求统计
agentcore metrics --requests

# 查看延迟指标
agentcore metrics --latency

# 查看错误率
agentcore metrics --error-rate
```

## 故障排除指南

### 常见问题及解决方案

1. **权限错误**
   ```bash
   # 检查IAM角色权限
   aws iam get-role --role-name AmazonBedrockAgentCoreExecutionRole
   
   # 验证Bedrock访问权限
   aws bedrock list-foundation-models --region us-east-1
   ```

2. **构建失败**
   ```bash
   # 查看详细构建日志
   agentcore logs --build --verbose
   
   # 检查Dockerfile配置
   docker build --no-cache -t test-build .
   ```

3. **容器启动失败**
   ```bash
   # 查看容器日志
   docker logs <container_id>
   
   # 检查端口冲突
   lsof -i :8080
   ```

4. **网络连接问题**
   ```bash
   # 测试网络连通性
   curl -v http://localhost:8080/health
   
   # 检查防火墙设置
   sudo ufw status
   ```

### 调试模式
```bash
# 启用详细调试日志
export LOG_LEVEL=DEBUG

# 使用调试模式部署
agentcore launch --debug --verbose

# 进入容器进行调试
docker exec -it <container_id> bash
```

## 自动化部署

### GitHub Actions自动化
创建 `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS Bedrock AgentCore

on:
  push:
    branches: [main]
    
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
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install bedrock-agentcore
        pip install -r requirements.txt
    
    - name: Deploy to Bedrock AgentCore
      run: agentcore launch
```

### 本地部署脚本
使用 `deploy.sh` 进行一键部署：
```bash
#!/bin/bash

# 部署脚本
echo "🚀 开始部署到AWS Bedrock AgentCore..."

# 检查前置条件
if ! command -v agentcore &> /dev/null; then
    echo "❌ 请先安装bedrock-agentcore: pip install bedrock-agentcore"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS凭证未配置，请运行: aws configure"
    exit 1
fi

# 执行部署
echo "📦 构建和部署中..."
if agentcore launch; then
    echo "✅ 部署成功！"
    echo "📊 查看状态: agentcore status"
    echo "📝 查看日志: agentcore logs --follow"
else
    echo "❌ 部署失败"
    exit 1
fi
```

## 最佳实践

### 安全实践
1. 使用IAM角色而不是访问密钥
2. 启用VPC网络隔离
3. 定期轮转凭据
4. 启用CloudTrail日志记录
5. 使用AWS Secrets Manager管理敏感信息

### 性能优化
```yaml
# 资源配置优化
resources:
  cpu: 1024
  memory: 2048
  ephemeral_storage: 20

# 自动缩放配置
scaling:
  min_capacity: 1
  max_capacity: 5
  target_cpu_utilization: 70
```

### 成本控制
1. 设置适当的资源限制
2. 启用自动缩放
3. 监控CloudWatch费用
4. 使用预留实例折扣

## 支持资源

- [AWS Bedrock AgentCore官方文档](https://docs.aws.amazon.com/bedrock/latest/agentcoreguide/)
- [AWS开发者论坛](https://forums.aws.amazon.com/)
- [GitHub Issues](https://github.com/your-repo/issues)
- [AWS支持中心](https://aws.amazon.com/support/)

---

**注意**: 部署前请确保已正确配置所有AWS凭证和权限，并仔细检查配置文件中的占位符是否已替换为实际值。