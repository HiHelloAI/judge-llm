"""
Gemini Provider implementation using google-genai SDK.
"""

from typing import Any, Dict, Optional
import os
import time
from google import genai
from google.genai import types

from judge_llm.providers.base import BaseProvider
from judge_llm.core.models import EvalCase, ProviderResult, Invocation, Content, Part
from judge_llm.utils.logger import get_logger


class GeminiProvider(BaseProvider):
    """
    Gemini provider for LLM evaluation.

    Provider Metadata:
        - api_key: Gemini API key (optional, falls back to GOOGLE_API_KEY env var)
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

        # Initialize client
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info(f"Initialized Gemini provider with model: {self.model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise

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
            f"GeminiProvider executing eval case: {eval_case.eval_id} "
            f"with {len(eval_case.conversation)} turns"
        )

        try:
            # Build system instruction if available
            system_instruction = None
            if eval_case.session_input.system_instruction:
                system_instruction = eval_case.session_input.system_instruction

            # Prepare generation config
            generation_config = types.GenerateContentConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_tokens,
                system_instruction=system_instruction,
                **self.extra_params
            )

            # Execute all turns in the conversation sequentially using a chat session
            # This ensures Gemini maintains context across all turns
            conversation_history = []
            total_cost = 0.0
            total_token_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }

            # Create a chat session to maintain conversation context
            chat_session = self.client.chats.create(
                model=self.model,
                config=generation_config
            )

            for turn_idx, invocation in enumerate(eval_case.conversation):
                self.logger.debug(
                    f"Executing turn {turn_idx + 1}/{len(eval_case.conversation)} "
                    f"for eval_id {eval_case.eval_id}"
                )

                # Extract user prompt from this invocation
                user_prompt = self._extract_user_prompt_from_invocation(invocation)

                if not user_prompt:
                    self.logger.warning(
                        f"No user prompt found for turn {turn_idx + 1}, skipping"
                    )
                    continue

                # Send message in chat session - this maintains conversation history
                response = chat_session.send_message(user_prompt)

                # Extract response text
                response_text = response.text if hasattr(response, 'text') else str(response)

                # Extract token usage for this turn
                turn_token_usage = {}
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    turn_token_usage = {
                        "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                        "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                        "total_tokens": getattr(usage, 'total_token_count', 0)
                    }

                    # Accumulate token usage
                    total_token_usage["prompt_tokens"] += turn_token_usage["prompt_tokens"]
                    total_token_usage["completion_tokens"] += turn_token_usage["completion_tokens"]
                    total_token_usage["total_tokens"] += turn_token_usage["total_tokens"]

                # Calculate cost for this turn
                turn_cost = self._calculate_cost(turn_token_usage)
                total_cost += turn_cost

                # Create invocation with actual Gemini response
                result_invocation = Invocation(
                    invocation_id=invocation.invocation_id,
                    user_content=invocation.user_content,
                    final_response=Content(
                        parts=[Part(text=response_text)],
                        role=None
                    ),
                    intermediate_data=invocation.intermediate_data,
                    creation_timestamp=invocation.creation_timestamp
                )

                conversation_history.append(result_invocation)

                self.logger.debug(
                    f"Turn {turn_idx + 1} completed: tokens={turn_token_usage.get('total_tokens', 0)}, "
                    f"cost=${turn_cost:.6f}, context maintained"
                )

            result = ProviderResult(
                conversation_history=conversation_history,
                cost=total_cost,
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

            self.logger.info(
                f"GeminiProvider completed {len(conversation_history)} turns, "
                f"total cost: ${total_cost:.6f}, total tokens: {total_token_usage['total_tokens']}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Gemini API error for eval_id {eval_case.eval_id}: {e}")

            return ProviderResult(
                conversation_history=[],
                cost=0.0,
                token_usage={},
                metadata={
                    "provider": "gemini",
                    "agent_id": self.agent_id,
                    "model": self.model,
                    "eval_id": eval_case.eval_id,
                    "error": str(e)
                },
                success=False
            )

    def _extract_user_prompt_from_invocation(self, invocation: Invocation) -> str:
        """Extract the user prompt from a single invocation.

        Args:
            invocation: The invocation to extract the user prompt from

        Returns:
            The user prompt text
        """
        if invocation.user_content and invocation.user_content.parts:
            for part in invocation.user_content.parts:
                if part.text:
                    return part.text

        return ""

    def _extract_user_prompt(self, eval_case: EvalCase) -> str:
        """Extract the user prompt from eval case (deprecated, kept for backwards compatibility)."""
        # First, try to get from session_input.user_prompt
        if eval_case.session_input.user_prompt:
            return eval_case.session_input.user_prompt

        # Otherwise, get the last user message from conversation
        for invocation in reversed(eval_case.conversation):
            if invocation.user_content:
                # Check if user_content has role="user" or extract text regardless
                if invocation.user_content.parts:
                    text = invocation.user_content.parts[0].text
                    if text:
                        return text

        return "Please respond to the evaluation case."

    def _build_result_conversation(
        self, eval_case: EvalCase, response_text: str
    ) -> list[Invocation]:
        """
        Build conversation history matching the expected format.

        Returns a list with a single Invocation containing both user and model response.
        """
        import uuid

        # Get user content from eval case
        user_content = None
        for invocation in eval_case.conversation:
            if invocation.user_content:
                user_content = invocation.user_content
                break

        # If no user content found in conversation, create from session_input
        if not user_content and hasattr(eval_case.session_input, 'user_prompt'):
            user_content = Content(
                parts=[Part(text=eval_case.session_input.user_prompt)],
                role="user"
            )
        elif not user_content:
            # Fallback: create minimal user content
            user_content = Content(
                parts=[Part(text="")],
                role="user"
            )

        # Create model response content
        final_response = Content(
            parts=[Part(text=response_text)],
            role=None  # final_response typically has role=None
        )

        # Create invocation with both user and model content
        invocation = Invocation(
            invocation_id=f"gemini-{uuid.uuid4()}",
            user_content=user_content,
            final_response=final_response,
            creation_timestamp=time.time()
        )

        return [invocation]

    def _calculate_cost(self, token_usage: Dict[str, int]) -> float:
        """
        Calculate approximate cost based on Gemini pricing.

        Gemini 2.0 Flash pricing (approximate):
        - Input: $0.075 per 1M tokens
        - Output: $0.30 per 1M tokens

        Note: Update these rates based on actual Gemini pricing.
        """
        if not token_usage:
            return 0.0

        input_tokens = token_usage.get("prompt_tokens", 0)
        output_tokens = token_usage.get("completion_tokens", 0)

        # Pricing per million tokens
        input_cost_per_million = 0.075
        output_cost_per_million = 0.30

        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million

        return input_cost + output_cost

    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up Gemini provider")
        # Gemini client doesn't require explicit cleanup
        pass
