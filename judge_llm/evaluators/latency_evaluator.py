"""Latency evaluator"""

from typing import Any, Dict
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class LatencyEvaluator(BaseEvaluator):
    """Evaluate if latency is within threshold"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()
        self.max_latency_seconds = self.config.get("max_latency_seconds", 30.0)
        self.percentile = self.config.get("percentile", 100)  # Default to max latency

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
    ) -> EvaluatorResult:
        """Evaluate latency against threshold

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result

        Returns:
            EvaluatorResult with evaluation results
        """
        self.logger.debug(f"LatencyEvaluator evaluating case: {eval_case.eval_id}")

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        actual_latency = provider_result.time_taken
        passed = actual_latency <= self.max_latency_seconds

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=1.0 if passed else 0.0,
            threshold=self.max_latency_seconds,
            passed=passed,
            details={
                "actual_latency_seconds": actual_latency,
                "max_latency_seconds": self.max_latency_seconds,
                "latency_ratio": actual_latency / self.max_latency_seconds if self.max_latency_seconds > 0 else 0,
            },
        )
