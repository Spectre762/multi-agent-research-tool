import os
from anthropic import AsyncAnthropic

from .base import LLMProvider, LLMResponse


class ClaudeProvider(LLMProvider):
    """Claude LLM provider adapter."""

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-5"):
        self.client = AsyncAnthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using the Claude model.

        Note: Claude Sonnet 5 rejects non-default temperature/top_p/top_k
        with a 400 error, so we don't forward `temperature` to the API call.
        It stays in the method signature only to match the shared interface
        used by the other providers (Gemini, OpenAI).
        """
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "You are a helpful research assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return LLMResponse(
            text=text,
            model=self.model,
            provider="claude",
        )
