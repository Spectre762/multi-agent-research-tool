from .base import LLMProvider, LLMResponse
from .claude import ClaudeProvider
from .gemini import GeminiProvider
from .openai import OpenAIProvider

_REGISTRY = {
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
}


def get_provider(name: str, **kwargs) -> LLMProvider:
    """
    Usage:
        provider = get_provider("gemini")
        response = await provider.generate("what is the capital of India?")
    """

    if name not in _REGISTRY:
        raise ValueError(f"Unknown provider: {name}. Available providers: {list(_REGISTRY)}")
    return _REGISTRY[name](**kwargs)