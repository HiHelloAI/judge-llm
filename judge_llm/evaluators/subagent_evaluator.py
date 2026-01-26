"""Sub-agent evaluator

Evaluates agent transfer chains in multi-agent orchestration systems.
Tracks which agents were invoked and in what order.
"""

from typing import Any, Dict, List, Optional, Set
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult, Invocation
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.utils.logger import get_logger


class SubAgentEvaluator(BaseEvaluator):
    """Evaluate agent transfer chains in multi-agent systems

    Tracks agent transfers and validates:
    - Which agents were called
    - Order of agent invocations (optional)
    - Agent transfer patterns match expected behavior

    Configuration:
        sequence_match_type (str): How to match agent chains
            - "exact": Exact order and count must match
            - "subset": Expected agents must be present (order matters)
            - "contains": Expected agents must be present (order doesn't matter)
            - "flexible": Any overlap is considered partial success
        allow_extra_agents (bool): Whether extra agents in actual are OK (default: True)
        min_match_ratio (float): Minimum match ratio to pass (default: 0.8)
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
        """Evaluate agent transfer chain

        Args:
            eval_case: Original evaluation case
            agent_metadata: Agent metadata
            provider_result: Provider execution result
            eval_config: Per-test-case evaluator configuration

        Returns:
            EvaluatorResult with evaluation results
        """
        config = self.get_config(eval_config)
        sequence_match_type = config.get("sequence_match_type", "contains")
        allow_extra_agents = config.get("allow_extra_agents", True)
        min_match_ratio = config.get("min_match_ratio", 0.8)

        self.logger.debug(
            f"SubAgentEvaluator evaluating case: {eval_case.eval_id} "
            f"(match_type={sequence_match_type})"
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
                threshold=min_match_ratio,
                passed=False,
                details={
                    "mismatch": "conversation_length",
                    "expected_length": len(expected_conv),
                    "actual_length": len(actual_conv),
                },
            )

        # Compare agent chains for each invocation
        invocation_results = []
        total_score = 0.0

        for i, (expected_inv, actual_inv) in enumerate(zip(expected_conv, actual_conv)):
            expected_agents = self._extract_agent_chain(expected_inv)
            actual_agents = self._extract_actual_agent_chain(actual_inv, provider_result)

            score, match_details = self._compare_agent_chains(
                expected_agents,
                actual_agents,
                sequence_match_type,
                allow_extra_agents,
            )

            total_score += score

            invocation_results.append({
                "invocation": i,
                "expected_agents": expected_agents,
                "actual_agents": actual_agents,
                "score": score,
                "match_details": match_details,
            })

        avg_score = total_score / len(expected_conv) if expected_conv else 1.0
        passed = avg_score >= min_match_ratio

        # Aggregate all unique agents found
        all_expected_agents: Set[str] = set()
        all_actual_agents: Set[str] = set()
        for result in invocation_results:
            all_expected_agents.update(result["expected_agents"])
            all_actual_agents.update(result["actual_agents"])

        details = {
            "sequence_match_type": sequence_match_type,
            "allow_extra_agents": allow_extra_agents,
            "min_match_ratio": min_match_ratio,
            "average_score": avg_score,
            "invocation_results": invocation_results,
            "all_expected_agents": sorted(all_expected_agents),
            "all_actual_agents": sorted(all_actual_agents),
            "agents_missing": sorted(all_expected_agents - all_actual_agents),
            "agents_extra": sorted(all_actual_agents - all_expected_agents),
        }

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=avg_score,
            threshold=min_match_ratio,
            passed=passed,
            details=details,
        )

    def _extract_agent_chain(self, invocation: Invocation) -> List[str]:
        """Extract expected agent chain from invocation intermediate data

        Looks for agent transfers in:
        1. intermediate_responses with type="agent_transfer"
        2. tool_uses with name="transfer_to_agent"

        Args:
            invocation: Invocation to extract from

        Returns:
            List of agent names in order
        """
        agents = []

        # Check intermediate_responses for agent transfers
        for response in invocation.intermediate_data.intermediate_responses:
            if isinstance(response, dict):
                if response.get("type") == "agent_transfer":
                    if "from_agent" in response and response["from_agent"]:
                        if not agents:  # Add starting agent
                            agents.append(response["from_agent"])
                    if "to_agent" in response:
                        agents.append(response["to_agent"])
                elif "agent_name" in response:
                    agents.append(response["agent_name"])

        # Check tool_uses for transfer_to_agent calls
        for tool_use in invocation.intermediate_data.tool_uses:
            if tool_use.name == "transfer_to_agent":
                agent_name = tool_use.args.get("agent_name")
                if agent_name and agent_name not in agents:
                    agents.append(agent_name)

        return agents

    def _extract_actual_agent_chain(
        self, invocation: Invocation, provider_result: ProviderResult
    ) -> List[str]:
        """Extract actual agent chain from provider result

        Looks for agent information in:
        1. Provider metadata (agent_chain from ADK HTTP provider)
        2. Invocation intermediate_data
        3. Tool uses

        Args:
            invocation: Actual invocation
            provider_result: Provider result with metadata

        Returns:
            List of agent names in order
        """
        agents = []

        # Check provider metadata for agent_chain (from ADK HTTP provider)
        metadata = provider_result.metadata
        if "agent_chain" in metadata:
            agents.extend(metadata["agent_chain"])
        elif "agent_chains" in metadata:
            # Multiple invocations might have separate chains
            chains = metadata["agent_chains"]
            if isinstance(chains, list) and chains:
                # Get chain for this invocation
                inv_id = invocation.invocation_id
                for chain_info in chains:
                    if isinstance(chain_info, dict) and chain_info.get("invocation_id") == inv_id:
                        agents.extend(chain_info.get("agents", []))
                        break

        # If no metadata, extract from invocation itself
        if not agents:
            agents = self._extract_agent_chain(invocation)

        return agents

    def _compare_agent_chains(
        self,
        expected: List[str],
        actual: List[str],
        match_type: str,
        allow_extra: bool,
    ) -> tuple[float, dict]:
        """Compare expected and actual agent chains

        Args:
            expected: Expected agent chain
            actual: Actual agent chain
            match_type: Type of matching to perform
            allow_extra: Whether extra agents are allowed

        Returns:
            Tuple of (score, details)
        """
        if not expected and not actual:
            return 1.0, {"note": "Both chains empty"}

        if not expected:
            return 1.0 if allow_extra else 0.0, {
                "note": "No expected agents",
                "actual_count": len(actual)
            }

        if not actual:
            return 0.0, {"note": "No actual agents", "expected_count": len(expected)}

        expected_set = set(expected)
        actual_set = set(actual)

        if match_type == "exact":
            # Exact match: same order and count
            if expected == actual:
                return 1.0, {"exact_match": True}
            # Partial credit for overlap
            overlap = len(expected_set & actual_set)
            max_len = max(len(expected), len(actual))
            score = overlap / max_len if max_len > 0 else 0.0
            return score, {
                "exact_match": False,
                "expected_sequence": expected,
                "actual_sequence": actual,
                "overlap_count": overlap,
            }

        elif match_type == "subset":
            # Subset match: expected must appear in actual in order
            score = self._subsequence_match_ratio(expected, actual)
            return score, {
                "subsequence_ratio": score,
                "expected_in_order": expected,
                "actual_sequence": actual,
            }

        elif match_type == "contains":
            # Contains match: all expected agents must be present (order doesn't matter)
            missing = expected_set - actual_set
            if not missing:
                score = 1.0 if allow_extra or not (actual_set - expected_set) else 0.9
            else:
                score = len(expected_set & actual_set) / len(expected_set)
            return score, {
                "all_expected_present": len(missing) == 0,
                "missing_agents": list(missing),
                "extra_agents": list(actual_set - expected_set),
            }

        else:  # flexible
            # Flexible: any overlap counts
            overlap = expected_set & actual_set
            union = expected_set | actual_set
            jaccard = len(overlap) / len(union) if union else 1.0
            recall = len(overlap) / len(expected_set) if expected_set else 1.0
            # Use recall as primary score (did we hit the expected agents?)
            return recall, {
                "overlap_agents": list(overlap),
                "jaccard_similarity": jaccard,
                "recall": recall,
                "missing": list(expected_set - actual_set),
                "extra": list(actual_set - expected_set),
            }

    def _subsequence_match_ratio(self, expected: List[str], actual: List[str]) -> float:
        """Calculate what fraction of expected appears as subsequence in actual

        Args:
            expected: Expected sequence
            actual: Actual sequence

        Returns:
            Ratio of expected items found in order (0.0 to 1.0)
        """
        if not expected:
            return 1.0
        if not actual:
            return 0.0

        # Find longest subsequence of expected in actual
        expected_idx = 0
        for agent in actual:
            if expected_idx < len(expected) and agent == expected[expected_idx]:
                expected_idx += 1

        return expected_idx / len(expected)
