"""Base evaluator interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult


class BaseEvaluator(ABC):
    """Abstract base class for evaluators"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evaluator

        Args:
            config: Evaluator configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
    ) -> EvaluatorResult:
        """Evaluate the provider result against expected data

        Args:
            eval_case: Original evaluation case with expected data
            agent_metadata: Agent metadata
            provider_result: Result from provider execution

        Returns:
            EvaluatorResult with success status, score, and details
        """
        pass

    def get_evaluator_name(self) -> str:
        """Get evaluator name

        Returns:
            Evaluator name string
        """
        return self.__class__.__name__

    def get_evaluator_type(self) -> str:
        """Get evaluator type

        Returns:
            Evaluator type string
        """
        return self.__class__.__name__.replace("Evaluator", "").lower()
