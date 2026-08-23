from ollama import AsyncClient


class OllamaClient:
    """Client for communicating with a local Ollama model."""

    def __init__(
        self,
        model: str = "qwen3:8b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.client = AsyncClient(host=host)

    async def chat(self, messages, tools=None):
        """Send messages and optional tools to the LLM."""

        return await self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools or [],
            think=False,
            options={"temperature": 0,
                     "num_ctx": 8192,},
        )