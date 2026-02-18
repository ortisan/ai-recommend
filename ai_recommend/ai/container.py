from autogen_ext.models.openai import OpenAIChatCompletionClient
from dependency_injector import containers, providers

from ai_recommend.ai.agent import AgentFactory


class AIContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    model_client = providers.Singleton(
        OpenAIChatCompletionClient,
        provider=config.ai_provider,
        model=config.ai_model,
        api_key=config.openai_api_key,
    )

    agent_factory = providers.Singleton(AgentFactory, model_client=model_client)
