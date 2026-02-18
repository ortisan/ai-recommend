from typing import Annotated

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException

from ai_recommend.ai.agent import AgentFactory
from ai_recommend.ai.container import AIContainer

router = APIRouter()

@router.get("/chat", response_model=TextMessage)
@inject
async def chat(
    agent_factory: Annotated[AgentFactory, Depends(Provide[AIContainer.agent_factory])],
    request: TextMessage,
) -> TextMessage:
    try:
        # Get the agent and respond to the message.
        agent = agent_factory.get_agent()
        response = await agent.on_messages(
            messages=[request], cancellation_token=CancellationToken()
        )

        assert isinstance(response.chat_message, TextMessage)
        return response.chat_message
    except Exception as e:
        error_message = {"type": "error", "content": f"Error: {str(e)}", "source": "system"}
        raise HTTPException(status_code=500, detail=error_message) from e
