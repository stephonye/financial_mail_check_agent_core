'''
AWS Bedrock AgentCore 客服助手测试脚本
Description: 测试基于Amazon Nova Pro模型的智能客服助手
Model: amazon.nova-pro-v1:0 (Amazon Nova Pro)
Version: 1.0.0
Author: Tom Zhou
Date: 2025-08-02 22:49:16
LastEditors: Tom Zhou
LastEditTime: 2025-08-05 15:08:25

功能特性:
- 使用Amazon Nova Pro Foundation Model
- 支持系统提示 (System Messages)
- 集成客户信息查询工具
- 集成订单管理工具  
- 集成知识库搜索功能
'''
import json

import boto3

# 测试输入 - 客户订单查询请求
input_text = '{"prompt": "Hello, I need help with my order for me@example.net"}'

# 创建Bedrock AgentCore客户端
agent_core_client = boto3.client('bedrock-agentcore', region_name="us-east-1")

# 调用Agent Runtime
# Agent使用Amazon Nova Pro模型 (amazon.nova-pro-v1:0)
# 支持system messages和工具调用
response = agent_core_client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:211125355591:runtime/customer_support_1-erOKi4CEVs",
    qualifier="myendpoint",  # AgentCore端点标识符
    payload=input_text
)

response_body = response['response'].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)