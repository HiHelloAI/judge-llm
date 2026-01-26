"""Unit tests for ADK HTTP Provider components."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json

from judge_llm.core.models import (
    Content,
    EvalCase,
    Invocation,
    IntermediateData,
    Part,
    ProviderResult,
    SessionInput,
    ToolUse,
)
from judge_llm.providers.adk_http.models import (
    ADKEvent,
    ADKContent,
    ADKPart,
    ADKFunctionCall,
    ADKFunctionResponse,
    ADKUsageMetadata,
    ADKActions,
)
from judge_llm.providers.adk_http.sse_parser import SSEParser
from judge_llm.providers.adk_http.event_mapper import EventMapper
from judge_llm.providers.adk_http.session_manager import SessionManager
from judge_llm.providers.adk_http.pricing import PricingCalculator


class TestADKModels:
    """Tests for ADK event Pydantic models."""

    def test_adk_function_call(self):
        """Test ADKFunctionCall model."""
        fc = ADKFunctionCall(
            id="fc_001",
            name="search_flights",
            args={"origin": "SFO", "destination": "TYO"},
        )
        assert fc.id == "fc_001"
        assert fc.name == "search_flights"
        assert fc.args["origin"] == "SFO"

    def test_adk_function_response(self):
        """Test ADKFunctionResponse model."""
        fr = ADKFunctionResponse(
            id="fr_001",
            name="search_flights",
            response={"results": ["Flight 1", "Flight 2"]},
        )
        assert fr.id == "fr_001"
        assert fr.name == "search_flights"
        assert len(fr.response["results"]) == 2

    def test_adk_part_with_text(self):
        """Test ADKPart with text."""
        part = ADKPart(text="Hello, how can I help?")
        assert part.text == "Hello, how can I help?"
        assert part.functionCall is None
        assert part.functionResponse is None

    def test_adk_part_with_function_call(self):
        """Test ADKPart with function call."""
        part = ADKPart(
            functionCall=ADKFunctionCall(
                id="fc_001",
                name="transfer_to_agent",
                args={"agent_name": "SearchAgent"},
            )
        )
        assert part.functionCall is not None
        assert part.functionCall.name == "transfer_to_agent"

    def test_adk_content(self):
        """Test ADKContent model."""
        content = ADKContent(
            parts=[ADKPart(text="Hello!")],
            role="model",
        )
        assert len(content.parts) == 1
        assert content.role == "model"

    def test_adk_usage_metadata(self):
        """Test ADKUsageMetadata model."""
        usage = ADKUsageMetadata(
            candidatesTokenCount=50,
            promptTokenCount=100,
            totalTokenCount=150,
        )
        assert usage.candidatesTokenCount == 50
        assert usage.promptTokenCount == 100
        assert usage.totalTokenCount == 150

    def test_adk_actions(self):
        """Test ADKActions model."""
        actions = ADKActions(
            stateDelta={"key": "value"},
            transferToAgent="SearchAgent",
        )
        assert actions.stateDelta["key"] == "value"
        assert actions.transferToAgent == "SearchAgent"

    def test_adk_event_full(self):
        """Test full ADKEvent model."""
        event = ADKEvent(
            modelVersion="gemini-2.0-flash",
            content=ADKContent(
                parts=[ADKPart(text="Hello!")],
                role="model",
            ),
            finishReason="STOP",
            usageMetadata=ADKUsageMetadata(
                candidatesTokenCount=10,
                promptTokenCount=20,
                totalTokenCount=30,
            ),
            invocationId="inv_001",
            author="TravelCoordinator",
            timestamp=1704067200.0,
        )
        assert event.modelVersion == "gemini-2.0-flash"
        assert event.finishReason == "STOP"
        assert event.author == "TravelCoordinator"

    def test_adk_event_from_json(self):
        """Test ADKEvent parsing from JSON."""
        json_data = {
            "modelVersion": "gemini-2.0-flash",
            "content": {
                "parts": [{"text": "Hello!"}],
                "role": "model",
            },
            "usageMetadata": {
                "candidatesTokenCount": 43,
                "promptTokenCount": 619,
                "totalTokenCount": 662,
            },
            "invocationId": "e-xxx",
            "author": "TravelCoordinator",
            "timestamp": 1769308141.839758,
        }
        event = ADKEvent.model_validate(json_data)
        assert event.modelVersion == "gemini-2.0-flash"
        assert event.usageMetadata.totalTokenCount == 662


class TestSSEParser:
    """Tests for SSE stream parser."""

    def test_parse_line_data(self):
        """Test parsing a data line."""
        parser = SSEParser()
        result = parser.parse_line('data: {"text": "hello"}')
        assert result is not None
        assert result["text"] == "hello"

    def test_parse_line_empty(self):
        """Test parsing empty line."""
        parser = SSEParser()
        result = parser.parse_line("")
        assert result is None

    def test_parse_line_comment(self):
        """Test parsing comment line."""
        parser = SSEParser()
        result = parser.parse_line(": this is a comment")
        assert result is None

    def test_parse_line_invalid_json(self):
        """Test parsing invalid JSON."""
        parser = SSEParser()
        result = parser.parse_line("data: {invalid json}")
        assert result is None

    def test_parse_string_single_event(self):
        """Test parsing a single event from string."""
        parser = SSEParser()
        data = 'data: {"content": {"parts": [{"text": "Hello"}], "role": "model"}}'

        events = list(parser.parse_string(data))
        assert len(events) == 1
        assert events[0].content.parts[0].text == "Hello"

    def test_parse_string_multiple_events(self):
        """Test parsing multiple events from string."""
        parser = SSEParser()
        data = """data: {"content": {"parts": [{"text": "First"}], "role": "model"}}

