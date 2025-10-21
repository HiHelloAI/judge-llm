"""Unit tests for core Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from judge_llm.core.models import (
    Part,
    Content,
    ToolUse,
    IntermediateResponse,
    IntermediateData,
    Invocation,
    SessionInput,
    EvalCase,
    EvalSet,
    ExecutionConfig,
    ProviderResult,
    EvaluatorResult,
    ExecutionRun,
    EvaluationReport,
)


class TestPart:
    """Test Part model."""

    def test_part_with_text(self):
        """Test Part creation with text."""
        part = Part(text="Hello world")
        assert part.text == "Hello world"
        assert part.function_call is None

    def test_part_with_function_call(self):
        """Test Part creation with function call."""
        part = Part(function_call={"name": "get_weather", "args": {"city": "Paris"}})
        assert part.function_call["name"] == "get_weather"
        assert part.text is None

    def test_part_with_thought(self):
        """Test Part creation with thought."""
        part = Part(thought="I need to calculate this")
        assert part.thought == "I need to calculate this"

    def test_part_with_inline_data(self):
        """Test Part creation with inline data."""
        part = Part(inline_data={"mime_type": "image/png", "data": "base64data"})
        assert part.inline_data["mime_type"] == "image/png"

    def test_part_empty(self):
        """Test Part creation with no fields."""
        part = Part()
        assert part.text is None
        assert part.function_call is None


class TestContent:
    """Test Content model."""

    def test_content_basic(self):
        """Test Content creation with basic parts."""
        content = Content(
            role="user",
            parts=[Part(text="Hello")]
        )
        assert content.role == "user"
        assert len(content.parts) == 1
        assert content.parts[0].text == "Hello"

    def test_content_multiple_parts(self):
        """Test Content with multiple parts."""
        content = Content(
            role="model",
            parts=[
                Part(text="The weather is"),
                Part(function_call={"name": "get_weather"}),
            ]
        )
        assert len(content.parts) == 2

    def test_content_without_role(self):
        """Test Content without role."""
        content = Content(parts=[Part(text="Hello")])
        assert content.role is None

    def test_content_empty_parts(self):
        """Test Content with empty parts list is allowed."""
        content = Content(role="user", parts=[])
        assert content.parts == []


class TestToolUse:
    """Test ToolUse model."""

    def test_tool_use_creation(self):
        """Test ToolUse creation."""
        tool = ToolUse(
            id="tool_123",
            name="get_weather",
            args={"city": "Paris", "units": "celsius"}
        )
        assert tool.id == "tool_123"
        assert tool.name == "get_weather"
        assert tool.args["city"] == "Paris"

    def test_tool_use_validation(self):
        """Test ToolUse validation requires all fields."""
        with pytest.raises(ValidationError):
            ToolUse(id="tool_123", name="get_weather")


class TestIntermediateData:
    """Test IntermediateData model."""

    def test_intermediate_data_empty(self):
        """Test IntermediateData with default empty lists."""
        data = IntermediateData()
        assert data.tool_uses == []
        assert data.intermediate_responses == []

    def test_intermediate_data_with_tools(self):
        """Test IntermediateData with tool uses."""
        data = IntermediateData(
            tool_uses=[
                ToolUse(id="1", name="tool1", args={}),
                ToolUse(id="2", name="tool2", args={}),
            ]
        )
        assert len(data.tool_uses) == 2


class TestInvocation:
    """Test Invocation model."""

    def test_invocation_creation(self):
        """Test Invocation creation."""
        invocation = Invocation(
            invocation_id="inv_123",
            user_content=Content(role="user", parts=[Part(text="Hello")]),
            final_response=Content(role="model", parts=[Part(text="Hi")]),
            creation_timestamp=1234567890.0
        )
        assert invocation.invocation_id == "inv_123"
        assert invocation.user_content.parts[0].text == "Hello"
        assert invocation.final_response.parts[0].text == "Hi"

    def test_invocation_with_intermediate_data(self):
        """Test Invocation with intermediate data."""
        invocation = Invocation(
            invocation_id="inv_123",
            user_content=Content(role="user", parts=[Part(text="Hello")]),
            final_response=Content(role="model", parts=[Part(text="Hi")]),
            intermediate_data=IntermediateData(
                tool_uses=[ToolUse(id="1", name="tool", args={})]
            ),
            creation_timestamp=1234567890.0
        )
        assert len(invocation.intermediate_data.tool_uses) == 1


class TestSessionInput:
    """Test SessionInput model."""

    def test_session_input_basic(self):
        """Test SessionInput creation."""
        session = SessionInput(
            app_name="test_app",
            user_id="user_123",
            user_prompt="Hello"
        )
        assert session.app_name == "test_app"
        assert session.user_id == "user_123"
        assert session.user_prompt == "Hello"

    def test_session_input_with_state(self):
        """Test SessionInput with state."""
        session = SessionInput(
            app_name="test_app",
            user_id="user_123",
            state={"context": "shopping", "cart_items": 3}
        )
        assert session.state["context"] == "shopping"

    def test_session_input_extra_fields(self):
        """Test SessionInput allows extra fields."""
        session = SessionInput(
            app_name="test_app",
            user_id="user_123",
            custom_field="custom_value"
        )
        # Extra fields should be allowed
        assert hasattr(session, "app_name")


class TestEvalCase:
    """Test EvalCase model."""

    def test_eval_case_creation(self):
        """Test EvalCase creation."""
        eval_case = EvalCase(
            eval_id="eval_123",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi")]),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )
        assert eval_case.eval_id == "eval_123"
        assert len(eval_case.conversation) == 1

    def test_eval_case_with_evaluator_config(self):
        """Test EvalCase with evaluator config."""
        eval_case = EvalCase(
            eval_id="eval_123",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0,
            evaluator_config={"response": {"threshold": 0.9}}
        )
        assert eval_case.evaluator_config["response"]["threshold"] == 0.9


class TestEvalSet:
    """Test EvalSet model."""

    def test_eval_set_creation(self):
        """Test EvalSet creation."""
        eval_set = EvalSet(
            eval_set_id="set_123",
            name="Test Set",
            description="A test evaluation set",
            eval_cases=[],
            creation_timestamp=1234567890.0
        )
        assert eval_set.eval_set_id == "set_123"
        assert eval_set.name == "Test Set"

    def test_eval_set_with_cases(self):
        """Test EvalSet with multiple cases."""
        eval_set = EvalSet(
            eval_set_id="set_123",
            name="Test Set",
            eval_cases=[
                EvalCase(
                    eval_id="eval_1",
                    conversation=[],
                    session_input=SessionInput(app_name="test", user_id="user1"),
                    creation_timestamp=1234567890.0
                ),
                EvalCase(
                    eval_id="eval_2",
                    conversation=[],
                    session_input=SessionInput(app_name="test", user_id="user2"),
                    creation_timestamp=1234567890.0
                ),
            ],
            creation_timestamp=1234567890.0
        )
        assert len(eval_set.eval_cases) == 2


class TestExecutionConfig:
    """Test ExecutionConfig model."""

    def test_execution_config_defaults(self):
        """Test ExecutionConfig with default values."""
        config = ExecutionConfig()
        assert config.num_runs == 1
        assert config.parallel_execution is False
        assert config.max_workers == 4
        assert config.fail_on_threshold_violation is True
        assert config.log_level == "INFO"

    def test_execution_config_custom(self):
        """Test ExecutionConfig with custom values."""
        config = ExecutionConfig(
            num_runs=5,
            parallel_execution=True,
            max_workers=8,
            log_level="DEBUG"
        )
        assert config.num_runs == 5
        assert config.parallel_execution is True
        assert config.max_workers == 8
        assert config.log_level == "DEBUG"


class TestProviderResult:
    """Test ProviderResult model."""

    def test_provider_result_success(self):
        """Test ProviderResult for successful execution."""
        result = ProviderResult(
            conversation_history=[],
            cost=0.05,
            time_taken=1.5,
            token_usage={"input": 100, "output": 50},
            success=True
        )
        assert result.success is True
        assert result.cost == 0.05
        assert result.error is None

    def test_provider_result_failure(self):
        """Test ProviderResult for failed execution."""
        result = ProviderResult(
            conversation_history=[],
            success=False,
            error="API timeout"
        )
        assert result.success is False
        assert result.error == "API timeout"

    def test_provider_result_defaults(self):
        """Test ProviderResult default values."""
        result = ProviderResult(conversation_history=[])
        assert result.cost == 0.0
        assert result.time_taken == 0.0
        assert result.success is True
        assert result.token_usage == {}


class TestEvaluatorResult:
    """Test EvaluatorResult model."""

    def test_evaluator_result_passed(self):
        """Test EvaluatorResult for passing evaluation."""
        result = EvaluatorResult(
            evaluator_name="response_similarity",
            evaluator_type="response",
            success=True,
            score=0.85,
            threshold=0.7,
            passed=True,
            details={"method": "rouge"}
        )
        assert result.passed is True
        assert result.score == 0.85

    def test_evaluator_result_failed(self):
        """Test EvaluatorResult for failing evaluation."""
        result = EvaluatorResult(
            evaluator_name="cost_check",
            evaluator_type="cost",
            success=True,
            score=0.10,
            threshold=0.05,
            passed=False,
            details={"exceeded_by": 0.05}
        )
        assert result.passed is False
        assert result.score == 0.10

    def test_evaluator_result_error(self):
        """Test EvaluatorResult with error."""
        result = EvaluatorResult(
            evaluator_name="trajectory",
            evaluator_type="trajectory",
            success=False,
            passed=False,
            error="Invalid trajectory format"
        )
        assert result.success is False
        assert result.error is not None


class TestExecutionRun:
    """Test ExecutionRun model."""

    def test_execution_run_creation(self):
        """Test ExecutionRun creation."""
        run = ExecutionRun(
            execution_id="exec_123",
            run_number=1,
            eval_set_id="set_123",
            eval_case_id="case_123",
            provider_type="mock",
            provider_result=ProviderResult(conversation_history=[]),
            overall_success=True
        )
        assert run.execution_id == "exec_123"
        assert run.run_number == 1
        assert run.overall_success is True

    def test_execution_run_with_evaluators(self):
        """Test ExecutionRun with evaluator results."""
        run = ExecutionRun(
            execution_id="exec_123",
            run_number=1,
            eval_set_id="set_123",
            eval_case_id="case_123",
            provider_type="mock",
            provider_result=ProviderResult(conversation_history=[]),
            evaluator_results=[
                EvaluatorResult(
                    evaluator_name="response",
                    evaluator_type="response",
                    success=True,
                    passed=True
                ),
                EvaluatorResult(
                    evaluator_name="cost",
                    evaluator_type="cost",
                    success=True,
                    passed=True
                ),
            ],
            overall_success=True
        )
        assert len(run.evaluator_results) == 2

    def test_execution_run_timestamp(self):
        """Test ExecutionRun timestamp is auto-generated."""
        run = ExecutionRun(
            execution_id="exec_123",
            run_number=1,
            eval_set_id="set_123",
            eval_case_id="case_123",
            provider_type="mock",
            provider_result=ProviderResult(conversation_history=[]),
            overall_success=True
        )
        assert isinstance(run.timestamp, datetime)


class TestEvaluationReport:
    """Test EvaluationReport model."""

    def test_evaluation_report_creation(self):
        """Test EvaluationReport creation."""
        report = EvaluationReport(
            execution_runs=[],
            summary={"total": 10, "passed": 8, "failed": 2},
            total_cost=0.50,
            total_time=15.5,
            success_rate=0.8,
            overall_success=True
        )
        assert report.overall_success is True
        assert report.total_cost == 0.50
        assert report.success_rate == 0.8

    def test_evaluation_report_with_runs(self):
        """Test EvaluationReport with execution runs."""
        runs = [
            ExecutionRun(
                execution_id=f"exec_{i}",
                run_number=i,
                eval_set_id="set_123",
                eval_case_id=f"case_{i}",
                provider_type="mock",
                provider_result=ProviderResult(conversation_history=[]),
                overall_success=True
            )
            for i in range(3)
        ]
        report = EvaluationReport(
            execution_runs=runs,
            overall_success=True
        )
        assert len(report.execution_runs) == 3

    def test_evaluation_report_timestamp(self):
        """Test EvaluationReport timestamp is auto-generated."""
        report = EvaluationReport(
            execution_runs=[],
            overall_success=True
        )
        assert isinstance(report.generated_at, datetime)

    def test_evaluation_report_defaults(self):
        """Test EvaluationReport default values."""
        report = EvaluationReport(
            execution_runs=[],
            overall_success=True
        )
        assert report.total_cost == 0.0
        assert report.total_time == 0.0
        assert report.success_rate == 0.0
        assert report.summary == {}
