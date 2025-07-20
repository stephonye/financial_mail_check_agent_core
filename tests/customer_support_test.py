import json

import boto3

input_text = '{"prompt": "WHAT ARE THE ORDERS FOR CUSTOMER ID 123?"}'

agent_core_client = boto3.client('bedrock-agentcore', region_name="us-west-2")

response = agent_core_client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-west-2:xxx:runtime/customer_support-66NzMPH3ic",
    qualifier="myendpoint",
    payload=input_text
)
response_body = response['response'].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)