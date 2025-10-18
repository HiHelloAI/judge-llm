"""Unit tests for providers."""

import pytest
from judge_llm.core.models import (
    Part,
    Content,
    SessionInput,
    EvalCase,
    Invocation,
    IntermediateData,
)
from judge_llm.providers.mock_provider import MockProvider
from judge_llm.core.registry import ProviderRegistry, EvaluatorRegistry


class TestMockProvider:
    """Test MockProvider class."""

    def test_mock_provider_creation(self):
        """Test MockProvider instantiation."""
        provider = MockProvider(agent_id="test_agent")
        assert provider is not None

    def test_mock_provider_with_metadata(self):
        """Test MockProvider with metadata."""
        provider = MockProvider(
            agent_id="test_agent",
            agent_metadata={"version": "1.0"}
        )
        assert provider is not None

    def test_mock_provider_execute_simple(self):
        """Test simple execution with MockProvider."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi there!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        assert result is not None
        assert result.success is True
        assert len(result.conversation_history) > 0

    def test_mock_provider_execute_multiple_turns(self):
        """Test multi-turn conversation execution."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                ),
                Invocation(
                    invocation_id="inv_2",
                    user_content=Content(role="user", parts=[Part(text="How are you?")]),
                    final_response=Content(role="model", parts=[Part(text="Good!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        assert result.success is True
        assert len(result.conversation_history) == 2

    def test_mock_provider_cost_tracking(self):
        """Test that MockProvider tracks costs."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        assert result.cost >= 0

    def test_mock_provider_latency_tracking(self):
        """Test that MockProvider tracks latency."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        assert result.time_taken >= 0

    def test_mock_provider_metadata(self):
        """Test that MockProvider includes metadata."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(role="user", parts=[Part(text="Hello")]),
                    final_response=Content(role="model", parts=[Part(text="Hi!")]),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        assert isinstance(result.metadata, dict)

    def test_mock_provider_empty_conversation(self):
        """Test MockProvider with empty conversation."""
        provider = MockProvider(agent_id="test_agent")

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[],
            session_input=SessionInput(app_name="test", user_id="user1"),
            creation_timestamp=1234567890.0
        )

        result = provider.execute(eval_case)

        # Should handle gracefully
        assert result is not None


class TestProviderRegistry:
    """Test provider registry functionality."""

    def test_register_provider(self):
        """Test registering a custom provider."""
        class CustomProvider:
            def __init__(self, agent_id, **kwargs):
                self.agent_id = agent_id

            def execute(self, eval_case):
                pass

        # Register provider using the singleton instance
        registry = ProviderRegistry()
        registry.register("custom", CustomProvider)

        # Verify registration
        assert "custom" in ProviderRegistry._providers

    def test_get_provider(self):
        """Test getting a registered provider."""
        # Get mock provider using the singleton instance
        registry = ProviderRegistry()
        provider_class = registry.get("mock")

        assert provider_class is not None
        assert provider_class == MockProvider

    def test_get_all_providers(self):
        """Test getting all registered providers."""
        providers = ProviderRegistry._providers

        assert isinstance(providers, dict)
        assert "mock" in providers
