import os
from google import genai

from .base import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    """Gemini LLM provider adapter."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-3.6-flash"):
        self.client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
        self.model = model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using the Gemini model."""
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "system_instruction": system or "You are a helpful research assistant.",
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        return LLMResponse(
            text=response.text,
            model=self.model,
            provider="gemini",
        )