data: {"content": {"parts": [{"text": "Second"}], "role": "model"}}"""

        events = list(parser.parse_string(data))
        assert len(events) == 2
        assert events[0].content.parts[0].text == "First"
        assert events[1].content.parts[0].text == "Second"

    def test_parse_string_with_function_call(self):
        """Test parsing event with function call."""
        parser = SSEParser()
        data = '''data: {"content": {"parts": [{"functionCall": {"id": "fc_001", "name": "search", "args": {"q": "test"}}}], "role": "model"}, "author": "Agent1"}'''

        events = list(parser.parse_string(data))
        assert len(events) == 1
        assert events[0].content.parts[0].functionCall.name == "search"
        assert events[0].author == "Agent1"


class TestEventMapper:
    """Tests for event mapper."""

    def test_map_simple_text_response(self):
        """Test mapping simple text response."""
        mapper = EventMapper()

        events = [
            ADKEvent(
                content=ADKContent(
                    parts=[ADKPart(text="Hello, how can I help?")],
                    role="model",
                ),
                author="Assistant",
            )
        ]

        original = Invocation(
            invocation_id="inv_1",
            user_content=Content(parts=[Part(text="Hi")], role="user"),
            final_response=Content(parts=[], role="model"),
            intermediate_data=IntermediateData(),
            creation_timestamp=1234567890.0,
        )

        result = mapper.map_to_invocation(events, original)

        assert result.final_response.parts[0].text == "Hello, how can I help?"
        assert result.invocation_id == "inv_1"

    def test_map_with_function_call(self):
        """Test mapping with function call."""
        mapper = EventMapper()

        events = [
            ADKEvent(
                content=ADKContent(
                    parts=[
                        ADKPart(
                            functionCall=ADKFunctionCall(
                                id="fc_001",
                                name="search_flights",
                                args={"origin": "SFO"},
                            )
                        )
                    ],
                    role="model",
                ),
                author="TravelAgent",
            )
        ]

        original = Invocation(
            invocation_id="inv_1",
            user_content=Content(parts=[Part(text="Find flights")], role="user"),
            final_response=Content(parts=[], role="model"),
            intermediate_data=IntermediateData(),
            creation_timestamp=1234567890.0,
        )

        result = mapper.map_to_invocation(events, original)

        assert len(result.intermediate_data.tool_uses) == 1
        assert result.intermediate_data.tool_uses[0].name == "search_flights"
        assert result.intermediate_data.tool_uses[0].args["origin"] == "SFO"

    def test_map_with_agent_transfer(self):
        """Test mapping with agent transfer."""
        mapper = EventMapper()

        events = [
            ADKEvent(
                content=ADKContent(
                    parts=[ADKPart(text="Transferring...")],
                    role="model",
                ),
                author="Coordinator",
                actions=ADKActions(transferToAgent="SearchExpert"),
            )
        ]

        original = Invocation(
            invocation_id="inv_1",
            user_content=Content(parts=[Part(text="Search")], role="user"),
            final_response=Content(parts=[], role="model"),
            intermediate_data=IntermediateData(),
            creation_timestamp=1234567890.0,
        )

        result = mapper.map_to_invocation(events, original)

        # Check agent transfer is recorded in intermediate responses
        transfers = [
            r
            for r in result.intermediate_data.intermediate_responses
            if r.get("type") == "agent_transfer"
        ]
        assert len(transfers) == 1
        assert transfers[0]["from_agent"] == "Coordinator"
        assert transfers[0]["to_agent"] == "SearchExpert"

    def test_aggregate_token_usage(self):
        """Test token usage aggregation."""
        mapper = EventMapper()

        events = [
            ADKEvent(
                usageMetadata=ADKUsageMetadata(
                    promptTokenCount=100,
                    candidatesTokenCount=50,
                    totalTokenCount=150,
                )
            ),
            ADKEvent(
                usageMetadata=ADKUsageMetadata(
                    promptTokenCount=150,
                    candidatesTokenCount=75,
                    totalTokenCount=225,
                )
            ),
        ]

        result = mapper.aggregate_token_usage(events)

        # Should take max values
        assert result["prompt_tokens"] == 150
        assert result["completion_tokens"] == 75
        assert result["total_tokens"] == 225

    def test_get_agent_chain(self):
        """Test getting agent chain."""
        mapper = EventMapper()

        events = [
            ADKEvent(author="Coordinator"),
            ADKEvent(author="Coordinator"),
            ADKEvent(author="SearchExpert"),
            ADKEvent(author="SearchExpert"),
            ADKEvent(author="ResultsOrganizer"),
        ]

        chain = mapper.get_agent_chain(events)
        assert chain == ["Coordinator", "SearchExpert", "ResultsOrganizer"]

    def test_extract_tool_uses(self):
        """Test extracting tool uses."""
        mapper = EventMapper()

        events = [
            ADKEvent(
                content=ADKContent(
                    parts=[
                        ADKPart(
                            functionCall=ADKFunctionCall(
                                id="fc_001", name="tool1", args={}
                            )
                        ),
                        ADKPart(
                            functionCall=ADKFunctionCall(
                                id="fc_002", name="tool2", args={}
                            )
                        ),
                    ],
                    role="model",
                )
            )
        ]

        tool_uses = mapper.extract_tool_uses(events)
        assert len(tool_uses) == 2
        assert tool_uses[0].name == "tool1"
        assert tool_uses[1].name == "tool2"


class TestSessionManager:
    """Tests for session manager."""

    def test_create_session(self):
        """Test session creation."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
        )

        assert session_id is not None
        assert session_id.startswith("eval_session_")

    def test_create_session_with_custom_id(self):
        """Test session creation with custom ID."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="custom_session_123",
        )

        assert session_id == "custom_session_123"

    def test_get_session(self):
        """Test getting session."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
            initial_state={"key": "value"},
        )

        session = manager.get_session(session_id)
        assert session is not None
        assert session.app_name == "test_app"
        assert session.user_id == "test_user"
        assert session.state["key"] == "value"

    def test_update_state(self):
        """Test updating session state."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
            initial_state={"key1": "value1"},
        )

        manager.update_state(session_id, {"key2": "value2"})

        session = manager.get_session(session_id)
        assert session.state["key1"] == "value1"
        assert session.state["key2"] == "value2"
        assert session.message_count == 1

    def test_close_session(self):
        """Test closing session."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
        )

        manager.close_session(session_id)

        session = manager.get_session(session_id)
        assert session.is_active is False

    def test_delete_session(self):
        """Test deleting session."""
        manager = SessionManager()
        session_id = manager.create_session(
            app_name="test_app",
            user_id="test_user",
        )

        manager.delete_session(session_id)

        session = manager.get_session(session_id)
        assert session is None

    def test_get_active_sessions(self):
        """Test getting active sessions."""
        manager = SessionManager()
        sid1 = manager.create_session(app_name="app", user_id="user")
        sid2 = manager.create_session(app_name="app", user_id="user")
        manager.close_session(sid2)

        active = manager.get_active_sessions()
        assert sid1 in active
        assert sid2 not in active


