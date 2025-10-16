"""Response validator evaluator"""

from typing import Any, Dict
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class ResponseValidator(BaseEvaluator):
    """Validate final responses against expected responses"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()
        self.similarity_threshold = self.config.get("similarity_threshold", 0.8)
        self.match_type = self.config.get("match_type", "exact")  # exact or semantic

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
    ) -> EvaluatorResult:
        """Evaluate response similarity

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result

        Returns:
            EvaluatorResult with evaluation results
        """
        self.logger.debug(f"ResponseValidator evaluating case: {eval_case.eval_id}")

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        # Compare conversation lengths
        expected_conv = eval_case.conversation
        actual_conv = provider_result.conversation_history

        if len(expected_conv) != len(actual_conv):
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=True,
                score=0.0,
                threshold=self.similarity_threshold,
                passed=False,
                details={
                    "mismatch": "conversation_length",
                    "expected_length": len(expected_conv),
                    "actual_length": len(actual_conv),
                },
            )

        # Compare each response
        total_score = 0.0
        comparisons = []

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            expected_text = self._extract_text(expected_inv.final_response.parts)
            actual_text = self._extract_text(actual_inv.final_response.parts)

            if self.match_type == "exact":
                score = 1.0 if expected_text == actual_text else 0.0
            else:
                # Simple semantic similarity (can be enhanced with embeddings)
                score = self._simple_similarity(expected_text, actual_text)

            total_score += score

            comparisons.append({
                "invocation": i,
                "expected": expected_text[:100],  # Truncate for brevity
                "actual": actual_text[:100],
                "score": score,
            })

        avg_score = total_score / len(expected_conv) if expected_conv else 0.0
        passed = avg_score >= self.similarity_threshold

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=avg_score,
            threshold=self.similarity_threshold,
            passed=passed,
            details={
                "match_type": self.match_type,
                "comparisons": comparisons,
                "average_score": avg_score,
            },
        )

    def _extract_text(self, parts: list) -> str:
        """Extract text from parts

        Args:
            parts: List of Part objects

        Returns:
            Combined text string
        """
        texts = [part.text for part in parts if part.text]
        return " ".join(texts).strip()

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0

        if text1 == text2:
            return 1.0

        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
