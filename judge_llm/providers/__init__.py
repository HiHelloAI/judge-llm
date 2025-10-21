"""LLM provider integrations"""

from judge_llm.providers.base import BaseProvider
from judge_llm.providers.mock_provider import MockProvider
from judge_llm.core.registry import register_provider

# Auto-register built-in providers
register_provider("mock", MockProvider)

# Optional providers (registered if dependencies are available)
try:
    from judge_llm.providers.gemini_provider import GeminiProvider
    register_provider("gemini", GeminiProvider)
except ImportError:
    pass  # google-genai not installed

try:
    from judge_llm.providers.adk_provider import GoogleADKProvider
    register_provider("google_adk", GoogleADKProvider)
except ImportError:
    pass  # google-adk not installed

__all__ = [
    "BaseProvider",
    "MockProvider",
]
