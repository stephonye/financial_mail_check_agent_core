# AWS Bedrock AgentCore Gateway 配置指南

## 部署状态总结

✅ **Memory组件部署完成**
- CustomerSupportMemory-Aw12Z7FdL6 (ACTIVE)
- SessionSummaryMemory-4Ms5DT3HVO (ACTIVE)

📋 **Gateway配置说明**
Bedrock AgentCore的Gateway组件需要通过AWS Management Console进行配置。

## Gateway配置步骤

### 1. 访问AWS Management Console
1. 登录AWS Management Console
2. 导航到Bedrock服务
3. 选择"Agent Core"选项卡

### 2. 创建Gateway配置
1. 在Agent Core控制台中，找到"Gateways"部分
2. 点击"Create Gateway"
3. 配置Gateway参数：
   - **名称**: CustomerSupportGateway
   - **描述**: Gateway for customer support agent
   - **类型**: HTTP Gateway
   - **端点**: /customer-support
   - **超时**: 30秒
   - **速率限制**: 100请求/分钟

### 3. 配置安全设置
1. **认证方式**: 
   - 选择IAM认证（推荐）
   - 或配置API Key认证
2. **网络配置**:
   - VPC设置（如果需要）
   - 安全组配置
3. **访问控制**:
   - 配置IAM策略
   - 设置访问权限

### 4. 测试Gateway连接
配置完成后，可以使用以下方式测试Gateway：

```bash
# 测试Gateway健康检查
curl -X GET https://your-gateway-endpoint/health

# 测试Agent调用
curl -X POST https://your-gateway-endpoint/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "测试请求"}'
```

## Memory组件使用指南

### 1. 基础Memory使用
```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-west-2")

# 存储数据
client.put_memory_record(
    memory_id="CustomerSupportMemory-Aw12Z7FdL6",
    record={
        "key": "user_preference",
        "value": {"language": "zh-CN", "timezone": "Asia/Shanghai"}
    }
)

# 检索数据
records = client.get_memory_record(
    memory_id="CustomerSupportMemory-Aw12Z7FdL6",
    key="user_preference"
)
```

### 2. 会话摘要Memory使用
```python
# 存储会话摘要
client.put_memory_record(
    memory_id="SessionSummaryMemory-4Ms5DT3HVO",
    record={
        "key": "session_123_summary",
        "value": {
            "session_id": "session_123",
            "summary": "用户询问了财务邮件处理相关的问题",
            "key_points": ["发票处理", "汇率转换", "数据存储"],
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
)
```

## 部署验证

### 1. 验证Memory组件
```bash
python3 check_deployment_status.py --region us-west-2
```

### 2. 验证Agent运行时
```bash
# 检查Agent状态
aws bedrock-agent get-agent --agent-id customer_support-vZmDFmAIuL --region us-west-2

# 测试Agent调用
aws bedrock-agent invoke-agent \
  --agent-id customer_support-vZmDFmAIuL \
  --agent-alias-id TSTALIASID \
  --session-id test-session \
  --text "测试Agent功能" \
  --region us-west-2
```

## 监控和维护

### 1. CloudWatch监控
- 监控Memory使用情况
- 跟踪Gateway请求指标
- 设置告警规则

### 2. 日志查看
```bash
# 查看Agent Core日志
aws logs tail /aws/bedrock/agent/core --region us-west-2

# 查看Memory操作日志
aws logs tail /aws/bedrock/agent/core/memory --region us-west-2
```

## 故障排除

### 常见问题
1. **Memory访问失败**
   - 检查IAM权限
   - 验证Memory ID是否正确
   - 确认区域设置

2. **Gateway连接问题**
   - 检查网络配置
   - 验证认证设置
   - 确认安全组规则

3. **Agent调用失败**
   - 检查Agent状态
   - 验证输入格式
   - 确认会话配置

## 下一步

1. 配置Gateway端点（通过AWS控制台）
2. 测试完整的Agent功能
3. 配置监控和告警
4. 部署到生产环境

---

**注意**: Gateway配置需要通过AWS Management Console完成，具体步骤可能因AWS控制台界面更新而有所变化。