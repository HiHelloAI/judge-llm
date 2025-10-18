"""Pytest configuration and shared fixtures for judge_llm tests."""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from judge_llm.core.models import (
    Part,
    Content,
    Invocation,
    IntermediateData,
    SessionInput,
    EvalCase,
    EvalSet,
    ExecutionRun,
    EvaluationReport,
    ProviderResult,
)


@pytest.fixture
def sample_part():
    """Create a sample Part instance."""
    return Part(text="What is the capital of France?")


@pytest.fixture
def sample_content():
    """Create a sample Content instance."""
    return Content(
        role="user",
        parts=[Part(text="What is the capital of France?")]
    )


@pytest.fixture
def sample_invocation():
    """Create a sample Invocation instance."""
    return Invocation(
        invocation_id="inv_1",
        user_content=Content(role="user", parts=[Part(text="Hello")]),
        final_response=Content(role="model", parts=[Part(text="Hi there!")]),
        intermediate_data=IntermediateData(),
        creation_timestamp=1234567890.0
    )


@pytest.fixture
def sample_eval_case():
    """Create a sample EvalCase instance."""
    return EvalCase(
        eval_id="test_case_1",
        conversation=[
            Invocation(
                invocation_id="inv_1",
                user_content=Content(role="user", parts=[Part(text="What is 2+2?")]),
                final_response=Content(role="model", parts=[Part(text="4")]),
                intermediate_data=IntermediateData(),
                creation_timestamp=1234567890.0
            )
        ],
        session_input=SessionInput(app_name="test", user_id="user1"),
        creation_timestamp=1234567890.0
    )


@pytest.fixture
def sample_eval_set():
    """Create a sample EvalSet with multiple cases."""
    return EvalSet(
        eval_set_id="set_1",
        name="test_set",
        description="A test evaluation set",
        eval_cases=[
            EvalCase(
                eval_id="case_1",
                conversation=[],
                session_input=SessionInput(app_name="test", user_id="user1"),
                creation_timestamp=1234567890.0
            ),
            EvalCase(
                eval_id="case_2",
                conversation=[],
                session_input=SessionInput(app_name="test", user_id="user2"),
                creation_timestamp=1234567890.0
            ),
        ],
        creation_timestamp=1234567890.0
    )


@pytest.fixture
def sample_execution_run():
    """Create a sample ExecutionRun instance."""
    return ExecutionRun(
        execution_id="exec_1",
        run_number=1,
        eval_set_id="set_1",
        eval_case_id="test_case_1",
        provider_type="mock",
        provider_result=ProviderResult(
            conversation_history=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            cost=0.001,
            time_taken=0.1,
            success=True
        ),
        evaluator_results=[],
        overall_success=True
    )


@pytest.fixture
def sample_evaluation_report():
    """Create a sample EvaluationReport instance."""
    return EvaluationReport(
        execution_runs=[],
        summary={
            "total_cases": 1,
            "passed": 1,
            "failed": 0,
            "total_cost_usd": 0.001,
            "total_latency_ms": 100.0
        },
        total_cost=0.001,
        total_time=0.1,
        success_rate=1.0,
        overall_success=True
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Create a sample configuration dictionary."""
    return {
        "provider": {
            "name": "mock",
            "config": {"model": "mock-model"}
        },
        "evaluators": [
            {
                "name": "response",
                "type": "response",
                "config": {
                    "method": "rouge",
                    "threshold": 0.7
                }
            }
        ],
        "reporters": [
            {"name": "console", "type": "console"}
        ],
        "execution": {
            "parallel": True,
            "max_workers": 4
        }
    }


@pytest.fixture
def sample_eval_set_json(temp_dir):
    """Create a sample evaluation set JSON file."""
    eval_set_data = {
        "eval_set_id": "test_set_1",
        "name": "test_set",
        "description": "Test evaluation set",
        "creation_timestamp": 1234567890.0,
        "eval_cases": [
            {
                "eval_id": "case_1",
                "conversation": [],
                "session_input": {
                    "app_name": "test",
                    "user_id": "user1"
                },
                "creation_timestamp": 1234567890.0
            },
            {
                "eval_id": "case_2",
                "conversation": [],
                "session_input": {
                    "app_name": "test",
                    "user_id": "user2"
                },
                "creation_timestamp": 1234567890.0
            }
        ]
    }

    file_path = temp_dir / "test_evalset.json"
    with open(file_path, "w") as f:
        json.dump(eval_set_data, f, indent=2)

    return file_path


@pytest.fixture
def sample_config_yaml(temp_dir):
    """Create a sample configuration YAML file."""
    import yaml

    config = {
        "provider": {
            "name": "mock",
            "config": {"model": "mock-model"}
        },
        "evaluators": [
            {
                "name": "response",
                "type": "response",
                "config": {"method": "rouge", "threshold": 0.7}
            }
        ],
        "reporters": [
            {"name": "console", "type": "console"}
        ]
    }

    file_path = temp_dir / "test_config.yaml"
    with open(file_path, "w") as f:
        yaml.dump(config, f)

    return file_path


@pytest.fixture(autouse=True)
def reset_registries():
    """Reset registries before each test to avoid pollution."""
    from judge_llm.core.registry import ProviderRegistry, EvaluatorRegistry

    # Store original registries
    original_providers = ProviderRegistry._providers.copy()
    original_evaluators = EvaluatorRegistry._evaluators.copy()

    yield

    # Restore original registries
    ProviderRegistry._providers = original_providers
    EvaluatorRegistry._evaluators = original_evaluators


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    return _set_env
