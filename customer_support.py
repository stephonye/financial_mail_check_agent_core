'''
Descripttion: ****
version: 1.0.0
Author: Tom Zhou
Date: 2025-08-02 22:49:16
LastEditors: Tom Zhou
LastEditTime: 2025-08-05 13:06:04
'''
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models.bedrock import BedrockModel

# Import the AgentCore SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp

WELCOME_MESSAGE = """
Welcome to the Customer Support Assistant! How can I help you today?
"""

SYSTEM_PROMPT = """
You are an helpful customer support assistant.
When provided with a customer email, gather all necessary info and prepare the response email.
When asked about an order, look for it and tell the full description and date of the order to the customer.
Don't mention the customer ID in your reply.
"""


@tool
def get_customer_id(email_address: str):
    if email_address == "me@example.net":
        return {"customer_id": 123}
    else:
        return {"message": "customer not found"}


@tool
def get_orders(customer_id: int):
    if customer_id == 123:
        return [{
            "order_id": 1234,
            "items": ["smartphone", "smartphone USB-C charger", "smartphone black cover"],
            "date": "20250607"
        }]
    else:
        return {"message": "no order found"}


@tool
def get_knowledge_base_info(topic: str):
    kb_info = []
    if "smartphone" in topic:
        if "cover" in topic:
            kb_info.append("To put on the cover, insert the bottom first, then push from the back up to the top.")
            kb_info.append("To remove the cover, push the top and bottom of the cover at the same time.")
        if "charger" in topic:
            kb_info.append("Input: 100-240V AC, 50/60Hz")
            kb_info.append("Includes US/UK/EU plug adapters")
    if len(kb_info) > 0:
        return kb_info
    else:
        return {"message": "no info found"}


# Create an AgentCore app
app = BedrockAgentCoreApp()

# Use Amazon Nova Pro model - supports system messages and direct invocation
model = BedrockModel(model_id="amazon.nova-pro-v1:0")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[calculator, current_time, get_customer_id, get_orders, get_knowledge_base_info]
)


# Specify the entry point function invoking the agent
@app.entrypoint
def invoke(payload):
    """Handler for agent invocation"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
