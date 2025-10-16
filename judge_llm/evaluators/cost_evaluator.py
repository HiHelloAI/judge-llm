"""Cost evaluator"""

from typing import Any, Dict
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class CostEvaluator(BaseEvaluator):
    """Evaluate if cost is within threshold"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()
        self.max_cost_per_case = self.config.get("max_cost_per_case", 1.0)
        self.currency = self.config.get("currency", "USD")

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
    ) -> EvaluatorResult:
        """Evaluate cost against threshold

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result

        Returns:
            EvaluatorResult with evaluation results
        """
        self.logger.debug(f"CostEvaluator evaluating case: {eval_case.eval_id}")

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        actual_cost = provider_result.cost
        passed = actual_cost <= self.max_cost_per_case

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=1.0 if passed else 0.0,
            threshold=self.max_cost_per_case,
            passed=passed,
            details={
                "actual_cost": actual_cost,
                "max_cost": self.max_cost_per_case,
                "currency": self.currency,
                "cost_ratio": actual_cost / self.max_cost_per_case if self.max_cost_per_case > 0 else 0,
            },
        )
