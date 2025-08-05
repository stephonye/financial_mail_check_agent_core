# AWS Agent Core - Customer Support Assistant

基于AWS Bedrock AgentCore构建的智能客服助手项目，演示如何使用AWS Bedrock AgentCore SDK创建和部署AI助手。

## 项目概述

本项目实现了一个功能完整的客服助手，能够：
- 根据客户邮箱查询客户信息
- 查询订单详情和历史记录
- 提供产品知识库信息
- 使用Amazon Titan等Foundation Models提供智能对话

## 主要功能

### 🔧 核心工具
- **客户信息查询** - 通过邮箱地址获取客户ID
- **订单管理** - 查询客户订单详情和历史
- **知识库搜索** - 提供产品相关信息和使用指南
- **计算器工具** - 支持基础数学计算
- **时间查询** - 获取当前时间信息

### 🚀 部署方式
- **本地开发模式** - 快速本地测试和开发
- **AWS云端部署** - 基于CodeBuild的自动化部署
- **容器化支持** - Docker容器化部署

## 环境要求

- **Python 3.8+** - 主要开发语言
- **AWS CLI** - AWS服务访问工具 (可通过 `brew install awscli` 安装)
- **AWS账户及凭证** - 需要有效的AWS凭证配置
- **uv** - Python包管理工具 (可选，也可使用pip)
- **Docker** - 容器化部署 (可选，仅云端部署时需要)

## 快速开始

### 1. 环境设置

```bash
# 创建并激活虚拟环境
uv venv
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

### 1.5. 配置AWS CLI

#### **前置要求：安装AWS CLI**

首先确保您的系统已安装AWS CLI：

**macOS (推荐使用Homebrew):**
```bash
# 安装Homebrew (如果还没有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装AWS CLI
brew install awscli

# 验证安装
aws --version
```

**其他平台:**
```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows (使用PowerShell)
# 下载安装程序：https://awscli.amazonaws.com/AWSCLIV2.msi
```

#### **推荐方式：AWS SSO (IAM Identity Center)**

如果您的组织使用AWS SSO，推荐使用以下方式配置：

```bash
# 配置AWS SSO
aws configure sso

# 按提示输入以下信息：
# SSO session name: bedrock-agentcore (或任意名称)
# SSO start URL: https://your-sso-url.awsapps.com/start/#
# SSO region: us-east-1
# SSO registration scopes: [直接按Enter使用默认]
```

配置完成后，验证凭证：
```bash
# 使用返回的profile名称测试
aws sts get-caller-identity --profile YourProfileName-AccountId

# 设置为默认profile
export AWS_PROFILE=YourProfileName-AccountId
```

#### **传统方式：访问密钥**

如果使用永久访问密钥：
```bash
aws configure
# AWS Access Key ID: 您的访问密钥ID
# AWS Secret Access Key: 您的私有访问密钥
# Default region: us-east-1
# Default output format: json
```

#### **重要说明**
- ⚠️ **避免使用临时凭证** - 以`ASIA`开头的访问密钥需要额外的session token
- ✅ **推荐SSO** - 更安全，自动刷新，权限管理更便捷
- 🔑 **权限要求** - 确保您的IAM用户/角色具有必要权限（见下方权限部分）

### 2. 本地运行

```bash
# 本地模式启动 (推荐用于开发)
agentcore launch --local

# 访问 http://localhost:8080 测试Agent
```

### 3. 云端部署

```bash
# 部署到AWS Bedrock AgentCore
agentcore launch
```

### 4. 测试Agent

```bash
# 命令行测试
agentcore invoke '{"prompt": "Hello, I need help with my order for me@example.net"}'
```

## 配置说明

### AWS权限要求

确保您的AWS账户具有以下权限：

#### **必需权限**
- **Amazon Bedrock模型访问权限** - 在Bedrock控制台启用Titan模型
- **Bedrock AgentCore权限** - `bedrock-agentcore:*`
- **IAM角色管理权限** - `iam:GetRole`, `iam:PassRole`, `iam:CreateRole`
- **ECR仓库权限** - 容器镜像存储和访问
- **CodeBuild执行权限** - 云端部署构建

#### **推荐的IAM策略**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:*",
                "bedrock-agentcore:*",
                "iam:GetRole",
                "iam:PassRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "ecr:*",
                "codebuild:*",
                "logs:*"
            ],
            "Resource": "*"
        }
    ]
}
```

