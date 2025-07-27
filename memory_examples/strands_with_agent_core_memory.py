import time

from strands import Agent
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider


def get_response_from_agent(memory_id):
    strands_provider = AgentCoreMemoryToolProvider(
        memory_id=memory_id,
        actor_id="rdeb",
        session_id="session123",
        namespace="/users/rdeb",
        region="us-west-2"
    )
    agent = Agent(tools=strands_provider.tools, callback_handler=None)

    while True:
        user_input = input("Ask your question:\n")
        if user_input == "quit":
            break
        else:
            response = agent(user_input)
            print(response)
            # time.sleep(60)


if __name__ == "__main__":
    memory_id = "UserPrefMemory-Wm0VInFi7V"
    response = get_response_from_agent(memory_id)
    print(response)
