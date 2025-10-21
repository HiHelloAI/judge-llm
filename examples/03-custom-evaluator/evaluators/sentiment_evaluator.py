"""Custom sentiment evaluator example"""

from typing import Any, Dict, Optional
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult


class SentimentEvaluator(BaseEvaluator):
    """Evaluate sentiment of responses (simple example)

    This example shows how to:
    - Use per-test-case configuration
    - Merge global config with test-specific config
    - Implement custom evaluation logic
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Don't store config values as instance variables
        # They will be retrieved per-evaluation to support per-test-case config

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        """Evaluate response sentiment

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result
            eval_config: Per-test-case evaluator configuration (overrides global config)

        Returns:
            EvaluatorResult with sentiment analysis results
        """
        # Merge config: per-test-case config overrides instance config
        config = self.get_config(eval_config)

        # Get configuration values from merged config
        min_positive_sentiment = config.get("min_positive_sentiment", 0.5)
        custom_positive_words = config.get("positive_words", None)
        custom_negative_words = config.get("negative_words", None)

        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
                error="Provider execution failed",
            )

        # Simple sentiment analysis (count positive/negative words)
        # Use custom words if provided, otherwise use defaults
        positive_words = custom_positive_words if custom_positive_words else {
            "good", "great", "excellent", "happy", "wonderful", "amazing"
        }
        negative_words = custom_negative_words if custom_negative_words else {
            "bad", "terrible", "awful", "sad", "horrible", "disappointing"
        }

        total_positive = 0
        total_negative = 0
        sentiments = []

        for inv in provider_result.conversation_history:
            response_text = " ".join(
                part.text.lower() for part in inv.final_response.parts if part.text
            )

            positive_count = sum(1 for word in positive_words if word in response_text)
            negative_count = sum(1 for word in negative_words if word in response_text)

            total_positive += positive_count
            total_negative += negative_count

            sentiments.append({
                "invocation_id": inv.invocation_id,
                "positive_words": positive_count,
                "negative_words": negative_count,
            })

        # Calculate sentiment score
        total_words = total_positive + total_negative
        if total_words == 0:
            sentiment_score = 0.5  # Neutral
        else:
            sentiment_score = total_positive / total_words

        passed = sentiment_score >= min_positive_sentiment

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=sentiment_score,
            threshold=min_positive_sentiment,
            passed=passed,
            details={
                "sentiment_score": sentiment_score,
                "min_positive_sentiment": min_positive_sentiment,
                "total_positive_words": total_positive,
                "total_negative_words": total_negative,
                "sentiments_per_invocation": sentiments,
            },
        )