#### **SSO用户建议**
如果使用AWS SSO，推荐使用 **PowerUserAccess** 权限集，或联系管理员创建包含上述权限的自定义权限集。

### 配置文件

项目配置文件 `.bedrock_agentcore.yaml` 包含：
- Agent配置信息
- AWS资源设置
- 部署参数

## 项目结构

```
aws_agent_core/
├── customer_support.py        # 主要Agent实现
├── .bedrock_agentcore.yaml   # AgentCore配置
├── Dockerfile                # Docker容器配置
├── requirements.txt          # Python依赖
├── memory_examples/          # 内存管理示例
├── tests/                    # 测试文件
└── policies/                 # AWS策略文件
```

## 最新更新

### v1.0.0 (2025-08-03)

**功能增强：**
- ✅ 修复了Dockerfile在CodeBuild中的访问问题
- ✅ 解决了ECR权限配置问题  
- ✅ 更新了IAM角色信任策略以支持Bedrock AgentCore
- ✅ 切换到Amazon Titan模型以避免地区限制
- ✅ 优化了Docker构建配置和.dockerignore设置

**技术改进：**
- 更新了执行角色权限配置
- 优化了本地开发和云端部署流程
- 改进了错误处理和日志记录
- 增强了容器化部署稳定性

**已知问题解决：**
- 修复了"Dockerfile not found"错误
- 解决了ECR推送权限问题
- 修复了模型访问权限问题
- 优化了Agent部署流程

## 故障排除

### 常见问题

### **AWS凭证相关问题**

1. **❌ No AWS credentials found**
   - **原因**: 未配置AWS凭证
   - **解决**: 按照上方"配置AWS CLI"部分进行配置
   - **验证**: `aws sts get-caller-identity`

2. **❌ InvalidClientTokenId: The security token included in the request is invalid**
   - **原因**: 凭证输入错误或使用了不完整的临时凭证
   - **解决**: 
     - 检查Access Key ID和Secret Access Key是否完整正确
     - 如果使用临时凭证(以ASIA开头)，需要额外提供session token
     - 推荐改用AWS SSO配置

3. **❌ Token has expired and refresh failed**
   - **原因**: AWS SSO会话已过期，需要重新登录
   - **解决**: 使用以下命令重新登录SSO
     ```bash
     aws sso login --profile YourProfileName-AccountId
     
     # 示例：
     aws sso login --profile PowerUserAccess-211125355591
     ```
   - **说明**: 命令会自动打开浏览器，在AWS SSO页面重新授权即可
   - **验证**: 重新登录后再次尝试 `agentcore invoke` 命令

4. **❌ AccessDenied: User is not authorized to perform iam:GetRole**
   - **原因**: IAM权限不足
   - **解决**: 联系AWS管理员为您的用户/角色添加以下权限：
     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Effect": "Allow",
                 "Action": [
                     "iam:GetRole",
                     "iam:PassRole",
                     "iam:CreateRole",
                     "iam:AttachRolePolicy",
                     "bedrock:*",
                     "bedrock-agentcore:*"
                 ],
                 "Resource": "*"
             }
         ]
     }
     ```

5. **❌ RuntimeClientError (500): 执行角色权限不足**
   - **现象**: 直接调用`aws bedrock-runtime invoke-model`成功，但`agentcore invoke`失败
   - **原因**: AgentCore使用的执行角色缺少Bedrock调用权限
   - **解决**: 联系管理员为配置文件中的`execution_role`添加以下权限：
     ```json
     {
         "Version": "2012-10-17", 
         "Statement": [
             {
                 "Effect": "Allow",
                 "Action": [
                     "bedrock:InvokeModel",
                     "bedrock:InvokeModelWithResponseStream"
                 ],
                 "Resource": "arn:aws:bedrock:*::foundation-model/*"
             }
         ]
     }
     ```
   - **临时方案**: 使用本地模式 `agentcore launch --local`

### **Bedrock和模型相关问题**

1. **Bedrock访问被拒绝**
   - 确保在AWS控制台启用了Bedrock模型访问权限
   - 检查IAM角色是否有足够权限
   - 确认在正确的AWS区域(us-east-1)

### **部署相关问题**

2. **CodeBuild部署失败**
   - 验证ECR仓库权限
   - 检查Dockerfile是否在.dockerignore中被排除

3. **本地运行错误**
   - 确保虚拟环境已激活
   - 验证所有依赖已正确安装

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目基于MIT许可证开源。

## 联系方式

如有问题，请通过GitHub Issues联系。
