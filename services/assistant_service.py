from typing import List, Optional

from agent.agent import CareerPlusAgent
from agent.tool_registry import ToolRegistry
from api.schemas import ChatMessage, ChatResponse, ToolCallTrace
from infrastructure.llm.ollama_client import OllamaClient


class AssistantService:
    """
    Application service wrapping the agent. Also acts as a composition
    root for the tool registry (it owns the shared singletons).
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
        ollama_host: str = "http://localhost:11434",
        companies_repo=None,
        projects_repo=None,
        cvs_repo=None,
        applications_repo=None,
        email_sender=None,
        scraper=None,
        company_retriever=None,
    ):
        self.model = model
        self.llm = OllamaClient(model=model, host=ollama_host)

        shared = {
            "companies_repo": companies_repo,
            "projects_repo": projects_repo,
            "cvs_repo": cvs_repo,
            "applications_repo": applications_repo,
            "email_sender": email_sender,
            "scraper": scraper,
            "company_retriever": company_retriever,
            "llm": self.llm,
        }

        self.tool_registry = ToolRegistry(shared=shared)
        self.agent = CareerPlusAgent(llm=self.llm, tool_registry=self.tool_registry)

    async def chat(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
        include_trace: bool = True,
    ) -> ChatResponse:
        history_data = []
        if history:
            history_data = [{"role": h.role, "content": h.content} for h in history]

        result = await self.agent.run_with_trace(
            user_query=message,
            history=history_data,
        )

        traces = []
        if include_trace:
            traces = [
                ToolCallTrace(step=c["step"], tool=c["tool"], arguments=c["arguments"])
                for c in result["tool_calls"]
            ]

        return ChatResponse(
            response=result["response"],
            tool_calls=traces,
            steps=result["steps"],
            success=True,
        )