"""Trajectory evaluator"""

from typing import Any, Dict, Optional
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class TrajectoryEvaluator(BaseEvaluator):
    """Evaluate tool uses and intermediate responses"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        """Evaluate trajectory (tool uses and intermediate responses)

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result
            eval_config: Per-test-case evaluator configuration

        Returns:
            EvaluatorResult with evaluation results
        """
        # Merge config: per-test-case overrides instance config
        config = self.get_config(eval_config)
        sequence_match_type = config.get("sequence_match_type", "exact")
        allow_partial_match = config.get("allow_partial_match", False)

        self.logger.debug(f"TrajectoryEvaluator evaluating case: {eval_case.eval_id}")

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        expected_conv = eval_case.conversation
        actual_conv = provider_result.conversation_history

        if len(expected_conv) != len(actual_conv):
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=True,
                score=0.0,
                passed=False,
                details={
                    "mismatch": "conversation_length",
                    "expected_length": len(expected_conv),
                    "actual_length": len(actual_conv),
                },
            )

        # Compare tool uses for each invocation
        tool_matches = []
        total_matches = 0
        total_invocations = 0

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            expected_tools = expected_inv.intermediate_data.tool_uses
            actual_tools = actual_inv.intermediate_data.tool_uses

            if sequence_match_type == "exact":
                match = self._exact_match(expected_tools, actual_tools)
            else:
                match = self._partial_match(expected_tools, actual_tools)

            tool_matches.append({
                "invocation": i,
                "expected_tool_count": len(expected_tools),
                "actual_tool_count": len(actual_tools),
                "match": match,
                "expected_tools": [t.name for t in expected_tools],
                "actual_tools": [t.name for t in actual_tools],
            })

            if match:
                total_matches += 1
            total_invocations += 1

        score = total_matches / total_invocations if total_invocations > 0 else 1.0
        passed = score >= 1.0 if sequence_match_type == "exact" else score >= 0.5

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=score,
            passed=passed,
            details={
                "sequence_match_type": sequence_match_type,
                "allow_partial_match": allow_partial_match,
                "tool_matches": tool_matches,
                "match_rate": score,
            },
        )

    def _exact_match(self, expected_tools: list, actual_tools: list) -> bool:
        """Check if tool sequences match exactly

        Args:
            expected_tools: Expected tool uses
            actual_tools: Actual tool uses

        Returns:
            True if sequences match exactly
        """
        if len(expected_tools) != len(actual_tools):
            return False

        for exp, act in zip(expected_tools, actual_tools):
            if exp.name != act.name:
                return False

        return True

    def _partial_match(self, expected_tools: list, actual_tools: list) -> bool:
        """Check if tool sequences partially match

        Args:
            expected_tools: Expected tool uses
            actual_tools: Actual tool uses

        Returns:
            True if there is some overlap
        """
        if not expected_tools and not actual_tools:
            return True

        if not expected_tools or not actual_tools:
            return False

        expected_names = set(t.name for t in expected_tools)
        actual_names = set(t.name for t in actual_tools)

        overlap = expected_names.intersection(actual_names)
        return len(overlap) > 0
