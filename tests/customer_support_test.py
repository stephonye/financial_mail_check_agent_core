'''
Descripttion: ****
version: 1.0.0
Author: Tom Zhou
Date: 2025-08-02 22:49:16
LastEditors: Tom Zhou
LastEditTime: 2025-08-03 14:31:38
'''
import json

import boto3

input_text = '{"prompt": "WHAT ARE THE ORDERS FOR CUSTOMER ID 123?"}'

agent_core_client = boto3.client('bedrock-agentcore', region_name="us-east-1")

# response = agent_core_client.invoke_agent_runtime(
#     agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:211125355591:runtime/customer_support-66NzMPH3ic",
#     qualifier="myendpoint",
#     payload=input_text
# )

response = agent_core_client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:211125355591:runtime/customer_support_1-erOKi4CEVs",
    qualifier="myendpoint",
    payload=input_text
)
response_body = response['response'].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)