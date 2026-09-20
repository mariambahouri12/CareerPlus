from ollama import AsyncClient

import config


class OllamaClient:
    """Async client for the local Ollama model."""

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or config.OLLAMA_MODEL
        self.client = AsyncClient(host=host or config.OLLAMA_HOST)

    async def chat(self, messages, tools=None):
        return await self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools or [],
            think=False,
            options={"temperature": 0, "num_ctx": 8192},
        )

    def generate(self, prompt: str) -> str:
        """Synchronous generation for non-agent use (email drafting)."""
        import ollama
        client = ollama.Client(host=config.OLLAMA_HOST)
        resp = client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0, "num_ctx": 8192},
        )
        try:
            return resp["message"]["content"]
        except Exception:
            return resp.message.content  # type: ignore[attr-defined]