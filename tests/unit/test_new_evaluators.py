"""Unit tests for new evaluators"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from judge_llm.core.models import (
    EvalCase, ProviderResult, Invocation, Content, Part,
    IntermediateData, ToolUse, SessionInput
)
from judge_llm.evaluators.subagent_evaluator import SubAgentEvaluator
from judge_llm.evaluators.trajectory_evaluator import TrajectoryEvaluator
from judge_llm.evaluators.llm_judge_evaluator import LLMJudgeEvaluator
from judge_llm.evaluators.embedding_similarity_evaluator import EmbeddingSimilarityEvaluator


# Test fixtures
@pytest.fixture
def sample_eval_case():
    """Create a sample eval case for testing"""
    return EvalCase(
        eval_id="test_001",
        session_input=SessionInput(
            app_name="test_app",
            user_id="test_user",
        ),
        conversation=[
            Invocation(
                invocation_id="inv_001",
                user_content=Content(
                    parts=[Part(text="What are flights from NYC to LA?")],
                    role="user"
                ),
                final_response=Content(
                    parts=[Part(text="I found several flight options from NYC to LA.")],
                    role="model"
                ),
                intermediate_data=IntermediateData(
                    tool_uses=[
                        ToolUse(id="t1", name="transfer_to_agent", args={"agent_name": "FlightSearchAgent"}),
                        ToolUse(id="t2", name="search_flights", args={"from": "NYC", "to": "LA"}),
                    ],
                    intermediate_responses=[
                        {"type": "agent_transfer", "from_agent": "Coordinator", "to_agent": "FlightSearchAgent"}
                    ]
                ),
                creation_timestamp=1234567890.0
            )
        ],
        creation_timestamp=1234567890.0
    )


@pytest.fixture
def sample_provider_result():
    """Create a sample provider result for testing"""
    return ProviderResult(
        conversation_history=[
            Invocation(
                invocation_id="inv_001",
                user_content=Content(
                    parts=[Part(text="What are flights from NYC to LA?")],
                    role="user"
                ),
                final_response=Content(
                    parts=[Part(text="Here are flights from New York to Los Angeles.")],
                    role="model"
                ),
                intermediate_data=IntermediateData(
                    tool_uses=[
                        ToolUse(id="t1", name="transfer_to_agent", args={"agent_name": "FlightSearchAgent"}),
                        ToolUse(id="t2", name="search_flights", args={"origin": "NYC", "destination": "LA"}),
                    ],
                    intermediate_responses=[
                        {"type": "agent_transfer", "from_agent": "Coordinator", "to_agent": "FlightSearchAgent"}
                    ]
                ),
                creation_timestamp=1234567890.0
            )
        ],
        success=True,
        metadata={"agent_chain": ["Coordinator", "FlightSearchAgent"]}
    )


# =============================================================================
# SubAgentEvaluator Tests
# =============================================================================

class TestSubAgentEvaluator:
    """Tests for SubAgentEvaluator"""

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = SubAgentEvaluator()
        assert evaluator.get_evaluator_name() == "SubAgentEvaluator"
        assert evaluator.get_evaluator_type() == "subagent"

    def test_extract_agent_chain_from_intermediate_responses(self, sample_eval_case):
        """Test extracting agent chain from intermediate_responses"""
        evaluator = SubAgentEvaluator()
        invocation = sample_eval_case.conversation[0]
        agents = evaluator._extract_agent_chain(invocation)
        assert "Coordinator" in agents or "FlightSearchAgent" in agents

    def test_extract_agent_chain_from_tool_uses(self):
        """Test extracting agent chain from transfer_to_agent tool uses"""
        evaluator = SubAgentEvaluator()
        invocation = Invocation(
            invocation_id="test",
            user_content=Content(parts=[Part(text="test")], role="user"),
            final_response=Content(parts=[Part(text="response")], role="model"),
            intermediate_data=IntermediateData(
                tool_uses=[
                    ToolUse(id="t1", name="transfer_to_agent", args={"agent_name": "AgentA"}),
                    ToolUse(id="t2", name="transfer_to_agent", args={"agent_name": "AgentB"}),
                ],
            ),
            creation_timestamp=0.0
        )
        agents = evaluator._extract_agent_chain(invocation)
        assert "AgentA" in agents
        assert "AgentB" in agents

    def test_compare_agent_chains_exact_match(self):
        """Test exact agent chain matching"""
        evaluator = SubAgentEvaluator()
        expected = ["AgentA", "AgentB"]
        actual = ["AgentA", "AgentB"]
        score, details = evaluator._compare_agent_chains(expected, actual, "exact", True)
        assert score == 1.0
        assert details["exact_match"] is True

    def test_compare_agent_chains_contains(self):
        """Test contains matching"""
        evaluator = SubAgentEvaluator()
        expected = ["AgentA"]
        actual = ["AgentA", "AgentB", "AgentC"]
        score, details = evaluator._compare_agent_chains(expected, actual, "contains", True)
        assert score == 1.0
        assert details["all_expected_present"] is True

    def test_compare_agent_chains_flexible(self):
        """Test flexible matching"""
        evaluator = SubAgentEvaluator()
        expected = ["AgentA", "AgentB"]
        actual = ["AgentB", "AgentC"]
        score, details = evaluator._compare_agent_chains(expected, actual, "flexible", True)
        assert 0 < score < 1  # Partial match
        assert "overlap_agents" in details

    def test_evaluate_success(self, sample_eval_case, sample_provider_result):
        """Test successful evaluation"""
        evaluator = SubAgentEvaluator(config={"sequence_match_type": "contains"})
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        assert result.success is True
        assert result.score is not None

    def test_evaluate_provider_failure(self, sample_eval_case):
        """Test handling of provider failure"""
        evaluator = SubAgentEvaluator()
        failed_result = ProviderResult(
            conversation_history=[],
            success=False,
            error="Provider failed"
        )
        result = evaluator.evaluate(sample_eval_case, {}, failed_result)
        assert result.success is False
        assert result.passed is False


# =============================================================================
# Enhanced TrajectoryEvaluator Tests
# =============================================================================

class TestEnhancedTrajectoryEvaluator:
    """Tests for enhanced TrajectoryEvaluator with argument comparison"""

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = TrajectoryEvaluator()
        assert evaluator.get_evaluator_name() == "TrajectoryEvaluator"

    def test_match_tool_name_exact(self):
        """Test exact tool name matching"""
        evaluator = TrajectoryEvaluator()
        assert evaluator._match_tool_name("search", "search", "exact") is True
        assert evaluator._match_tool_name("search", "Search", "exact") is False

    def test_match_tool_name_contains(self):
        """Test contains tool name matching"""
        evaluator = TrajectoryEvaluator()
        assert evaluator._match_tool_name("search", "google_search", "contains") is True
        assert evaluator._match_tool_name("google_search", "search", "contains") is True

    def test_match_tool_name_regex(self):
        """Test regex tool name matching"""
        evaluator = TrajectoryEvaluator()
        assert evaluator._match_tool_name("search.*", "search_flights", "regex") is True
        assert evaluator._match_tool_name("^search$", "search_flights", "regex") is False

    def test_compare_arguments_exact(self):
        """Test exact argument comparison"""
        evaluator = TrajectoryEvaluator()
        expected = {"from": "NYC", "to": "LA"}
        actual = {"from": "NYC", "to": "LA"}
        score = evaluator._compare_arguments(expected, actual, "exact", 0.8)
        assert score == 1.0

    def test_compare_arguments_subset(self):
        """Test subset argument comparison"""
        evaluator = TrajectoryEvaluator()
        expected = {"from": "NYC"}
        actual = {"from": "NYC", "to": "LA", "date": "2024-01-01"}
        score = evaluator._compare_arguments(expected, actual, "subset", 0.8)
        assert score == 1.0

    def test_compare_arguments_fuzzy(self):
        """Test fuzzy argument comparison"""
        evaluator = TrajectoryEvaluator()
        expected = {"query": "flights from new york"}
        actual = {"query": "flights from New York to LA"}
        score = evaluator._compare_arguments(expected, actual, "fuzzy", 0.5)
        assert score > 0.5

    def test_exact_sequence_match(self, sample_eval_case, sample_provider_result):
        """Test exact sequence matching"""
        evaluator = TrajectoryEvaluator(config={
            "sequence_match_type": "exact",
            "compare_arguments": False
        })
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        assert result.success is True

    def test_flexible_match(self, sample_eval_case, sample_provider_result):
        """Test flexible matching"""
        evaluator = TrajectoryEvaluator(config={
            "sequence_match_type": "flexible",
            "compare_arguments": False
        })
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        assert result.success is True

    def test_with_argument_comparison(self, sample_eval_case, sample_provider_result):
        """Test with argument comparison enabled"""
        evaluator = TrajectoryEvaluator(config={
            "sequence_match_type": "flexible",
            "compare_arguments": True,
            "argument_match_type": "fuzzy"
        })
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        assert result.success is True
        assert "argument_matches" in result.details["tool_matches"][0]


# =============================================================================
# LLMJudgeEvaluator Tests
# =============================================================================

class TestLLMJudgeEvaluator:
    """Tests for LLMJudgeEvaluator"""

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = LLMJudgeEvaluator()
        assert evaluator.get_evaluator_name() == "LLMJudgeEvaluator"
        assert evaluator.get_evaluator_type() == "llmjudge"

    def test_init_without_api_key(self):
        """Test initialization without API key"""
        evaluator = LLMJudgeEvaluator()
        # Client should be None initially (lazy init)
        assert evaluator._client is None

    def test_parse_json_response_direct(self):
        """Test parsing direct JSON response"""
        evaluator = LLMJudgeEvaluator()
        result = evaluator._parse_json_response('{"score": 4, "reasoning": "Good"}')
        assert result is not None
        assert result["score"] == 4

    def test_parse_json_response_markdown(self):
        """Test parsing JSON in markdown code block"""
        evaluator = LLMJudgeEvaluator()
        result = evaluator._parse_json_response('```json\n{"score": 4}\n```')
        assert result is not None
        assert result["score"] == 4

    def test_parse_json_response_with_text(self):
        """Test parsing JSON with surrounding text"""
        evaluator = LLMJudgeEvaluator()
        result = evaluator._parse_json_response('Here is my evaluation: {"score": 4}')
        assert result is not None
        assert result["score"] == 4

    def test_evaluate_without_client(self, sample_eval_case, sample_provider_result):
        """Test evaluation returns error without client"""
        evaluator = LLMJudgeEvaluator()
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        # Should fail gracefully without API key
        assert result.success is False
        assert "not available" in result.error

    @patch('judge_llm.evaluators.llm_judge_evaluator.LLMJudgeEvaluator._get_client')
    def test_evaluate_with_mock_client(self, mock_get_client, sample_eval_case, sample_provider_result):
        """Test evaluation with mocked client"""
        # Create mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"overall_score": 4, "reasoning": "Good response"}'
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        evaluator = LLMJudgeEvaluator(config={"evaluation_type": "comprehensive"})
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)

        assert result.success is True
        assert result.score is not None


# =============================================================================
# EmbeddingSimilarityEvaluator Tests
# =============================================================================

class TestEmbeddingSimilarityEvaluator:
    """Tests for EmbeddingSimilarityEvaluator"""

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = EmbeddingSimilarityEvaluator()
        assert evaluator.get_evaluator_name() == "EmbeddingSimilarityEvaluator"
        assert evaluator.get_evaluator_type() == "embeddingsimilarity"

    def test_get_default_model(self):
        """Test default model selection"""
        evaluator = EmbeddingSimilarityEvaluator()
        assert evaluator._get_default_model("gemini") == "text-embedding-004"
        assert evaluator._get_default_model("openai") == "text-embedding-3-small"
        assert evaluator._get_default_model("sentence_transformers") == "all-MiniLM-L6-v2"

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        evaluator = EmbeddingSimilarityEvaluator()

        # Identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        assert evaluator._cosine_similarity(vec1, vec2) == pytest.approx(1.0)

        # Orthogonal vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        assert evaluator._cosine_similarity(vec1, vec2) == pytest.approx(0.0)

        # Similar vectors
        vec1 = [1.0, 0.5, 0.0]
        vec2 = [1.0, 0.6, 0.0]
        sim = evaluator._cosine_similarity(vec1, vec2)
        assert 0.9 < sim < 1.0

    def test_chunk_text(self):
        """Test text chunking"""
        evaluator = EmbeddingSimilarityEvaluator()
        text = "This is a test sentence. " * 50  # Long text
        chunks = evaluator._chunk_text(text, max_length=100)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 150  # Allow some flexibility

    def test_average_embeddings(self):
        """Test embedding averaging"""
        evaluator = EmbeddingSimilarityEvaluator()
        embeddings = [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
        ]
        avg = evaluator._average_embeddings(embeddings)
        assert avg == [2.0, 3.0, 4.0]

    def test_evaluate_without_client(self, sample_eval_case, sample_provider_result):
        """Test evaluation returns error without client"""
        evaluator = EmbeddingSimilarityEvaluator()
        result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)
        # Should fail gracefully without API key
        assert result.success is False
        assert "not available" in result.error

    @patch('judge_llm.evaluators.embedding_similarity_evaluator.EmbeddingSimilarityEvaluator._get_embedder')
    def test_evaluate_with_mock_embedder(self, mock_get_embedder, sample_eval_case, sample_provider_result):
        """Test evaluation with mocked embedder"""
        # Create mock embedder
        mock_embedder = {"type": "mock"}
        mock_get_embedder.return_value = mock_embedder

        evaluator = EmbeddingSimilarityEvaluator()

        # Mock the _embed_single method
        with patch.object(evaluator, '_embed_single', return_value=[1.0, 0.5, 0.3]):
            result = evaluator.evaluate(sample_eval_case, {}, sample_provider_result)

        assert result.success is True
        assert result.score is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestEvaluatorRegistry:
    """Test that evaluators are properly registered"""

    def test_subagent_evaluator_registered(self):
        """Test SubAgentEvaluator is registered"""
        from judge_llm.core.registry import get_evaluator_registry
        registry = get_evaluator_registry()
        evaluator_class = registry.get("subagent_evaluator")
        assert evaluator_class == SubAgentEvaluator

    def test_llm_judge_evaluator_registered(self):
        """Test LLMJudgeEvaluator is registered"""
        from judge_llm.core.registry import get_evaluator_registry
        registry = get_evaluator_registry()
        evaluator_class = registry.get("llm_judge_evaluator")
        assert evaluator_class == LLMJudgeEvaluator

    def test_embedding_similarity_evaluator_registered(self):
        """Test EmbeddingSimilarityEvaluator is registered"""
        from judge_llm.core.registry import get_evaluator_registry
        registry = get_evaluator_registry()
        evaluator_class = registry.get("embedding_similarity_evaluator")
        assert evaluator_class == EmbeddingSimilarityEvaluator
