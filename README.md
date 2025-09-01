# Financial Mail Check Agent Core

这是一个基于AWS Bedrock AgentCore的财务邮件处理系统，支持Gmail邮件处理和数据分析。

## 功能特性

- 自动搜索和处理Gmail中的财务邮件（发票、订单、对账单）
- 使用LLM增强功能深度解析邮件内容
- 实时外币到USD的汇率转换
- 将结果保存到PostgreSQL数据库（支持直接连接和MCP连接）
- 提供丰富的查询和统计分析功能

## 新增安全和管理功能

### 工具管理器
工具管理器提供标准化的工具注册和管理功能：
- 工具分类管理
- 工具启用/禁用控制
- 工具使用统计
- 工具版本管理

### 凭证管理器
凭证管理器安全地存储和管理应用凭证：
- 凭证加密存储
- 凭证生命周期管理
- 凭证访问控制

### 权限控制器
权限控制器管理应用权限和访问控制：
- 基于角色的权限控制
- 细粒度权限管理
- 权限检查和验证

## 安装依赖

```bash
pip install -r requirements.txt
pip install cryptography
```

## 配置

1. 配置Gmail API凭证
2. 配置数据库连接字符串
3. 配置汇率API密钥

## 使用方法

```bash
python customer_support.py
```

## 部署指南

有关详细的部署信息，请参阅以下文档：
- [部署指南](DEPLOYMENT_GUIDE.md) - 标准部署步骤
- [完整部署指南](COMPLETE_DEPLOYMENT_GUIDE.md) - 详细的部署说明

## 安全特性

- 所有敏感凭证都经过加密存储
- 基于角色的访问控制
- 权限验证和审计

## 改进总结

有关详细改进信息，请参阅以下文件：
- [改进总结](IMPROVEMENT_SUMMARY.md) - 所有改进的概述
- [新功能总结](NEW_FEATURES_SUMMARY.md) - 新添加功能的详细说明

## 文档

- [权限配置](permissions.json) - 应用权限配置文件