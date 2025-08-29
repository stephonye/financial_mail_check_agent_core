# LLM增强功能说明

## 概述

本项目已成功集成LLM（大型语言模型）增强功能，为财务邮件处理提供了更智能的分析能力。LLM增强功能包括：

### 🎯 主要改进

1. **智能邮件内容分析** - 使用Amazon Bedrock LLM深度解析邮件内容
2. **结构化信息提取** - 自动提取复杂的财务信息
3. **异常检测** - 识别可疑或异常的财务信息
4. **多级回退机制** - 确保系统在各种情况下都能正常工作

## 新增文件

### 1. `llm_email_analyzer.py`
核心LLM分析器，提供以下功能：
- `LLMEmailAnalyzer` 类：主要的LLM分析引擎
- `analyze_email_content_llm()` 函数：便捷的LLM分析接口
- 多级回退机制：LLM → 规则分析 → 简单分析

### 2. 集成修改
- `email_processor.py`：自动集成LLM分析到邮件处理流程
- `customer_support.py`：添加LLM分析工具函数
- `test_llm_enhancement.py`：LLM功能测试脚本

## 功能特性

### 🔧 LLM分析能力

```python
# 使用LLM分析邮件
analyzer = LLMEmailAnalyzer()
result = analyzer.analyze_email_with_llm(subject, body, email_type)
```

**提取的信息包括：**
- 文档类型识别 (invoice/order/statement/payment/receipt)
- 交易状态分析 (收款/付款/完成付款/待处理)
- 交易对手方识别
- 金额和币种提取
- 日期信息提取 (签发日期、到期日期)
- 异常检测
- 置信度评分

### 🛡️ 回退机制

系统采用三级回退策略：
1. **LLM分析** (首选) - 使用Amazon Bedrock进行智能分析
2. **规则分析** (次要) - 使用原有的正则表达式规则
3. **简单分析** (保底) - 基础的关键词匹配和金额提取

### 📊 分析结果格式

```json
{
  "document_type": "invoice",
  "status": "收款",
  "counterparty": "Amazon Web Services",
  "amount": 347.35,
  "currency": "USD",
  "usd_amount": 347.35,
  "exchange_rate": 1.0,
  "issue_date": "2024-01-15",
  "due_date": "2024-02-15",
  "confidence": 0.85,
  "anomalies": [],
  "analysis_method": "llm"
}
```

## 使用方法

### 1. 直接调用LLM分析

```python
from llm_email_analyzer import analyze_email_content_llm

result = analyze_email_content_llm(
    "Invoice from Amazon Web Services",
    "Invoice details: $245.67 due on 2024-02-15",
    "invoice"
)
```

### 2. 集成到邮件处理流程

LLM分析已自动集成到现有的邮件处理流程中。在 `email_processor.py` 中：

```python
# 自动使用LLM分析财务信息
def _extract_financial_info(self, subject: str, body: str):
    # 首先尝试LLM分析
    llm_result = self._analyze_with_llm(subject, body)
    
    # 如果LLM置信度高，使用LLM结果
    if llm_result.get('confidence', 0) > 0.7:
        return self._format_llm_result(llm_result, subject)
    
    # 否则使用规则分析
    return self._extract_with_rules(subject, body)
```

### 3. 通过Agent工具调用

在Agent对话中可以直接使用LLM分析工具：

```bash
# 使用LLM分析特定邮件内容
agentcore invoke '{"prompt": "请分析这个邮件: 主题: Invoice from AWS, 内容: 金额$245.67 due on Feb 15"}'
```

## 配置要求

### AWS Bedrock配置

确保您的AWS账户已正确配置Bedrock服务：

1. **启用Bedrock模型访问**：在AWS控制台启用所需模型
2. **配置执行角色权限**：确保执行角色有Bedrock调用权限
3. **模型可用性**：检查 `amazon.nova-pro-v1:0` 或其他指定模型的可用性

### 错误处理

如果遇到模型调用错误，系统会自动回退到规则分析：

```
# 常见错误：
- "Invocation of model ID ... isn't supported"：模型配置问题
- "AccessDenied"：权限不足
- "ModelNotAvailable"：模型不可用
```

## 测试验证

运行测试脚本验证LLM功能：

```bash
python test_llm_enhancement.py
```

测试内容包括：
- LLM分析器基本功能
- 直接函数调用
- 回退机制验证
- 多种邮件类型测试

## 性能考虑

### 优点
- ✅ 更准确的复杂信息提取
- ✅ 更好的异常检测能力
- ✅ 支持非结构化文本分析
- ✅ 自动学习新的邮件格式

### 注意事项
- ⚠️ LLM调用有额外延迟
- ⚠️ 需要稳定的网络连接
- ⚠️ 可能产生AWS费用
- ⚠️ 依赖AWS服务可用性

## 故障排除

### 常见问题

1. **LLM调用失败**
   - 检查AWS凭证配置
   - 验证Bedrock模型访问权限
   - 确认执行角色有足够权限

2. **分析结果不准确**
   - 调整置信度阈值
   - 优化提示词模板
   - 增加训练数据多样性

3. **性能问题**
   - 启用缓存机制
   - 批量处理邮件
   - 使用更小的模型（如果可用）

## 后续优化建议

1. **模型微调**：针对财务邮件领域微调LLM
2. **缓存优化**：实现分析结果缓存
3. **批量处理**：支持批量邮件分析
4. **自定义模型**：部署领域特定模型
5. **性能监控**：添加LLM调用性能监控

## 支持

如有LLM增强功能相关问题，请参考：
- [AWS Bedrock文档](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents文档](https://docs.strands.ag/)
- 项目GitHub Issues

享受更智能的财务邮件处理体验！🚀