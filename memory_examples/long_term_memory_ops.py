from datetime import datetime

from bedrock_agentcore.memory import MemoryClient
from strands import Agent
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider


class AgentCoreLongTermMemory():

    def create_memory(self, strategy="summ"):
        client = MemoryClient(region_name="us-west-2")

        if strategy == "summ":
            memory = client.create_memory_and_wait(
                name="MemorySummarizer",
                description="Summarizes the memory",
                event_expiry_days=7,
                max_wait=300,
                poll_interval=10,
                strategies=[{
                    "summaryMemoryStrategy": {
                        # Name of the extraction model/strategy
                        "name": "SessionSummarizer",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"]
                    }
                }]
            )
        else:
            memory = client.create_memory_and_wait(
                name="UserPrefMemory",
                strategies=[{
                    "userPreferenceMemoryStrategy": {
                        "name": "UserPreference01",
                        "namespaces": ["/users/{actorId}"]
                    }
                }]
            )

        return memory


if __name__ == "__main__":
    am = AgentCoreLongTermMemory()
    memory = am.create_memory(strategy="user_pref")
    print(memory)
