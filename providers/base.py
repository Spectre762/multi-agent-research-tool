"""
Common interface every LLM provider adapter must implement.
"""

# ABC / @abstractmethod: Enforces a strict blueprint—child classes MUST implement these methods.
from abc import ABC, abstractmethod
# @dataclass: Auto-generates boilerplate code (__init__, __repr__, __eq__) for data-holding classes.
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str


class LLMProvider(ABC):
    """Every provider (Claude, Gemini, GPT) implements this."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> LLMResponse:
        raise NotImplementedError
