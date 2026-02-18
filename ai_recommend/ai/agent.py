import aiofiles
import httpx
from aiofiles import os
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient


class AgentFactory:
    def __init__(self, model_client: ChatCompletionClient):
        self.agent = AssistantAgent(
            name="assistant",
            model_client=model_client,
            reflect_on_tool_use=True,
            model_client_stream=True,
            system_message="You are a helpful assistant.",
        )

    def get_agent(self):
        return self.agent


#
#
# custom_client = httpx.AsyncClient(verify=False)
# model_client = OpenAIChatCompletionClient(
#     provider="autogen_ext_models.openai.OpenAiChatCompletionClient",
#     model="gpt-4o",
#     api_key=os.environ.get("OPENAI_API_KEY"),
#     http_client=custom_client
# )
#
#
#
# async def get_agent() -> AssistantAgent:
#     """Get the assistant agent, load state from file."""
#     # Get model client from config.
#     # Create the assistant agent.
#     agent = AssistantAgent(
#         name="assistant",
#         model_client=model_client,
#         reflect_on_tool_use=True,
#         model_client_stream=True,
#         system_message="You are a helpful assistant.",
#     )
#     # Load state from file.
#     if not os.path.exists(state_path):
#         return agent  # Return agent without loading state.
#     async with aiofiles.open(state_path, "r") as file:
#         state = json.loads(await file.read())
#     await agent.load_state(state)
#     return agent