class TestPricingCalculator:
    """Tests for pricing calculator."""

    def test_calculate_cost_gemini_flash(self):
        """Test cost calculation for Gemini Flash."""
        calculator = PricingCalculator()

        cost = calculator.calculate_cost(
            model="gemini-2.0-flash",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )

        # $0.075 input + $0.30 output = $0.375
        assert cost == pytest.approx(0.375, rel=0.01)

    def test_calculate_cost_gemini_pro(self):
        """Test cost calculation for Gemini Pro."""
        calculator = PricingCalculator()

        cost = calculator.calculate_cost(
            model="gemini-1.5-pro",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )

        # $1.25 input + $5.00 output = $6.25
        assert cost == pytest.approx(6.25, rel=0.01)

    def test_calculate_cost_small_tokens(self):
        """Test cost calculation with small token counts."""
        calculator = PricingCalculator()

        cost = calculator.calculate_cost(
            model="gemini-2.0-flash",
            prompt_tokens=1000,
            completion_tokens=500,
        )

        # Very small cost
        expected = (1000 / 1_000_000 * 0.075) + (500 / 1_000_000 * 0.30)
        assert cost == pytest.approx(expected, rel=0.01)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model uses default."""
        calculator = PricingCalculator()

        cost = calculator.calculate_cost(
            model="unknown-model",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )

        # Default: $0.10 input + $0.40 output = $0.50
        assert cost == pytest.approx(0.50, rel=0.01)

    def test_custom_pricing(self):
        """Test custom pricing override."""
        calculator = PricingCalculator(
            custom_pricing={
                "custom-model": {"input": 1.0, "output": 2.0},
            }
        )

        cost = calculator.calculate_cost(
            model="custom-model",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )

        assert cost == pytest.approx(3.0, rel=0.01)

    def test_get_supported_models(self):
        """Test getting supported models."""
        calculator = PricingCalculator()
        models = calculator.get_supported_models()

        assert "gemini-2.0-flash" in models
        assert "gemini-1.5-pro" in models
        assert "default" not in models

    def test_estimate_cost(self):
        """Test cost estimation breakdown."""
        calculator = PricingCalculator()
        estimate = calculator.estimate_cost(
            model="gemini-2.0-flash",
            estimated_input_tokens=100_000,
            estimated_output_tokens=50_000,
        )

        assert "input_cost" in estimate
        assert "output_cost" in estimate
        assert "total_cost" in estimate
        assert estimate["total_cost"] == estimate["input_cost"] + estimate["output_cost"]


class TestADKHTTPProvider:
    """Tests for ADK HTTP Provider."""

    def test_provider_init_requires_endpoint(self):
        """Test that provider requires endpoint_url."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        with pytest.raises(ValueError, match="endpoint_url is required"):
            ADKHTTPProvider(agent_id="test")

    def test_provider_init_with_config(self):
        """Test provider initialization with config."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        provider = ADKHTTPProvider(
            agent_id="test_agent",
            endpoint_url="http://localhost:8000/run_sse",
            auth_type="bearer",
            api_key="test_key",
            timeout=120,
            model="gemini-2.0-flash",
        )

        assert provider.agent_id == "test_agent"
        assert provider.endpoint_url == "http://localhost:8000/run_sse"
        assert provider.auth_type == "bearer"
        assert provider.api_key == "test_key"
        assert provider.timeout == 120

    def test_provider_build_auth_headers_bearer(self):
        """Test building bearer auth headers."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
            auth_type="bearer",
            api_key="my_token",
        )

        headers = provider._build_auth_headers()
        assert headers["Authorization"] == "Bearer my_token"

    def test_provider_build_auth_headers_api_key(self):
        """Test building API key auth headers."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
            auth_type="api_key",
            api_key="my_key",
            auth_header="X-Custom-Key",
        )

        headers = provider._build_auth_headers()
        assert headers["X-Custom-Key"] == "my_key"

    def test_provider_build_auth_headers_basic(self):
        """Test building basic auth headers."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider
        import base64

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
            auth_type="basic",
            username="user",
            password="pass",
        )

        headers = provider._build_auth_headers()
        expected = base64.b64encode(b"user:pass").decode()
        assert headers["Authorization"] == f"Basic {expected}"

    def test_provider_build_auth_headers_none(self):
        """Test building no auth headers."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
            auth_type="none",
        )

        headers = provider._build_auth_headers()
        assert len(headers) == 0

    def test_provider_extract_user_message(self):
        """Test extracting user message from invocation."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
        )

        invocation = Invocation(
            invocation_id="inv_1",
            user_content=Content(
                parts=[Part(text="Hello"), Part(text="World")],
                role="user",
            ),
            final_response=Content(parts=[], role="model"),
            intermediate_data=IntermediateData(),
            creation_timestamp=1234567890.0,
        )

        message = provider._extract_user_message(invocation)
        assert message == "Hello World"

    @patch("httpx.Client")
    def test_provider_execute_success(self, mock_client_class):
        """Test successful execution with mocked HTTP."""
        from judge_llm.providers.adk_http_provider import ADKHTTPProvider

        # Setup mock response
        mock_response = MagicMock()
        mock_response.iter_bytes.return_value = iter([
            b'data: {"content": {"parts": [{"text": "Hello!"}], "role": "model"}, '
            b'"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5, "totalTokenCount": 15}, '
            b'"author": "Assistant"}\n\n'
        ])

        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_response)
        mock_context.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_context
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)

        mock_client_class.return_value = mock_client

        provider = ADKHTTPProvider(
            agent_id="test",
            endpoint_url="http://localhost:8000/run_sse",
        )

        eval_case = EvalCase(
            eval_id="test_1",
            conversation=[
                Invocation(
                    invocation_id="inv_1",
                    user_content=Content(parts=[Part(text="Hi")], role="user"),
                    final_response=Content(parts=[], role="model"),
                    intermediate_data=IntermediateData(),
                    creation_timestamp=1234567890.0,
                )
            ],
            session_input=SessionInput(app_name="test", user_id="user1", state={}),
            creation_timestamp=1234567890.0,
        )

        result = provider.execute(eval_case)

        assert result.success is True
        assert len(result.conversation_history) == 1
        assert result.token_usage["total_tokens"] == 15


# Mark all tests as unit tests
pytestmark = pytest.mark.unit
