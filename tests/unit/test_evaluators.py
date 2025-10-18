"""Unit tests for all evaluators."""

import pytest
from judge_llm.core.models import (
    Part,
    Content,
    ToolUse,
    IntermediateData,
    Invocation,
    SessionInput,
    EvalCase,
    ProviderResult,
)
from judge_llm.evaluators.response_evaluator import ResponseEvaluator
from judge_llm.evaluators.cost_evaluator import CostEvaluator
from judge_llm.evaluators.latency_evaluator import LatencyEvaluator
from judge_llm.evaluators.trajectory_evaluator import TrajectoryEvaluator


class TestResponseEvaluator:
    """Test ResponseEvaluator class."""

    def test_exact_match_success(self):
        """Test exact match similarity with matching responses."""
        evaluator = ResponseEvaluator({"match_type": "exact", "similarity_threshold": 1.0})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True
        assert result.score == 1.0

    def test_exact_match_failure(self):
        """Test exact match similarity with non-matching responses."""
        evaluator = ResponseEvaluator({"match_type": "exact", "similarity_threshold": 1.0})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hello there")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is False
        assert result.score == 0.0

    def test_jaccard_similarity(self):
        """Test Jaccard similarity calculation."""
        evaluator = ResponseEvaluator({"match_type": "semantic", "similarity_threshold": 0.5})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What is the capital?")]),
                    final_response=Content(role="model", parts=[Part(text="Paris is the capital")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What is the capital?")]),
                    final_response=Content(role="model", parts=[Part(text="The capital is Paris")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.score > 0.5  # Should have decent overlap

    def test_recall_similarity(self):
        """Test recall similarity calculation."""
        evaluator = ResponseEvaluator({"match_type": "recall", "similarity_threshold": 0.8})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Paris France")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Paris is in France and has many attractions")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        # Should have high recall since all expected words are present
        assert result.score == 1.0

    def test_conversation_length_mismatch(self):
        """Test handling of conversation length mismatch."""
        evaluator = ResponseEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                ),
                Invocation(
                    invocation_id="inv_2",
                    user_content=Content(role="user", parts=[Part(text="Bye")]),
                    final_response=Content(role="model", parts=[Part(text="Goodbye")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is False
        assert result.details["mismatch"] == "conversation_length"

    def test_provider_failure(self):
        """Test handling of provider execution failure."""
        evaluator = ResponseEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            success=False,
            error="API Error"
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is False
        assert result.passed is False
        assert result.error is not None

    def test_case_sensitivity(self):
        """Test case-sensitive matching."""
        evaluator = ResponseEvaluator({
            "match_type": "exact",
            "case_sensitive": True,
            "similarity_threshold": 1.0
        })

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hello")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="hello")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.passed is False

    def test_per_case_config_override(self):
        """Test per-test-case configuration override."""
        evaluator = ResponseEvaluator({"similarity_threshold": 0.5})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there friend")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        # Override with higher threshold
        result = evaluator.evaluate(eval_case, {}, provider_result, eval_config={"similarity_threshold": 0.9})

        assert result.threshold == 0.9


class TestCostEvaluator:
    """Test CostEvaluator class."""

    def test_cost_within_threshold(self):
        """Test cost evaluation within threshold."""
        evaluator = CostEvaluator({"max_cost_per_case": 0.10})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            cost=0.05,
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True
        assert result.score == 1.0
        assert result.details["actual_cost"] == 0.05

    def test_cost_exceeds_threshold(self):
        """Test cost evaluation exceeding threshold."""
        evaluator = CostEvaluator({"max_cost_per_case": 0.10})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            cost=0.15,
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is False
        assert result.score == 0.0
        assert result.details["cost_ratio"] > 1.0

    def test_cost_provider_failure(self):
        """Test cost evaluator with provider failure."""
        evaluator = CostEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            success=False
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is False
        assert result.passed is False

    def test_cost_config_override(self):
        """Test cost evaluator with per-case config override."""
        evaluator = CostEvaluator({"max_cost_per_case": 0.10})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            cost=0.15,
            success=True
        )

        # Override with higher threshold
        result = evaluator.evaluate(eval_case, {}, provider_result, eval_config={"max_cost_per_case": 0.20})

        assert result.passed is True
        assert result.threshold == 0.20


class TestLatencyEvaluator:
    """Test LatencyEvaluator class."""

    def test_latency_within_threshold(self):
        """Test latency evaluation within threshold."""
        evaluator = LatencyEvaluator({"max_latency_seconds": 5.0})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            time_taken=3.0,
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True
        assert result.score == 1.0
        assert result.details["actual_latency_seconds"] == 3.0

    def test_latency_exceeds_threshold(self):
        """Test latency evaluation exceeding threshold."""
        evaluator = LatencyEvaluator({"max_latency_seconds": 5.0})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            time_taken=7.0,
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is False
        assert result.score == 0.0
        assert result.details["latency_ratio"] > 1.0

    def test_latency_provider_failure(self):
        """Test latency evaluator with provider failure."""
        evaluator = LatencyEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            success=False
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is False
        assert result.passed is False

    def test_latency_config_override(self):
        """Test latency evaluator with per-case config override."""
        evaluator = LatencyEvaluator({"max_latency_seconds": 5.0})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            time_taken=7.0,
            success=True
        )

        # Override with higher threshold
        result = evaluator.evaluate(eval_case, {}, provider_result, eval_config={"max_latency_seconds": 10.0})

        assert result.passed is True
        assert result.threshold == 10.0


class TestTrajectoryEvaluator:
    """Test TrajectoryEvaluator class."""

    def test_exact_trajectory_match(self):
        """Test exact trajectory matching."""
        evaluator = TrajectoryEvaluator({"sequence_match_type": "exact"})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_weather", args={"city": "Paris"}),
                            ToolUse(id="2", name="format_response", args={})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_weather", args={"city": "Paris"}),
                            ToolUse(id="2", name="format_response", args={})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True
        assert result.score == 1.0

    def test_trajectory_mismatch(self):
        """Test trajectory mismatch."""
        evaluator = TrajectoryEvaluator({"sequence_match_type": "exact"})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_weather", args={"city": "Paris"})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_location", args={}),
                            ToolUse(id="2", name="get_weather", args={"city": "Paris"})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is False
        assert result.score == 0.0

    def test_partial_trajectory_match(self):
        """Test partial trajectory matching."""
        evaluator = TrajectoryEvaluator({"sequence_match_type": "partial"})

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_weather", args={"city": "Paris"}),
                            ToolUse(id="2", name="format_response", args={})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="What's the weather?")]),
                    final_response=Content(role="model", parts=[Part(text="It's sunny")]),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            ToolUse(id="1", name="get_weather", args={"city": "Paris"})
                        ]
                    ),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True  # Partial match should pass

    def test_trajectory_provider_failure(self):
        """Test trajectory evaluator with provider failure."""
        evaluator = TrajectoryEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[],
            success=False
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is False
        assert result.passed is False

    def test_empty_tool_sequences(self):
        """Test trajectory evaluation with no tool uses."""
        evaluator = TrajectoryEvaluator()

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi")]),
                    intermediate_data=IntermediateData(tool_uses=[]),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        provider_result = ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi")]),
                    intermediate_data=IntermediateData(tool_uses=[]),
                    creation_timestamp=1234567890.0
                )
            ],
            success=True
        )

        result = evaluator.evaluate(eval_case, {}, provider_result)

        assert result.success is True
        assert result.passed is True  # Empty tool sequences should match
