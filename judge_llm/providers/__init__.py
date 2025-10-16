"""LLM provider integrations"""

from judge_llm.providers.base import BaseProvider
from judge_llm.providers.mock_provider import MockProvider
from judge_llm.core.registry import register_provider

# Auto-register built-in providers
register_provider("mock", MockProvider)

__all__ = [
    "BaseProvider",
    "MockProvider",
]
