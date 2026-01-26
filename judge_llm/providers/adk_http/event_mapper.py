"""Event mapper for converting ADK events to framework models."""

from typing import Any, Dict, List, Optional

from judge_llm.core.models import (
    Content,
    IntermediateData,
    Invocation,
    Part,
    ToolUse,
)
from judge_llm.providers.adk_http.models import ADKEvent


class EventMapper:
    """Maps ADK SSE events to framework models.

    Handles the conversion of ADK-specific event structures to the
    judge-llm framework's Invocation, Content, Part, and ToolUse models.
    """

    def map_to_invocation(
        self,
        events: List[ADKEvent],
        original_invocation: Invocation,
    ) -> Invocation:
        """Map a sequence of ADK events to a framework Invocation.

        Strategy:
        1. Collect all text parts from model responses for final_response
        2. Extract all functionCall events as tool_uses
        3. Track agent transfers and function responses as intermediate_responses
        4. Use the last event's timestamp

        Args:
            events: List of ADK events from a single conversation turn
            original_invocation: The original invocation with user content

        Returns:
            Invocation with actual response data from ADK events
        """
        final_text_parts: List[str] = []
        tool_uses: List[ToolUse] = []
        intermediate_responses: List[Dict[str, Any]] = []

        for event in events:
            if not event.content:
                continue

            for part in event.content.parts:
                # Collect text parts from model responses
                if part.text and event.content.role == "model":
                    final_text_parts.append(part.text)

                # Extract function calls as tool uses
                if part.functionCall:
                    fc = part.functionCall
                    tool_uses.append(
                        ToolUse(
                            id=fc.id,
                            name=fc.name,
                            args=fc.args,
                        )
                    )

                    # Also track as intermediate response with agent context
                    if event.author:
                        intermediate_responses.append(
                            {
                                "type": "function_call",
                                "agent_name": event.author,
                                "function_name": fc.name,
                                "function_id": fc.id,
                                "args": fc.args,
                                "timestamp": event.timestamp,
                            }
                        )

                # Track function responses
                if part.functionResponse:
                    fr = part.functionResponse
                    intermediate_responses.append(
                        {
                            "type": "function_response",
                            "function_id": fr.id,
                            "function_name": fr.name,
                            "response": fr.response,
                            "timestamp": event.timestamp,
                        }
                    )

            # Track agent transfers
            if event.actions and event.actions.transferToAgent:
                intermediate_responses.append(
                    {
                        "type": "agent_transfer",
                        "from_agent": event.author,
                        "to_agent": event.actions.transferToAgent,
                        "timestamp": event.timestamp,
                    }
                )

        # Build final response content
        combined_text = " ".join(final_text_parts) if final_text_parts else ""
        final_response = Content(
            parts=[Part(text=combined_text)] if combined_text else [],
            role="model",
        )

        # Build intermediate data
        intermediate_data = IntermediateData(
            tool_uses=tool_uses,
            intermediate_responses=intermediate_responses,
        )

        # Get timestamp from last event or use original
        last_timestamp = (
            events[-1].timestamp
            if events and events[-1].timestamp
            else original_invocation.creation_timestamp
        )

        return Invocation(
            invocation_id=original_invocation.invocation_id,
            user_content=original_invocation.user_content,
            final_response=final_response,
            intermediate_data=intermediate_data,
            creation_timestamp=last_timestamp,
        )

    def extract_tool_uses(self, events: List[ADKEvent]) -> List[ToolUse]:
        """Extract all tool uses from a list of events.

        Args:
            events: List of ADK events

        Returns:
            List of ToolUse objects
        """
        tool_uses: List[ToolUse] = []

        for event in events:
            if event.content:
                for part in event.content.parts:
                    if part.functionCall:
                        fc = part.functionCall
                        tool_uses.append(
                            ToolUse(
                                id=fc.id,
                                name=fc.name,
                                args=fc.args,
                            )
                        )

        return tool_uses

    def get_agent_chain(self, events: List[ADKEvent]) -> List[str]:
        """Get the sequence of agents that handled the request.

        Args:
            events: List of ADK events

        Returns:
            List of agent names in order of handling
        """
        agents: List[str] = []

        for event in events:
            if event.author and (not agents or agents[-1] != event.author):
                agents.append(event.author)

        return agents

    def aggregate_token_usage(self, events: List[ADKEvent]) -> Dict[str, int]:
        """Aggregate token usage across all events.

        Note: Token counts may be reported in multiple events. This method
        takes the maximum values seen, as ADK may report cumulative or
        per-turn token counts.

        Args:
            events: List of ADK events

        Returns:
            Dict with prompt_tokens, completion_tokens, total_tokens
        """
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        for event in events:
            if event.usageMetadata:
                usage = event.usageMetadata
                prompt_tokens = max(prompt_tokens, usage.promptTokenCount)
                completion_tokens = max(completion_tokens, usage.candidatesTokenCount)
                total_tokens = max(total_tokens, usage.totalTokenCount)

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    def get_final_text(self, events: List[ADKEvent]) -> str:
        """Extract the final text response from events.

        Args:
            events: List of ADK events

        Returns:
            Combined text from all model response parts
        """
        text_parts: List[str] = []

        for event in events:
            if event.content and event.content.role == "model":
                for part in event.content.parts:
                    if part.text:
                        text_parts.append(part.text)

        return " ".join(text_parts)

    def get_model_version(self, events: List[ADKEvent]) -> Optional[str]:
        """Get the model version from events.

        Args:
            events: List of ADK events

        Returns:
            Model version string or None
        """
        for event in events:
            if event.modelVersion:
                return event.modelVersion

        return None
