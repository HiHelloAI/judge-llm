"""Base provider interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from judge_llm.core.models import EvalCase, ProviderResult


class BaseProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(
        self,
        agent_id: str,
        agent_config_path: Optional[str] = None,
        agent_metadata: Optional[Dict[str, Any]] = None,
        **provider_metadata,
    ):
        """Initialize provider

        Args:
            agent_id: Unique identifier for the agent
            agent_config_path: Path to agent configuration directory
            agent_metadata: Agent metadata dictionary
            **provider_metadata: Additional provider-specific metadata
        """
        self.agent_id = agent_id
        self.agent_config_path = agent_config_path
        self.agent_metadata = agent_metadata or {}
        self.provider_metadata = provider_metadata

    @abstractmethod
    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case with the provider

        Args:
            eval_case: Evaluation case to execute

        Returns:
            ProviderResult with conversation history, cost, time, etc.
        """
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources after execution"""
        pass

    def get_provider_type(self) -> str:
        """Get provider type name

        Returns:
            Provider type string
        """
        return self.__class__.__name__.replace("Provider", "").lower()
