"""Mock provider for testing and examples"""

from typing import Any, Dict, Optional
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part
from judge_llm.providers.base import BaseProvider
from judge_llm.utils.logger import get_logger


class MockProvider(BaseProvider):
    """Mock provider that echoes back the expected responses"""

    def __init__(
        self,
        agent_id: str,
        agent_config_path: Optional[str] = None,
        agent_metadata: Optional[Dict[str, Any]] = None,
        **provider_metadata,
    ):
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)
        self.logger = get_logger()

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """Execute evaluation case (mock implementation)

        Args:
            eval_case: Evaluation case to execute

        Returns:
            ProviderResult with conversation history
        """
        self.logger.info(f"MockProvider executing eval case: {eval_case.eval_id}")

        # Simply copy the conversation from the eval case
        # In a real provider, this would call the actual LLM
        conversation_history = eval_case.conversation.copy()

        # Mock cost and token usage
        total_tokens = sum(
            len(inv.user_content.parts[0].text or "")
            + len(inv.final_response.parts[0].text or "")
            for inv in conversation_history
        )

        result = ProviderResult(
            conversation_history=conversation_history,
            cost=total_tokens * 0.00001,  # Mock cost calculation
            token_usage={
                "prompt_tokens": total_tokens // 2,
                "completion_tokens": total_tokens // 2,
                "total_tokens": total_tokens,
            },
            metadata={
                "provider": "mock",
                "agent_id": self.agent_id,
                "model": "mock-model-v1",
            },
            success=True,
        )

        self.logger.debug(
            f"MockProvider completed, "
            f"cost: ${result.cost:.4f}, tokens: {total_tokens}"
        )

        return result

    def cleanup(self):
        """Cleanup resources"""
        self.logger.debug("MockProvider cleanup completed")
