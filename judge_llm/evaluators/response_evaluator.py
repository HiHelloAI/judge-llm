"""Response evaluator

Evaluates agent responses against expected responses using various similarity metrics.
Supports ROUGE-1 (preferred) with fallback to simpler metrics.
"""

import re
from typing import Any, Dict, Optional
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class ResponseEvaluator(BaseEvaluator):
    """Evaluate final responses against expected responses

    Supports multiple similarity metrics:
    - exact: Exact string matching (after normalization)
    - semantic: Word-based similarity (Jaccard index)
    - rouge: ROUGE-1 F1 score (preferred, requires rouge-score package)
    - recall: Word recall (overlap / expected_words)

    Configuration:
        similarity_threshold (float): Threshold for passing (0.0-1.0, default: 0.8)
        match_type (str): Type of matching (exact/semantic/rouge/recall, default: semantic)
        case_sensitive (bool): Whether to match case-sensitively (default: False)
        normalize_whitespace (bool): Normalize whitespace and list markers (default: True)
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger()

        # Check for ROUGE availability
        self._rouge_available = False
        try:
            from rouge_score import rouge_scorer
            self._rouge_available = True
            self.logger.debug("ROUGE scorer available")
        except ImportError:
            self.logger.debug("ROUGE scorer not available, will use fallback metrics")

    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        """Evaluate response similarity

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
        similarity_threshold = config.get("similarity_threshold", 0.8)
        match_type = config.get("match_type", "semantic")
        case_sensitive = config.get("case_sensitive", False)
        normalize_whitespace = config.get("normalize_whitespace", True)

        # Auto-select ROUGE if available and match_type is semantic
        if match_type == "semantic" and self._rouge_available:
            match_type = "rouge"
            self.logger.debug(f"Auto-selecting ROUGE metric (available)")

        self.logger.debug(
            f"ResponseEvaluator evaluating case: {eval_case.eval_id} "
            f"(match_type={match_type}, threshold={similarity_threshold})"
        )

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
                threshold=similarity_threshold,
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
        low_score_examples = []

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            expected_text = self._extract_text(expected_inv.final_response.parts)
            actual_text = self._extract_text(actual_inv.final_response.parts)

            # Calculate similarity based on match_type
            score, metric_details = self._calculate_similarity(
                expected_text,
                actual_text,
                match_type,
                case_sensitive,
                normalize_whitespace
            )

            total_score += score

            comparison = {
                "invocation": i,
                "expected_preview": expected_text[:100],  # Truncate for brevity
                "actual_preview": actual_text[:100],
                "score": score,
                "metric": match_type,
                "details": metric_details,
            }
            comparisons.append(comparison)

            # Track low-scoring examples for detailed reporting
            if score < similarity_threshold:
                low_score_examples.append({
                    "invocation": i,
                    "score": score,
                    "expected": expected_text,
                    "actual": actual_text,
                })

        avg_score = total_score / len(expected_conv) if expected_conv else 0.0
        passed = avg_score >= similarity_threshold

        details = {
            "match_type": match_type,
            "similarity_threshold": similarity_threshold,
            "comparisons": comparisons,
            "average_score": avg_score,
            "num_invocations": len(expected_conv),
            "num_low_scores": len(low_score_examples),
        }

        # Add low-scoring examples to details if any
        if low_score_examples:
            # Include first example in summary for debugging
            first_low = low_score_examples[0]
            details["low_score_example"] = {
                "invocation": first_low["invocation"],
                "score": first_low["score"],
                "expected_preview": first_low["expected"][:200],
                "actual_preview": first_low["actual"][:200],
            }

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=avg_score,
            threshold=similarity_threshold,
            passed=passed,
            details=details,
        )

    def _extract_text(self, parts: list) -> str:
        """Extract text from parts

        Args:
            parts: List of Part objects

        Returns:
            Combined text string
        """
        if not parts:
            return ""

        # Strip each part's text before joining to avoid extra whitespace
        texts = [part.text.strip() for part in parts if part.text and part.text.strip()]
        return " ".join(texts)

    def _calculate_similarity(
        self,
        expected: str,
        actual: str,
        match_type: str,
        case_sensitive: bool,
        normalize_whitespace: bool
    ) -> tuple[float, dict]:
        """Calculate similarity score between expected and actual text

        Args:
            expected: Expected text
            actual: Actual text
            match_type: Type of matching (exact/semantic/rouge/recall)
            case_sensitive: Whether to match case-sensitively
            normalize_whitespace: Whether to normalize whitespace

        Returns:
            Tuple of (score, metric_details)
        """
        # Handle empty strings
        if not expected and not actual:
            return 1.0, {"note": "Both texts are empty"}
        if not expected:
            return 0.0, {"note": "Expected text is empty"}
        if not actual:
            return 0.0, {"note": "Actual text is empty"}

        # Normalize texts based on config
        expected_normalized = self._normalize_text(
            expected, case_sensitive, normalize_whitespace
        )
        actual_normalized = self._normalize_text(
            actual, case_sensitive, normalize_whitespace
        )

        # Calculate score based on match_type
        if match_type == "exact":
            score = 1.0 if expected_normalized == actual_normalized else 0.0
            return score, {"exact_match": score == 1.0}

        elif match_type == "rouge":
            return self._rouge_similarity(expected_normalized, actual_normalized)

        elif match_type == "recall":
            return self._recall_similarity(expected_normalized, actual_normalized)

        else:  # semantic (Jaccard)
            return self._jaccard_similarity(expected_normalized, actual_normalized)

    def _normalize_text(
        self,
        text: str,
        case_sensitive: bool,
        normalize_whitespace: bool
    ) -> str:
        """Normalize text for comparison

        Args:
            text: Text to normalize
            case_sensitive: Whether to preserve case
            normalize_whitespace: Whether to normalize whitespace and list markers

        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Convert case if needed
        if not case_sensitive:
            text = text.lower()

        # Normalize whitespace and list markers if enabled
        if normalize_whitespace:
            # Remove numbered list markers: 1., 1), etc at line start
            text = re.sub(r'^\s*\d+[.)]\s*', '', text, flags=re.MULTILINE)
            # Remove bullet point markers: •, *, - at line start
            text = re.sub(r'^\s*[•\*\-]\s+', '', text, flags=re.MULTILINE)
            # Normalize whitespace (multiple spaces/newlines to single space)
            text = ' '.join(text.split())
        else:
            # Just strip leading/trailing whitespace
            text = text.strip()

        return text

    def _rouge_similarity(self, expected: str, actual: str) -> tuple[float, dict]:
        """Calculate ROUGE-1 F1 similarity

        ROUGE-1 is an industry-standard metric for comparing text similarity
        based on unigram overlap. Uses F1 score (harmonic mean of precision and recall).

        Args:
            expected: Expected text
            actual: Actual text

        Returns:
            Tuple of (score, details)
        """
        if not self._rouge_available:
            # Fallback to Jaccard if ROUGE not available
            self.logger.warning("ROUGE requested but not available, falling back to Jaccard")
            return self._jaccard_similarity(expected, actual)

        try:
            from rouge_score import rouge_scorer

            scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
            scores = scorer.score(expected, actual)
            rouge1_fmeasure = scores['rouge1'].fmeasure

            details = {
                "rouge1_precision": scores['rouge1'].precision,
                "rouge1_recall": scores['rouge1'].recall,
                "rouge1_fmeasure": rouge1_fmeasure,
            }

            return rouge1_fmeasure, details

        except Exception as e:
            self.logger.error(f"ROUGE calculation failed: {e}, falling back to Jaccard")
            return self._jaccard_similarity(expected, actual)

    def _recall_similarity(self, expected: str, actual: str) -> tuple[float, dict]:
        """Calculate word recall similarity (overlap / expected_words)

        This metric focuses on how much of the expected content is present,
        similar to Google's approach. More lenient than Jaccard for responses
        with extra information.

        Args:
            expected: Expected text
            actual: Actual text

        Returns:
            Tuple of (score, details)
        """
        expected_words = set(expected.split())
        actual_words = set(actual.split())

        if not expected_words:
            return 1.0 if not actual_words else 0.0, {"note": "No expected words"}

        overlap = expected_words & actual_words
        recall = len(overlap) / len(expected_words)

        details = {
            "expected_word_count": len(expected_words),
            "actual_word_count": len(actual_words),
            "overlap_count": len(overlap),
            "recall": recall,
        }

        return recall, details

    def _jaccard_similarity(self, expected: str, actual: str) -> tuple[float, dict]:
        """Calculate Jaccard similarity (intersection / union)

        Jaccard index is a classic similarity metric that penalizes both
        missing words and extra words equally.

        Args:
            expected: Expected text
            actual: Actual text

        Returns:
            Tuple of (score, details)
        """
        expected_words = set(expected.split())
        actual_words = set(actual.split())

        if not expected_words and not actual_words:
            return 1.0, {"note": "No words in either text"}

        intersection = expected_words & actual_words
        union = expected_words | actual_words

        if not union:
            return 0.0, {"note": "No words in union"}

        jaccard = len(intersection) / len(union)

        details = {
            "expected_word_count": len(expected_words),
            "actual_word_count": len(actual_words),
            "intersection_count": len(intersection),
            "union_count": len(union),
            "jaccard_index": jaccard,
        }

        return jaccard, details
