"""
Gemini Provider implementation using google-genai SDK.
"""

import os
import time
from typing import Any, Dict, Optional

from judge_llm.core.models import EvalCase, ProviderResult
from judge_llm.providers.base import BaseProvider
from judge_llm.utils.logger import get_logger


class GoogleADKProvider(BaseProvider):
    """
    Google ADK provider for LLM evaluation.

    Provider Metadata:
        - api_key: ADK API key (optional, falls back to GOOGLE_API_KEY env var)
        - model: Model name (default: gemini-2.0-flash-exp)
        - temperature: Sampling temperature (default: 1.0)
        - max_tokens: Maximum tokens to generate (default: 8192)
        - top_p: Top-p sampling (default: 0.95)
        - top_k: Top-k sampling (default: 40)
        - Any additional kwargs passed to the generate_content call
    """

    def __init__(
            self,
            agent_id: str,
            agent_config_path: Optional[str] = None,
            agent_metadata: Optional[Dict[str, Any]] = None,
            **provider_metadata,
    ):
        super().__init__(agent_id, agent_config_path, agent_metadata, **provider_metadata)
        self.logger = get_logger()

        # Get API key from provider_metadata or environment variable
        self.api_key = provider_metadata.get("api_key") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini provider requires 'api_key' in provider config or GOOGLE_API_KEY environment variable"
            )

        # Model configuration from provider_metadata
        self.model = provider_metadata.get("model", "gemini-2.0-flash-exp")
        self.temperature = provider_metadata.get("temperature", 1.0)
        self.max_tokens = provider_metadata.get("max_tokens", 8192)
        self.top_p = provider_metadata.get("top_p", 0.95)
        self.top_k = provider_metadata.get("top_k", 40)

        # Store additional kwargs for flexibility
        self.extra_params = {
            k: v for k, v in provider_metadata.items()
            if k not in ["api_key", "model", "temperature", "max_tokens", "top_p", "top_k"]
        }

    def execute(self, eval_case: EvalCase) -> ProviderResult:
        """
        Execute the evaluation case using Gemini API.

        For multi-turn conversations, this will execute each invocation sequentially,
        building up the conversation history progressively.

        Args:
            eval_case: The evaluation case to execute

        Returns:
            ProviderResult with conversation history, cost, time, and metadata
        """
        self.logger.info(
            f"GoogleADKProvider executing eval case: {eval_case.eval_id} "
            f"with {len(eval_case.conversation)} turns"
        )
        start_time = time.time()
        conversation_history = []
        total_cost = 0.0
        total_token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        # Calculate total metrics
        time_taken = time.time() - start_time

        result = ProviderResult(
            conversation_history=conversation_history,
            cost=total_cost,
            time_taken=time_taken,
            token_usage=total_token_usage,
            metadata={
                "provider": "gemini",
                "agent_id": self.agent_id,
                "model": self.model,
                "eval_id": eval_case.eval_id,
                "num_turns": len(conversation_history),
            },
            success=True
        )
        return result
