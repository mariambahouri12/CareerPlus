from typing import List, Optional

from agent.agent import CareerPlusAgent
from agent.tool_registry import ToolRegistry
from llm.ollama_client import OllamaClient

from api.schemas import ChatMessage, ChatResponse, ToolCallTrace


class AssistantService:
    """
    Application service responsible for running CareerPlus.

    FastAPI does not directly manipulate the agent.
    It calls this service instead.
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
        ollama_host: str = "http://localhost:11434",
    ):
        self.model = model

        self.llm = OllamaClient(
            model=model,
            host=ollama_host,
        )

        self.tool_registry = ToolRegistry()

        self.agent = CareerPlusAgent(
            llm=self.llm,
            tool_registry=self.tool_registry,
        )

    async def chat(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
        include_trace: bool = True,
    ) -> ChatResponse:
        """
        Execute a CareerPlus agent request.
        """

        history_data = []

        if history:
            history_data = [
                {
                    "role": item.role,
                    "content": item.content,
                }
                for item in history
            ]

        result = await self.agent.run_with_trace(
            user_query=message,
            history=history_data,
        )

        traces = []

        if include_trace:
            traces = [
                ToolCallTrace(
                    step=item["step"],
                    tool=item["tool"],
                    arguments=item["arguments"],
                )
                for item in result["tool_calls"]
            ]

        return ChatResponse(
            response=result["response"],
            tool_calls=traces,
            steps=result["steps"],
            success=True,
        )