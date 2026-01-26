"""Trajectory evaluator

Evaluates tool usage patterns and sequences against expected behavior.
Supports matching tool names, arguments, and execution order.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult, ToolUse
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class TrajectoryEvaluator(BaseEvaluator):
    """Evaluate tool uses and intermediate responses

    Configuration:
        sequence_match_type (str): How to match tool sequences
            - "exact": Exact order and tools must match
            - "flexible": Tools must be present but order can differ
            - "subset": Expected tools must be subset of actual
            - "superset": Actual tools must be subset of expected
        compare_arguments (bool): Whether to compare tool arguments (default: False)
        argument_match_type (str): How to compare arguments
            - "exact": Arguments must match exactly
            - "subset": Expected args must be subset of actual args
            - "regex": Use regex patterns in expected args
            - "fuzzy": Fuzzy string matching for string values
        argument_similarity_threshold (float): Threshold for fuzzy matching (default: 0.8)
        allow_extra_tools (bool): Allow extra tools in actual (default: True)
        tool_name_match (str): How to match tool names
            - "exact": Exact name match
            - "contains": Expected name contained in actual
            - "regex": Regex pattern matching
        min_score_threshold (float): Minimum score to pass (default: 0.5)
    """

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
        config = self.get_config(eval_config)
        sequence_match_type = config.get("sequence_match_type", "exact")
        compare_arguments = config.get("compare_arguments", False)
        argument_match_type = config.get("argument_match_type", "exact")
        argument_threshold = config.get("argument_similarity_threshold", 0.8)
        allow_extra_tools = config.get("allow_extra_tools", True)
        tool_name_match = config.get("tool_name_match", "exact")
        min_score_threshold = config.get("min_score_threshold", 0.5)

        self.logger.debug(
            f"TrajectoryEvaluator evaluating case: {eval_case.eval_id} "
            f"(match_type={sequence_match_type}, compare_args={compare_arguments})"
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

        expected_conv = eval_case.conversation
        actual_conv = provider_result.conversation_history

        if len(expected_conv) != len(actual_conv):
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=True,
                score=0.0,
                threshold=min_score_threshold,
                passed=False,
                details={
                    "mismatch": "conversation_length",
                    "expected_length": len(expected_conv),
                    "actual_length": len(actual_conv),
                },
            )

        # Compare tool uses for each invocation
        tool_matches = []
        total_score = 0.0
        total_invocations = 0

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            expected_tools = expected_inv.intermediate_data.tool_uses
            actual_tools = actual_inv.intermediate_data.tool_uses

            # Calculate match score based on configuration
            match_result = self._calculate_tool_match(
                expected_tools,
                actual_tools,
                sequence_match_type,
                compare_arguments,
                argument_match_type,
                argument_threshold,
                allow_extra_tools,
                tool_name_match,
            )

            tool_matches.append({
                "invocation": i,
                "expected_tool_count": len(expected_tools),
                "actual_tool_count": len(actual_tools),
                "score": match_result["score"],
                "name_matches": match_result["name_matches"],
                "argument_matches": match_result.get("argument_matches", []),
                "expected_tools": [{"name": t.name, "args": t.args} for t in expected_tools],
                "actual_tools": [{"name": t.name, "args": t.args} for t in actual_tools],
                "details": match_result.get("details", {}),
            })

            total_score += match_result["score"]
            total_invocations += 1

        avg_score = total_score / total_invocations if total_invocations > 0 else 1.0
        passed = avg_score >= min_score_threshold

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=avg_score,
            threshold=min_score_threshold,
            passed=passed,
            details={
                "sequence_match_type": sequence_match_type,
                "compare_arguments": compare_arguments,
                "argument_match_type": argument_match_type,
                "allow_extra_tools": allow_extra_tools,
                "tool_name_match": tool_name_match,
                "tool_matches": tool_matches,
                "average_score": avg_score,
            },
        )

    def _calculate_tool_match(
        self,
        expected_tools: List[ToolUse],
        actual_tools: List[ToolUse],
        sequence_match_type: str,
        compare_arguments: bool,
        argument_match_type: str,
        argument_threshold: float,
        allow_extra_tools: bool,
        tool_name_match: str,
    ) -> Dict[str, Any]:
        """Calculate comprehensive tool match score

        Args:
            expected_tools: Expected tool uses
            actual_tools: Actual tool uses
            sequence_match_type: How to match sequences
            compare_arguments: Whether to compare arguments
            argument_match_type: How to compare arguments
            argument_threshold: Threshold for fuzzy matching
            allow_extra_tools: Allow extra tools
            tool_name_match: How to match tool names

        Returns:
            Dictionary with score and match details
        """
        if not expected_tools and not actual_tools:
            return {"score": 1.0, "name_matches": [], "details": {"note": "Both empty"}}

        if not expected_tools:
            score = 1.0 if allow_extra_tools else 0.0
            return {
                "score": score,
                "name_matches": [],
                "details": {"note": "No expected tools", "actual_count": len(actual_tools)}
            }

        if not actual_tools:
            return {
                "score": 0.0,
                "name_matches": [],
                "details": {"note": "No actual tools", "expected_count": len(expected_tools)}
            }

        # Match tools based on sequence_match_type
        if sequence_match_type == "exact":
            return self._exact_sequence_match(
                expected_tools, actual_tools, compare_arguments,
                argument_match_type, argument_threshold, tool_name_match
            )
        elif sequence_match_type == "flexible":
            return self._flexible_match(
                expected_tools, actual_tools, compare_arguments,
                argument_match_type, argument_threshold, allow_extra_tools, tool_name_match
            )
        elif sequence_match_type == "subset":
            return self._subset_match(
                expected_tools, actual_tools, compare_arguments,
                argument_match_type, argument_threshold, tool_name_match
            )
        elif sequence_match_type == "superset":
            return self._superset_match(
                expected_tools, actual_tools, compare_arguments,
                argument_match_type, argument_threshold, tool_name_match
            )
        else:
            # Default to flexible
            return self._flexible_match(
                expected_tools, actual_tools, compare_arguments,
                argument_match_type, argument_threshold, allow_extra_tools, tool_name_match
            )

    def _exact_sequence_match(
        self,
        expected_tools: List[ToolUse],
        actual_tools: List[ToolUse],
        compare_arguments: bool,
        argument_match_type: str,
        argument_threshold: float,
        tool_name_match: str,
    ) -> Dict[str, Any]:
        """Match tools in exact sequence order"""
        if len(expected_tools) != len(actual_tools):
            # Partial credit for overlap
            min_len = min(len(expected_tools), len(actual_tools))
            matches = 0
            name_matches = []
            arg_matches = []

            for i in range(min_len):
                name_match = self._match_tool_name(
                    expected_tools[i].name, actual_tools[i].name, tool_name_match
                )
                name_matches.append(name_match)

                if name_match and compare_arguments:
                    arg_score = self._compare_arguments(
                        expected_tools[i].args, actual_tools[i].args,
                        argument_match_type, argument_threshold
                    )
                    arg_matches.append({"index": i, "score": arg_score})
                    if arg_score >= argument_threshold:
                        matches += 1
                elif name_match:
                    matches += 1

            score = matches / len(expected_tools)
            return {
                "score": score,
                "name_matches": name_matches,
                "argument_matches": arg_matches,
                "details": {
                    "length_mismatch": True,
                    "expected_count": len(expected_tools),
                    "actual_count": len(actual_tools),
                }
            }

        # Same length - compare each position
        total_score = 0.0
        name_matches = []
        arg_matches = []

        for i, (exp, act) in enumerate(zip(expected_tools, actual_tools)):
            name_match = self._match_tool_name(exp.name, act.name, tool_name_match)
            name_matches.append(name_match)

            if not name_match:
                continue

            if compare_arguments:
                arg_score = self._compare_arguments(
                    exp.args, act.args, argument_match_type, argument_threshold
                )
                arg_matches.append({"index": i, "expected": exp.args, "actual": act.args, "score": arg_score})
                total_score += arg_score
            else:
                total_score += 1.0

        final_score = total_score / len(expected_tools)
        return {
            "score": final_score,
            "name_matches": name_matches,
            "argument_matches": arg_matches,
            "details": {"exact_sequence": True}
        }

    def _flexible_match(
        self,
        expected_tools: List[ToolUse],
        actual_tools: List[ToolUse],
        compare_arguments: bool,
        argument_match_type: str,
        argument_threshold: float,
        allow_extra_tools: bool,
        tool_name_match: str,
    ) -> Dict[str, Any]:
        """Match tools flexibly (order doesn't matter)"""
        matched_expected = set()
        matched_actual = set()
        name_matches = []
        arg_matches = []
        total_score = 0.0

        # For each expected tool, find best matching actual tool
        for exp_idx, exp in enumerate(expected_tools):
            best_match_idx = -1
            best_match_score = 0.0

            for act_idx, act in enumerate(actual_tools):
                if act_idx in matched_actual:
                    continue

                if self._match_tool_name(exp.name, act.name, tool_name_match):
                    if compare_arguments:
                        arg_score = self._compare_arguments(
                            exp.args, act.args, argument_match_type, argument_threshold
                        )
                        if arg_score > best_match_score:
                            best_match_score = arg_score
                            best_match_idx = act_idx
                    else:
                        best_match_score = 1.0
                        best_match_idx = act_idx
                        break

            if best_match_idx >= 0:
                matched_expected.add(exp_idx)
                matched_actual.add(best_match_idx)
                name_matches.append(True)
                total_score += best_match_score

                if compare_arguments:
                    arg_matches.append({
                        "expected_idx": exp_idx,
                        "actual_idx": best_match_idx,
                        "score": best_match_score
                    })
            else:
                name_matches.append(False)

        # Calculate final score
        score = total_score / len(expected_tools) if expected_tools else 1.0

        # Penalize extra tools if not allowed
        if not allow_extra_tools and len(actual_tools) > len(matched_actual):
            extra_count = len(actual_tools) - len(matched_actual)
            penalty = extra_count / (len(expected_tools) + extra_count)
            score = score * (1 - penalty * 0.5)  # 50% penalty for extras

        return {
            "score": score,
            "name_matches": name_matches,
            "argument_matches": arg_matches,
            "details": {
                "matched_expected": len(matched_expected),
                "matched_actual": len(matched_actual),
                "unmatched_expected": len(expected_tools) - len(matched_expected),
                "unmatched_actual": len(actual_tools) - len(matched_actual),
            }
        }

    def _subset_match(
        self,
        expected_tools: List[ToolUse],
        actual_tools: List[ToolUse],
        compare_arguments: bool,
        argument_match_type: str,
        argument_threshold: float,
        tool_name_match: str,
    ) -> Dict[str, Any]:
        """Check if expected tools are subset of actual (all expected must be present)"""
        result = self._flexible_match(
            expected_tools, actual_tools, compare_arguments,
            argument_match_type, argument_threshold, True, tool_name_match
        )
        # For subset, we don't care about extra tools
        return result

    def _superset_match(
        self,
        expected_tools: List[ToolUse],
        actual_tools: List[ToolUse],
        compare_arguments: bool,
        argument_match_type: str,
        argument_threshold: float,
        tool_name_match: str,
    ) -> Dict[str, Any]:
        """Check if actual tools are subset of expected (no unexpected tools)"""
        # Swap expected and actual for matching
        result = self._flexible_match(
            actual_tools, expected_tools, compare_arguments,
            argument_match_type, argument_threshold, True, tool_name_match
        )
        return result

    def _match_tool_name(self, expected: str, actual: str, match_type: str) -> bool:
        """Match tool names based on match type

        Args:
            expected: Expected tool name
            actual: Actual tool name
            match_type: Match type (exact, contains, regex)

        Returns:
            True if names match
        """
        if match_type == "exact":
            return expected == actual
        elif match_type == "contains":
            return expected.lower() in actual.lower() or actual.lower() in expected.lower()
        elif match_type == "regex":
            try:
                return bool(re.match(expected, actual, re.IGNORECASE))
            except re.error:
                return expected == actual
        else:
            return expected == actual

    def _compare_arguments(
        self,
        expected_args: Dict[str, Any],
        actual_args: Dict[str, Any],
        match_type: str,
        threshold: float,
    ) -> float:
        """Compare tool arguments

        Args:
            expected_args: Expected arguments
            actual_args: Actual arguments
            match_type: Comparison type (exact, subset, regex, fuzzy)
            threshold: Threshold for fuzzy matching

        Returns:
            Match score (0.0 to 1.0)
        """
        if not expected_args and not actual_args:
            return 1.0
        if not expected_args:
            return 1.0  # No expectations, any args are fine
        if not actual_args:
            return 0.0  # Expected args but none provided

        if match_type == "exact":
            return 1.0 if expected_args == actual_args else 0.0

        elif match_type == "subset":
            # All expected keys must be present with matching values
            matches = 0
            for key, expected_val in expected_args.items():
                if key in actual_args:
                    if self._values_match(expected_val, actual_args[key], "exact"):
                        matches += 1
            return matches / len(expected_args) if expected_args else 1.0

        elif match_type == "regex":
            # Use expected values as regex patterns
            matches = 0
            for key, expected_val in expected_args.items():
                if key in actual_args:
                    if self._values_match(expected_val, actual_args[key], "regex"):
                        matches += 1
            return matches / len(expected_args) if expected_args else 1.0

        elif match_type == "fuzzy":
            # Fuzzy string matching for values
            total_score = 0.0
            for key, expected_val in expected_args.items():
                if key in actual_args:
                    total_score += self._fuzzy_value_match(expected_val, actual_args[key])
            return total_score / len(expected_args) if expected_args else 1.0

        else:
            return 1.0 if expected_args == actual_args else 0.0

    def _values_match(self, expected: Any, actual: Any, match_type: str) -> bool:
        """Check if two values match

        Args:
            expected: Expected value
            actual: Actual value
            match_type: Match type

        Returns:
            True if values match
        """
        if match_type == "exact":
            return expected == actual
        elif match_type == "regex":
            if isinstance(expected, str) and isinstance(actual, str):
                try:
                    return bool(re.search(expected, actual, re.IGNORECASE))
                except re.error:
                    return expected == actual
            return expected == actual
        return expected == actual

    def _fuzzy_value_match(self, expected: Any, actual: Any) -> float:
        """Fuzzy match two values

        Args:
            expected: Expected value
            actual: Actual value

        Returns:
            Match score (0.0 to 1.0)
        """
        if expected == actual:
            return 1.0

        if isinstance(expected, str) and isinstance(actual, str):
            # Simple token overlap for strings
            expected_tokens = set(expected.lower().split())
            actual_tokens = set(actual.lower().split())
            if not expected_tokens:
                return 1.0 if not actual_tokens else 0.0
            overlap = expected_tokens & actual_tokens
            return len(overlap) / len(expected_tokens)

        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Numeric similarity
            if expected == 0:
                return 1.0 if actual == 0 else 0.0
            diff = abs(expected - actual) / abs(expected)
            return max(0.0, 1.0 - diff)

        return 0.0

    # Legacy methods for backwards compatibility
    def _exact_match(self, expected_tools: list, actual_tools: list) -> bool:
        """Check if tool sequences match exactly (legacy method)"""
        if len(expected_tools) != len(actual_tools):
            return False
        for exp, act in zip(expected_tools, actual_tools):
            if exp.name != act.name:
                return False
        return True

    def _partial_match(self, expected_tools: list, actual_tools: list) -> bool:
        """Check if tool sequences partially match (legacy method)"""
        if not expected_tools and not actual_tools:
            return True
        if not expected_tools or not actual_tools:
            return False
        expected_names = set(t.name for t in expected_tools)
        actual_names = set(t.name for t in actual_tools)
        overlap = expected_names.intersection(actual_names)
        return len(overlap) > 0
