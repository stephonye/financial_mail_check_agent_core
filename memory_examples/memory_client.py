from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-west-2")

memory = client.create_memory(
    name="CustomerSupportAgentMemory",
    description="Memory for customer support conversations",
)

# The memory_id will be used in following operations
print(f"Memory ID: {memory.get('id')}")
print(f"Memory: {memory}")

"""
CustomerSupportAgentMemory-D22Byv7Nu1
"""

