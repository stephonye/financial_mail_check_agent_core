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

- Python 3.8+
- uv (Python包管理工具)
- AWS CLI 配置
- Docker (可选，用于容器化部署)

## 快速开始

### 1. 环境设置

```bash
# 创建并激活虚拟环境
uv venv
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

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
- Amazon Bedrock模型访问权限
- IAM角色创建和管理权限
- ECR仓库权限
- CodeBuild执行权限

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

1. **Bedrock访问被拒绝**
   - 确保在AWS控制台启用了Bedrock模型访问权限
   - 检查IAM角色是否有足够权限

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
