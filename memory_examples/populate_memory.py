from typing import List, Tuple

from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")

# memories = client.list_memories()


def create_short_term_memories(memory_id, actor_id, session_id, messages: List[Tuple[str, str]], ):
    status = client.create_event(
        memory_id=memory_id,  # This is the id from create_memory or list_memories
        actor_id=actor_id,  # This is the identifier of the actor, could be an agent or end-user.
        session_id=session_id,  # Unique id for a particular request/conversation.
        messages=messages,
    )

    return status


def list_memories(memory_id,
                  actor_id,
                  session_id,
                  max_results):

    conversations = client.list_events(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_id,
        max_results=max_results,
    )

    return conversations


if __name__ == "__main__":
    memory_id = "CustomerSupportAgentMemory-D22Byv7Nu1"
    actor_id = "rajib"
    session_id = "s001"
    messages = [
        ("lookup_order(order_id='12345')", "TOOL")
    ]
    # messages = [
    #     ("Hi, I'm having trouble with my order #12345", "USER"),
    #     ("I'm sorry to hear that. Let me look up your order.", "ASSISTANT"),
    #     ("lookup_order(order_id='12345')", "TOOL"),
    #     ("I see your order was shipped 3 days ago. What specific issue are you experiencing?", "ASSISTANT"),
    #     ("Actually, before that - I also want to change my email address", "USER"),
    #     (
    #         "Of course! I can help with both. Let's start with updating your email. What's your new email?",
    #         "ASSISTANT",
    #     ),
    #     ("newemail@example.com", "USER"),
    #     ("update_customer_email(old='old@example.com', new='newemail@example.com')", "TOOL"),
    #     ("Email updated successfully! Now, about your order issue?", "ASSISTANT"),
    #     ("The package arrived damaged", "USER"),
    # ]
    # status = create_short_term_memories(memory_id, actor_id, session_id, messages)
    # print(status)
    #
    result = list_memories(memory_id=memory_id,actor_id=actor_id,session_id=session_id,max_results=2)

    conversations = (result[0]['payload'])
    for conversation in result:
        print(conversation)
